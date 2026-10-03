"""Julian Day conversion, Delta T and sidereal time.

All functions here are pure: they perform no I/O and depend only on their
arguments plus the standard library.

Units used throughout this module
---------------------------------
* Julian Day (JD) is in *days* (TT/UT continuous count, JD 0 = noon UT on
  -4712-01-01 in the proleptic Julian calendar).
* ``delta_t`` returns *seconds*.
* Sidereal time is returned in *degrees*; divide by 15 for hours.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Tuple

__all__ = [
    "J2000",
    "gregorian_to_jd",
    "julian_to_jd",
    "jd_to_calendar",
    "datetime_to_jd",
    "jd_to_datetime",
    "julian_centuries",
    "julian_millennia",
    "delta_t",
    "jd_tt_from_ut",
    "jd_ut_from_tt",
    "greenwich_mean_sidereal_time",
    "greenwich_apparent_sidereal_time",
]

# J2000.0 epoch (2000 January 1.5 TT).
J2000: float = 2451545.0


def gregorian_to_jd(year: int, month: int, day: float) -> float:
    """Convert a Gregorian calendar date to a Julian Day.

    ``day`` may be fractional (12.5 = noon on the 12th).  Dates use the
    proleptic Gregorian calendar, so this is valid for the whole supported
    1900-2100 range and well beyond.
    """
    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        + b
        - 1524.5
    )


def julian_to_jd(year: int, month: int, day: float) -> float:
    """Convert a Julian calendar date to a Julian Day (``day`` may be fractional)."""
    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        - 1524.5
    )


def jd_to_calendar(jd: float, gregorian: bool = True) -> Tuple[int, int, float]:
    """Convert a Julian Day to a ``(year, month, day)`` tuple.

    ``day`` is fractional.  Set ``gregorian=False`` for the Julian calendar
    (only meaningful before 1582-10-15).
    """
    jd = jd + 0.5
    z = int(math.floor(jd))
    f = jd - z
    if gregorian:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    else:
        a = z
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return year, month, day


def datetime_to_jd(dt: datetime) -> float:
    """Convert an aware UTC ``datetime`` to a Julian Day.

    A naive datetime is interpreted as UTC.
    """
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return gregorian_to_jd(
        dt.year,
        dt.month,
        dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0) / 24.0,
    )


def jd_to_datetime(jd: float) -> datetime:
    """Convert a Julian Day to a timezone-aware UTC ``datetime``."""
    year, month, day = jd_to_calendar(jd, gregorian=True)
    day_int = int(math.floor(day))
    frac = day - day_int
    total_seconds = frac * 86400.0
    hours = int(total_seconds // 3600)
    total_seconds -= hours * 3600
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    base = datetime(year, month, day_int, tzinfo=timezone.utc)
    # Round to the nearest microsecond without ever producing 60 seconds.
    return base + timedelta(hours=hours, minutes=minutes, seconds=seconds)


def julian_centuries(jd: float) -> float:
    """Julian centuries of TT since J2000.0."""
    return (jd - J2000) / 36525.0


def julian_millennia(jd: float) -> float:
    """Julian millennia of TT since J2000.0."""
    return (jd - J2000) / 365250.0


def _decimal_year(jd: float) -> float:
    """Decimal year (TT) used by the Delta T polynomials."""
    y, m, d = jd_to_calendar(jd, gregorian=True)
    # Approximate: day-of-year fraction over a mean year length.
    return y + (m - 0.5) / 12.0


# ---------------------------------------------------------------------------
# Delta T (TT - UT1), Espenak & Meeus (2006) polynomial expressions.
# Source: NASA/GSFC "Polynomial Expressions for Delta T" (Espenak & Meeus).
# ---------------------------------------------------------------------------
def delta_t(year: float) -> float:
    """Return Delta T = TT - UT1 in *seconds* for a decimal ``year``.

    Uses the Espenak & Meeus (2006) piecewise polynomial expressions.  The
    result is deterministic and requires no external data.  Accuracy is a few
    seconds across 1900-2100, which is far below the resolution of the
    panchang limbs computed here.
    """
    y = year
    if y < -500:
        u = (y - 1820.0) / 100.0
        return -20.0 + 32.0 * u * u
    if y < 500:
        u = y / 100.0
        return (
            10583.6
            - 1014.41 * u
            + 33.78311 * u**2
            - 5.952053 * u**3
            - 0.1798452 * u**4
            + 0.022174192 * u**5
            + 0.0090316521 * u**6
        )
    if y < 1600:
        u = (y - 1000.0) / 100.0
        return (
            1574.2
            - 556.01 * u
            + 71.23472 * u**2
            + 0.319781 * u**3
            - 0.8503463 * u**4
            - 0.005050998 * u**5
            + 0.0083572073 * u**6
        )
    if y < 1700:
        t = y - 1600.0
        return 120.0 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129.0
    if y < 1800:
        t = y - 1700.0
        return (
            8.83
            + 0.1603 * t
            - 0.0059285 * t**2
            + 0.00013336 * t**3
            - t**4 / 1174000.0
        )
    if y < 1860:
        t = y - 1800.0
        return (
            13.72
            - 0.332447 * t
            + 0.0068612 * t**2
            + 0.0041116 * t**3
            - 0.00037436 * t**4
            + 0.0000121272 * t**5
            - 0.0000001699 * t**6
            + 0.000000000875 * t**7
        )
    if y < 1900:
        t = y - 1860.0
        return (
            7.62
            + 0.5737 * t
            - 0.251754 * t**2
            + 0.01680668 * t**3
            - 0.0004473624 * t**4
            + t**5 / 233174.0
        )
    if y < 1920:
        t = y - 1900.0
        return -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    if y < 1941:
        t = y - 1920.0
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if y < 1961:
        t = y - 1950.0
        return 29.07 + 0.407 * t - t**2 / 233.0 + t**3 / 2547.0
    if y < 1986:
        t = y - 1975.0
        return 45.45 + 1.067 * t - t**2 / 260.0 - t**3 / 718.0
    if y < 2005:
        t = y - 2000.0
        return (
            63.86
            + 0.3345 * t
            - 0.060374 * t**2
            + 0.0017275 * t**3
            + 0.000651814 * t**4
            + 0.00002373599 * t**5
        )
    if y < 2050:
        t = y - 2000.0
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    if y < 2150:
        u = (y - 1820.0) / 100.0
        return -20.0 + 32.0 * u * u - 0.5628 * (2150.0 - y)
    u = (y - 1820.0) / 100.0
    return -20.0 + 32.0 * u * u


def jd_tt_from_ut(jd_ut: float) -> float:
    """Convert a UT Julian Day to a TT Julian Day using ``delta_t``."""
    return jd_ut + delta_t(_decimal_year(jd_ut)) / 86400.0


def jd_ut_from_tt(jd_tt: float) -> float:
    """Convert a TT Julian Day to a UT Julian Day using ``delta_t``."""
    return jd_tt - delta_t(_decimal_year(jd_tt)) / 86400.0


def greenwich_mean_sidereal_time(jd_ut: float) -> float:
    """Greenwich Mean Sidereal Time in *degrees* (Meeus, ch. 12).

    Valid for the supported range; accuracy ~0.1 second of time.
    """
    t = (jd_ut - J2000) / 36525.0
    theta = (
        280.46061837
        + 360.98564736629 * (jd_ut - J2000)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0
    )
    return theta % 360.0


def greenwich_apparent_sidereal_time(jd_ut: float) -> float:
    """Greenwich Apparent Sidereal Time in *degrees* (GMST plus equation of equinoxes)."""
    t = (jd_ut - J2000) / 36525.0
    # Mean obliquity (Meeus 22.2) and nutation in longitude (dominant term).
    eps0 = (
        23.0
        + 26.0 / 60.0
        + 21.448 / 3600.0
        - (46.8150 * t + 0.00059 * t * t - 0.001813 * t**3) / 3600.0
    )
    omega = math.radians(125.04452 - 1934.136261 * t)
    dpsi = -17.20 * math.sin(omega) / 3600.0  # degrees
    eps = math.radians(eps0)
    equation_of_equinoxes = dpsi * math.cos(eps)  # degrees
    return (greenwich_mean_sidereal_time(jd_ut) + equation_of_equinoxes) % 360.0
