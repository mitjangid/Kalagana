"""Daily muhurta (electional) windows derived from sunrise and sunset.

Conventions
-----------
* Rahu Kalam, Yamaganda and Gulika divide the daylight span (sunrise to
  sunset) into eight equal *kalas*; the weekday picks which kala is
  inauspicious (Rahu: Sun 8th, Mon 2nd, Tue 7th, Wed 5th, Thu 6th, Fri 4th,
  Sat 3rd; the others per the Narada Purana).
* Abhijit is the 8th of the 15 equal daytime muhurtas (around local noon).
* Brahma Muhurta is the 2 muhurtas before sunrise (sunrise-96 to -48 min).
* Choghadiya names cycle through Udveg, Char, Labh, Amrit, Kaal, Shubh, Rog.
* Hora are planetary hours in the Chaldean order, 12 by day and 12 by night.
* Durmuhurta uses the South Indian (Telugu) table; see ``DURMUHURTA``.

Times are timezone-aware datetimes in the observer's zone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .location import Location
from .sunrise import sunrise_sunset

__all__ = [
    "RAHU_INDEX",
    "YAMAGANDA_INDEX",
    "GULIKA_INDEX",
    "DURMUHURTA",
    "CHOGHADIYA_NAMES",
    "HORA_ORDER",
    "MuhurtaWindow",
    "rahu_kalam",
    "yamaganda",
    "gulika_kalam",
    "abhijit_muhurta",
    "brahma_muhurta",
    "durmuhurta",
    "choghadiya",
    "hora",
    "day_timings",
]

# 1-based kala (of 8) by weekday, Sunday first.
RAHU_INDEX = (8, 2, 7, 5, 6, 4, 3)
YAMAGANDA_INDEX = (5, 4, 3, 2, 1, 7, 6)
GULIKA_INDEX = (7, 6, 5, 4, 3, 2, 1)

# Durmuhurta as daytime muhurta numbers (of 15), Sunday first.
# Source: South Indian (Telugu) panchangam convention.
DURMUHURTA = {
    0: (14,),           # Sunday
    1: (9, 12),         # Monday
    2: (4,),            # Tuesday
    3: (8,),            # Wednesday
    4: (6, 12),         # Thursday
    5: (4, 12),         # Friday
    6: (1, 2),          # Saturday (double length)
}

CHOGHADIYA_NAMES = ("Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog")
_CHOGHADIYA_DAY_START = (0, 3, 6, 2, 5, 1, 4)   # Sunday first
_CHOGHADIYA_NIGHT_START = (5, 1, 4, 0, 3, 2, 6)

HORA_ORDER = ("Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars")
_DAY_LORD = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


@dataclass(frozen=True)
class MuhurtaWindow:
    """A named time window."""

    name: str
    start: datetime
    end: datetime


def _sun0(day: date) -> int:
    """Weekday index with Sunday = 0."""
    return (day.weekday() + 1) % 7


def _need_sun(day: date, loc: Location) -> Tuple[datetime, datetime]:
    r, s = sunrise_sunset(day, loc)
    if r is None or s is None:
        raise ValueError("Sun does not rise/set on this date at this location")
    return r, s


def _kala(sunrise: datetime, sunset: datetime, index_1based: int) -> MuhurtaWindow:
    span = (sunset - sunrise) / 8
    start = sunrise + span * (index_1based - 1)
    return MuhurtaWindow("", start, start + span)


def rahu_kalam(day: date, loc: Location) -> MuhurtaWindow:
    """Rahu Kalam: the inauspicious kala of the day (1 of 8 daylight kalas)."""
    r, s = _need_sun(day, loc)
    w = _kala(r, s, RAHU_INDEX[_sun0(day)])
    return MuhurtaWindow("Rahu Kalam", w.start, w.end)


def yamaganda(day: date, loc: Location) -> MuhurtaWindow:
    """Yamaganda (Yamaghantaka) kala."""
    r, s = _need_sun(day, loc)
    w = _kala(r, s, YAMAGANDA_INDEX[_sun0(day)])
    return MuhurtaWindow("Yamaganda", w.start, w.end)


def gulika_kalam(day: date, loc: Location) -> MuhurtaWindow:
    """Gulika (Kulika) kala."""
    r, s = _need_sun(day, loc)
    w = _kala(r, s, GULIKA_INDEX[_sun0(day)])
    return MuhurtaWindow("Gulika Kalam", w.start, w.end)


def abhijit_muhurta(day: date, loc: Location) -> MuhurtaWindow:
    """Abhijit Muhurta: the 8th of the 15 daytime muhurtas (around local noon)."""
    r, s = _need_sun(day, loc)
    span = (s - r) / 15
    start = r + span * 7
    return MuhurtaWindow("Abhijit", start, start + span)


def brahma_muhurta(day: date, loc: Location) -> MuhurtaWindow:
    """Brahma Muhurta: the two muhurtas before sunrise (sunrise-96 .. -48 min)."""
    r, _s = _need_sun(day, loc)
    return MuhurtaWindow("Brahma Muhurta", r - timedelta(minutes=96), r - timedelta(minutes=48))


def durmuhurta(day: date, loc: Location) -> List[MuhurtaWindow]:
    """Durmuhurta windows (South Indian table) for the day."""
    r, s = _need_sun(day, loc)
    span = (s - r) / 15
    out: List[MuhurtaWindow] = []
    for m in DURMUHURTA[_sun0(day)]:
        start = r + span * (m - 1)
        out.append(MuhurtaWindow("Durmuhurta", start, start + span))
    return out


def choghadiya(day: date, loc: Location) -> Dict[str, List[MuhurtaWindow]]:
    """Day and night Choghadiya (eight windows each)."""
    r, s = _need_sun(day, loc)
    next_r, _ = sunrise_sunset(date.fromordinal(day.toordinal() + 1), loc)
    if next_r is None:
        next_r = s + (s - r)  # fall back: mirror the day length

    d0 = _CHOGHADIYA_DAY_START[_sun0(day)]
    n0 = _CHOGHADIYA_NIGHT_START[_sun0(day)]

    day_span = (s - r) / 8
    night_span = (next_r - s) / 8
    day_windows = []
    for i in range(8):
        name = CHOGHADIYA_NAMES[(d0 + i) % 7]
        start = r + day_span * i
        day_windows.append(MuhurtaWindow(name, start, start + day_span))
    night_windows = []
    for i in range(8):
        name = CHOGHADIYA_NAMES[(n0 + i) % 7]
        start = s + night_span * i
        night_windows.append(MuhurtaWindow(name, start, start + night_span))
    return {"day": day_windows, "night": night_windows}


def hora(day: date, loc: Location) -> Dict[str, List[MuhurtaWindow]]:
    """Planetary hours (Hora): 12 by day, 12 by night."""
    r, s = _need_sun(day, loc)
    next_r, _ = sunrise_sunset(date.fromordinal(day.toordinal() + 1), loc)
    if next_r is None:
        next_r = s + (s - r)

    lord = _DAY_LORD[_sun0(day)]
    start_idx = HORA_ORDER.index(lord)

    day_span = (s - r) / 12
    night_span = (next_r - s) / 12
    day_horas = []
    night_horas = []
    for i in range(24):
        name = HORA_ORDER[(start_idx + i) % 7]
        if i < 12:
            start = r + day_span * i
            day_horas.append(MuhurtaWindow(name, start, start + day_span))
        else:
            j = i - 12
            start = s + night_span * j
            night_horas.append(MuhurtaWindow(name, start, start + night_span))
    return {"day": day_horas, "night": night_horas}


def day_timings(day: date, loc: Location) -> Dict[str, object]:
    """Convenience bundle of the principal muhurta windows for ``day``."""
    return {
        "rahu_kalam": rahu_kalam(day, loc),
        "yamaganda": yamaganda(day, loc),
        "gulika_kalam": gulika_kalam(day, loc),
        "abhijit": abhijit_muhurta(day, loc),
        "brahma_muhurta": brahma_muhurta(day, loc),
        "durmuhurta": durmuhurta(day, loc),
        "choghadiya": choghadiya(day, loc),
        "hora": hora(day, loc),
    }
