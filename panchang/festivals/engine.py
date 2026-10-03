"""Rule interpreter: compute festival dates for a year and place.

The engine never stores dates.  It walks each civil day, evaluates the panchang
for that day, and tests it against every :class:`FestivalRule`.  A rule matches
when the requested tithi is present during the requested time window in the
requested (purnimanta) lunar month, subject to any nakshatra/weekday/rashi
condition and the adhika-masa policy.

When a tithi spans two sunrises (vriddhi) two days can match; ``tie_break``
selects which.  Skipped (kshaya) tithis simply produce no match that month.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from .. import julian
from ..calendar_month import masa_at, sankranti_rashis_between
from ..limbs import (
    NAKSHATRAS,
    nakshatra_number,
    sidereal_sun_longitude,
    tithi_number,
    tithi_name,
)
from ..location import Location
from ..moon import moon_longitude
from ..sunrise import sunrise_sunset, moonrise_moonset
from .rules import FESTIVAL_RULES, FestivalRule

__all__ = [
    "FestivalOccurrence",
    "festival_dates",
    "festivals_for_year",
    "find_next",
]

_TRADITION_REGION = {
    "north": "North",
    "south": "South",
    "tamil": "South",
    "telugu": "South",
    "kannada": "South",
    "malayalam": "South",
    "bengali": "East",
    "east": "East",
    "odia": "East",
    "gujarati": "West",
    "marathi": "West",
    "west": "West",
}


@dataclass(frozen=True)
class FestivalOccurrence:
    """A computed festival date."""

    name: str
    date: date
    month: Optional[str]
    paksha: Optional[str]
    tithi: Optional[str]
    note: str = ""

    def __str__(self) -> str:
        when = self.month and f"{self.month} {self.paksha} {self.tithi}"
        return f"{self.date.isoformat()}  {self.name}" + (f"  [{when}]" if when else "")


def _jd_tt(dt: datetime) -> float:
    from ..julian import delta_t

    jd = julian.datetime_to_jd(dt)
    return jd + delta_t(dt.year + (dt.month - 0.5) / 12.0) / 86400.0


@dataclass
class _DayInfo:
    day: date
    sunrise: datetime
    sunset: datetime
    next_sunrise: datetime
    moonrise: Optional[datetime]
    sun0: int
    tithi_at_sunrise: int
    nak_at_sunrise: int
    sun_rashi: int
    sankrantis: Tuple[int, ...]
    adhika: bool
    _ayanamsa: str
    _cache: Dict[str, Tuple[Optional[str], Optional[str], Optional[int]]]

    def _reference_tt(self, window: str) -> float:
        if window == "sunrise":
            return _jd_tt(self.sunrise)
        if window == "arunodaya":
            return _jd_tt(self.sunrise - timedelta(minutes=96))
        if window == "madhyahna":
            return _jd_tt(self.sunrise + (self.sunset - self.sunrise) / 2)
        if window == "aparahna":
            return _jd_tt(self.sunrise + (self.sunset - self.sunrise) * 3 / 5)
        if window == "pradosh":
            return _jd_tt(self.sunset + timedelta(minutes=45))
        if window == "nishita":
            return _jd_tt(self.sunset + (self.next_sunrise - self.sunset) / 2)
        if window == "moonrise":
            return _jd_tt(self.moonrise) if self.moonrise else _jd_tt(self.sunset)
        raise ValueError(f"unknown window {window!r}")

    def at_window(self, window: str) -> Tuple[str, str, int]:
        """Return ``(masa, paksha, within_paksha_tithi)`` at ``window``."""
        cached = self._cache.get(window)
        if cached is not None:
            m, p, t = cached
            return (m or "", p or "", t or 0)
        jd = self._reference_tt(window)
        tithi = tithi_number(jd)
        paksha = "Shukla" if tithi <= 15 else "Krishna"
        within = tithi if tithi <= 15 else tithi - 15
        m = masa_at(jd, self._ayanamsa)
        name = m.name
        if paksha == "Krishna":
            from ..calendar_month import LUNAR_MONTHS

            name = LUNAR_MONTHS[(LUNAR_MONTHS.index(m.name) + 1) % 12]
        self._cache[window] = (name, paksha, within)
        return (name, paksha, within)


def _day_info(day: date, loc: Location, ayanamsa: str) -> Optional[_DayInfo]:
    sunrise, sunset = sunrise_sunset(day, loc)
    if sunrise is None or sunset is None:
        return None
    next_sunrise, _ = sunrise_sunset(date.fromordinal(day.toordinal() + 1), loc)
    if next_sunrise is None:
        return None
    moonrise, _ms = moonrise_moonset(day, loc)

    jd_s = _jd_tt(sunrise)
    jd_ns = _jd_tt(next_sunrise)
    sankrantis = tuple(r for r, _t in sankranti_rashis_between(jd_s, jd_ns, ayanamsa))
    sun_rashi = int(sidereal_sun_longitude(jd_s, ayanamsa) // 30.0)
    adhika = masa_at(jd_s, ayanamsa).adhika
    return _DayInfo(
        day=day,
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        moonrise=moonrise,
        sun0=(day.weekday() + 1) % 7,
        tithi_at_sunrise=tithi_number(jd_s),
        nak_at_sunrise=nakshatra_number(jd_s, ayanamsa),
        sun_rashi=sun_rashi,
        sankrantis=sankrantis,
        adhika=adhika,
        _ayanamsa=ayanamsa,
        _cache={},
    )


def _matches_lunar(rule: FestivalRule, info: _DayInfo) -> bool:
    if rule.weekday is not None and info.sun0 != rule.weekday:
        return False
    if rule.nakshatra is not None and NAKSHATRAS[info.nak_at_sunrise - 1] != rule.nakshatra:
        return False
    if rule.sun_in_rashi is not None and info.sun_rashi != rule.sun_in_rashi:
        return False
    masa, paksha, within = info.at_window(rule.window)
    if rule.paksha is not None and paksha != rule.paksha:
        return False
    if rule.tithi is not None and within != rule.tithi:
        return False
    if rule.masa is not None and masa != rule.masa:
        return False
    # Adhika-masa policy.
    adhika = info.adhika
    if adhika and rule.adhika_policy == "nija":
        return False
    if (not adhika) and rule.adhika_policy == "adhika":
        return False
    return True


def _group_pick(days: List[date], tie_break: str) -> List[date]:
    """Collapse runs of consecutive matching days to one date each."""
    if not days:
        return []
    days = sorted(days)
    groups: List[List[date]] = [[days[0]]]
    for d in days[1:]:
        if (d - groups[-1][-1]).days <= 4:
            groups[-1].append(d)
        else:
            groups.append([d])
    out = []
    for g in groups:
        out.append(g[0] if tie_break == "first" else g[-1])
    return out


def _occurrence(rule: FestivalRule, info: _DayInfo) -> FestivalOccurrence:
    masa, paksha, within = info.at_window(rule.window)
    t = tithi_name(within if paksha == "Shukla" else within + 15)
    return FestivalOccurrence(
        name=rule.name,
        date=info.day,
        month=masa,
        paksha=paksha,
        tithi=t,
        note=rule.note,
    )


def festival_dates(
    year: int,
    loc: Location,
    tradition: str = "north",
    ayanamsa: str = "lahiri",
    month_system: str = "purnimanta",
    include_monthly: bool = True,
    rules: Sequence[FestivalRule] = FESTIVAL_RULES,
) -> List[FestivalOccurrence]:
    """Compute all festival occurrences in ``year`` for ``loc``.

    ``tradition`` is one of north, south, tamil, telugu, kannada, malayalam,
    bengali, odia, gujarati, marathi (it selects the regional rule set).
    ``month_system`` is accepted for API compatibility; dates are independent
    of it (only the displayed month name changes).
    """
    region = _TRADITION_REGION.get(tradition.strip().lower(), "North")

    # Build day info for a window that overhangs the year so festivals near
    # the January boundary are captured, then filter to the requested year.
    start = date(year, 1, 1) - timedelta(days=20)
    end = date(year, 12, 31) + timedelta(days=20)
    infos: List[_DayInfo] = []
    d = start
    while d <= end:
        info = _day_info(d, loc, ayanamsa)
        if info is not None:
            infos.append(info)
        d += timedelta(days=1)

    occurrences: List[FestivalOccurrence] = []
    for rule in rules:
        if rule.monthly and not include_monthly:
            continue
        if region not in rule.regions:
            continue

        if rule.system == "solar":
            hit_days: List[date] = []
            for info in infos:
                if rule.sankranti_rashi is None:
                    if info.sankrantis:
                        hit_days.append(info.day)
                elif rule.sankranti_rashi in info.sankrantis:
                    hit_days.append(info.day)
            if rule.name == "Lohri":
                hit_days = [d - timedelta(days=1) for d in hit_days]
            for hd in hit_days:
                if hd.year == year:
                    occurrences.append(
                        FestivalOccurrence(
                            name=rule.name,
                            date=hd,
                            month=None,
                            paksha=None,
                            tithi=None,
                            note=rule.note or "Solar (sankranti-based).",
                        )
                    )
            continue

        matching = [info for info in infos if _matches_lunar(rule, info)]
        chosen_days = _group_pick([i.day for i in matching], rule.tie_break)
        for cd in chosen_days:
            if cd.year != year:
                continue
            # Recover the matching info for this day for labeling.
            info = next(i for i in matching if i.day == cd)
            occurrences.append(_occurrence(rule, info))

    occurrences.sort(key=lambda o: (o.date, o.name))
    return occurrences


def festivals_for_year(
    year: int,
    loc: Location,
    tradition: str = "north",
    **kwargs,
) -> List[FestivalOccurrence]:
    """Convenience alias for :func:`festival_dates`."""
    return festival_dates(year, loc, tradition=tradition, **kwargs)


def find_next(
    name: str,
    after: date,
    loc: Location,
    tradition: str = "north",
    ayanamsa: str = "lahiri",
    max_years: int = 3,
) -> Optional[FestivalOccurrence]:
    """Find the next occurrence of the named festival on/after ``after``."""
    y = after.year
    for _ in range(max_years):
        occs = festival_dates(y, loc, tradition=tradition, ayanamsa=ayanamsa)
        for o in occs:
            if o.name.lower() == name.lower() and o.date >= after:
                return o
        y += 1
    return None
