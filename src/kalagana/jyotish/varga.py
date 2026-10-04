"""Divisional charts (vargas) -- the Shodasavarga (sixteen divisions).

Each varga divides every 30-degree rashi into ``n`` equal parts and maps each
part to a sign by a fixed rule.  The rules encoded here are the widely used
Parashari ones; where traditions differ the choice is noted in the code.

The returned value is always a rashi index (0 = Aries .. 11 = Pisces).
"""

from __future__ import annotations

from typing import Dict, Tuple

__all__ = ["VARGA_NAMES", "SHODASAVARGA", "varga_sign", "varga_positions"]

#: Number of divisions -> conventional name.
VARGA_NAMES: Dict[int, str] = {
    1: "Rashi (D1)",
    2: "Hora (D2)",
    3: "Drekkana (D3)",
    4: "Chaturthamsa (D4)",
    7: "Saptamsa (D7)",
    9: "Navamsa (D9)",
    10: "Dasamsa (D10)",
    12: "Dwadasamsa (D12)",
    16: "Shodasamsa (D16)",
    20: "Vimsamsa (D20)",
    24: "Chaturvimsamsa (D24)",
    27: "Bhamsa (D27)",
    30: "Trimsamsa (D30)",
    40: "Khavedamsa (D40)",
    45: "Akshavedamsa (D45)",
    60: "Shashtiamsa (D60)",
}

#: The sixteen standard vargas, in the conventional order.
SHODASAVARGA: Tuple[int, ...] = (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)

# Movable (chara), fixed (sthira) and dual (dvisvabhava) signs.
_MOVABLE = (0, 3, 6, 9)
_FIXED = (1, 4, 7, 10)
_DUAL = (2, 5, 8, 11)


def _is_odd_sign(sign: int) -> bool:
    """True for the 'odd' (1st, 3rd, ...) signs, i.e. index 0, 2, 4, ..."""
    return sign % 2 == 0


def _trimsamsa(within: float, odd: bool) -> int:
    if odd:
        if within < 5.0:
            return 0    # Mars -> Aries
        if within < 10.0:
            return 10   # Saturn -> Aquarius
        if within < 18.0:
            return 8    # Jupiter -> Sagittarius
        if within < 25.0:
            return 2    # Mercury -> Gemini
        return 6        # Venus -> Libra
    if within < 5.0:
        return 1        # Venus -> Taurus
    if within < 12.0:
        return 5        # Mercury -> Virgo
    if within < 20.0:
        return 11       # Jupiter -> Pisces
    if within < 25.0:
        return 9        # Saturn -> Capricorn
    return 7            # Mars -> Scorpio


def varga_sign(longitude: float, divisions: int) -> int:
    """Return the rashi index of ``longitude`` in the ``divisions``-fold varga."""
    lon = longitude % 360.0
    sign = int(lon // 30.0)
    within = lon % 30.0
    part = int(within / (30.0 / divisions)) if divisions > 0 else 0
    odd = _is_odd_sign(sign)

    if divisions == 1:
        return sign
    if divisions == 2:  # Hora -> only Cancer (Moon) and Leo (Sun)
        if odd:
            return 4 if part == 0 else 3
        return 3 if part == 0 else 4
    if divisions == 3:  # Drekkana: the sign, the 5th, the 9th
        return (sign + part * 4) % 12
    if divisions == 4:  # Chaturthamsa: sign, 4th, 7th, 10th
        return (sign + part * 3) % 12
    if divisions == 7:  # Saptamsa: odd from the sign, even from the 7th
        start = sign if odd else (sign + 6) % 12
        return (start + part) % 12
    if divisions == 9:  # Navamsa: continuous from Aries
        return int(lon * 3.0 / 10.0) % 12
    if divisions == 10:  # Dasamsa: odd from the sign, even from the 9th
        start = sign if odd else (sign + 8) % 12
        return (start + part) % 12
    if divisions == 12:  # Dwadasamsa: continuous from Aries
        return int(lon / 2.5) % 12
    if divisions == 16:  # Shodasamsa: movable Aries, fixed Leo, dual Sagittarius
        start = 0 if sign in _MOVABLE else (4 if sign in _FIXED else 8)
        return (start + part) % 12
    if divisions == 20:  # Vimsamsa: movable Aries, fixed Sagittarius, dual Leo
        start = 0 if sign in _MOVABLE else (8 if sign in _FIXED else 4)
        return (start + part) % 12
    if divisions == 24:  # Chaturvimsamsa: odd from Leo, even from Cancer
        start = 4 if odd else 3
        return (start + part) % 12
    if divisions == 27:  # Bhamsa: continuous from Aries
        return int(lon * 0.9) % 12
    if divisions == 30:
        return _trimsamsa(within, odd)
    if divisions == 40:  # Khavedamsa: odd from Aries, even from Libra
        start = 0 if odd else 6
        return (start + part) % 12
    if divisions == 45:  # Akshavedamsa: movable Aries, fixed Leo, dual Sagittarius
        start = 0 if sign in _MOVABLE else (4 if sign in _FIXED else 8)
        return (start + part) % 12
    if divisions == 60:  # Shashtiamsa: continuous from Aries
        return int(lon * 2.0) % 12
    raise ValueError(f"unsupported varga divisions {divisions!r}")


def varga_positions(longitudes: Dict[str, float], divisions: int) -> Dict[str, int]:
    """Map a dict of graha longitudes to their rashi indices in one varga."""
    return {name: varga_sign(lon, divisions) for name, lon in longitudes.items()}
