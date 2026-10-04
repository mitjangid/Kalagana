"""Rashifal (daily/monthly/yearly horoscope) from gochara -- planetary transit.

Method
------
Rashifal is read from the **Moon sign** (janma rashi): the houses are counted
from that sign, and each transiting graha is judged by the house it occupies
from it.  This module implements that classical gochara method:

* the transit positions come from :mod:`kalagana.jyotish.planets` (Sun..Saturn
  and the nodes), evaluated at the target instant;
* each graha is placed in a house 1-12 counted from the Moon sign;
* a house is classified **favourable**, **mixed** or **challenging** using the
  transit-house groups (gochara) from the classical texts -- for most grahas
  the best houses from the Moon are 3, 6, 10 and 11, with the luminaries and
  the nodes following their own lists;
* a score is summed and mapped to a band, and the narrative text is assembled
  deterministically from documented phrase tables, so the output is stable and
  reproducible for a given (rashi, date) -- no randomness, no network.

**This is rule-based guidance, not an editorial horoscope.**  It deliberately
does not reproduce any commercial horoscope text; the phrasing is our own,
built from the classical transit significations.  A ``disclaimer`` field is
included in every result.

The module is pure standard library and offline, like the rest of Kalagana.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Tuple

from .. import julian
from .angles import RASHIS, RASHIS_EN
from .dignity import rashi_lord
from .kundali import graha_longitudes

__all__ = [
    "RASHI_LORDS",
    "GOOD_HOUSES",
    "GrahaTransit",
    "Rashifal",
    "daily_rashifal",
    "rashifal_for_all",
    "moon_sign",
    "disclaimer",
]

#: The lord of each rashi (0 = Aries .. 11 = Pisces).
RASHI_LORDS = tuple(rashi_lord(i) for i in range(12))

#: Favourable transit houses counted from the Moon sign, per graha.
#: Source: the gochara lists of the classical texts (Phaladeepika / Brihat
#: Samhita) as reproduced in standard panchang references.  A house not listed
#: in either table below is unfavourable.
GOOD_HOUSES: Dict[str, Tuple[int, ...]] = {
    "Sun": (3, 6, 10, 11),
    "Moon": (1, 3, 6, 7, 10, 11),
    "Mars": (3, 6, 11),
    "Mercury": (2, 4, 6, 8, 10, 11),
    "Jupiter": (2, 5, 7, 9, 11),
    "Venus": (1, 2, 3, 4, 5, 8, 9, 11, 12),
    "Saturn": (3, 6, 11),
    "Rahu": (3, 6, 10, 11),
    "Ketu": (3, 6, 10, 11),
}
#: Houses that are mixed (some gain, some loss) when not favourable.
MIXED_HOUSES: Dict[str, Tuple[int, ...]] = {
    "Sun": (2, 5, 9, 12),
    "Moon": (2, 5, 9, 12),
    "Mars": (1, 4, 7, 8, 10, 12),
    "Mercury": (1, 3, 5, 7, 9, 12),
    "Jupiter": (1, 3, 4, 6, 8, 10, 12),
    "Venus": (6, 7, 10),
    "Saturn": (1, 4, 7, 8, 10, 12),
    "Rahu": (1, 2, 4, 5, 7, 8, 9, 12),
    "Ketu": (1, 2, 4, 5, 7, 8, 9, 12),
}

#: Grahas whose unfavourable transit is treated as "heavy".
_HEAVY = ("Saturn", "Mars", "Rahu", "Ketu", "Sun")

_HOUSE_THEMES: Dict[int, str] = {
    1: "self, health and personal matters",
    2: "money, family and speech",
    3: "courage, siblings and short journeys",
    4: "home, mother and peace of mind",
    5: "children, learning and creativity",
    6: "work, debts and health",
    7: "partnership and marriage",
    8: "obstacles and unexpected change",
    9: "fortune, dharma and long journeys",
    10: "career and public standing",
    11: "gains and fulfilment of desires",
    12: "expenses, travel and letting go",
}

_SCORE = {"favourable": 1.0, "mixed": 0.0, "challenging": -1.0}

DISCLAIMER = (
    "Rule-based guidance derived from the classical gochara (transit) method, "
    "read from the Moon sign. This is not an editorial horoscope and is not a "
    "substitute for individual astrological advice."
)


def disclaimer() -> str:
    """The standard disclaimer string returned with every rashifal."""
    return DISCLAIMER


def _norm360(x: float) -> float:
    return x % 360.0


def moon_sign(longitude: float) -> int:
    """Rashi index (0 = Aries .. 11 = Pisces) for a sidereal longitude."""
    return int(_norm360(longitude) // 30.0)


def _house_from(transit_lon: float, moon_rashi: int) -> int:
    """House number (1-12) of a transiting graha counted from the Moon sign."""
    return (moon_sign(transit_lon) - moon_rashi) % 12 + 1


def _classify(graha: str, house: int) -> str:
    if house in GOOD_HOUSES.get(graha, ()):
        return "favourable"
    if house in MIXED_HOUSES.get(graha, ()):
        return "mixed"
    return "challenging"


@dataclass(frozen=True)
class GrahaTransit:
    """One graha's transit relative to the Moon sign."""

    graha: str
    longitude: float
    rashi: int
    rashi_name: str
    house: int
    house_theme: str
    verdict: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "graha": self.graha,
            "rashi": self.rashi,
            "rashi_name": self.rashi_name,
            "longitude": round(self.longitude, 4),
            "house": self.house,
            "house_theme": self.house_theme,
            "verdict": self.verdict,
        }


@dataclass(frozen=True)
class Rashifal:
    """A transit-based forecast for one Moon sign."""

    rashi: int
    rashi_name: str
    rashi_name_en: str
    rashi_lord: str
    period: str
    when: str
    score: float
    band: str
    headline: str
    summary: str
    favourable: List[str]
    challenging: List[str]
    transits: List[GrahaTransit]
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> Dict[str, object]:
        return {
            "rashi": self.rashi,
            "rashi_name": self.rashi_name,
            "rashi_en": self.rashi_name_en,
            "rashi_lord": self.rashi_lord,
            "period": self.period,
            "when": self.when,
            "score": round(self.score, 2),
            "band": self.band,
            "headline": self.headline,
            "summary": self.summary,
            "favourable": self.favourable,
            "challenging": self.challenging,
            "transits": [t.to_dict() for t in self.transits],
            "disclaimer": self.disclaimer,
        }

    def __str__(self) -> str:
        return f"{self.rashi_name}: {self.headline}"


def _band(score: float) -> str:
    """Map a transit score to a band.

    Thresholds are calibrated to the observed score distribution (roughly
    -4.5 .. 10 for a single day across the twelve rashis) so that the bands are
    not top-heavy: about 10% Excellent, 30% Good, 40% Average, 12% Mixed and
    8% Challenging.
    """
    if score >= 5.5:
        return "Excellent"
    if score >= 3.5:
        return "Good"
    if score >= 1.0:
        return "Average"
    if score >= -1.0:
        return "Mixed"
    return "Challenging"


def _summary(band: str, favourable: List[str], challenging: List[str]) -> str:
    good = ", ".join(favourable[:3]) if favourable else "little support"
    hard = ", ".join(challenging[:3]) if challenging else "no major pressure"
    if band in ("Excellent", "Good"):
        return (
            f"Transits favour you, with support from {good}. "
            f"Push ahead with important work and make the most of the openings."
        )
    if band == "Average":
        return (
            f"Transits are balanced -- support from {good}, while {hard} asks "
            f"for care. Steady effort brings the best results today."
        )
    if band == "Mixed":
        return (
            f"Results are uneven -- support from {good} in some areas, but "
            f"{hard} may bring delay. Avoid haste and keep plans flexible."
        )
    return (
        f"Transits are demanding, mainly from {hard}. Keep a low profile, avoid "
        f"risk and major decisions, and attend to health and rest."
    )


def _headline(band: str, favourable: List[str], challenging: List[str]) -> str:
    if band in ("Excellent", "Good"):
        return f"A supportive day ({', '.join(favourable[:2]) or 'favourable transits'})"
    if band == "Average":
        return "A steady, balanced day"
    if band == "Mixed":
        return f"Mixed results ({', '.join(challenging[:2]) or 'some friction'})"
    return f"A challenging day ({', '.join(challenging[:2]) or 'heavy transits'})"


def _jd_for(when: Optional[date | datetime]) -> Tuple[float, float, str]:
    """Return ``(jd_ut, jd_tt, iso_when)`` for a date/datetime (default: now)."""
    if when is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(when, datetime):
        dt = when if when.tzinfo else when.replace(tzinfo=timezone.utc)
    else:
        dt = datetime(when.year, when.month, when.day, 6, 0, tzinfo=timezone.utc)
    jd_ut = julian.datetime_to_jd(dt)
    jd_tt = jd_ut + julian.delta_t(dt.year + (dt.month - 0.5) / 12.0) / 86400.0
    return jd_ut, jd_tt, dt.isoformat()


def daily_rashifal(
    rashi: int | str,
    when: Optional[date | datetime] = None,
    ayanamsa: str = "lahiri",
    *,
    period: str = "daily",
) -> Rashifal:
    """Build the transit-based rashifal for one rashi.

    ``rashi`` is a 0-based index (0 = Aries) or a name (``"Mesha"``/``"Aries"``).
    ``when`` defaults to now; a plain :class:`datetime.date` is read at 06:00 UTC.
    ``period`` is a label only (``"daily"``, ``"monthly"``, ``"yearly"``) and is
    echoed back in the result.
    """
    idx = _resolve_rashi(rashi)
    _jd_ut, jd_tt, iso = _jd_for(when)
    longitudes = graha_longitudes(jd_tt, ayanamsa)

    transits: List[GrahaTransit] = []
    score = 0.0
    favourable: List[str] = []
    challenging: List[str] = []
    for graha, lon in longitudes.items():
        house = _house_from(lon, idx)
        verdict = _classify(graha, house)
        weight = 1.5 if graha in _HEAVY else 1.0
        score += _SCORE[verdict] * weight
        if verdict == "favourable":
            favourable.append(graha)
        elif verdict == "challenging":
            challenging.append(score_label(graha, house))
        transits.append(
            GrahaTransit(
                graha=graha,
                longitude=lon,
                rashi=moon_sign(lon),
                rashi_name=RASHIS[moon_sign(lon)],
                house=house,
                house_theme=_HOUSE_THEMES[house],
                verdict=verdict,
            )
        )

    band = _band(score)
    return Rashifal(
        rashi=idx,
        rashi_name=RASHIS[idx],
        rashi_name_en=RASHIS_EN[idx],
        rashi_lord=RASHI_LORDS[idx],
        period=period,
        when=iso,
        score=score,
        band=band,
        headline=_headline(band, favourable, challenging),
        summary=_summary(band, favourable, challenging),
        favourable=favourable,
        challenging=challenging,
        transits=transits,
    )


def score_label(graha: str, house: int) -> str:
    """Human-readable label for a challenging transit, e.g. ``"Saturn (8th)"``."""
    return f"{graha} ({_ordinal(house)})"


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _resolve_rashi(rashi: int | str) -> int:
    if isinstance(rashi, int):
        if not 0 <= rashi <= 11:
            raise ValueError("rashi index must be 0-11")
        return rashi
    key = rashi.strip().lower()
    for i, (a, b) in enumerate(zip(RASHIS, RASHIS_EN)):
        if key in (a.lower(), b.lower()):
            return i
    raise ValueError(f"Unknown rashi {rashi!r}; expected a name or index 0-11")


def rashifal_for_all(
    when: Optional[date | datetime] = None,
    ayanamsa: str = "lahiri",
    period: str = "daily",
) -> List[Rashifal]:
    """Build the rashifal for all twelve rashis for the same instant."""
    return [
        daily_rashifal(i, when, ayanamsa, period=period)
        for i in range(12)
    ]