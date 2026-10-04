"""The Kundali (birth chart): graha placements, houses, vargas and dasha.

A :class:`Kundali` is built from a birth instant and place.  Everything is
derived -- nothing is stored.  The chart contains:

* the nine grahas with their nirayana longitude, rashi, nakshatra, pada,
  retrograde/combust flags, dignity and house;
* the Lagna (ascendant) and the Midheaven;
* whole-sign houses and Rashi (D1) placements;
* the sixteen divisional charts (Shodasavarga) as rashi indices;
* the Vimshottari dasha (optional depth);
* the birth panchang (tithi, vara, nakshatra, yoga, karana);
* the Avakhada Chakra (rashi/nakshatra/gana/yoni/nadi/varna/vashya).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .. import julian, limbs
from ..ayanamsa import ayanamsa_degrees
from ..limbs import NAKSHATRAS, NAKSHATRA_SIZE, PADA_SIZE, VARA_NAMES, VARA_NAMES_EN
from ..location import Location
from . import angles, chart as _chart, planets, varga
from .dasha import DashaPeriod, vimshottari
from .dignity import dignity as _dignity, is_combust as _is_combust
from .match import MatchResult, ashtakoota, mangal_dosha
from .varga import SHODASAVARGA

__all__ = [
    "GrahaPosition",
    "Kundali",
    "kundali",
    "kundali_match",
    "graha_longitudes",
    "NINE_GRAHAS",
]

NINE_GRAHAS = planets.GRAHAS


def _nak_name(number: int) -> str:
    return NAKSHATRAS[(number - 1) % 27]


@dataclass(frozen=True)
class GrahaPosition:
    """One graha's placement at birth."""

    name: str
    longitude: float
    rashi: int
    rashi_name: str
    rashi_name_en: str
    degree_in_rashi: float
    nakshatra: int
    nakshatra_name: str
    pada: int
    house: int
    retrograde: bool
    combust: bool
    dignity: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "longitude": round(self.longitude, 5),
            "rashi": self.rashi,
            "rashi_name": self.rashi_name,
            "rashi_en": self.rashi_name_en,
            "degree_in_rashi": round(self.degree_in_rashi, 4),
            "nakshatra": self.nakshatra,
            "nakshatra_name": self.nakshatra_name,
            "pada": self.pada,
            "house": self.house,
            "retrograde": self.retrograde,
            "combust": self.combust,
            "dignity": self.dignity,
        }


@dataclass
class Kundali:
    """A complete birth chart."""

    when: datetime
    location: Location
    ayanamsa: str
    jd_ut: float
    jd_tt: float
    ascendant: angles.Ascendant
    grahas: Dict[str, GrahaPosition]
    houses: List[int]              # house 1..12 -> rashi index (whole sign)
    vargas: Dict[int, Dict[str, int]]  # divisions -> {graha: rashi index}
    dasha: List[DashaPeriod]
    panchang: Dict[str, object]
    avakhada: Dict[str, object]

    # --- convenience -----------------------------------------------------
    @property
    def lagna(self) -> str:
        return self.ascendant.rashi_name

    @property
    def moon(self) -> GrahaPosition:
        return self.grahas["Moon"]

    def chart(self, fmt: str = "north") -> List[Dict[str, object]]:
        """Chart layout data in one Indian format (``north``/``south``/``east``)."""
        return _chart.charts(
            self.ascendant.rashi,
            {g: p.rashi for g, p in self.grahas.items()},
        )[fmt.strip().lower()]

    def charts(self) -> Dict[str, List[Dict[str, object]]]:
        """Chart layout data in all three Indian formats at once."""
        return _chart.charts(
            self.ascendant.rashi,
            {g: p.rashi for g, p in self.grahas.items()},
        )

    def to_dict(self, with_dasha: bool = True) -> Dict[str, object]:
        return {
            "when": self.when.isoformat(),
            "location": {
                "name": self.location.name,
                "lat": self.location.lat,
                "lon": self.location.lon,
                "tz": self.location.tz,
            },
            "ayanamsa": self.ayanamsa,
            "julian_day_ut": round(self.jd_ut, 6),
            "julian_day_tt": round(self.jd_tt, 6),
            "ascendant": {
                "longitude": round(self.ascendant.sidereal, 5),
                "rashi": self.ascendant.rashi,
                "rashi_name": self.ascendant.rashi_name,
                "degree_in_rashi": round(self.ascendant.degree_in_rashi, 4),
                "midheaven": round(self.ascendant.midheaven, 5),
                "sidereal_time": round(self.ascendant.sidereal_time, 5),
            },
            "houses": [
                {"house": i + 1, "rashi": r, "rashi_name": angles.RASHIS[r]}
                for i, r in enumerate(self.houses)
            ],
            "grahas": {name: p.to_dict() for name, p in self.grahas.items()},
            "vargas": {
                str(div): {
                    "name": varga.VARGA_NAMES[div],
                    "placements": {
                        g: {"rashi": r, "rashi_name": angles.RASHIS[r]}
                        for g, r in placements.items()
                    },
                }
                for div, placements in self.vargas.items()
            },
            "panchang": self.panchang,
            "avakhada": self.avakhada,
            "charts": self.charts(),
            "dasha": [p.to_dict() for p in self.dasha] if with_dasha else [],
        }


def graha_longitudes(jd_tt: float, ayanamsa: str = "lahiri") -> Dict[str, float]:
    """Sidereal longitudes of the nine grahas at ``jd_tt`` (degrees).

    Shared by the kundali builder and the transit-based rashifal generator.
    """
    rahu, ketu = planets.rahu_ketu(jd_tt, ayanamsa)
    return {
        "Sun": limbs.sidereal_sun_longitude(jd_tt, ayanamsa),
        "Moon": limbs.sidereal_moon_longitude(jd_tt, ayanamsa),
        "Mars": planets.sidereal_longitude("Mars", jd_tt, ayanamsa),
        "Mercury": planets.sidereal_longitude("Mercury", jd_tt, ayanamsa),
        "Jupiter": planets.sidereal_longitude("Jupiter", jd_tt, ayanamsa),
        "Venus": planets.sidereal_longitude("Venus", jd_tt, ayanamsa),
        "Saturn": planets.sidereal_longitude("Saturn", jd_tt, ayanamsa),
        "Rahu": rahu,
        "Ketu": ketu,
    }


def _local(dt: datetime, loc: Location) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=loc.zoneinfo)
    return dt


def kundali(
    when: datetime,
    loc: Location,
    ayanamsa: str = "lahiri",
    *,
    dasha_depth: int = 2,
    with_dasha: bool = True,
) -> Kundali:
    """Build the :class:`Kundali` for a birth instant and place.

    ``when`` should be timezone-aware; a naive datetime is interpreted as local
    wall-clock time at ``loc``.  ``dasha_depth`` controls the Vimshottari tree
    (1 = mahadasha, 2 = + antardasha, 3 = + pratyantardasha).
    """
    when = _local(when, loc)
    jd_ut = julian.datetime_to_jd(when)
    jd_tt = jd_ut + julian.delta_t(when.year + (when.month - 0.5) / 12.0) / 86400.0

    asc = angles.ascendant(jd_ut, jd_tt, loc.lat, loc.lon, ayanamsa)
    longitudes = graha_longitudes(jd_tt, ayanamsa)

    houses = [(asc.rashi + i) % 12 for i in range(12)]

    positions: Dict[str, GrahaPosition] = {}
    for name, lon in longitudes.items():
        rashi = int(lon // 30.0)
        within = lon % 30.0
        nak = int(lon // NAKSHATRA_SIZE) + 1
        pada = int((lon % NAKSHATRA_SIZE) // PADA_SIZE) + 1
        retro = planets.is_retrograde(name.lower(), jd_tt, ayanamsa)
        combust = _is_combust(name, lon, longitudes["Sun"], retro)
        positions[name] = GrahaPosition(
            name=name,
            longitude=lon,
            rashi=rashi,
            rashi_name=angles.RASHIS[rashi],
            rashi_name_en=angles.RASHIS_EN[rashi],
            degree_in_rashi=within,
            nakshatra=nak,
            nakshatra_name=_nak_name(nak),
            pada=pada,
            house=angles.house_of_longitude(lon, asc.sidereal, "whole_sign"),
            retrograde=retro,
            combust=combust,
            dignity=_dignity(name, lon),
        )

    # Divisional charts.
    vargas: Dict[int, Dict[str, int]] = {}
    for div in SHODASAVARGA:
        vargas[div] = {g: varga.varga_sign(lon, div) for g, lon in longitudes.items()}

    # Birth panchang.
    tithi_no = limbs.tithi_number(jd_tt)
    nak_no = limbs.nakshatra_number(jd_tt, ayanamsa)
    yoga_no = limbs.yoga_number(jd_tt, ayanamsa)
    karana_no = limbs.karana_number(jd_tt)
    panchang = {
        "tithi": limbs.tithi_name(tithi_no),
        "tithi_number": tithi_no,
        "nakshatra": _nak_name(nak_no),
        "nakshatra_number": nak_no,
        "yoga": limbs.YOGAS[yoga_no - 1],
        "karana": limbs.karana_name(karana_no),
        "paksha": "Shukla" if tithi_no <= 15 else "Krishna",
        "vara": VARA_NAMES[(when.weekday() + 1) % 7],
        "vara_en": VARA_NAMES_EN[(when.weekday() + 1) % 7],
    }

    avakhada = _avakhada(positions["Moon"], asc.rashi)

    review: List[DashaPeriod] = []
    if with_dasha:
        review = vimshottari(positions["Moon"].longitude, jd_tt, depth=dasha_depth)

    return Kundali(
        when=when,
        location=loc,
        ayanamsa=ayanamsa,
        jd_ut=jd_ut,
        jd_tt=jd_tt,
        ascendant=asc,
        grahas=positions,
        houses=houses,
        vargas=vargas,
        dasha=review,
        panchang=panchang,
        avakhada=avakhada,
    )


def _avakhada(moon: GrahaPosition, lagna_rashi: int) -> Dict[str, object]:
    from .dasha import nakshatra_lord
    from .dignity import rashi_lord
    from .match import GANA_BY_NAKSHATRA, NADI_BY_NAKSHATRA, VASHYA_BY_RASHI, VARNA_BY_RASHI
    from .match import YONI_BY_NAKSHATRA

    gana_names = ("Deva", "Manushya", "Rakshasa")
    vashya_names = ("Chatushpada", "Manava", "Jalachara", "Keeta")
    nadi_names = ("Adi", "Madhya", "Antya")
    varna_names = ("Shudra", "Vaishya", "Kshatriya", "Brahmin")
    animal, gender = YONI_BY_NAKSHATRA[moon.nakshatra - 1]
    return {
        "rashi": moon.rashi_name,
        "rashi_lord": rashi_lord(moon.rashi),
        "nakshatra": moon.nakshatra_name,
        "nakshatra_lord": nakshatra_lord(moon.nakshatra),
        "pada": moon.pada,
        "gana": gana_names[GANA_BY_NAKSHATRA[moon.nakshatra - 1]],
        "yoni": f"{animal} ({gender})",
        "nadi": nadi_names[NADI_BY_NAKSHATRA[moon.nakshatra - 1]],
        "varna": varna_names[VARNA_BY_RASHI[moon.rashi] - 1],
        "vashya": vashya_names[VASHYA_BY_RASHI[moon.rashi]],
        "lagna": angles.RASHIS[lagna_rashi],
        "lagna_lord": rashi_lord(lagna_rashi),
    }


def _mars_house_from(k: Kundali, ref_rashi: int) -> int:
    return angles.house_of_longitude(k.grahas["Mars"].longitude, ref_rashi * 30.0, "whole_sign")


def kundali_match(boy: Kundali, girl: Kundali) -> Dict[str, object]:
    """Compare two kundalis for marriage (Ashtakoota + Mangal dosha)."""
    result: MatchResult = ashtakoota(
        boy.moon.rashi, boy.moon.nakshatra,
        girl.moon.rashi, girl.moon.nakshatra,
    )
    def _dosha(k: Kundali) -> Dict[str, object]:
        mars = k.grahas["Mars"].longitude
        return mangal_dosha({
            "lagna": _mars_house_from(k, k.ascendant.rashi),
            "moon": angles.house_of_longitude(mars, k.moon.longitude, "whole_sign"),
            "venus": angles.house_of_longitude(mars, k.grahas["Venus"].longitude, "whole_sign"),
        })

    boy_dosha = _dosha(boy)
    girl_dosha = _dosha(girl)
    return {
        "boy": {
            "moon_rashi": boy.moon.rashi_name,
            "moon_nakshatra": boy.moon.nakshatra_name,
            "lagna": boy.ascendant.rashi_name,
            "mangal_dosha": boy_dosha,
        },
        "girl": {
            "moon_rashi": girl.moon.rashi_name,
            "moon_nakshatra": girl.moon.nakshatra_name,
            "lagna": girl.ascendant.rashi_name,
            "mangal_dosha": girl_dosha,
        },
        "ashtakoota": result.to_dict(),
    }
