"""kalagana -- an offline Hindu (Drik) panchang and festival calculator.

Pure standard library, no network, no external data files.  Astronomy is
computed from the Meeus algorithms; calendar and festival rules are Python
data structures evaluated at runtime, so every date is derived, never stored.

Quick start
-----------
>>> from datetime import date
>>> from kalagana import Location, daily_panchang, festivals_for_year
>>> loc = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")
>>> day = daily_panchang(date(2024, 8, 26), loc)
>>> day.tithi[0].name
'Krishna Ashtami'
>>> day.masa_purnimanta
'Bhadrapada'
>>> [f.name for f in festivals_for_year(2024, loc, tradition="north")][:2]
['Masik Shivaratri', 'Pradosh Vrat']
"""

from __future__ import annotations

__version__ = "0.1.1"

from .api import (
    Eclipse,
    Panchang,
    daily_panchang,
    eclipses_for_year,
)
from .ayanamsa import SUPPORTED as AYANAMSAS
from .festivals import FestivalOccurrence, FestivalRule, festival_dates, find_next
from .festivals import festivals_for_year as festivals_for_year
from .festivals import national_holidays
from .limbs import tithi_name
from .location import CITIES, Location, city_lookup

__all__ = [
    "Location",
    "CITIES",
    "city_lookup",
    "daily_panchang",
    "festivals_for_year",
    "festival_dates",
    "national_holidays",
    "find_next",
    "eclipses_for_year",
    "Panchang",
    "Eclipse",
    "FestivalOccurrence",
    "FestivalRule",
    "AYANAMSAS",
    "tithi_name",
    "__version__",
]
