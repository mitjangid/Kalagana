"""Lunar month (masa) structure: naming, adhika/kshaya, amanta/purnimanta.

Naming rule
-----------
A lunar month is bounded by two successive new moons (amanta system).  During
that span the Sun makes (usually) one sankranti -- an entry into a sidereal
sign.  The month is named from that ingress sign:

    Meena -> Chaitra, Mesha -> Vaishakha, Vrishabha -> Jyeshtha,
    Mithuna -> Ashadha, Karka -> Shravana, Simha -> Bhadrapada,
    Kanya -> Ashwin, Tula -> Kartika, Vrischika -> Margashirsha,
    Dhanu -> Pausha, Makara -> Magha, Kumbha -> Phalguna

* **Adhika masa** -- a lunar month with *no* sankranti inside it (the Sun does
  not change sign); it takes the name of the following month and is observed
  as an extra month.
* **Kshaya masa** -- a lunar month with *two* sankrantis (rare).

The **purnimanta** (North Indian) system assigns the dark fortnight to the
*next* named month, so a purnimanta month conventionally runs from one full
moon to the next.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from . import julian
from .ayanamsa import ayanamsa_degrees
from .limbs import elongation, sidereal_sun_longitude
from .solver import next_crossing, solve_angle

__all__ = [
    "RASHI_NAMES",
    "LUNAR_MONTHS",
    "next_new_moon",
    "prev_new_moon",
    "next_full_moon",
    "prev_full_moon",
    "sankranti_rashis_between",
    "next_sankranti",
    "Masa",
    "masa_at",
    "paksha_at",
]

# Margin (in days) used when chaining "next crossing" calls.  It must exceed
# the solver tolerance (~1 second) so a just-found crossing is not re-found.
_EPS_DAY = 0.01

RASHI_NAMES = (
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
)

# Lunar month names indexed by the sidereal sign the *Sun enters* during them.
# The month takes the name of the solar month the Sun is in while it runs, so
# the index lines up one-to-one: Mesha -> Chaitra, ..., Meena -> Phalguna.
_MONTH_BY_INGRESS = (
    "Chaitra",     # Mesha
    "Vaishakha",   # Vrishabha
    "Jyeshtha",    # Mithuna
    "Ashadha",     # Karka
    "Shravana",    # Simha
    "Bhadrapada",  # Kanya
    "Ashwin",      # Tula
    "Kartika",     # Vrischika
    "Margashirsha",  # Dhanu
    "Pausha",      # Makara
    "Magha",       # Kumbha
    "Phalguna",    # Meena
)

# Canonical ordered list of the 12 lunar month names (Chaitra first).
LUNAR_MONTHS = (
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
)


def next_new_moon(jd_tt: float) -> float:
    """Instant (JD TT) of the first new moon at or after ``jd_tt``."""
    r = next_crossing(elongation, 0.0, jd_tt, max_days=40.0)
    if r is None:
        raise RuntimeError("next_new_moon: no crossing found")
    return r


def prev_new_moon(jd_tt: float) -> float:
    """Instant (JD TT) of the last new moon at or before ``jd_tt``."""
    return _prev_crossing(0.0, jd_tt)


def _nudge(jd: float) -> float:
    """Advance just past a crossing so the next search excludes it."""
    return jd + _EPS_DAY


def _prev_crossing(target: float, jd_tt: float, lookback: float = 40.0) -> float:
    """Last elongation crossing of ``target`` at or before ``jd_tt``."""
    jd = jd_tt - lookback
    nm = next_crossing(elongation, target, jd, max_days=lookback + 5.0)
    if nm is None:
        raise RuntimeError("prev crossing: none found")
    best = nm
    while nm <= jd_tt:
        best = nm
        nm = next_crossing(elongation, target, nm + 0.5, max_days=40.0)
        if nm is None:
            break
    return best


def next_full_moon(jd_tt: float) -> float:
    """Instant (JD TT) of the first full moon at or after ``jd_tt``."""
    r = next_crossing(elongation, 180.0, jd_tt, max_days=40.0)
    if r is None:
        raise RuntimeError("next_full_moon: no crossing found")
    return r


def prev_full_moon(jd_tt: float) -> float:
    """Instant (JD TT) of the last full moon at or before ``jd_tt``."""
    return _prev_crossing(180.0, jd_tt)


def _sidereal_sun(jd: float) -> float:
    return sidereal_sun_longitude(jd, "lahiri")


def next_sankranti(jd_tt: float, ayanamsa: str = "lahiri") -> Tuple[int, float]:
    """Next sidereal sign ingress at/after ``jd_tt``.

    Returns ``(rashi_index_0_11, jd)`` where rashi 0 = Mesha.
    """
    v0 = sidereal_sun_longitude(jd_tt, ayanamsa)
    m = int(v0 // 30.0) + 1  # next multiple of 30 ahead

    def f(jd: float) -> float:
        return sidereal_sun_longitude(jd, ayanamsa)

    jd = jd_tt
    for _ in range(4):
        target = (m * 30.0) % 360.0
        jc = solve_angle(f, target, jd, jd + 40.0, scan_step=0.25)
        if jc is not None:
            return m % 12, jc
        jd += 40.0
    raise RuntimeError("next_sankranti: no ingress found")


def sankranti_rashis_between(
    jd_start: float,
    jd_end: float,
    ayanamsa: str = "lahiri",
) -> List[Tuple[int, float]]:
    """All sidereal sign ingresses in ``(jd_start, jd_end]``.

    Returns a list of ``(rashi_index_0_11, jd)``.
    """
    out: List[Tuple[int, float]] = []
    v0 = sidereal_sun_longitude(jd_start, ayanamsa)
    m = int(v0 // 30.0) + 1
    jd = jd_start
    while jd < jd_end:
        target = (m * 30.0) % 360.0
        jc = solve_angle(
            lambda x: sidereal_sun_longitude(x, ayanamsa),
            target,
            jd,
            jd_end + 0.5,
            scan_step=0.25,
        )
        if jc is None or jc > jd_end:
            break
        out.append((m % 12, jc))
        jd = _nudge(jc)
        m += 1
    return out


@dataclass(frozen=True)
class Masa:
    """A lunar month with its structure and naming."""

    name: str
    amanta: bool
    adhika: bool
    kshaya: bool
    start: datetime
    end: datetime
    ingress_rashi: Optional[int]
    ingress_time: Optional[datetime]

    @property
    def display(self) -> str:
        return f"Adhika {self.name}" if self.adhika else self.name


def masa_at(jd_tt: float, ayanamsa: str = "lahiri") -> Masa:
    """Determine the lunar month containing ``jd_tt`` (amanta system)."""
    start = prev_new_moon(jd_tt)
    end = next_new_moon(_nudge(jd_tt))
    ingress = sankranti_rashis_between(start, end, ayanamsa)

    adhika = len(ingress) == 0
    kshaya = len(ingress) > 1

    if adhika:
        # Adhika month takes the name of the *following* nija month.
        nxt = sankranti_rashis_between(end, next_new_moon(_nudge(end)), ayanamsa)
        if nxt:
            name = _MONTH_BY_INGRESS[nxt[0][0]]
        else:
            name = LUNAR_MONTHS[0]
        rashi = None
        itime = None
    else:
        rashi, itime_jd = ingress[0]
        name = _MONTH_BY_INGRESS[rashi]
        itime = julian.jd_to_datetime(itime_jd)

    return Masa(
        name=name,
        amanta=True,
        adhika=adhika,
        kshaya=kshaya,
        start=julian.jd_to_datetime(start),
        end=julian.jd_to_datetime(end),
        ingress_rashi=rashi,
        ingress_time=itime,
    )


def paksha_at(jd_tt: float) -> str:
    """Return 'Shukla' (waxing) or 'Krishna' (waning) at ``jd_tt``."""
    return "Shukla" if elongation(jd_tt) < 180.0 else "Krishna"


def purnimanta_name(jd_tt: float, ayanamsa: str = "lahiri") -> str:
    """Lunar month name in the purnimanta (North Indian) convention.

    In the dark fortnight the purnimanta month is the *next* named month, so
    the purnimanta month runs from full moon to full moon.
    """
    m = masa_at(jd_tt, ayanamsa)
    if paksha_at(jd_tt) == "Krishna":
        idx = LUNAR_MONTHS.index(m.name)
        return LUNAR_MONTHS[(idx + 1) % 12]
    return m.name
