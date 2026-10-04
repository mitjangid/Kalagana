"""Ascendant (Lagna), Midheaven and house systems.

The ascendant is the point of the ecliptic rising over the eastern horizon at
a given instant and place.  It is derived from the local apparent sidereal time
``theta`` (the right ascension of the meridian, RAMC), the obliquity of the
ecliptic ``eps`` and the geographic latitude ``phi``::

    lambda_asc = atan2( cos(theta),
                        -(sin(theta) * cos(eps) + tan(phi) * sin(eps)) )

The result is a *tropical* (sayana) longitude, which is converted to the
nirayana (sidereal) zodiac by removing the ayanamsa, exactly as the Sun and
Moon are handled in :mod:`kalagana.limbs`.

Two house systems are offered:

* ``whole_sign`` (rashi) -- house 1 is the whole sign of the Lagna, house 2 the
  next sign, and so on.  This is the traditional Parashari scheme and the one
  used by most Indian panchangs.
* ``equal`` -- the cusps are placed every 30 degrees from the exact Lagna.

The Midheaven (10th house cusp on the meridian) is also returned.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

from .. import julian
from ..ayanamsa import ayanamsa_degrees
from ..sun import mean_obliquity

__all__ = [
    "RASHIS",
    "RASHIS_EN",
    "local_apparent_sidereal_time",
    "true_obliquity",
    "ascendant",
    "midheaven",
    "Ascendant",
    "house_cusps_equal",
    "whole_sign_of",
    "house_of_longitude",
    "rashi_of",
]

_DEG = math.pi / 180.0

RASHIS = (
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
)
RASHIS_EN = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


def _norm360(x: float) -> float:
    return x % 360.0


def local_apparent_sidereal_time(jd_ut: float, longitude: float) -> float:
    """Local apparent sidereal time in *degrees* (east longitude positive)."""
    return _norm360(julian.greenwich_apparent_sidereal_time(jd_ut) + longitude)


def true_obliquity(jd_tt: float) -> float:
    """True obliquity of the ecliptic in *degrees* (mean plus nutation)."""
    t = julian.julian_centuries(jd_tt)
    omega = (125.04 - 1934.136 * t) * _DEG
    return mean_obliquity(jd_tt) + 0.00256 * math.cos(omega)


def _ascendant_tropical(theta: float, eps: float, phi: float) -> float:
    t = math.radians(theta)
    e = math.radians(eps)
    p = math.radians(phi)
    lam = math.atan2(
        math.cos(t),
        -(math.sin(t) * math.cos(e) + math.tan(p) * math.sin(e)),
    )
    return _norm360(math.degrees(lam))


def _midheaven_tropical(theta: float, eps: float) -> float:
    t = math.radians(theta)
    e = math.radians(eps)
    lam = math.atan2(math.sin(t), math.cos(t) * math.cos(e))
    return _norm360(math.degrees(lam))


def midheaven(jd_ut: float, jd_tt: float, lat: float, lon: float,
              ayanamsa: str = "lahiri") -> Tuple[float, float]:
    """Return the Midheaven ``(sidereal, tropical)`` longitude in degrees."""
    theta = local_apparent_sidereal_time(jd_ut, lon)
    trop = _midheaven_tropical(theta, true_obliquity(jd_tt))
    sid = _norm360(trop - ayanamsa_degrees(jd_tt, ayanamsa))
    return sid, trop


@dataclass(frozen=True)
class Ascendant:
    """The Lagna (rising sign) and its supporting angles."""

    sidereal: float        # nirayana longitude in degrees
    tropical: float        # sayana longitude in degrees
    rashi: int             # 0 = Aries .. 11 = Pisces
    rashi_name: str
    degree_in_rashi: float
    midheaven: float       # sidereal MC longitude
    midheaven_tropical: float
    sidereal_time: float   # local apparent sidereal time, degrees


def ascendant(
    jd_ut: float,
    jd_tt: float,
    lat: float,
    lon: float,
    ayanamsa: str = "lahiri",
) -> Ascendant:
    """Compute the ascendant (Lagna) for a place at an instant."""
    theta = local_apparent_sidereal_time(jd_ut, lon)
    eps = true_obliquity(jd_tt)
    trop = _ascendant_tropical(theta, eps, lat)
    sid = _norm360(trop - ayanamsa_degrees(jd_tt, ayanamsa))
    mc_sid, mc_trop = midheaven(jd_ut, jd_tt, lat, lon, ayanamsa)
    rashi = int(sid // 30.0)
    return Ascendant(
        sidereal=sid,
        tropical=trop,
        rashi=rashi,
        rashi_name=RASHIS[rashi],
        degree_in_rashi=sid % 30.0,
        midheaven=mc_sid,
        midheaven_tropical=mc_trop,
        sidereal_time=theta,
    )


def rashi_of(longitude: float) -> int:
    """Rashi index (0 = Aries .. 11 = Pisces) for a sidereal longitude."""
    return int(_norm360(longitude) // 30.0)


def whole_sign_of(longitude: float) -> str:
    """Rashi name for a sidereal longitude."""
    return RASHIS[rashi_of(longitude)]


def house_cusps_equal(asc: float) -> List[float]:
    """Equal-house cusps (12 sidereal longitudes) from the Lagna longitude."""
    return [(_norm360(asc) + 30.0 * i) % 360.0 for i in range(12)]


def house_of_longitude(longitude: float, asc: float, system: str = "whole_sign") -> int:
    """House number (1-12) holding a sidereal ``longitude``.

    ``system`` is ``"whole_sign"`` (default, traditional) or ``"equal"``.
    """
    if system == "equal":
        return int(_norm360(longitude - asc) // 30.0) + 1
    if system == "whole_sign":
        return (rashi_of(longitude) - rashi_of(asc)) % 12 + 1
    raise ValueError(f"unknown house system {system!r}")
