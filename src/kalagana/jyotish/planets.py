"""Geocentric planetary longitudes for jyotish, using Keplerian elements.

Method
------
Each planet's heliocentric position is found from the Keplerian elements and
rates of Standish & Williams (JPL Solar System Dynamics, "Approximate Positions
of the Planets", Table 1), which are fitted for 1800-2050.  The algorithm is:

1. elements at ``T`` (Julian centuries from J2000) = ``a0 + a1*T`` etc.;
2. solve Kepler's equation ``M = E - e* sin E``;
3. heliocentric coordinates in the orbital plane -> J2000 ecliptic
   rectangular coordinates;
4. subtract the Earth/Moon barycentre to obtain the *geocentric* vector, and
   take its ecliptic longitude/latitude.

The longitudes are the **J2000 mean-ecliptic** longitudes.  Because the sidereal
(nirayana) zodiac is fixed with respect to the stars, the nirayana longitude is
obtained simply by removing the ayanamsa's J2000 epoch value::

    sidereal = (j2000_longitude - ayanamsa_epoch_value) mod 360

This mirrors what :mod:`kalagana.limbs` does for the Sun and Moon (where the
tropical longitude-of-date and the ayanamsa's precession term cancel), so all
grahas in the package agree.

Accuracy
--------
The Standish elements are quoted to ~15-400 arcseconds in heliocentric
longitude for Mercury..Jupiter and ~600" for Saturn over 1800-2050 (i.e. well
under 0.2 degrees).  That is comfortably enough to place a graha in a rashi
(30 deg) or nakshatra (13 deg 20'), and adequate for a pada (3 deg 20') except
within ~0.2 deg of a boundary.  Light-time and aberration corrections
(<~0.03 deg) are deliberately omitted; they are below the element accuracy.
Uranus and Neptune are provided for completeness but are not grahas.

The lunar *mean* node (Rahu) is computed directly from the standard polynomial
of date and reduced with the ayanamsa, matching how the ascendant is handled.
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

from ..ayanamsa import AYANAMSA_EPOCH_J2000, normalize_name
from ..julian import julian_centuries

__all__ = [
    "PLANETS",
    "EXTRA_PLANETS",
    "GRAHAS",
    "elements",
    "heliocentric_j2000",
    "geocentric_j2000",
    "sidereal_longitude",
    "sidereal_latitude",
    "mean_node_longitude",
    "sidereal_node_longitude",
    "rahu_ketu",
    "is_retrograde",
    "sun_sidereal_longitude",
]

_DEG = math.pi / 180.0

# Standish & Williams, JPL "Approximate Positions of the Planets", Table 1
# (1800 AD - 2050 AD).  Order: a, e, I, L, long.peri., long.node.
# Values with an overbar are the element; the second tuple is the rate per
# Julian century.
_ELEMENTS: Dict[str, Tuple[Tuple[float, ...], Tuple[float, ...]]] = {
    "mercury": (
        (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593),
        (0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    ),
    "venus": (
        (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255),
        (0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    ),
    "earth": (
        (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0),
        (0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    ),
    "mars": (
        (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891),
        (0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    ),
    "jupiter": (
        (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909),
        (-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    ),
    "saturn": (
        (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448),
        (-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
    ),
    "uranus": (
        (19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503),
        (-0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589),
    ),
    "neptune": (
        (30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574),
        (0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664),
    ),
}

#: The five non-luminary classical planets (English names, capitalised).
PLANETS = ("Mercury", "Venus", "Mars", "Jupiter", "Saturn")
#: Extra planets, not used by Vedic astrology.
EXTRA_PLANETS = ("Uranus", "Neptune")
#: The nine grahas in traditional order.
GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


def _norm360(x: float) -> float:
    return x % 360.0


def _norm180(x: float) -> float:
    """Normalise an angle to (-180, 180]."""
    return (x + 180.0) % 360.0 - 180.0


def elements(name: str, jd_tt: float) -> Tuple[float, float, float, float, float, float]:
    """Return ``(a, e, I, L, long_peri, node)`` for ``name`` at ``jd_tt``.

    Angles are in degrees, ``a`` in astronomical units.
    """
    key = name.strip().lower()
    try:
        base, rate = _ELEMENTS[key]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(
            f"Unknown planet {name!r}; known: {sorted(_ELEMENTS)}"
        ) from exc
    t = julian_centuries(jd_tt)
    return tuple(b + r * t for b, r in zip(base, rate))  # type: ignore[return-value]


def _solve_kepler(m_deg: float, e: float) -> float:
    """Solve Kepler's equation, returning the eccentric anomaly in *degrees*.

    ``m_deg`` is the mean anomaly in degrees; ``e`` the eccentricity.
    """
    m = math.radians(_norm180(m_deg))
    ecc = m + e * math.sin(m)
    for _ in range(60):
        delta = (m - (ecc - e * math.sin(ecc))) / (1.0 - e * math.cos(ecc))
        ecc += delta
        if abs(delta) < 1e-12:
            break
    return math.degrees(ecc)


def heliocentric_j2000(name: str, jd_tt: float) -> Tuple[float, float, float]:
    """Heliocentric rectangular coordinates in AU, J2000 ecliptic frame."""
    a, e, inc, _L, peri, node = elements(name, jd_tt)
    arg_peri = peri - node
    m = _norm180(_mean_anomaly(name, jd_tt))
    ecc_anom = _solve_kepler(m, e)

    x_orb = a * (math.cos(math.radians(ecc_anom)) - e)
    y_orb = a * math.sqrt(max(0.0, 1.0 - e * e)) * math.sin(math.radians(ecc_anom))

    w = math.radians(arg_peri)
    o = math.radians(node)
    i = math.radians(inc)
    cw, sw = math.cos(w), math.sin(w)
    co, so = math.cos(o), math.sin(o)
    ci, si = math.cos(i), math.sin(i)

    x = (cw * co - sw * so * ci) * x_orb + (-sw * co - cw * so * ci) * y_orb
    y = (cw * so + sw * co * ci) * x_orb + (-sw * so + cw * co * ci) * y_orb
    z = (sw * si) * x_orb + (cw * si) * y_orb
    return x, y, z


def _mean_anomaly(name: str, jd_tt: float) -> float:
    """Mean anomaly in degrees: ``L - long.peri`` (Table 1 has no extra terms)."""
    _a, _e, _i, l, peri, _node = elements(name, jd_tt)
    return l - peri


def _earth_vector(jd_tt: float) -> Tuple[float, float, float]:
    return heliocentric_j2000("earth", jd_tt)


def geocentric_j2000(name: str, jd_tt: float) -> Tuple[float, float]:
    """Geocentric J2000-ecliptic ``(longitude, latitude)`` in degrees.

    ``name`` may be any table planet, or the Sun (computed from the Earth
    vector).  For the Sun the returned latitude is ~0.
    """
    key = name.strip().lower()
    if key == "sun":
        ex, ey, ez = _earth_vector(jd_tt)
        x, y, z = -ex, -ey, -ez
    else:
        px, py, pz = heliocentric_j2000(key, jd_tt)
        ex, ey, ez = _earth_vector(jd_tt)
        x, y, z = px - ex, py - ey, pz - ez
    lon = math.degrees(math.atan2(y, x))
    lat = math.degrees(math.atan2(z, math.hypot(x, y)))
    return _norm360(lon), lat


def _epoch_ayanamsa(ayanamsa: str) -> float:
    return AYANAMSA_EPOCH_J2000[normalize_name(ayanamsa)]


def sidereal_longitude(name: str, jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Nirayana (sidereal) geocentric longitude in degrees."""
    lon, _lat = geocentric_j2000(name, jd_tt)
    return _norm360(lon - _epoch_ayanamsa(ayanamsa))


def sidereal_latitude(name: str, jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Geocentric ecliptic latitude in degrees (ayanamsa-independent)."""
    _lon, lat = geocentric_j2000(name, jd_tt)
    return lat


def sun_sidereal_longitude(jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Nirayana Sun longitude via this module's Keplerian Earth vector."""
    return sidereal_longitude("Sun", jd_tt, ayanamsa)


def mean_node_longitude(jd_tt: float) -> float:
    """Mean longitude of the ascending lunar node (Rahu), tropical of date.

    Meeus, *Astronomical Algorithms*, 2nd ed., ch. 47 (mean elements of the
    Moon's orbit).  The node regresses ~19.34 deg per year.
    """
    t = julian_centuries(jd_tt)
    omega = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * t * t
        + t**3 / 467441.0
        - t**4 / 60616000.0
    )
    return _norm360(omega)


def sidereal_node_longitude(jd_tt: float, ayanamsa: str = "lahiri") -> float:
    """Nirayana longitude of Rahu (mean ascending node), in degrees."""
    from ..ayanamsa import ayanamsa_degrees

    return _norm360(mean_node_longitude(jd_tt) - ayanamsa_degrees(jd_tt, ayanamsa))


def rahu_ketu(jd_tt: float, ayanamsa: str = "lahiri") -> Tuple[float, float]:
    """Return ``(rahu, ketu)`` nirayana longitudes in degrees (Ketu = Rahu+180)."""
    rahu = sidereal_node_longitude(jd_tt, ayanamsa)
    return rahu, _norm360(rahu + 180.0)


def is_retrograde(name: str, jd_tt: float, ayanamsa: str = "lahiri") -> bool:
    """Whether ``name`` is retrograde (vakri) at ``jd_tt``.

    Determined from the sign of the daily motion of the nirayana longitude over
    a +/- 12 hour window.  The Sun and Moon are never retrograde; Rahu/Ketu are
    always retrograde by convention yet are reported as ``False`` here (their
    nodes regress, which is handled separately).
    """
    key = name.strip().lower()
    if key in ("sun", "moon"):
        return False
    if key in ("rahu", "ketu"):
        return True
    before = sidereal_longitude(name, jd_tt - 0.5, ayanamsa)
    after = sidereal_longitude(name, jd_tt + 0.5, ayanamsa)
    return _norm180(after - before) < 0.0
