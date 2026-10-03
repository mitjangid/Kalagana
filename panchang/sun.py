"""Solar position: apparent geocentric longitude, RA/dec, equation of time.

Formula source: Jean Meeus, *Astronomical Algorithms*, 2nd ed., chapter 25
("Solar Coordinates"), including the nutation and aberration corrections from
the same chapter.  The series kept here is rated by Meeus at about 0.01 degree
accuracy, which is sufficient for panchang limb boundaries.

Units
-----
* Longitudes/latitudes are in *degrees*.
* Right ascension is in *degrees* (divide by 15 for hours).
* ``equation_of_time`` returns *minutes*.
"""

from __future__ import annotations

import math

from .julian import julian_centuries

__all__ = [
    "mean_obliquity",
    "sun_geometric_longitude",
    "sun_apparent_longitude",
    "sun_declination",
    "sun_right_ascension",
    "equation_of_time",
]

_DEG = math.pi / 180.0


def _norm360(x: float) -> float:
    return x % 360.0


def mean_obliquity(jd_tt: float) -> float:
    """Mean obliquity of the ecliptic in *degrees* (Meeus 22.2, without nutation)."""
    t = julian_centuries(jd_tt)
    return (
        23.0
        + 26.0 / 60.0
        + 21.448 / 3600.0
        - (46.8150 * t + 0.00059 * t * t - 0.001813 * t**3) / 3600.0
    )


def sun_geometric_longitude(jd_tt: float) -> float:
    """Sun's geometric longitude in *degrees* (true longitude, no corrections)."""
    t = julian_centuries(jd_tt)
    l0 = _norm360(280.46646 + 36000.76983 * t + 0.0003032 * t * t)
    m = _norm360(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    mr = m * _DEG
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(mr)
        + (0.019993 - 0.000101 * t) * math.sin(2.0 * mr)
        + 0.000289 * math.sin(3.0 * mr)
    )
    return _norm360(l0 + c)


def sun_apparent_longitude(jd_tt: float) -> float:
    """Sun's apparent geocentric longitude in *degrees*.

    Applies the nutation in longitude and the aberration correction
    (Meeus ch. 25), giving ~0.01 degree accuracy.
    """
    true_long = sun_geometric_longitude(jd_tt)
    t = julian_centuries(jd_tt)
    omega = (125.04 - 1934.136 * t) * _DEG
    return _norm360(true_long - 0.00569 - 0.00478 * math.sin(omega))


def sun_declination(jd_tt: float) -> float:
    """Sun's apparent declination in *degrees*."""
    t = julian_centuries(jd_tt)
    eps0 = mean_obliquity(jd_tt)
    omega = (125.04 - 1934.136 * t) * _DEG
    # Meeus 25.8: apparent obliquity corrected for nutation.
    eps = (eps0 + 0.00256 * math.cos(omega)) * _DEG
    lam = sun_apparent_longitude(jd_tt) * _DEG
    return math.asin(math.sin(eps) * math.sin(lam)) / _DEG


def sun_right_ascension(jd_tt: float) -> float:
    """Sun's apparent right ascension in *degrees*."""
    t = julian_centuries(jd_tt)
    eps0 = mean_obliquity(jd_tt)
    omega = (125.04 - 1934.136 * t) * _DEG
    eps = (eps0 + 0.00256 * math.cos(omega)) * _DEG
    lam = sun_apparent_longitude(jd_tt) * _DEG
    # Meeus 25.6 (apparent RA uses the same form with apparent lambda/eps).
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    return _norm360(ra / _DEG)


def equation_of_time(jd_tt: float) -> float:
    """Equation of time in *minutes* (apparent solar time minus mean solar time).

    Implemented via the difference between the mean and apparent right
    ascension, reduced through the obliquity (Meeus ch. 28).
    """
    t = julian_centuries(jd_tt)
    l0 = _norm360(280.4664567 + 360007.6982779 * t + 0.03032028 * t * t)
    alpha = sun_right_ascension(jd_tt)
    # Meeus 28.3: E = L0 - 0.0057183 - alpha + nutation*cos(eps)
    omega = (125.04 - 1934.136 * t) * _DEG
    dpsi = -0.00478 * math.sin(omega)  # degrees (matches the aberration group above)
    eps = mean_obliquity(jd_tt) * _DEG
    e_deg = l0 - 0.0057183 - alpha + dpsi * math.cos(eps)
    # Normalise into (-180, 180].
    e_deg = (e_deg + 180.0) % 360.0 - 180.0
    return e_deg * 4.0  # degrees -> minutes (1 deg = 4 min of time)
