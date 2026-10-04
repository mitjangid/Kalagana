"""Vimshottari dasha -- the 120-year cycle of planetary periods.

The starting period is fixed by the birth nakshatra of the Moon and the balance
is proportional to the fraction of that nakshatra still to run.  Sub-periods
(antardasha, pratyantardasha) subdivide each period in the same fixed order,
each proportional to its lord's years.

A year is taken as :data:`YEAR_DAYS` (365.2425 days, the mean Gregorian year);
some software uses 365.25, a difference of a few hours over a full 120-year
cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .. import julian
from ..limbs import NAKSHATRAS, NAKSHATRA_SIZE

__all__ = [
    "DASHA_ORDER",
    "DASHA_YEARS",
    "YEAR_DAYS",
    "NAKSHATRA_LORDS",
    "DashaPeriod",
    "vimshottari",
    "nakshatra_lord",
]

#: Vimshottari order of the nine lords.
DASHA_ORDER: Tuple[str, ...] = (
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
)
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
TOTAL_YEARS = 120.0

#: Mean length of a year in days used to convert dasha years to calendar days.
YEAR_DAYS = 365.2425

#: Lord assigned to each nakshatra (index 0 = Ashwini), cycling through
#: :data:`DASHA_ORDER`.
NAKSHATRA_LORDS = tuple(DASHA_ORDER[i % 9] for i in range(27))


def nakshatra_lord(nakshatra_number: int) -> str:
    """Vimshottari lord of a nakshatra (1-27)."""
    return NAKSHATRA_LORDS[(nakshatra_number - 1) % 27]


@dataclass
class DashaPeriod:
    """A dasha period with an optional tree of sub-periods."""

    lord: str
    level: str
    start_jd: float
    end_jd: float
    sub: List["DashaPeriod"] = field(default_factory=list)

    @property
    def years(self) -> float:
        return (self.end_jd - self.start_jd) / YEAR_DAYS

    def to_dict(self, with_sub: bool = True) -> dict:
        d = {
            "lord": self.lord,
            "level": self.level,
            "start": julian.jd_to_datetime(self.start_jd).isoformat(),
            "end": julian.jd_to_datetime(self.end_jd).isoformat(),
            "years": round(self.years, 4),
        }
        if with_sub and self.sub:
            d["sub"] = [p.to_dict(with_sub) for p in self.sub]
        return d


def _subdivide(
    lord: str,
    start_jd: float,
    total_years: float,
    depth: int,
    level_name: str,
) -> List[DashaPeriod]:
    """Split a period into its sub-periods starting from ``lord``."""
    periods: List[DashaPeriod] = []
    jd = start_jd
    start_idx = DASHA_ORDER.index(lord)
    for k in range(9):
        sub_lord = DASHA_ORDER[(start_idx + k) % 9]
        years = total_years * DASHA_YEARS[sub_lord] / TOTAL_YEARS
        end_jd = jd + years * YEAR_DAYS
        subs: List[DashaPeriod] = []
        if depth > 1:
            subs = _subdivide(sub_lord, jd, years, depth - 1, "pratyantardasha")
        periods.append(
            DashaPeriod(
                lord=sub_lord,
                level=level_name,
                start_jd=jd,
                end_jd=end_jd,
                sub=subs,
            )
        )
        jd = end_jd
    return periods


def vimshottari(
    moon_longitude: float,
    birth_jd: float,
    depth: int = 2,
    count: int = 9,
) -> List[DashaPeriod]:
    """Compute the Vimshottari mahadashas from a birth instant.

    ``moon_longitude`` is the **sidereal** Moon longitude in degrees.
    ``birth_jd`` is the birth instant as a Julian Day (TT or UT; the offset is
    immaterial at dasha resolution).  ``depth`` selects how many nested levels
    to build (1 = mahadasha only, 2 = + antardasha, 3 = + pratyantardasha).
    ``count`` is how many mahadashas to return (9 covers the full 120 years).
    """
    lon = moon_longitude % 360.0
    nak_index = int(lon // NAKSHATRA_SIZE)
    within = lon % NAKSHATRA_SIZE
    elapsed_fraction = within / NAKSHATRA_SIZE

    start_lord = NAKSHATRA_LORDS[nak_index % 27]
    first_years = DASHA_YEARS[start_lord]
    # The balance of the first mahadasha still to run at birth.
    elapsed_days = elapsed_fraction * first_years * YEAR_DAYS
    start_jd = birth_jd - elapsed_days

    out: List[DashaPeriod] = []
    jd = start_jd
    start_idx = DASHA_ORDER.index(start_lord)
    for k in range(count):
        lord = DASHA_ORDER[(start_idx + k) % 9]
        years = float(DASHA_YEARS[lord])
        end_jd = jd + years * YEAR_DAYS
        subs = _subdivide(lord, jd, years, depth - 1, "antardasha") if depth > 1 else []
        out.append(DashaPeriod(lord=lord, level="mahadasha", start_jd=jd, end_jd=end_jd, sub=subs))
        jd = end_jd
    return out


def current_period(periods: List[DashaPeriod], jd: float) -> Optional[Tuple[DashaPeriod, ...]]:
    """Return the chain of periods containing ``jd`` (mahadasha, antardasha, ...)."""
    chain: List[DashaPeriod] = []
    level = periods
    while level:
        found = next((p for p in level if p.start_jd <= jd < p.end_jd), None)
        if found is None:
            break
        chain.append(found)
        level = found.sub
    return tuple(chain) if chain else None
