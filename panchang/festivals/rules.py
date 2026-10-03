"""Festival rules as data.

A festival is never a hardcoded date.  Each entry is a :class:`FestivalRule`
describing *which* lunar month, paksha, tithi (or solar sankranti) defines it,
*when* during the day the tithi must be present (the ``window``), and any extra
conditions (nakshatra, weekday, region).  The engine in ``engine.py`` turns
these into dates for a given year and place.

Masa is given in the **purnimanta** (North Indian) convention, because that is
how most festivals are named; the engine labels months the same way.  The civil
date of a festival does not depend on the amanta/purnimanta choice -- only the
month *name* does.

``window`` values
-----------------
``sunrise``, ``arunodaya`` (96 min before sunrise), ``madhyahna`` (midday),
``aparahna`` (3/5 of the day), ``pradosh`` (just after sunset), ``nishita``
(midnight), ``moonrise``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

__all__ = ["FestivalRule", "FESTIVAL_RULES", "rules_by_name", "WINDOWS"]

WINDOWS = (
    "sunrise",
    "arunodaya",
    "madhyahna",
    "aparahna",
    "pradosh",
    "nishita",
    "moonrise",
)

NORTH = ("North",)
SOUTH = ("South",)
EAST = ("East",)
WEST = ("West",)
ALL_IN = ("North", "South", "East", "West")


@dataclass(frozen=True)
class FestivalRule:
    """A single festival definition (all fields documented in the module docstring)."""

    name: str
    masa: Optional[str] = None
    paksha: Optional[str] = None
    tithi: Optional[int] = None          # within-paksha number 1..15
    window: str = "sunrise"
    system: str = "lunar"                # "lunar" or "solar"
    sankranti_rashi: Optional[int] = None  # 0=Mesha .. 11=Meena
    sun_in_rashi: Optional[int] = None   # Sun's sidereal sign 0=Mesha .. 11=Meena
    nakshatra: Optional[str] = None
    weekday: Optional[int] = None        # 0=Sunday .. 6=Saturday
    regions: Tuple[str, ...] = NORTH
    adhika_policy: str = "nija"          # "nija", "adhika", "both"
    monthly: bool = False
    tie_break: str = "first"             # "first" or "last" matching day
    names_regional: Dict[str, str] = field(default_factory=dict)
    note: str = ""


def _r(
    name: str,
    masa: Optional[str],
    paksha: Optional[str],
    tithi: Optional[int],
    window: str = "sunrise",
    *,
    system: str = "lunar",
    sankranti_rashi: Optional[int] = None,
    sun_in_rashi: Optional[int] = None,
    nakshatra: Optional[str] = None,
    weekday: Optional[int] = None,
    regions: Tuple[str, ...] = NORTH,
    adhika_policy: str = "nija",
    monthly: bool = False,
    tie_break: str = "first",
    note: str = "",
) -> FestivalRule:
    return FestivalRule(
        name=name,
        masa=masa,
        paksha=paksha,
        tithi=tithi,
        window=window,
        system=system,
        sankranti_rashi=sankranti_rashi,
        sun_in_rashi=sun_in_rashi,
        nakshatra=nakshatra,
        weekday=weekday,
        regions=regions,
        adhika_policy=adhika_policy,
        monthly=monthly,
        tie_break=tie_break,
        note=note,
    )


# ---------------------------------------------------------------------------
# Major pan-Indian festivals, in calendar order.
# ---------------------------------------------------------------------------
FESTIVAL_RULES: Tuple[FestivalRule, ...] = (
    # --- Solar new year / harvest ---
    _r("Makar Sankranti", None, None, None, system="solar", sankranti_rashi=9,
       regions=ALL_IN, note="Sun enters Makara (sidereal)."),
    _r("Pongal", None, None, None, system="solar", sankranti_rashi=9,
       regions=SOUTH, note="Tamil Thai 1, the day of Makara Sankranti."),
    _r("Lohri", None, None, None, system="solar", sankranti_rashi=9,
       regions=("North", "West"), note="Observed the day before Makar Sankranti."),
    _r("Vishu", None, None, None, system="solar", sankranti_rashi=0,
       regions=SOUTH, note="Malayalam new year, Mesha 1."),
    _r("Puthandu", None, None, None, system="solar", sankranti_rashi=0,
       regions=SOUTH, note="Tamil new year, Mesha 1."),
    _r("Baisakhi", None, None, None, system="solar", sankranti_rashi=0,
       regions=NORTH, note="Punjabi new year / harvest."),
    _r("Pohela Boishakh", None, None, None, system="solar", sankranti_rashi=0,
       regions=EAST, note="Bengali new year, Boishakh 1."),

    # --- Magha ---
    _r("Vasant Panchami", "Magha", "Shukla", 5),
    _r("Ratha Saptami", "Magha", "Shukla", 7, regions=SOUTH),
    _r("Basant Panchami (Saraswati Puja)", "Magha", "Shukla", 5, regions=EAST),
    _r("Maha Shivaratri", "Phalguna", "Krishna", 14, "nishita",
       note="Nishita kaal (midnight) observance."),

    # --- Phalguna / Holi ---
    _r("Holika Dahan", "Phalguna", "Shukla", 15, "pradosh",
       note="Purnima at pradosh, avoiding Bhadra."),
    _r("Holi", "Phalguna", "Krishna", 1),

    # --- Chaitra ---
    _r("Chaitra Navratri", "Chaitra", "Shukla", 1),
    _r("Gudi Padwa", "Chaitra", "Shukla", 1, regions=("West", "North")),
    _r("Ugadi", "Chaitra", "Shukla", 1, regions=SOUTH),
    _r("Chaitra Navratri Begins", "Chaitra", "Shukla", 1, regions=SOUTH),
    _r("Gangaur", "Chaitra", "Shukla", 3, regions=WEST),
    _r("Rama Navami", "Chaitra", "Shukla", 9, "madhyahna",
       note="Madhyahna (midday) observance."),
    _r("Hanuman Jayanti", "Chaitra", "Shukla", 15),

    # --- Vaishakha ---
    _r("Akshaya Tritiya", "Vaishakha", "Shukla", 3),
    _r("Buddha Purnima", "Vaishakha", "Shukla", 15),

    # --- Ashadha ---
    _r("Rath Yatra", "Ashadha", "Shukla", 2),
    _r("Guru Purnima", "Ashadha", "Shukla", 15, adhika_policy="both"),

    # --- Shravana ---
    _r("Nag Panchami", "Shravana", "Shukla", 5),
    _r("Raksha Bandhan", "Shravana", "Shukla", 15),
    _r("Varalakshmi Vratam", "Shravana", "Shukla", 2, "sunrise", weekday=5,
       regions=SOUTH, note="Friday before Shravana Purnima."),

    # --- Bhadrapada ---
    _r("Krishna Janmashtami", "Bhadrapada", "Krishna", 8, "nishita",
       note="Ashtami at nishita kaal."),
    _r("Ganesh Chaturthi", "Bhadrapada", "Shukla", 4, "madhyahna"),
    _r("Hartalika Teej", "Bhadrapada", "Shukla", 3),
    _r("Anant Chaturdashi", "Bhadrapada", "Shukla", 14),
    _r("Pitru Paksha Begins", "Bhadrapada", "Shukla", 15),
    _r("Mahalaya Amavasya", "Bhadrapada", "Krishna", 15),

    # --- Ashwin ---
    _r("Sharad Navratri", "Ashwin", "Shukla", 1),
    _r("Durga Ashtami", "Ashwin", "Shukla", 8),
    _r("Maha Navami", "Ashwin", "Shukla", 9),
    _r("Ayudha Puja", "Ashwin", "Shukla", 9, regions=SOUTH),
    _r("Dussehra", "Ashwin", "Shukla", 10),
    _r("Durga Puja (Shashthi)", "Ashwin", "Shukla", 6, regions=EAST),
    _r("Kali Puja", "Kartika", "Krishna", 15, "nishita",
       regions=EAST, note="New-moon night, Diwali night in Bengal."),

    # --- Kartika ---
    _r("Karwa Chauth", "Kartika", "Krishna", 4, "moonrise",
       note="Moonrise during Chaturthi."),
    _r("Dhanteras", "Kartika", "Krishna", 13, "pradosh"),
    _r("Naraka Chaturdashi", "Kartika", "Krishna", 14),
    _r("Diwali", "Kartika", "Krishna", 15, "pradosh",
       note="Amavasya at pradosh (Lakshmi Puja)."),
    _r("Govardhan Puja", "Kartika", "Shukla", 1),
    _r("Bhai Dooj", "Kartika", "Shukla", 2),
    _r("Chhath Puja", "Kartika", "Shukla", 6, regions=("North", "East")),
    _r("Kartik Purnima", "Kartika", "Shukla", 15),
    _r("Dev Deepawali", "Kartika", "Shukla", 15),

    # --- Margashirsha ---
    _r("Vaikuntha Ekadashi", "Margashirsha", "Shukla", 11, regions=SOUTH),
    _r("Gita Jayanti", "Margashirsha", "Shukla", 11),

    # --- Pausha ---
    _r("Ratha Saptami (Pausha)", "Pausha", "Shukla", 7, regions=SOUTH),
    _r("Thaipusam", "Magha", "Shukla", 15, nakshatra="Pushya", regions=SOUTH,
       note="Purnima with Pushya nakshatra."),
    _r("Karthigai Deepam", "Kartika", "Shukla", 15, regions=SOUTH),

    # --- Onam (Thiruvonam = Shravana nakshatra in the solar month Chingam) ---
    _r("Onam", None, None, None, "sunrise", nakshatra="Shravana", sun_in_rashi=4,
       regions=SOUTH,
       note="Thiruvonam (Shravana) nakshatra, solar month Chingam (Sun in Simha)."),
)

# Monthly observances, generated for every lunar month.
_MONTHLY = (
    _r("Ekadashi", None, "Shukla", 11, "arunodaya", monthly=True,
       note="Sunrise-based (Smartha); Vaishnava uses arunodaya."),
    _r("Ekadashi", None, "Krishna", 11, "arunodaya", monthly=True,
       note="Sunrise-based (Smartha); Vaishnava uses arunodaya."),
    _r("Pradosh Vrat", None, "Shukla", 13, "pradosh", monthly=True),
    _r("Pradosh Vrat", None, "Krishna", 13, "pradosh", monthly=True),
    _r("Vinayaka Chaturthi", None, "Shukla", 4, monthly=True),
    _r("Sankashti Chaturthi", None, "Krishna", 4, "moonrise", monthly=True),
    _r("Masik Shivaratri", None, "Krishna", 14, "nishita", monthly=True),
    _r("Purnima", None, "Shukla", 15, monthly=True),
    _r("Amavasya", None, "Krishna", 15, monthly=True),
    _r("Sankranti", None, None, None, system="solar", monthly=True),
)

FESTIVAL_RULES = FESTIVAL_RULES + _MONTHLY


def rules_by_name(name: str) -> Tuple[FestivalRule, ...]:
    """Return all rules whose name matches (case-insensitive)."""
    key = name.strip().lower()
    return tuple(r for r in FESTIVAL_RULES if r.name.lower() == key)
