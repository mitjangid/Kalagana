"""Lunar position: longitude, latitude and distance (Meeus chapter 47).

Source: Jean Meeus, *Astronomical Algorithms*, 2nd ed., chapter 47
("Position of the Moon").  The periodic term tables 47.A (longitude and
distance) and 47.B (latitude) are reproduced here as module-level tuples.
Meeus rates the resulting longitude to about 10 arcseconds, far better than
the ~1 arcminute needed to resolve tithi boundaries to a minute.

Units
-----
* Longitudes/latitudes are in *degrees*.
* Distance is in *kilometres*.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from .julian import julian_centuries

__all__ = [
    "moon_longitude",
    "moon_latitude",
    "moon_distance",
    "moon_position",
    "moon_ra_dec",
    "fundamental_arguments",
]

_DEG = math.pi / 180.0

# Table 47.A: arguments (D, M, M', F) and coefficients for Sum(l) in 1e-6 deg
# and Sum(r) in 1e-3 km.
_TERMS_LR: Tuple[Tuple[int, int, int, int, int, int], ...] = (
    (0, 0, 1, 0, 6288774, -20905355),
    (2, 0, -1, 0, 1274027, -3699111),
    (2, 0, 0, 0, 658314, -2955968),
    (0, 0, 2, 0, 213618, -569925),
    (0, 1, 0, 0, -185116, 48888),
    (0, 0, 0, 2, -114332, -3149),
    (2, 0, -2, 0, 58793, 246158),
    (2, -1, -1, 0, 57066, -152138),
    (2, 0, 1, 0, 53322, -170733),
    (2, -1, 0, 0, 45758, -204586),
    (0, 1, -1, 0, -40923, -129620),
    (1, 0, 0, 0, -34720, 108743),
    (0, 1, 1, 0, -30383, 104755),
    (2, 0, 0, -2, 15327, 10321),
    (0, 0, 1, 2, -12528, 0),
    (0, 0, 1, -2, 10980, 79661),
    (4, 0, -1, 0, 10675, -34782),
    (0, 0, 3, 0, 10034, -23210),
    (4, 0, -2, 0, 8548, -21636),
    (2, 1, -1, 0, -7888, 24208),
    (2, 1, 0, 0, -6766, 30824),
    (1, 0, -1, 0, -5163, -8379),
    (1, 1, 0, 0, 4987, -16675),
    (2, -1, 1, 0, 4036, -12831),
    (2, 0, 2, 0, 3994, -10445),
    (4, 0, 0, 0, 3861, -11650),
    (2, 0, -3, 0, 3665, 14403),
    (0, 1, -2, 0, -2689, -7003),
    (2, 0, -1, 2, -2602, 0),
    (2, -1, -2, 0, 2390, 10056),
    (1, 0, 1, 0, -2348, 6322),
    (2, -2, 0, 0, 2236, -9884),
    (0, 1, 2, 0, -2120, 5751),
    (0, 2, 0, 0, -2069, 0),
    (2, -2, -1, 0, 2048, -4950),
    (2, 0, 1, -2, -1773, 4130),
    (2, 0, 0, 2, -1595, 0),
    (4, -1, -1, 0, 1215, -3958),
    (0, 0, 2, 2, -1110, 0),
    (3, 0, -1, 0, -892, 3258),
    (2, 1, 1, 0, -810, 2616),
    (4, -1, -2, 0, 759, -1897),
    (0, 2, -1, 0, -713, -2117),
    (2, 2, -1, 0, -700, 2354),
    (2, 1, -2, 0, 691, 0),
    (2, -1, 0, -2, 596, 0),
    (4, 0, 1, 0, 549, -1423),
    (0, 0, 4, 0, 537, -1117),
    (4, -1, 0, 0, 520, -1571),
    (1, 0, -2, 0, -487, -1739),
    (2, 1, 0, -2, -399, 0),
    (0, 0, 2, -2, -381, -4421),
    (1, 1, 1, 0, 351, 0),
    (3, 0, -2, 0, -340, 0),
    (4, 0, -3, 0, 330, 0),
    (2, -1, 2, 0, 327, 0),
    (0, 2, 1, 0, -323, 1165),
    (1, 1, -1, 0, 299, 0),
    (2, 0, 3, 0, 294, 0),
    (2, 0, -1, -2, 0, 8752),
)

# Table 47.B: arguments and coefficients for Sum(b) in 1e-6 deg.
_TERMS_B: Tuple[Tuple[int, int, int, int, int], ...] = (
    (0, 0, 0, 1, 5128122),
    (0, 0, 1, 1, 280602),
    (0, 0, 1, -1, 277693),
    (2, 0, 0, -1, 173237),
    (2, 0, -1, 1, 55413),
    (2, 0, -1, -1, 46271),
    (2, 0, 0, 1, 32573),
    (0, 0, 2, 1, 17198),
    (2, 0, 1, -1, 9266),
    (0, 0, 2, -1, 8822),
    (2, -1, 0, -1, 8216),
    (2, 0, -2, -1, 4324),
    (2, 0, 1, 1, 4200),
    (2, 1, 0, -1, -3359),
    (2, -1, -1, 1, 2463),
    (2, -1, 0, 1, 2211),
    (2, -1, -1, -1, 2065),
    (0, 1, -1, -1, -1870),
    (4, 0, -1, -1, 1828),
    (0, 1, 0, 1, -1794),
    (0, 0, 0, 3, -1749),
    (0, 1, -1, 1, -1565),
    (1, 0, 0, 1, -1491),
    (0, 1, 1, 1, -1475),
    (0, 1, 1, -1, -1410),
    (0, 1, 0, -1, -1344),
    (1, 0, 0, -1, -1335),
    (0, 0, 3, 1, 1107),
    (4, 0, 0, -1, 1021),
    (4, 0, -1, 1, 833),
    (0, 0, 1, -3, 777),
    (4, 0, -2, 1, 671),
    (2, 0, 0, -3, 607),
    (2, 0, 2, -1, 596),
    (2, -1, 1, -1, 491),
    (2, 0, -2, 1, -451),
    (0, 0, 3, -1, 439),
    (2, 0, 2, 1, 422),
    (2, 0, -3, -1, 421),
    (2, 1, -1, 1, -366),
    (2, 1, 0, 1, -351),
    (4, 0, 0, 1, 331),
    (2, -1, 1, 1, 315),
    (2, -2, 0, -1, 302),
    (0, 0, 1, 3, -283),
    (2, 1, 1, -1, -229),
    (1, 1, 0, -1, 223),
    (1, 1, 0, 1, 223),
    (0, 1, -2, -1, -220),
    (2, 1, -1, -1, -220),
    (1, 0, 1, 1, -185),
    (2, -1, -2, -1, 181),
    (0, 1, 2, 1, -177),
    (4, 0, -2, -1, 176),
    (4, -1, -1, -1, 166),
    (1, 0, 1, -1, -164),
    (4, 0, 1, -1, 132),
    (1, 0, -1, -1, -119),
    (4, -1, 0, -1, 115),
    (2, -2, 0, 1, 107),
)

# Coefficients for the additive terms on Sum(l) and Sum(b) (Meeus 47.1, 47.2).
_L_ADD = (3958, 1962, 318)  # A1, (L'-F), A2
_B_ADD = (-2235, 382, 175, 175, 127, -115)  # L', A3, (A1-F), (A1+F), (L'-M'), (L'+M')


def fundamental_arguments(jd_tt: float) -> Tuple[float, float, float, float, float, float, float]:
    """Return the Moon's fundamental arguments in *degrees*.

    Order: ``(Lp, D, M, Mp, F, A1, A2, A3)`` -- except A1..A3 are returned
    separately as the last three values, giving an 8-tuple:
    ``(Lp, D, M, Mp, F, A1, A2, A3)``.
    """
    t = julian_centuries(jd_tt)
    lp = 218.3164477 + 481267.88123421 * t - 0.0015786 * t**2 + t**3 / 538841.0 - t**4 / 65194000.0
    d = 297.8501921 + 445267.1114034 * t - 0.0018819 * t**2 + t**3 / 545868.0 - t**4 / 113065000.0
    m = 357.5291092 + 35999.0502909 * t - 0.0001536 * t**2 + t**3 / 24490000.0
    mp = 134.9633964 + 477198.8675055 * t + 0.0087414 * t**2 + t**3 / 69699.0 - t**4 / 14712000.0
    f = 93.2720950 + 483202.0175233 * t - 0.0036539 * t**2 - t**3 / 3526000.0 + t**4 / 863310000.0
    a1 = 119.75 + 131.849 * t
    a2 = 53.09 + 479264.290 * t
    a3 = 313.45 + 481266.484 * t
    return lp, d, m, mp, f, a1, a2, a3


def _eccentricity_factor(t: float) -> float:
    return 1.0 - 0.002516 * t - 0.0000074 * t * t


def _sum_series(
    terms: Tuple[Tuple[int, int, int, int, int], ...],
    d: float,
    m: float,
    mp: float,
    f: float,
    e: float,
    *,
    longitude: bool,
) -> float:
    """Accumulate a Meeus table, applying the eccentricity factor to terms in M."""
    total = 0.0
    for term in terms:
        cd, cm, cmp_, cf = term[0], term[1], term[2], term[3]
        coeff = term[4]
        arg = (cd * d + cm * m + cmp_ * mp + cf * f) * _DEG
        factor = 1.0
        if cm == 1 or cm == -1:
            factor = e
        elif cm == 2 or cm == -2:
            factor = e * e
        total += coeff * factor * math.sin(arg)
    return total


def moon_longitude(jd_tt: float) -> float:
    """Moon's geocentric apparent longitude in *degrees* (Meeus 47.1)."""
    t = julian_centuries(jd_tt)
    lp, d, m, mp, f, a1, a2, _a3 = fundamental_arguments(jd_tt)
    e = _eccentricity_factor(t)
    total = _sum_series(_TERMS_LR, d, m, mp, f, e, longitude=True)
    # Additive terms: only the longitude coefficients (index 4) are used here.
    additive = 3958 * math.sin(a1 * _DEG)
    additive += 1962 * math.sin((lp - f) * _DEG)
    additive += 318 * math.sin(a2 * _DEG)
    total += additive
    return (lp + total / 1e6) % 360.0


def moon_latitude(jd_tt: float) -> float:
    """Moon's geocentric apparent latitude in *degrees* (Meeus 47.2)."""
    t = julian_centuries(jd_tt)
    lp, d, m, mp, f, a1, a2, a3 = fundamental_arguments(jd_tt)
    e = _eccentricity_factor(t)
    total = _sum_series(_TERMS_B, d, m, mp, f, e, longitude=False)
    total += -2235 * math.sin(lp * _DEG)
    total += 382 * math.sin(a3 * _DEG)
    total += 175 * math.sin((a1 - f) * _DEG)
    total += 175 * math.sin((a1 + f) * _DEG)
    total += 127 * math.sin((lp - mp) * _DEG)
    total += -115 * math.sin((lp + mp) * _DEG)
    return total / 1e6


def moon_distance(jd_tt: float) -> float:
    """Moon's geocentric distance in *kilometres* (Meeus 47.3)."""
    t = julian_centuries(jd_tt)
    lp, d, m, mp, f, _a1, _a2, _a3 = fundamental_arguments(jd_tt)
    e = _eccentricity_factor(t)
    total = 0.0
    for cd, cm, cmp_, cf, _l, r in _TERMS_LR:
        arg = (cd * d + cm * m + cmp_ * mp + cf * f) * _DEG
        factor = 1.0
        if cm in (1, -1):
            factor = e
        elif cm in (2, -2):
            factor = e * e
        total += r * factor * math.cos(arg)
    return 385000.56 + total / 1000.0


def moon_position(jd_tt: float) -> Tuple[float, float, float]:
    """Return ``(longitude_deg, latitude_deg, distance_km)`` for the Moon."""
    return moon_longitude(jd_tt), moon_latitude(jd_tt), moon_distance(jd_tt)


def moon_ra_dec(jd_tt: float) -> Tuple[float, float]:
    """Return the Moon's apparent ``(right_ascension_deg, declination_deg)``.

    Converts the ecliptic longitude/latitude through the apparent obliquity
    of the ecliptic (Meeus 13.3, 13.4).
    """
    from .sun import mean_obliquity

    lam = moon_longitude(jd_tt) * _DEG
    beta = moon_latitude(jd_tt) * _DEG
    t = julian_centuries(jd_tt)
    eps = mean_obliquity(jd_tt) * _DEG
    # Nutation in obliquity (dominant term) for apparent coordinates.
    omega = (125.04 - 1934.136 * t) * _DEG
    eps += (0.00256 * math.cos(omega)) * _DEG
    ra = math.atan2(
        math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps),
        math.cos(lam),
    )
    dec = math.asin(
        math.sin(beta) * math.cos(eps) + math.cos(beta) * math.sin(eps) * math.sin(lam)
    )
    return (ra / _DEG) % 360.0, dec / _DEG
