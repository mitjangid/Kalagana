"""Chart layouts for the three Indian birth-chart styles.

These helpers return plain data (sign indices, houses and graha names) so a
presentation layer can draw them.  No drawing code lives in the package.

The three styles encode identical data; only the arrangement differs:

* **North Indian** -- *houses* are fixed and the *signs* rotate.  House 1 is
  always the top-centre diamond and the signs run anti-clockwise.
* **South Indian** -- *signs* are fixed in a 4x4 perimeter grid (Pisces at the
  top-left, running clockwise) and the *houses* rotate.  The Lagna cell is
  marked with a diagonal.
* **East Indian** (Bengali / Odia / Surya Chakra) -- *signs* are fixed in a
  grid-with-diagonals layout and the *houses* rotate.  The Lagna cell is marked.

Conventions and caveats
-----------------------
The South Indian sign order below (Pisces, Aries, Taurus, Gemini, Cancer, Leo,
Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, clockwise from the
top-left) is the standard one and is not disputed.

The **East Indian** arrangement varies slightly between regional traditions and
published sources.  This module implements one consistent, documented scheme
(signs fixed, running anti-clockwise from Aries in the top rectangle) and
exposes the order as a module constant (:data:`EAST_SIGN_ORDER`) so it can be
adjusted.  Treat the East Indian cell geometry as conventional, not canonical.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from .angles import RASHIS, RASHIS_EN

__all__ = [
    "NORTH_ORDER",
    "SOUTH_SIGN_ORDER",
    "SOUTH_CELLS",
    "EAST_SIGN_ORDER",
    "EAST_CELLS",
    "north_chart",
    "south_chart",
    "east_chart",
    "charts",
    "CHART_FORMATS",
]

#: North Indian: houses are fixed; house 1 is the top diamond.
NORTH_ORDER = tuple(range(1, 13))

#: South Indian: sign at each perimeter cell, clockwise from the top-left.
#: Pisces, Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio,
#: Sagittarius, Capricorn, Aquarius.
SOUTH_SIGN_ORDER: Tuple[int, ...] = (11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

#: (row, col) of each South Indian cell in a 4x4 grid, matching SOUTH_SIGN_ORDER.
SOUTH_CELLS: Tuple[Tuple[int, int], ...] = (
    (0, 0), (0, 1), (0, 2), (0, 3),
    (1, 3), (2, 3), (3, 3), (3, 2),
    (3, 1), (3, 0), (2, 0), (1, 0),
)

#: East Indian: sign at each cell, anti-clockwise from Aries at the top.
#: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius,
#: Capricorn, Aquarius, Pisces.
EAST_SIGN_ORDER: Tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

#: Named East Indian cells, matching EAST_SIGN_ORDER.  Geometry: a 3x3 grid with
#: the four corners split by diagonals, giving 4 edge rectangles (top/left/
#: right/bottom) and 8 corner triangles.
EAST_CELLS: Tuple[Tuple[str, str], ...] = (
    ("edge", "top"),
    ("corner", "top-left-upper"),
    ("corner", "top-left-left"),
    ("edge", "left"),
    ("corner", "bottom-left-left"),
    ("corner", "bottom-left-lower"),
    ("edge", "bottom"),
    ("corner", "bottom-right-lower"),
    ("corner", "bottom-right-right"),
    ("edge", "right"),
    ("corner", "top-right-right"),
    ("corner", "top-right-upper"),
)

#: The supported format names.
CHART_FORMATS = ("north", "south", "east")


def _grahas_in(rashi_by_graha: Dict[str, int], rashi: int) -> List[str]:
    return [g for g, r in rashi_by_graha.items() if r == rashi]


def _house_of(rashi: int, asc_rashi: int) -> int:
    return (rashi - asc_rashi) % 12 + 1


def north_chart(asc_rashi: int, rashi_by_graha: Dict[str, int]) -> List[Dict[str, object]]:
    """Return 12 house cells for a North Indian chart.

    Houses are fixed (1..12, anti-clockwise from the top diamond); the sign in
    each house rotates with the Lagna.
    """
    cells: List[Dict[str, object]] = []
    for h in range(1, 13):
        rashi = (asc_rashi + h - 1) % 12
        cells.append({
            "house": h,
            "rashi": rashi,
            "rashi_name": RASHIS[rashi],
            "rashi_en": RASHIS_EN[rashi],
            "grahas": _grahas_in(rashi_by_graha, rashi),
            "lagna": h == 1,
        })
    return cells


def south_chart(asc_rashi: int, rashi_by_graha: Dict[str, int]) -> List[Dict[str, object]]:
    """Return 12 fixed-sign cells for a South Indian chart.

    Each cell carries its ``row``/``col`` in the 4x4 grid and the house number
    counted clockwise from the Lagna.
    """
    cells: List[Dict[str, object]] = []
    for (row, col), rashi in zip(SOUTH_CELLS, SOUTH_SIGN_ORDER):
        cells.append({
            "row": row,
            "col": col,
            "rashi": rashi,
            "rashi_name": RASHIS[rashi],
            "rashi_en": RASHIS_EN[rashi],
            "house": _house_of(rashi, asc_rashi),
            "grahas": _grahas_in(rashi_by_graha, rashi),
            "lagna": rashi == asc_rashi,
        })
    return cells


def east_chart(asc_rashi: int, rashi_by_graha: Dict[str, int]) -> List[Dict[str, object]]:
    """Return 12 fixed-sign cells for an East Indian (Bengali) chart.

    Each cell carries its ``kind`` (``"edge"``/``"corner"``) and ``position``
    label, the house counted from the Lagna, and the grahas in it.
    """
    cells: List[Dict[str, object]] = []
    for (kind, position), rashi in zip(EAST_CELLS, EAST_SIGN_ORDER):
        cells.append({
            "kind": kind,
            "position": position,
            "rashi": rashi,
            "rashi_name": RASHIS[rashi],
            "rashi_en": RASHIS_EN[rashi],
            "house": _house_of(rashi, asc_rashi),
            "grahas": _grahas_in(rashi_by_graha, rashi),
            "lagna": rashi == asc_rashi,
        })
    return cells


def charts(
    asc_rashi: int,
    rashi_by_graha: Dict[str, int],
    formats: Sequence[str] = CHART_FORMATS,
) -> Dict[str, List[Dict[str, object]]]:
    """Build any or all of the three Indian chart layouts.

    ``rashi_by_graha`` maps graha name -> rashi index; ``asc_rashi`` is the
    Lagna's rashi index.
    """
    builders = {"north": north_chart, "south": south_chart, "east": east_chart}
    out: Dict[str, List[Dict[str, object]]] = {}
    for fmt in formats:
        key = fmt.strip().lower()
        if key not in builders:
            raise ValueError(f"unknown chart format {fmt!r}; expected one of {CHART_FORMATS}")
        out[key] = builders[key](asc_rashi, rashi_by_graha)
    return out