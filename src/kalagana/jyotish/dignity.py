"""Graha dignity: exaltation, ownership, moolatrikona, friendship, combustion.

All tables follow the classical Parashari conventions that are reproduced by
most Indian panchangs and jyotish software.  Contemporary authors differ on a
few points (especially Rahu/Ketu); the choices here are documented so they can
be adjusted.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

__all__ = [
    "PLANETS",
    "RASHI_LORDS",
    "EXALTATION",
    "DEBILITATION",
    "OWN_SIGNS",
    "MOOLATRIKONA",
    "NATURAL_FRIENDS",
    "NATURAL_ENEMIES",
    "COMBUSTION_LIMIT",
    "rashi_lord",
    "dignity",
    "relationship",
    "is_combust",
    "combustion_limit",
]

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

RASHI_LORDS = (
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
)
#: Rahu and Ketu are (by convention) co-lords of certain signs.
RAHU_CO_LORD_SIGNS = (2, 5, 10)   # Gemini, Virgo, Aquarius
KETU_CO_LORD_SIGNS = (5, 8, 11)   # Virgo, Sagittarius, Pisces

# (rashi_index, degree) of deep exaltation.
EXALTATION: Dict[str, Tuple[int, float]] = {
    "Sun": (0, 10.0), "Moon": (1, 3.0), "Mars": (9, 28.0), "Mercury": (5, 15.0),
    "Jupiter": (3, 5.0), "Venus": (11, 27.0), "Saturn": (6, 20.0),
    "Rahu": (1, 20.0), "Ketu": (7, 20.0),
}
#: Debilitation is the opposite sign at the same degree.
DEBILITATION: Dict[str, Tuple[int, float]] = {
    p: ((s + 6) % 12, d) for p, (s, d) in EXALTATION.items()
}

OWN_SIGNS: Dict[str, Tuple[int, ...]] = {
    "Sun": (4,), "Moon": (3,), "Mars": (0, 7), "Mercury": (2, 5),
    "Jupiter": (8, 11), "Venus": (1, 6), "Saturn": (9, 10),
    "Rahu": (10,), "Ketu": (7,),
}

#: (rashi_index, start_degree, end_degree) of the moolatrikona span.
MOOLATRIKONA: Dict[str, Tuple[int, float, float]] = {
    "Sun": (4, 0.0, 20.0), "Moon": (1, 3.0, 30.0), "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 15.0, 20.0), "Jupiter": (8, 0.0, 10.0), "Venus": (6, 0.0, 15.0),
    "Saturn": (10, 0.0, 20.0),
}

#: Natural (naisargika) friendships.  Anything not listed as a friend or enemy
#: is a neutral (sama) relationship.
NATURAL_FRIENDS: Dict[str, Tuple[str, ...]] = {
    "Sun": ("Moon", "Mars", "Jupiter"),
    "Moon": ("Sun", "Mercury"),
    "Mars": ("Sun", "Moon", "Jupiter"),
    "Mercury": ("Sun", "Venus"),
    "Jupiter": ("Sun", "Moon", "Mars"),
    "Venus": ("Mercury", "Saturn"),
    "Saturn": ("Mercury", "Venus"),
    "Rahu": ("Venus", "Saturn", "Mercury"),
    "Ketu": ("Venus", "Saturn", "Mercury"),
}
NATURAL_ENEMIES: Dict[str, Tuple[str, ...]] = {
    "Sun": ("Venus", "Saturn"),
    "Moon": (),
    "Mars": ("Mercury",),
    "Mercury": ("Moon",),
    "Jupiter": ("Mercury", "Venus"),
    "Venus": ("Sun", "Moon"),
    "Saturn": ("Sun", "Moon", "Mars"),
    "Rahu": ("Sun", "Moon", "Mars"),
    "Ketu": ("Sun", "Moon", "Mars"),
}

#: Combustion (asta) limits -- maximum elongation from the Sun, in degrees,
#: within which the graha is considered combust.  Values for retrograde
#: Mercury/Venus are tighter.
COMBUSTION_LIMIT: Dict[str, Tuple[float, float]] = {
    # planet: (direct_limit, retrograde_limit)
    "Moon": (12.0, 12.0),
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}


def rashi_lord(rashi: int) -> str:
    """Lord (owner) of a rashi index (0 = Aries .. 11 = Pisces)."""
    return RASHI_LORDS[rashi % 12]


def relationship(a: str, b: str) -> str:
    """Natural relationship of planet ``a`` towards ``b``.

    Returns ``"friend"``, ``"neutral"`` or ``"enemy"``.
    """
    if a in NATURAL_FRIENDS.get(b, ()) or b in NATURAL_FRIENDS.get(a, ()):
        # Friendship is taken as mutual for the natural scheme.
        pass
    if b in NATURAL_FRIENDS.get(a, ()):
        return "friend"
    if b in NATURAL_ENEMIES.get(a, ()):
        return "enemy"
    return "neutral"


def dignity(planet: str, longitude: float) -> str:
    """Dignity of ``planet`` at a sidereal ``longitude`` (degrees).

    One of ``"exalted"``, ``"moolatrikona"``, ``"own"``, ``"friend"``,
    ``"neutral"``, ``"enemy"`` or ``"debilitated"``.
    """
    lon = longitude % 360.0
    rashi = int(lon // 30.0)
    degree = lon % 30.0

    ex = EXALTATION.get(planet)
    # Exaltation/debilitation are by sign (the deep degree refines strength).
    if ex and rashi == ex[0]:
        return "exalted"
    de = DEBILITATION.get(planet)
    if de and rashi == de[0]:
        return "debilitated"

    mt = MOOLATRIKONA.get(planet)
    if mt and rashi == mt[0] and mt[1] <= degree < mt[2]:
        return "moolatrikona"

    if rashi in OWN_SIGNS.get(planet, ()):
        return "own"

    lord = rashi_lord(rashi)
    if lord == planet:
        return "own"
    rel = relationship(planet, lord)
    return {"friend": "friend", "enemy": "enemy", "neutral": "neutral"}[rel]


def combustion_limit(planet: str, retrograde: bool = False) -> Optional[float]:
    """Combustion limit in degrees for ``planet`` (``None`` if not applicable)."""
    limits = COMBUSTION_LIMIT.get(planet)
    if limits is None:
        return None
    return limits[1] if retrograde else limits[0]


def is_combust(planet: str, longitude: float, sun_longitude: float,
               retrograde: bool = False) -> bool:
    """Whether ``planet`` is combust (too close to the Sun) in longitude."""
    limit = combustion_limit(planet, retrograde)
    if limit is None:
        return False
    diff = abs((longitude - sun_longitude + 180.0) % 360.0 - 180.0)
    return diff <= limit
