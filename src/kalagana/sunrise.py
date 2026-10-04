"""Sunrise, sunset, moonrise, moonset and transit times.

Method: the altitude of the body is evaluated directly from its apparent
right ascension/declination and the local apparent sidereal time, then the
crossing of the standard altitude is located with a scan-and-bisect root
finder.  This is the same approach described in Meeus, *Astronomical
Algorithms*, ch. 15.

Standard altitudes
------------------
* Sun: ``-0.833 deg`` by default (upper limb at the horizon, including
  refraction); pass ``-0.5667`` for the centre of the disc.
* Moon: ``+0.125 deg`` by default (Meeus's value for the Moon's centre,
  balancing refraction against the Moon's large horizontal parallax).

Polar cases return ``None`` rather than raising.

Units
-----
* Latitude/longitude and altitudes are *degrees*.
* Julian Days are *mixed TT/UT* as noted per function; clock outputs are
  timezone-aware datetimes in the observer's zone.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timezone
from typing import Optional, Tuple

from . import julian, sun
from .location import Location
from .moon import moon_ra_dec
from .solver import find_crossing

__all__ = [
    "SUN_ALTITUDE_STANDARD",
    "SUN_ALTITUDE_CENTRE",
    "MOON_ALTITUDE_STANDARD",
    "sun_altitude",
    "moon_altitude",
    "sunrise_sunset",
    "moonrise_moonset",
    "solar_noon",
]

_DEG = math.pi / 180.0

SUN_ALTITUDE_STANDARD = -0.833
SUN_ALTITUDE_CENTRE = -0.5667
MOON_ALTITUDE_STANDARD = 0.125


def _local_sidereal_degrees(jd_ut: float, lon_east: float) -> float:
    return (julian.greenwich_apparent_sidereal_time(jd_ut) + lon_east) % 360.0


def sun_altitude(jd_ut: float, lat: float, lon: float) -> float:
    """Geometric altitude of the Sun's centre in *degrees* at ``jd_ut`` (UT)."""
    jd_tt = julian.jd_tt_from_ut(jd_ut)
    dec = sun.sun_declination(jd_tt) * _DEG
    ra = sun.sun_right_ascension(jd_tt)
    h = (_local_sidereal_degrees(jd_ut, lon) - ra) * _DEG
    phi = lat * _DEG
    sin_alt = math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(h)
    return math.asin(max(-1.0, min(1.0, sin_alt))) / _DEG


def moon_altitude(jd_ut: float, lat: float, lon: float) -> float:
    """Geometric altitude of the Moon's centre in *degrees* at ``jd_ut`` (UT)."""
    jd_tt = julian.jd_tt_from_ut(jd_ut)
    ra, dec = moon_ra_dec(jd_tt)
    dec *= _DEG
    h = (_local_sidereal_degrees(jd_ut, lon) - ra) * _DEG
    phi = lat * _DEG
    sin_alt = math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(h)
    return math.asin(max(-1.0, min(1.0, sin_alt))) / _DEG


def _jd_of_local_midnight(day: date, loc: Location) -> float:
    """Julian Day (UT) of local midnight at the start of ``day``."""
    local = datetime(day.year, day.month, day.day, tzinfo=loc.zoneinfo)
    return julian.datetime_to_jd(local.astimezone(timezone.utc))


def _to_local(jd_ut: float, loc: Location) -> datetime:
    return julian.jd_to_datetime(jd_ut).astimezone(loc.zoneinfo)


def _rise_set(
    day: date,
    loc: Location,
    altitude_func,
    h0: float,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Shared rise/set driver for the Sun and Moon on a local civil ``day``."""
    jd0 = _jd_of_local_midnight(day, loc)
    jd1 = jd0 + 1.0
    step = 1.0 / 96.0  # 15 minutes; fine enough for both bodies' motion.

    def f(jd: float) -> float:
        return altitude_func(jd, loc.lat, loc.lon) - h0

    rise = find_crossing(f, jd0, jd1, step=step, ascending=True)
    sett = find_crossing(f, jd0, jd1, step=step, ascending=False)
    return (
        _to_local(rise, loc) if rise is not None else None,
        _to_local(sett, loc) if sett is not None else None,
    )


def sunrise_sunset(
    day: date,
    loc: Location,
    altitude: float = SUN_ALTITUDE_STANDARD,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Local sunrise and sunset for ``day``.

    Returns ``(sunrise, sunset)`` as timezone-aware datetimes in ``loc.tz``, or
    ``None`` for either when the Sun does not cross the altitude (polar night
    or midnight sun).  ``altitude`` selects the standard altitude: ``-0.833``
    for the upper limb with refraction, ``-0.5667`` for the centre.
    """
    return _rise_set(day, loc, sun_altitude, altitude)


def moonrise_moonset(
    day: date,
    loc: Location,
    altitude: float = MOON_ALTITUDE_STANDARD,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Local moonrise and moonset for ``day`` (``None`` if it does not occur)."""
    return _rise_set(day, loc, moon_altitude, altitude)


def solar_noon(day: date, loc: Location) -> Optional[datetime]:
    """Local solar transit (apparent noon) for ``day``, or ``None`` if undefined."""
    jd0 = _jd_of_local_midnight(day, loc)
    jd1 = jd0 + 1.0

    # Transit is where the altitude is maximal; a coarse scan plus a ternary
    # search is robust and avoids signed-hour-angle edge cases.
    best_jd = jd0
    best_alt = -999.0
    step = 1.0 / 288.0
    jd = jd0
    while jd <= jd1:
        a = sun_altitude(jd, loc.lat, loc.lon)
        if a > best_alt:
            best_alt = a
            best_jd = jd
        jd += step
    # Refine around the coarse maximum.
    lo, hi = best_jd - step, best_jd + step
    for _ in range(60):
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        if sun_altitude(m1, loc.lat, loc.lon) < sun_altitude(m2, loc.lat, loc.lon):
            lo = m1
        else:
            hi = m2
    return _to_local((lo + hi) / 2.0, loc)
