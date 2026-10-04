"""Marriage compatibility: Ashtakoota (Guna Milana) and Mangal dosha.

Ashtakoota scores eight kootas out of 36 points: Varna (1), Vashya (2),
Tara/Dina (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7) and Nadi (8).

Conventions
-----------
The assignments (varna, vashya, gana, nadi, yoni) are the standard ones found
in most Indian panchangs.  Two of the kootas are scored with *simplified*
tiers and are flagged as such in the result, because full classical tables
(especially the 14x14 Yoni matrix and the half-sign Vashya refinements) vary
between authors:

* **Vashya** -- full points when the groups match, otherwise a coarse tier.
* **Yoni**   -- full points for the same animal, zero for the classical sworn
  enemies, otherwise a neutral tier.

Treat the total as indicative and always show the koota breakdown.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

__all__ = [
    "VARNA_BY_RASHI",
    "VASHYA_BY_RASHI",
    "GANA_BY_NAKSHATRA",
    "NADI_BY_NAKSHATRA",
    "YONI_BY_NAKSHATRA",
    "MANgal_HOUSES",
    "Koota",
    "MatchResult",
    "ashtakoota",
    "mangal_dosha",
]

_VARNA_NAMES = ("Shudra", "Vaishya", "Kshatriya", "Brahmin")
# Rashi -> varna rank (1 Shudra .. 4 Brahmin).
VARNA_BY_RASHI = (
    3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4,
)

_VASHYA_NAMES = ("Chatushpada", "Manava", "Jalachara", "Keeta")
VASHYA_BY_RASHI = (
    0, 0, 1, 2, 0, 1, 1, 3, 0, 0, 1, 2,
)

_GANA_NAMES = ("Deva", "Manushya", "Rakshasa")
_GANA_BY_IDX = [
    0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0,
]
GANA_BY_NAKSHATRA = tuple(_GANA_BY_IDX)

_NADI_NAMES = ("Adi", "Madhya", "Antya")
_NADI_BY_IDX = [
    0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2,
]
NADI_BY_NAKSHATRA = tuple(_NADI_BY_IDX)

# Yoni: (animal, gender) per nakshatra; gender is 'M'/'F'.
_YONI_BY_IDX = [
    ("Horse", "M"), ("Elephant", "M"), ("Goat", "M"), ("Serpent", "M"),
    ("Serpent", "F"), ("Dog", "F"), ("Cat", "F"), ("Goat", "F"),
    ("Cat", "M"), ("Rat", "M"), ("Rat", "F"), ("Cow", "F"),
    ("Buffalo", "F"), ("Tiger", "F"), ("Buffalo", "M"), ("Tiger", "M"),
    ("Deer", "F"), ("Deer", "M"), ("Dog", "M"), ("Monkey", "M"),
    ("Mongoose", "M"), ("Monkey", "F"), ("Lion", "F"), ("Horse", "F"),
    ("Lion", "M"), ("Cow", "M"), ("Elephant", "F"),
]
YONI_BY_NAKSHATRA = tuple(_YONI_BY_IDX)

_YONI_ENEMIES = (
    frozenset(("Cow", "Tiger")),
    frozenset(("Elephant", "Lion")),
    frozenset(("Horse", "Buffalo")),
    frozenset(("Dog", "Deer")),
    frozenset(("Cat", "Rat")),
    frozenset(("Monkey", "Goat")),
    frozenset(("Mongoose", "Serpent")),
)

# Mangal (Kuja) dosha houses counted from a reference point.
MANgal_HOUSES = (1, 2, 4, 7, 8, 12)


@dataclass(frozen=True)
class Koota:
    name: str
    score: float
    maximum: float
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.score >= self.maximum * 0.5


@dataclass(frozen=True)
class MatchResult:
    kootas: List[Koota]
    total: float
    maximum: float
    verdict: str
    notes: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "total": round(self.total, 2),
            "maximum": self.maximum,
            "verdict": self.verdict,
            "kootas": [
                {"name": k.name, "score": k.score, "max": k.maximum, "detail": k.detail}
                for k in self.kootas
            ],
            "notes": self.notes,
        }


def _tara_points(a_nak: int, b_nak: int) -> float:
    """Tara (Dina) points for one direction (1.5 good, 0 bad)."""
    count = (b_nak - a_nak) % 27
    # Tara number = (count % 9) + 1; the 1st, 3rd, 5th and 7th are malefic.
    return 0.0 if (count % 9) in (0, 2, 4, 6) else 1.5


def _vashya_points(a_rashi: int, b_rashi: int) -> Tuple[float, str]:
    ga = VASHYA_BY_RASHI[a_rashi]
    gb = VASHYA_BY_RASHI[b_rashi]
    if ga == gb:
        return 2.0, _VASHYA_NAMES[ga]
    if "Keeta" in (_VASHYA_NAMES[ga], _VASHYA_NAMES[gb]):
        return 0.0, "one is Keeta (insect)"
    return 1.0, "different groups"


def _yoni_points(a_nak: int, b_nak: int) -> Tuple[float, str]:
    a_animal, _ = YONI_BY_NAKSHATRA[a_nak - 1]
    b_animal, _ = YONI_BY_NAKSHATRA[b_nak - 1]
    if a_animal == b_animal:
        return 4.0, f"same yoni ({a_animal})"
    if frozenset((a_animal, b_animal)) in _YONI_ENEMIES:
        return 0.0, f"sworn enemies ({a_animal}/{b_animal})"
    return 2.0, f"{a_animal}/{b_animal}"


def _graha_maitri_points(a_rashi: int, b_rashi: int) -> Tuple[float, str]:
    from .dignity import rashi_lord

    la, lb = rashi_lord(a_rashi), rashi_lord(b_rashi)
    if la == lb:
        return 5.0, f"same lord ({la})"
    ra = _friendship(la, lb)
    rb = _friendship(lb, la)
    pair = {ra, rb}
    if pair == {"friend"}:
        return 5.0, f"{la}/{lb} mutual friends"
    if ra == rb == "neutral":
        return 3.0, f"{la}/{lb} neutral"
    if pair == {"friend", "neutral"}:
        return 4.0, f"{la}/{lb} friend/neutral"
    if pair == {"friend", "enemy"}:
        return 1.0, f"{la}/{lb} friend/enemy"
    if pair == {"neutral", "enemy"}:
        return 0.5, f"{la}/{lb} neutral/enemy"
    return 0.0, f"{la}/{lb} mutual enemies"


def _friendship(a: str, b: str) -> str:
    from .dignity import NATURAL_ENEMIES, NATURAL_FRIENDS

    if b in NATURAL_FRIENDS.get(a, ()):
        return "friend"
    if b in NATURAL_ENEMIES.get(a, ()):
        return "enemy"
    return "neutral"


def _gana_points(a_nak: int, b_nak: int) -> Tuple[float, str]:
    ga = _GANA_NAMES[GANA_BY_NAKSHATRA[a_nak - 1]]
    gb = _GANA_NAMES[GANA_BY_NAKSHATRA[b_nak - 1]]
    if ga == gb:
        return 6.0, ga
    pair = frozenset((ga, gb))
    if pair == frozenset(("Deva", "Manushya")):
        return 5.0, f"{ga}/{gb}"
    if pair == frozenset(("Deva", "Rakshasa")):
        return 1.0, f"{ga}/{gb}"
    return 0.0, f"{ga}/{gb}"


def _bhakoot_points(a_rashi: int, b_rashi: int) -> Tuple[float, str]:
    # Count from the girl's rashi to the boy's.
    diff = (a_rashi - b_rashi) % 12 + 1
    if diff in (2, 12, 5, 9, 6, 8):
        return 0.0, f"inauspicious distance ({diff})"
    return 7.0, f"distance {diff}"


def _nadi_points(a_nak: int, b_nak: int) -> Tuple[float, str]:
    na = _NADI_NAMES[NADI_BY_NAKSHATRA[a_nak - 1]]
    nb = _NADI_NAMES[NADI_BY_NAKSHATRA[b_nak - 1]]
    if na == nb:
        return 0.0, f"same nadi ({na})"
    return 8.0, f"{na}/{nb}"


def ashtakoota(
    boy_rashi: int,
    boy_nakshatra: int,
    girl_rashi: int,
    girl_nakshatra: int,
) -> MatchResult:
    """Compute the Ashtakoota (Guna Milana) score for a boy/girl pair.

    ``*_rashi`` are 0-based rashi indices (0 = Aries); ``*_nakshatra`` are
    1-based nakshatra numbers (1 = Ashwini).
    """
    notes: List[str] = []
    kootas: List[Koota] = []

    # 1. Varna (1)
    bv, gv = VARNA_BY_RASHI[boy_rashi], VARNA_BY_RASHI[girl_rashi]
    kootas.append(Koota("Varna", 1.0 if bv >= gv else 0.0, 1.0,
                        f"{_VARNA_NAMES[bv - 1]}/{_VARNA_NAMES[gv - 1]}"))

    # 2. Vashya (2)
    vs, vd = _vashya_points(boy_rashi, girl_rashi)
    kootas.append(Koota("Vashya", vs, 2.0, vd + " (simplified tiers)"))
    notes.append("Vashya uses simplified tiers.")

    # 3. Tara / Dina (3)
    t1 = _tara_points(girl_nakshatra, boy_nakshatra)
    t2 = _tara_points(boy_nakshatra, girl_nakshatra)
    kootas.append(Koota("Tara", t1 + t2, 3.0, "both directions"))

    # 4. Yoni (4)
    ys, yd = _yoni_points(boy_nakshatra, girl_nakshatra)
    kootas.append(Koota("Yoni", ys, 4.0, yd + " (simplified tiers)"))
    notes.append("Yoni uses simplified tiers.")

    # 5. Graha Maitri (5)
    gs, gd = _graha_maitri_points(boy_rashi, girl_rashi)
    kootas.append(Koota("Graha Maitri", gs, 5.0, gd))

    # 6. Gana (6)
    gns, gnd = _gana_points(boy_nakshatra, girl_nakshatra)
    kootas.append(Koota("Gana", gns, 6.0, gnd))

    # 7. Bhakoot (7)
    bs, bd = _bhakoot_points(boy_rashi, girl_rashi)
    kootas.append(Koota("Bhakoot", bs, 7.0, bd))

    # 8. Nadi (8)
    ns, nd = _nadi_points(boy_nakshatra, girl_nakshatra)
    kootas.append(Koota("Nadi", ns, 8.0, nd))

    total = sum(k.score for k in kootas)
    maximum = sum(k.maximum for k in kootas)
    if total < 18:
        verdict = "Not recommended"
    elif total < 25:
        verdict = "Acceptable"
    elif total < 32:
        verdict = "Good"
    else:
        verdict = "Excellent"
    return MatchResult(kootas=kootas, total=total, maximum=maximum, verdict=verdict, notes=notes)


def mangal_dosha(rashi_houses: Dict[str, int]) -> Dict[str, object]:
    """Detect Mangal (Kuja) dosha from Mars house positions.

    ``rashi_houses`` maps a reference point (``"lagna"``, ``"moon"``,
    ``"venus"``) to the house number (1-12) occupied by Mars from it.  Dosha is
    present at a reference when Mars sits in house 1, 2, 4, 7, 8 or 12.
    """
    affected = [ref for ref, h in rashi_houses.items() if h in MANgal_HOUSES]
    return {
        "present": bool(affected),
        "from": affected,
        "houses": dict(rashi_houses),
        "note": "Cancellation (dosha bhanga) rules are not applied.",
    }
