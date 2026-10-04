"""Festival rules as data.

A festival is never a hardcoded date.  Each entry is a :class:`FestivalRule`
describing *which* lunar month, paksha, tithi (or solar sankranti, or fixed
Gregorian date) defines it, *when* during the day the tithi must be present
(the ``window``), and any extra conditions (nakshatra, weekday, region).  The
engine in ``engine.py`` turns these into dates for a given year and place.

Masa is given in the **purnimanta** (North Indian) convention, because that is
how most festivals are named; the engine labels months the same way.  The civil
date of a festival does not depend on the amanta/purnimanta choice -- only the
month *name* does.

``window`` values
-----------------
``sunrise``, ``arunodaya`` (96 min before sunrise), ``madhyahna`` (midday),
``aparahna`` (3/5 of the day), ``pradosh`` (just after sunset), ``nishita``
(midnight), ``moonrise``.

``system`` values
-----------------
``lunar``  defined by masa/paksha/tithi (the default)
``solar``  defined by a solar sankranti (Sun's entry into a rashi)
``fixed``  a fixed Gregorian calendar date (``fixed_month``/``fixed_day``),
           used for national holidays and commemorative observance days
``hijri``  a tabular Islamic calendar date (``hijri_month``/``hijri_day``),
           used for the Islamic festivals

``kind`` values
---------------
``festival``    a religious/seasonal festival (default)
``national``    a gazetted national holiday
``observance``  a commemorative or awareness day observed on a fixed date
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

__all__ = [
    "FestivalRule",
    "FESTIVAL_RULES",
    "SECONDARY_RULES",
    "FIXED_RULES",
    "ISLAMIC_RULES",
    "rules_by_name",
    "WINDOWS",
    "KINDS",
]

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

# ``kind`` categories (see module docstring).
KINDS = ("festival", "national", "observance")


@dataclass(frozen=True)
class FestivalRule:
    """A single festival definition (all fields documented in the module docstring)."""

    name: str
    masa: Optional[str] = None
    paksha: Optional[str] = None
    tithi: Optional[int] = None          # within-paksha number 1..15
    window: str = "sunrise"
    system: str = "lunar"                # "lunar", "solar" or "fixed"
    sankranti_rashi: Optional[int] = None  # 0=Mesha .. 11=Meena
    sun_in_rashi: Optional[int] = None   # Sun's sidereal sign 0=Mesha .. 11=Meena
    fixed_month: Optional[int] = None    # 1..12 (system="fixed")
    fixed_day: Optional[int] = None      # 1..31 (system="fixed")
    hijri_month: Optional[int] = None    # 1..12 (system="hijri")
    hijri_day: Optional[int] = None      # 1..30 (system="hijri")
    kind: str = "festival"               # "festival", "national", "observance"
    nakshatra: Optional[str] = None
    weekday: Optional[int] = None        # 0=Sunday .. 6=Saturday
    regions: Tuple[str, ...] = NORTH
    adhika_policy: str = "nija"          # "nija", "adhika", "both"
    month_system: str = "purnimanta"     # "purnimanta" (default) or "amanta"
    monthly: bool = False
    offset_days: int = 0                 # shift the matched day (e.g. Holi = Purnima+1)
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
    fixed_month: Optional[int] = None,
    fixed_day: Optional[int] = None,
    hijri_month: Optional[int] = None,
    hijri_day: Optional[int] = None,
    kind: str = "festival",
    nakshatra: Optional[str] = None,
    weekday: Optional[int] = None,
    regions: Tuple[str, ...] = NORTH,
    adhika_policy: str = "nija",
    month_system: str = "purnimanta",
    monthly: bool = False,
    offset_days: int = 0,
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
        fixed_month=fixed_month,
        fixed_day=fixed_day,
        hijri_month=hijri_month,
        hijri_day=hijri_day,
        kind=kind,
        nakshatra=nakshatra,
        weekday=weekday,
        regions=regions,
        adhika_policy=adhika_policy,
        month_system=month_system,
        monthly=monthly,
        offset_days=offset_days,
        tie_break=tie_break,
        note=note,
    )


def _f(
    name: str,
    month: int,
    day: int,
    *,
    kind: str = "observance",
    regions: Tuple[str, ...] = ALL_IN,
    note: str = "",
) -> FestivalRule:
    """A fixed Gregorian-calendar-date rule (``system="fixed"``).

    The date is the same everywhere and every year, so no astronomy is needed;
    ``month`` is 1..12 and ``day`` is 1..31.  Used for national holidays and
    commemorative observance days, most of which are pan-Indian.
    """
    return _r(
        name,
        None,
        None,
        None,
        system="fixed",
        fixed_month=month,
        fixed_day=day,
        kind=kind,
        regions=regions,
        note=note,
    )


def _h(
    name: str,
    hijri_month: int,
    hijri_day: int,
    *,
    regions: Tuple[str, ...] = ALL_IN,
    note: str = "",
) -> FestivalRule:
    """A Hijri-calendar rule (``system="hijri"``).

    ``hijri_month`` is 1..12 and ``hijri_day`` is 1..30.  The engine maps it
    through the tabular (arithmetic) Islamic calendar in ``kalagana.hijri``;
    actual crescent sighting can shift the observed date by 1-2 days.
    """
    return _r(
        name,
        None,
        None,
        None,
        system="hijri",
        hijri_month=hijri_month,
        hijri_day=hijri_day,
        regions=regions,
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
    _r("Holi", "Phalguna", "Shukla", 15, "pradosh", offset_days=1,
       note="Day after Holika Dahan (Dhulandi)."),

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
    _r("Pitru Paksha Begins", "Bhadrapada", "Krishna", 1, "madhyahna",
       month_system="amanta",
       note="Amanta Bhadrapada Krishna Pratipada (day Bhadrapada Purnima ends)."),
    _r("Mahalaya Amavasya", "Bhadrapada", "Krishna", 15, month_system="amanta",
       note="Amanta Bhadrapada Amavasya (Sarva Pitru Amavasya)."),

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

# ---------------------------------------------------------------------------
# Second-tier / regional festivals and named vrats, in calendar order.
# These fill the gaps against the published Drik Panchang Hindu calendar:
# named Ekadashis, the month-specific vrats (Sakat Chauth, Hariyali Teej, ...),
# jayantis, and the common aliases (Rakhi, Chhoti Holi, Lakshmi Puja, ...).
# ---------------------------------------------------------------------------
SECONDARY_RULES: Tuple[FestivalRule, ...] = (
    # --- Magha ---
    _r("Sakat Chauth", "Magha", "Krishna", 4, "moonrise"),
    _r("Mauni Amavas", "Magha", "Krishna", 15),
    _r("Bhishma Ashtami", "Magha", "Shukla", 8),
    _r("Shattila Ekadashi", "Magha", "Krishna", 11, "arunodaya"),
    _r("Jaya Ekadashi", "Magha", "Shukla", 11, "arunodaya"),

    # --- Phalguna ---
    _r("Chhoti Holi", "Phalguna", "Shukla", 15, note="Purnima eve of Holi."),
    _r("Vijaya Ekadashi", "Phalguna", "Krishna", 11, "arunodaya"),
    _r("Amalaki Ekadashi", "Phalguna", "Shukla", 11, "arunodaya"),

    # --- Chaitra ---
    _r("Sheetala Ashtami", "Chaitra", "Krishna", 8),
    _r("Basoda", "Chaitra", "Krishna", 8, note="Same day as Sheetala Ashtami."),
    _r("Gauri Puja", "Chaitra", "Shukla", 3),
    _r("Yamuna Chhath", "Chaitra", "Shukla", 6),
    _r("Swaminarayan Jayanti", "Chaitra", "Shukla", 9),
    _r("Kamada Ekadashi", "Chaitra", "Shukla", 11, "arunodaya"),

    # --- Vaishakha ---
    _r("Varuthini Ekadashi", "Vaishakha", "Krishna", 11, "arunodaya"),
    _r("Parashurama Jayanti", "Vaishakha", "Shukla", 3),
    _r("Ganga Saptami", "Vaishakha", "Shukla", 7),
    _r("Sita Navami", "Vaishakha", "Shukla", 9),
    _r("Mohini Ekadashi", "Vaishakha", "Shukla", 11, "arunodaya"),
    _r("Narasimha Jayanti", "Vaishakha", "Shukla", 14),

    # --- Jyeshtha (Vat Savitri / Shani Jayanti are the amanta Jyeshtha Amavasya) ---
    _r("Narada Jayanti", "Jyeshtha", "Krishna", 1),
    _r("Apara Ekadashi", "Jyeshtha", "Krishna", 11, "arunodaya"),
    _r("Vat Savitri Vrat", "Jyeshtha", "Krishna", 15),
    _r("Shani Jayanti", "Jyeshtha", "Krishna", 15),
    _r("Ganga Dussehra", "Jyeshtha", "Shukla", 10),
    _r("Nirjala Ekadashi", "Jyeshtha", "Shukla", 11, "arunodaya"),

    # --- Ashadha ---
    _r("Yogini Ekadashi", "Ashadha", "Krishna", 11, "arunodaya"),
    _r("Devshayani Ekadashi", "Ashadha", "Shukla", 11, "arunodaya"),

    # --- Shravana ---
    _r("Kamika Ekadashi", "Shravana", "Krishna", 11, "arunodaya"),
    _r("Hariyali Teej", "Shravana", "Shukla", 3),
    _r("Shravana Putrada Ekadashi", "Shravana", "Shukla", 11, "arunodaya"),
    _r("Gayatri Jayanti", "Shravana", "Shukla", 15),

    # --- Bhadrapada ---
    _r("Kajari Teej", "Bhadrapada", "Krishna", 3),
    _r("Aja Ekadashi", "Bhadrapada", "Krishna", 11, "arunodaya"),
    _r("Rishi Panchami", "Bhadrapada", "Shukla", 5),
    _r("Balarama Jayanti", "Bhadrapada", "Shukla", 6),
    _r("Radha Ashtami", "Bhadrapada", "Shukla", 8),
    _r("Parsva Ekadashi", "Bhadrapada", "Shukla", 11, "arunodaya"),
    _r("Ganesh Visarjan", "Bhadrapada", "Shukla", 14,
       note="Anant Chaturdashi, immersion of Ganesha."),

    # --- Ashwin ---
    _r("Indira Ekadashi", "Ashwin", "Krishna", 11, "arunodaya"),
    _r("Papankusha Ekadashi", "Ashwin", "Shukla", 11, "arunodaya"),
    _r("Kojagara Puja", "Ashwin", "Shukla", 15),
    _r("Sharad Purnima", "Ashwin", "Shukla", 15),

    # --- Kartika ---
    _r("Rama Ekadashi", "Kartika", "Krishna", 11, "arunodaya"),
    _r("Ahoi Ashtami", "Kartika", "Krishna", 8),
    _r("Govatsa Dwadashi", "Kartika", "Krishna", 12),
    _r("Kansa Vadh", "Kartika", "Shukla", 10),
    _r("Devutthana Ekadashi", "Kartika", "Shukla", 11, "arunodaya"),
    _r("Tulasi Vivah", "Kartika", "Shukla", 12),

    # --- Margashirsha ---
    _r("Kalabhairav Jayanti", "Margashirsha", "Krishna", 8),
    _r("Utpanna Ekadashi", "Margashirsha", "Krishna", 11, "arunodaya"),
    _r("Vivah Panchami", "Margashirsha", "Shukla", 5),
    _r("Mokshada Ekadashi", "Margashirsha", "Shukla", 11, "arunodaya"),
    _r("Dattatreya Jayanti", "Margashirsha", "Shukla", 15),

    # --- Pausha ---
    _r("Saphala Ekadashi", "Pausha", "Krishna", 11, "arunodaya"),
    _r("Pausha Putrada Ekadashi", "Pausha", "Shukla", 11, "arunodaya"),

    # --- Solar ---
    _r("Vishwakarma Puja", None, None, None, system="solar", sankranti_rashi=5,
       note="Kanya Sankranti day."),

    # --- Common aliases (distinct names for the same day) ---
    _r("Rakhi", "Shravana", "Shukla", 15, note="Alias of Raksha Bandhan."),
    _r("Kali Chaudas", "Kartika", "Krishna", 14, note="Alias of Naraka Chaturdashi."),
    _r("Lakshmi Puja", "Kartika", "Krishna", 15, "pradosh", note="Diwali night."),
    _r("Jagannath Rathyatra", "Ashadha", "Shukla", 2, note="Alias of Rath Yatra."),
    _r("Navratri Begins", "Ashwin", "Shukla", 1, note="Alias of Sharad Navratri."),
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

# ---------------------------------------------------------------------------
# Islamic (Hijri) festivals, in calendar order within the Hijri year.
# Dates come from the tabular Islamic calendar (see kalagana/hijri.py); the
# observed date in India can differ by 1-2 days because it depends on the
# actual sighting of the new crescent.
# ---------------------------------------------------------------------------
_TABULAR = "Tabular Hijri date; the observed date may differ by 1-2 days."
ISLAMIC_RULES: Tuple[FestivalRule, ...] = (
    _h("Islamic New Year", 1, 1, note="1 Muharram. " + _TABULAR),
    _h("Ashura", 1, 10, note="10 Muharram. " + _TABULAR),
    _h("Shab-e-Miraj", 7, 27, note="27 Rajab (Isra and Mi'raj). " + _TABULAR),
    _h("Shab-e-Barat", 8, 15, note="15 Sha'ban. " + _TABULAR),
    _h("Ramadan Begins", 9, 1, note="1 Ramadan. " + _TABULAR),
    _h("Laylat al-Qadr", 9, 27, note="27 Ramadan. " + _TABULAR),
    _h("Eid al-Fitr", 10, 1, note="1 Shawwal (Id-ul-Fitr). " + _TABULAR),
    _h("Eid al-Adha", 12, 10, note="10 Dhu al-Hijjah (Bakrid / Id-ul-Zuha). " + _TABULAR),
    _h("Milad-un-Nabi", 3, 12, note="12 Rabi' al-Awwal (Mawlid / Id-e-Milad). " + _TABULAR),
)


# ---------------------------------------------------------------------------
# Fixed Gregorian-date observances: national holidays and commemorative days.
# Their dates never change, but they are still *rules*, evaluated for the
# requested year -- nothing is stored.  Listed in calendar order.
# ---------------------------------------------------------------------------
FIXED_RULES: Tuple[FestivalRule, ...] = (
    # --- Gazetted national holidays ---
    _f("Republic Day", 1, 26, kind="national", note="Gazetted national holiday."),
    _f("Independence Day", 8, 15, kind="national", note="Gazetted national holiday."),
    _f("Gandhi Jayanti", 10, 2, kind="national", note="Gazetted national holiday."),

    # --- Other fixed-date festivals / public celebrations ---
    _f("New Year's Day", 1, 1, kind="festival"),
    _f("Valentine's Day", 2, 14, kind="festival"),
    _f("Christmas", 12, 25, kind="festival",
       note="Gazetted public holiday (Christian)."),

    # --- National and commemorative observance days ---
    _f("National Youth Day", 1, 12, note="Swami Vivekananda Jayanti."),
    _f("Army Day", 1, 15),
    _f("National Girl Child Day", 1, 24),
    _f("National Voters' Day", 1, 25),
    _f("Martyrs' Day", 1, 30, note="Shaheed Diwas; Mahatma Gandhi's assassination."),
    _f("World Cancer Day", 2, 4),
    _f("National Science Day", 2, 28, note="Raman effect discovery."),
    _f("International Women's Day", 3, 8),
    _f("World Water Day", 3, 22),
    _f("Ambedkar Jayanti", 4, 14, kind="festival", note="Dr. B. R. Ambedkar's birthday."),
    _f("World Heritage Day", 4, 18),
    _f("National Panchayati Raj Day", 4, 24),
    _f("Labour Day", 5, 1, note="May Day."),
    _f("World Press Freedom Day", 5, 3),
    _f("National Technology Day", 5, 11),
    _f("Anti-Terrorism Day", 5, 21),
    _f("World Environment Day", 6, 5),
    _f("World Blood Donor Day", 6, 14),
    _f("International Yoga Day", 6, 21),
    _f("National Doctors' Day", 7, 1, note="Dr. B. C. Roy's birthday."),
    _f("Kargil Vijay Diwas", 7, 26),
    _f("National Handloom Day", 8, 7),
    _f("National Sports Day", 8, 29, note="Dhyan Chand's birthday."),
    _f("Teachers' Day", 9, 5, kind="festival", note="Dr. S. Radhakrishnan's birthday."),
    _f("Hindi Diwas", 9, 14),
    _f("Engineers' Day", 9, 15, note="Sir M. Visvesvaraya's birthday."),
    _f("World Tourism Day", 9, 27),
    _f("International Day of Non-Violence", 10, 2, note="Gandhi's birthday."),
    _f("Air Force Day", 10, 8),
    _f("World Students' Day", 10, 15, note="Dr. A. P. J. Abdul Kalam's birthday."),
    _f("National Unity Day", 10, 31, note="Sardar Vallabhbhai Patel Jayanti."),
    _f("National Education Day", 11, 11, note="Maulana Abul Kalam Azad's birthday."),
    _f("Children's Day", 11, 14, kind="festival", note="Jawaharlal Nehru's birthday."),
    _f("National Integration Day", 11, 19, note="Indira Gandhi's birthday."),
    _f("Constitution Day", 11, 26, note="Samvidhan Divas."),
    _f("Navy Day", 12, 4),
    _f("Human Rights Day", 12, 10),
    _f("Vijay Diwas", 12, 16),
)

FESTIVAL_RULES = FESTIVAL_RULES + SECONDARY_RULES + ISLAMIC_RULES + FIXED_RULES + _MONTHLY


def rules_by_name(name: str) -> Tuple[FestivalRule, ...]:
    """Return all rules whose name matches (case-insensitive)."""
    key = name.strip().lower()
    return tuple(r for r in FESTIVAL_RULES if r.name.lower() == key)
