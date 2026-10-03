"""The five panchang limbs: tithi, vara, nakshatra, yoga, karana.

Definitions (all angles in *degrees*, times in Julian Days TT):

* **Tithi** -- floor((Moon apparent longitude - Sun apparent longitude) / 12),
  30 per lunar month, numbered 1-30.
* **Nakshatra** -- floor(sidereal Moon longitude / 13 deg 20'), 27 per zodiac,
  each divided into 4 padas of 3 deg 20'.
* **Yoga** -- floor((sidereal Sun + sidereal Moon) / 13 deg 20'), 27 per cycle.
* **Karana** -- half a tithi: 60 per lunar month (1 fixed + 56 movable cycle
  of 7 + 3 fixed).
* **Vara** -- the weekday reckoned from sunrise, because the Hindu civil day
  begins at sunrise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from . import julian, sun
from .ayanamsa import ayanamsa_degrees
from .location import Location
from .moon import moon_longitude
from .solver import solve_angle
from .sunrise import sunrise_sunset

__all__ = [
    "NAKSHATRAS",
    "YOGAS",
    "KARANAS_MOVABLE",
    "KARANAS_FIXED",
    "VARA_NAMES",
    "elongation",
    "sidereal_moon_longitude",
    "sidereal_sun_longitude",
    "tithi_number",
    "tithi_name",
    "nakshatra_number",
    "nakshatra_pada",
    "yoga_number",
    "karana_number",
    "karana_name",
    "vara_name",
    "Limb",
    "day_limbs",
]

_DEG = math.pi / 180.0
NAKSHATRA_SIZE = 360.0 / 27.0  # 13 deg 20'
PADA_SIZE = NAKSHATRA_SIZE / 4.0  # 3 deg 20'

NAKSHATRAS = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
)

YOGAS = (
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
)

KARANAS_MOVABLE = ("Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti")
KARANAS_FIXED = ("Shakuni", "Chatushpada", "Naga", "Kimstughna")

_TITHI_BASE = (
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi",
)

VARA_NAMES = (
    "Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara",
    "Shukravara", "Shanivara",
)
VARA_NAMES_EN = (
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
)


def elongation(jd_tt: float) -> float:
    """Moon minus Sun apparent longitude in *degrees*, normalised to [0, 360)."""
    return (moon_longitude(jd_tt) - sun.sun_apparent_longitude(jd_tt)) % 360.0


def sidereal_moon_longitude(jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Sidereal (nirayana) Moon longitude in *degrees*."""
    return (moon_longitude(jd_tt) - ayanamsa_degrees(jd_tt, ayanamsa)) % 360.0


def sidereal_sun_longitude(jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Sidereal (nirayana) Sun longitude in *degrees*."""
    return (sun.sun_apparent_longitude(jd_tt) - ayanamsa_degrees(jd_tt, ayanamsa)) % 360.0


def tithi_number(jd_tt: float) -> int:
    """Tithi number 1-30 (1-15 waxing, 16-30 waning)."""
    return int(elongation(jd_tt) // 12.0) + 1


def tithi_name(number: int, *, with_paksha: bool = True) -> str:
    """Name of tithi ``number`` (1-30)."""
    if not 1 <= number <= 30:
        raise ValueError("tithi number must be 1-30")
    if number <= 15:
        if number == 15:
            return "Purnima" if with_paksha else "Purnima"
        name = _TITHI_BASE[number - 1]
        return f"Shukla {name}" if with_paksha else name
    if number == 30:
        return "Amavasya" if with_paksha else "Amavasya"
    name = _TITHI_BASE[number - 16]
    return f"Krishna {name}" if with_paksha else name


def nakshatra_number(jd_tt: float, ayanamsa: str = "lahiri") -> int:
    """Nakshatra number 1-27 for the sidereal Moon longitude."""
    return int(sidereal_moon_longitude(jd_tt, ayanamsa) // NAKSHATRA_SIZE) + 1


def nakshatra_pada(jd_tt: float, ayanamsa: str = "lahiri") -> int:
    """Pada (quarter) 1-4 within the current nakshatra."""
    lon = sidereal_moon_longitude(jd_tt, ayanamsa)
    within = lon % NAKSHATRA_SIZE
    return int(within // PADA_SIZE) + 1


def yoga_number(jd_tt: float, ayanamsa: str = "lahiri") -> int:
    """Yoga number 1-27 from the sum of the sidereal Sun and Moon."""
    s = (sidereal_sun_longitude(jd_tt, ayanamsa) + sidereal_moon_longitude(jd_tt, ayanamsa)) % 360.0
    return int(s // NAKSHATRA_SIZE) + 1


def karana_number(jd_tt: float) -> int:
    """Karana number 1-60 (half-tithi index within the lunar month)."""
    return int(elongation(jd_tt) // 6.0) + 1


def karana_name(number: int) -> str:
    """Name of karana ``number`` (1-60)."""
    if not 1 <= number <= 60:
        raise ValueError("karana number must be 1-60")
    if number == 1:
        return "Kimstughna"
    if number <= 57:
        return KARANAS_MOVABLE[(number - 2) % 7]
    return KARANAS_FIXED[number - 58]


def vara_name(weekday: int, *, english: bool = False) -> str:
    """Vara name for a Python weekday index (0=Monday .. 6=Sunday)."""
    # Convert Monday=0 to Sunday=0 ordering used by the panchang.
    idx = (weekday + 1) % 7
    return (VARA_NAMES_EN if english else VARA_NAMES)[idx]


@dataclass(frozen=True)
class Limb:
    """One limb segment active between two instants (local time)."""

    name: str
    number: int
    start: datetime
    end: datetime


def _angle_crossings(
    func,
    step_deg: float,
    jd_start: float,
    jd_end: float,
) -> List[Tuple[int, float]]:
    """Indices ``m`` and instants where ``func`` crosses ``m * step_deg``.

    ``func`` must be increasing and expressed mod 360.  Returns a list of
    ``(multiple_index, jd)`` for every upward crossing inside the window.
    """
    out: List[Tuple[int, float]] = []
    v0 = func(jd_start) % 360.0
    m = int(math.floor(v0 / step_deg)) + 1
    jd = jd_start
    scan = max(0.02, step_deg / 60.0)
    while jd < jd_end:
        target = (m * step_deg) % 360.0
        jc = solve_angle(func, target, jd, jd_end, scan_step=scan)
        if jc is None:
            break
        out.append((m, jc))
        jd = jc + 1e-5
        m += 1
    return out


def _segments(
    func,
    step_deg: float,
    jd_start: float,
    jd_end: float,
    namer,
    tz,
) -> List[Limb]:
    """Build limb segments covering ``[jd_start, jd_end]``, expressed in ``tz``.

    The limb active at ``jd_start`` is included from the window start, and the
    final segment runs to the window end.  Segment start/end are converted from
    UT to the observer's timezone.
    """
    boundaries = _angle_crossings(func, step_deg, jd_start, jd_end)
    edges = [jd_start] + [jc for _m, jc in boundaries] + [jd_end]
    segs: List[Limb] = []
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        val = func(0.5 * (a + b))
        number = int(val // step_deg) + 1
        segs.append(
            Limb(
                name=namer(number),
                number=number,
                start=julian.jd_to_datetime(a).astimezone(tz),
                end=julian.jd_to_datetime(b).astimezone(tz),
            )
        )
    return segs


def day_limbs(
    day: date,
    loc: Location,
    ayanamsa: str = "lahiri",
) -> Dict[str, object]:
    """Compute all limbs for the Hindu day beginning at sunrise on ``day``.

    Returns a dict with the sunrise/sunset instants (local time), the vara, and
    the lists of tithi, nakshatra, yoga and karana segments active between this
    sunrise and the next.  Handles the cases where two segments occur in one
    day, a segment spans two sunrises, or a tithi is skipped.
    """
    sunrise, sunset = sunrise_sunset(day, loc)
    if sunrise is None:
        raise ValueError("Sun does not rise on this date at this location")
    next_sunrise, _ = sunrise_sunset(_next_day(day), loc)
    if next_sunrise is None:
        next_sunrise = sunrise.replace(hour=23, minute=59)

    jd_start = julian.datetime_to_jd(sunrise) + _delta_t_days(sunrise)
    jd_end = julian.datetime_to_jd(next_sunrise) + _delta_t_days(next_sunrise)

    tz = loc.zoneinfo
    tithis = _segments(elongation, 12.0, jd_start, jd_end, tithi_name, tz)
    naks = _segments(
        lambda jd: sidereal_moon_longitude(jd, ayanamsa),
        NAKSHATRA_SIZE,
        jd_start,
        jd_end,
        lambda n: NAKSHATRAS[(n - 1) % 27],
        tz,
    )
    yogas = _segments(
        lambda jd: (sidereal_sun_longitude(jd, ayanamsa) + sidereal_moon_longitude(jd, ayanamsa)) % 360.0,
        NAKSHATRA_SIZE,
        jd_start,
        jd_end,
        lambda n: YOGAS[(n - 1) % 27],
        tz,
    )
    karanas = _segments(elongation, 6.0, jd_start, jd_end, karana_name, tz)

    return {
        "date": day,
        "location": loc,
        "sunrise": sunrise,
        "sunset": sunset,
        "next_sunrise": next_sunrise,
        "vara": vara_name(day.weekday()),
        "vara_en": vara_name(day.weekday(), english=True),
        "tithi": tithis,
        "nakshatra": naks,
        "yoga": yogas,
        "karana": karanas,
    }


def _next_day(day: date) -> date:
    return date.fromordinal(day.toordinal() + 1)


def _delta_t_days(dt: datetime) -> float:
    from .julian import delta_t

    return delta_t(dt.year + (dt.month - 0.5) / 12.0) / 86400.0
