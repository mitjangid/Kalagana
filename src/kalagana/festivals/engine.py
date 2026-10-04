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

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

from .. import julian
from ..calendar_month import masa_at, sankranti_rashis_between
from ..hijri import hijri_to_gregorian, hijri_years_for_gregorian
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
    "national_holidays",
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
    kind: str = "festival"

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
    masa_amanta: str
    _ayanamsa: str
    _cache: Dict[str, Tuple[str, str, str, int]]

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

    def at_window(self, window: str) -> Tuple[str, str, str, int]:
        """Return ``(amanta, purnimanta, paksha, within_paksha_tithi)`` at ``window``.

        The month names are taken from the day's sunrise (a lunar month changes
        only at a new moon, which does not fall between sunrise and most of the
        day's windows); this keeps the whole day on one month label.
        """
        cached = self._cache.get(window)
        if cached is not None:
            return cached
        jd = self._reference_tt(window)
        tithi = tithi_number(jd)
        paksha = "Shukla" if tithi <= 15 else "Krishna"
        within = tithi if tithi <= 15 else tithi - 15
        amanta = self.masa_amanta
        from ..calendar_month import LUNAR_MONTHS

        if paksha == "Krishna":
            purnimanta = LUNAR_MONTHS[(LUNAR_MONTHS.index(amanta) + 1) % 12]
        else:
            purnimanta = amanta
        result = (amanta, purnimanta, paksha, within)
        self._cache[window] = result
        return result


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
    m_sunrise = masa_at(jd_s, ayanamsa)
    adhika = m_sunrise.adhika
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
        masa_amanta=m_sunrise.name,
        _ayanamsa=ayanamsa,
        _cache={},
    )


@lru_cache(maxsize=16)
def _day_infos(
    start_ord: int, end_ord: int, lat: float, lon: float, tz: str, ayanamsa: str
) -> Tuple[Optional[_DayInfo], ...]:
    """Day info for an ordinal range, memoised per year/place.

    Building this walks every civil day (sunrise, sunset, moonrise, sankranti,
    masa), which dominates the cost of a festival scan, so identical requests
    (e.g. re-rendering the year or probing several rules) reuse it.
    """
    loc = Location("cache", lat, lon, tz)
    out: List[Optional[_DayInfo]] = []
    d = date.fromordinal(start_ord)
    end = date.fromordinal(end_ord)
    while d <= end:
        out.append(_day_info(d, loc, ayanamsa))
        d += timedelta(days=1)
    return tuple(out)


def _matches_lunar(rule: FestivalRule, info: _DayInfo) -> bool:
    if rule.weekday is not None and info.sun0 != rule.weekday:
        return False
    if rule.nakshatra is not None and NAKSHATRAS[info.nak_at_sunrise - 1] != rule.nakshatra:
        return False
    if rule.sun_in_rashi is not None and info.sun_rashi != rule.sun_in_rashi:
        return False
    amanta, purnimanta, paksha, within = info.at_window(rule.window)
    if rule.paksha is not None and paksha != rule.paksha:
        return False
    if rule.tithi is not None and within != rule.tithi:
        return False
    masa = amanta if rule.month_system == "amanta" else purnimanta
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
    amanta, purnimanta, paksha, within = info.at_window(rule.window)
    masa = amanta if rule.month_system == "amanta" else purnimanta
    t = tithi_name(within if paksha == "Shukla" else within + 15)
    return FestivalOccurrence(
        name=rule.name,
        date=info.day,
        month=masa,
        paksha=paksha,
        tithi=t,
        note=rule.note,
        kind=rule.kind,
    )


def festival_dates(
    year: int,
    loc: Location,
    tradition: str = "north",
    ayanamsa: str = "lahiri",
    month_system: str = "purnimanta",
    include_monthly: bool = True,
    include_islamic: bool = True,
    include_fixed: bool = True,
    rules: Sequence[FestivalRule] = FESTIVAL_RULES,
    kinds: Optional[Sequence[str]] = None,
) -> List[FestivalOccurrence]:
    """Compute all festival occurrences in ``year`` for ``loc``.

    ``tradition`` is one of north, south, tamil, telugu, kannada, malayalam,
    bengali, odia, gujarati, marathi (it selects the regional rule set).
    ``month_system`` is accepted for API compatibility; dates are independent
    of it (only the displayed month name changes).  ``kinds`` optionally
    restricts output to the given categories (e.g. ``("national",)``).
    ``include_islamic`` and ``include_fixed`` switch off the Hijri and the
    fixed Gregorian-date rule groups respectively.
    """
    region = _TRADITION_REGION.get(tradition.strip().lower(), "North")

    def _selected(rule: FestivalRule) -> bool:
        if rule.monthly and not include_monthly:
            return False
        if rule.system == "hijri" and not include_islamic:
            return False
        if rule.system == "fixed" and not include_fixed:
            return False
        if region not in rule.regions:
            return False
        if kinds is not None and rule.kind not in kinds:
            return False
        return True

    chosen_rules = [r for r in rules if _selected(r)]

    # The day-by-day panchang is only needed by lunar and solar rules; fixed
    # and Hijri rules can be answered instantly without it.
    infos: Tuple[_DayInfo, ...] = ()
    if any(r.system in ("lunar", "solar") for r in chosen_rules):
        # Overhang the year so festivals near the January boundary are caught.
        start = date(year, 1, 1) - timedelta(days=20)
        end = date(year, 12, 31) + timedelta(days=20)
        infos = tuple(i for i in _day_infos(
            start.toordinal(), end.toordinal(), loc.lat, loc.lon, loc.tz, ayanamsa
        ) if i is not None)

    occurrences: List[FestivalOccurrence] = []
    for rule in chosen_rules:
        if rule.system == "fixed":
            if rule.fixed_month is None or rule.fixed_day is None:
                continue
            occurrences.append(
                FestivalOccurrence(
                    name=rule.name,
                    date=date(year, rule.fixed_month, rule.fixed_day),
                    month=None,
                    paksha=None,
                    tithi=None,
                    note=rule.note or "Fixed Gregorian date.",
                    kind=rule.kind,
                )
            )
            continue

        if rule.system == "hijri":
            if rule.hijri_month is None or rule.hijri_day is None:
                continue
            for hy in hijri_years_for_gregorian(year):
                gd = hijri_to_gregorian(hy, rule.hijri_month, rule.hijri_day)
                if gd.year != year:
                    continue
                occurrences.append(
                    FestivalOccurrence(
                        name=rule.name,
                        date=gd,
                        month=None,
                        paksha=None,
                        tithi=None,
                        note=rule.note or "Tabular Hijri date.",
                        kind=rule.kind,
                    )
                )
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
                            kind=rule.kind,
                        )
                    )
            continue

        matching = [info for info in infos if _matches_lunar(rule, info)]
        chosen_days = _group_pick([i.day for i in matching], rule.tie_break)
        for cd in chosen_days:
            # Recover the matching info for this day for labeling.
            info = next(i for i in matching if i.day == cd)
            occ = _occurrence(rule, info)
            if rule.offset_days:
                occ = replace(occ, date=occ.date + timedelta(days=rule.offset_days))
            if occ.date.year != year:
                continue
            occurrences.append(occ)

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


def national_holidays(
    year: int,
    loc: Location,
    tradition: str = "north",
    kinds: Sequence[str] = ("national",),
    **kwargs,
) -> List[FestivalOccurrence]:
    """Fixed-date national holidays (Republic/Independence/Gandhi Jayanti).

    Pass ``kinds=("national", "observance")`` to also include the
    commemorative observance days, or any other set of ``kind`` values.
    """
    return festival_dates(year, loc, tradition=tradition, kinds=kinds, **kwargs)


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
