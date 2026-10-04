"""Kalagana jyotish: kundali, divisional charts, dasha and marriage matching.

This subpackage adds Vedic astrology to the panchang engine.  It is pure
standard library and fully offline, like the rest of Kalagana.

Quick start
-----------
>>> from datetime import datetime
>>> from kalagana import Location
>>> from kalagana.jyotish import kundali
>>> loc = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")
>>> k = kundali(datetime(1990, 5, 15, 10, 30), loc)
>>> k.ascendant.rashi_name
>>> k.grahas["Moon"].rashi_name, k.grahas["Moon"].nakshatra_name
"""

from __future__ import annotations

from .angles import (
    RASHIS,
    RASHIS_EN,
    Ascendant,
    ascendant,
    house_cusps_equal,
    house_of_longitude,
    local_apparent_sidereal_time,
    midheaven,
    rashi_of,
    whole_sign_of,
)
from .chart import (
    CHART_FORMATS,
    EAST_CELLS,
    EAST_SIGN_ORDER,
    NORTH_ORDER,
    SOUTH_CELLS,
    SOUTH_SIGN_ORDER,
    charts,
    east_chart,
    north_chart,
    south_chart,
)
from .dasha import (
    DASHA_ORDER,
    DASHA_YEARS,
    DashaPeriod,
    current_period,
    nakshatra_lord,
    vimshottari,
)
from .dignity import (
    COMBUSTION_LIMIT,
    EXALTATION,
    NATURAL_ENEMIES,
    NATURAL_FRIENDS,
    OWN_SIGNS,
    dignity as graha_dignity,
    is_combust,
    rashi_lord,
)
from .kundali import GrahaPosition, Kundali, graha_longitudes, kundali, kundali_match
from .match import Koota, MatchResult, ashtakoota, mangal_dosha
from .rashifal import (
    GrahaTransit,
    Rashifal,
    daily_rashifal,
    moon_sign,
    rashifal_for_all,
)
from .planets import (
    GRAHAS,
    PLANETS,
    geocentric_j2000,
    mean_node_longitude,
    rahu_ketu,
    sidereal_longitude,
    sidereal_node_longitude,
    sun_sidereal_longitude,
)
from .varga import SHODASAVARGA, VARGA_NAMES, varga_positions, varga_sign

__all__ = [
    # angles
    "RASHIS", "RASHIS_EN", "Ascendant", "ascendant", "midheaven",
    "local_apparent_sidereal_time", "house_of_longitude", "house_cusps_equal",
    "rashi_of", "whole_sign_of",
    # planets
    "GRAHAS", "PLANETS", "geocentric_j2000", "sidereal_longitude",
    "sidereal_node_longitude", "mean_node_longitude", "rahu_ketu",
    "sun_sidereal_longitude",
    # charts / vargas
    "SHODASAVARGA", "VARGA_NAMES", "varga_sign", "varga_positions",
    "north_chart", "south_chart", "east_chart", "charts", "CHART_FORMATS",
    "NORTH_ORDER", "SOUTH_SIGN_ORDER", "SOUTH_CELLS", "EAST_SIGN_ORDER", "EAST_CELLS",
    # dignity
    "graha_dignity", "is_combust", "rashi_lord", "EXALTATION", "OWN_SIGNS",
    "NATURAL_FRIENDS", "NATURAL_ENEMIES", "COMBUSTION_LIMIT",
    # dasha
    "vimshottari", "current_period", "nakshatra_lord", "DashaPeriod",
    "DASHA_ORDER", "DASHA_YEARS",
    # kundali
    "Kundali", "GrahaPosition", "kundali", "kundali_match",
    # match
    "ashtakoota", "mangal_dosha", "MatchResult", "Koota",
    # rashifal
    "daily_rashifal", "rashifal_for_all", "Rashifal", "GrahaTransit", "moon_sign",
]
