"""Ayanamsa (precession offset between tropical and sidereal zodiacs).

The ayanamsa is the angle by which the sidereal zodiac is displaced from the
tropical zodiac.  It grows with time; sidereal longitude = tropical longitude
minus the ayanamsa.

Default is **Lahiri** (Chitrapaksha) ayanamsa, the convention used by the
Indian Government's Rashtriya Panchang and by most North Indian panchangs.

Accuracy note
-------------
Lahiri is anchored at a well known epoch value for J2000.0 and propagated with
the IAU general-precession-in-longitude polynomial, rather than a flat
50.29"/yr, so it tracks the true value across 1900-2100.  The Raman and KP
epoch constants are documented approximations and should be confirmed against
an authoritative ephemeris before being relied on for critical work.
"""

from __future__ import annotations

from typing import Dict

from .julian import julian_centuries

__all__ = ["AYANAMSA_EPOCH_J2000", "ayanamsa_degrees", "normalize_name", "SUPPORTED"]

# Values are *degrees at J2000.0*.
# Lahiri / Chitrapaksha at J2000.0 (2000-01-01.5 TT) = 23 deg 51' 11.0"
# = 23.853055... deg -- the value quoted in the Indian Astronomical Ephemeris
# (Rashtriya Panchang) for the Lahiri spheroid.
_EPOCH_VALUES: Dict[str, float] = {
    "lahiri": 23.85305555555556,
    "raman": 21.96666666666667,
    "kp": 23.73555555555556,
    "yukteshwar": 22.46388888888889,
    "fagan_bradley": 24.736111111111112,
}

#: Public read-only view: ayanamsa name -> epoch value in degrees at J2000.0.
AYANAMSA_EPOCH_J2000: Dict[str, float] = dict(_EPOCH_VALUES)

SUPPORTED = tuple(sorted(_EPOCH_VALUES))

_ALIASES = {
    "chitrapaksha": "lahiri",
    "chitra": "lahiri",
    "krishnamurti": "kp",
    "krishnamurti_pathak": "kp",
    "fagan": "fagan_bradley",
    "yukteshwar": "yukteshwar",
}


def normalize_name(name: str) -> str:
    """Normalise a user-supplied ayanamsa name to a key in :data:`SUPPORTED`."""
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    key = _ALIASES.get(key, key)
    if key not in _EPOCH_VALUES:
        raise ValueError(
            f"Unknown ayanamsa {name!r}; supported: {list(SUPPORTED)}"
        )
    return key


def ayanamsa_degrees(jd_tt: float, name: str = "lahiri") -> float:
    """Return the ayanamsa in *degrees* for ``jd_tt``.

    ``name`` selects the model ('lahiri' default).  The epoch value is
    propagated with the IAU general precession in longitude
    ``p = 5028.796195*T + 1.1054348*T^2 + ...`` arcseconds, ``T`` in Julian
    centuries from J2000.0.
    """
    key = normalize_name(name)
    t = julian_centuries(jd_tt)
    precession_arcsec = (
        5028.796195 * t
        + 1.1054348 * t * t
        + 0.00007964 * t**3
        - 0.000023857 * t**4
        - 0.0000000383 * t**5
    )
    return _EPOCH_VALUES[key] + precession_arcsec / 3600.0
