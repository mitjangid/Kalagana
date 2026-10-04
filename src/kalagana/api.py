"""High-level public API for the Kalagana package."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional

from . import calendar_month, eras, julian, limbs, muhurta
from .ayanamsa import ayanamsa_degrees
from .limbs import Limb, NAKSHATRAS, YOGAS
from .location import Location
from .moon import moon_latitude
from .sunrise import moonrise_moonset, sunrise_sunset

__all__ = [
    "Panchang", "daily_panchang", "eclipses_for_year", "Eclipse",
    "Kundali", "GrahaPosition", "kundali", "kundali_match",
    "Rashifal", "daily_rashifal", "rashifal_for_all",
]

from .festivals import festivals_for_year  # noqa: E402  (re-exported)
from .jyotish import (  # noqa: E402
    GrahaPosition,
    Kundali,
    Rashifal,
    daily_rashifal,
    kundali,
    kundali_match,
    rashifal_for_all,
)


@dataclass
class Panchang:
    """A full panchang for one civil day at one place."""

    date: date
    location: Location
    sunrise: Optional[datetime]
    sunset: Optional[datetime]
    moonrise: Optional[datetime]
    moonset: Optional[datetime]
    vara: str
    vara_en: str
    tithi: List[Limb]
    nakshatra: List[Limb]
    yoga: List[Limb]
    karana: List[Limb]
    paksha: str
    masa_amanta: str
    masa_purnimanta: str
    samvat: int
    shaka: int
    samvatsara: str
    ritu: str
    ayana: str
    muhurta: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """A JSON-serialisable view (datetimes as ISO strings)."""

        def iso(dt: Optional[datetime]) -> Optional[str]:
            return dt.isoformat() if dt else None

        return {
            "date": self.date.isoformat(),
            "location": {
                "name": self.location.name,
                "lat": self.location.lat,
                "lon": self.location.lon,
                "tz": self.location.tz,
            },
            "sunrise": iso(self.sunrise),
            "sunset": iso(self.sunset),
            "moonrise": iso(self.moonrise),
            "moonset": iso(self.moonset),
            "vara": self.vara,
            "vara_en": self.vara_en,
            "paksha": self.paksha,
            "masa_amanta": self.masa_amanta,
            "masa_purnimanta": self.masa_purnimanta,
            "samvat": self.samvat,
            "shaka": self.shaka,
            "samvatsara": self.samvatsara,
            "ritu": self.ritu,
            "ayana": self.ayana,
            "tithi": [_limb_dict(x) for x in self.tithi],
            "nakshatra": [_limb_dict(x) for x in self.nakshatra],
            "yoga": [_limb_dict(x) for x in self.yoga],
            "karana": [_limb_dict(x) for x in self.karana],
            "muhurta": _muhurta_dict(self.muhurta),
        }


def _limb_dict(limb: Limb) -> Dict[str, object]:
    return {
        "name": limb.name,
        "number": limb.number,
        "start": limb.start.isoformat(),
        "end": limb.end.isoformat(),
    }


def _muhurta_dict(m: Dict[str, object]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for key, val in m.items():
        if isinstance(val, muhurta.MuhurtaWindow):
            out[key] = {
                "name": val.name,
                "start": val.start.isoformat(),
                "end": val.end.isoformat(),
            }
        elif isinstance(val, list):
            out[key] = [
                {"name": w.name, "start": w.start.isoformat(), "end": w.end.isoformat()}
                for w in val
            ]
        elif isinstance(val, dict):
            out[key] = {
                k: [
                    {"name": w.name, "start": w.start.isoformat(), "end": w.end.isoformat()}
                    for w in ws
                ]
                for k, ws in val.items()
            }
        else:
            out[key] = val
    return out


def daily_panchang(
    day: date,
    loc: Location,
    ayanamsa: str = "lahiri",
    month_system: str = "purnimanta",
    with_muhurta: bool = True,
) -> Panchang:
    """Compute the full panchang for ``day`` at ``loc``.

    ``month_system`` selects which month name is used for the ``paksha`` and
    era summary; both amanta and purnimanta names are always reported.
    ``with_muhurta=False`` skips Rahu Kalam, Choghadiya, Hora, etc. for speed.
    """
    info = limbs.day_limbs(day, loc, ayanamsa=ayanamsa)
    sunrise = info["sunrise"]
    sunset = info["sunset"]
    moonrise, moonset = moonrise_moonset(day, loc)

    jd_s = julian.datetime_to_jd(sunrise)
    paksha = calendar_month.paksha_at(jd_s)
    amanta = calendar_month.masa_at(jd_s, ayanamsa)
    pn = calendar_month.purnimanta_name(jd_s, ayanamsa)
    sid_sun = limbs.sidereal_sun_longitude(jd_s, ayanamsa)

    muh: Dict[str, object] = {}
    if with_muhurta:
        muh = muhurta.day_timings(day, loc)

    return Panchang(
        date=day,
        location=loc,
        sunrise=sunrise,
        sunset=sunset,
        moonrise=moonrise,
        moonset=moonset,
        vara=info["vara"],
        vara_en=info["vara_en"],
        tithi=info["tithi"],
        nakshatra=info["nakshatra"],
        yoga=info["yoga"],
        karana=info["karana"],
        paksha=paksha,
        masa_amanta=amanta.display,
        masa_purnimanta=pn,
        samvat=eras.vikram_samvat(day),
        shaka=eras.shaka_year(day),
        samvatsara=eras.samvatsara_name(eras.shaka_year(day)),
        ritu=eras.ritu(sid_sun),
        ayana=eras.ayana(sid_sun),
        muhurta=muh,
    )


@dataclass(frozen=True)
class Eclipse:
    """An approximate eclipse event (see ``eclipses_for_year`` caveats)."""

    kind: str            # "solar" or "lunar"
    date: date
    greatest: datetime
    moon_latitude: float
    eclipse_type: str    # "total", "annular", "partial", "penumbral"
    approximate: bool = True

    def __str__(self) -> str:
        return f"{self.date.isoformat()}  {self.eclipse_type} {self.kind} eclipse"


def eclipses_for_year(year: int, loc: Location) -> List[Eclipse]:
    """List solar and lunar eclipses in ``year`` (approximate detector).

    This uses the Moon's ecliptic latitude at new/full moon to decide whether
    an eclipse occurs, and labels the type from the latitude magnitude.  It
    gives correct *dates* for eclipse windows but not the precise contact
    times or magnitudes of Besselian-element methods -- use it as an indicator,
    and consult an authoritative ephemeris for exact circumstances.
    """
    from .calendar_month import next_full_moon, next_new_moon

    start = julian.datetime_to_jd(datetime(year, 1, 1))
    end = julian.datetime_to_jd(datetime(year + 1, 1, 1))
    out: List[Eclipse] = []

    # Solar: new moons.
    jd = next_new_moon(start)
    while jd < end:
        beta = abs(moon_latitude(jd))
        if beta < 1.5:
            if beta < 0.15:
                etype = "total"
            elif beta < 0.9:
                etype = "annular/partial"
            else:
                etype = "partial"
            dt = julian.jd_to_datetime(jd).astimezone(loc.zoneinfo)
            out.append(Eclipse("solar", dt.date(), dt, beta, etype))
        jd = next_new_moon(jd + 1.0)

    # Lunar: full moons.
    jd = next_full_moon(start)
    while jd < end:
        beta = abs(moon_latitude(jd))
        if beta < 1.5:
            if beta < 0.4:
                etype = "total"
            elif beta < 1.0:
                etype = "partial"
            else:
                etype = "penumbral"
            dt = julian.jd_to_datetime(jd).astimezone(loc.zoneinfo)
            out.append(Eclipse("lunar", dt.date(), dt, beta, etype))
        jd = next_full_moon(jd + 1.0)

    out.sort(key=lambda e: e.greatest)
    return out
