"""Ground-truth reference values used by the test-suite.

Every value is hardcoded deliberately so the tests can be run offline.  Sources
are noted per block.  Values that the author could not verify against an
authoritative source are marked ``# UNVERIFIED`` and should be replaced once
confirmed -- the engine is not tuned to them.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

# ---------------------------------------------------------------------------
# Meeus, "Astronomical Algorithms" (2nd ed.) worked examples.
# ---------------------------------------------------------------------------
# Chapter 47.a -- 1992 April 12.0 TD.
MEEUS_MOON = {
    "jd": 2448724.5,
    "longitude": 133.162655,   # degrees
    "latitude": -3.229126,     # degrees
    "distance": 368409.7,      # km
}
# Chapter 25.b -- 1992 October 13.0 TD, apparent Sun.
MEEUS_SUN = {
    "jd": 2448908.5,
    "apparent_longitude": 199.90895,   # degrees
    "right_ascension": 198.38083,      # degrees
    "declination": -7.78507,           # degrees
}

# ---------------------------------------------------------------------------
# New moon instants (UTC), 2000.  Source: published astronomical tables
# (e.g. the U.S. Naval Observatory phases of the Moon) as commonly listed.
# ---------------------------------------------------------------------------
NEW_MOONS_2000 = [
    (datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)),
    (datetime(2000, 2, 5, 13, 3, tzinfo=timezone.utc)),
    (datetime(2000, 3, 6, 5, 17, tzinfo=timezone.utc)),
    (datetime(2000, 4, 4, 18, 12, tzinfo=timezone.utc)),
    (datetime(2000, 5, 4, 4, 12, tzinfo=timezone.utc)),
    (datetime(2000, 6, 2, 12, 14, tzinfo=timezone.utc)),
    (datetime(2000, 7, 1, 19, 20, tzinfo=timezone.utc)),
    (datetime(2000, 7, 31, 2, 25, tzinfo=timezone.utc)),
    (datetime(2000, 8, 29, 10, 19, tzinfo=timezone.utc)),
    (datetime(2000, 9, 27, 19, 53, tzinfo=timezone.utc)),
    (datetime(2000, 10, 27, 7, 58, tzinfo=timezone.utc)),
    (datetime(2000, 11, 25, 23, 11, tzinfo=timezone.utc)),
    (datetime(2000, 12, 25, 17, 22, tzinfo=timezone.utc)),
]

# ---------------------------------------------------------------------------
# Sunrise / sunset (local time as HH:MM) for New Delhi, Drik Panchang.
# ---------------------------------------------------------------------------
DELHI_SUNRISE_SUNSET = {
    date(2024, 3, 20): ("06:24", "18:32"),
    date(2024, 6, 21): ("05:24", "19:22"),
    date(2024, 12, 21): ("07:09", "17:28"),
}

# ---------------------------------------------------------------------------
# Festival dates for New Delhi, Drik Panchang.  (North / purnimanta.)
# ---------------------------------------------------------------------------
FESTIVALS_2024_DELHI = {
    "Makar Sankranti": date(2024, 1, 14),
    "Vasant Panchami": date(2024, 2, 14),
    "Maha Shivaratri": date(2024, 3, 8),
    "Holika Dahan": date(2024, 3, 24),
    "Holi": date(2024, 3, 25),
    "Chaitra Navratri": date(2024, 4, 9),
    "Rama Navami": date(2024, 4, 17),
    "Hanuman Jayanti": date(2024, 4, 23),
    "Akshaya Tritiya": date(2024, 5, 10),
    "Buddha Purnima": date(2024, 5, 23),
    "Rath Yatra": date(2024, 7, 7),
    "Guru Purnima": date(2024, 7, 21),
    "Nag Panchami": date(2024, 8, 9),
    "Raksha Bandhan": date(2024, 8, 19),
    "Krishna Janmashtami": date(2024, 8, 26),
    "Ganesh Chaturthi": date(2024, 9, 7),
    "Anant Chaturdashi": date(2024, 9, 17),
    "Mahalaya Amavasya": date(2024, 10, 2),
    "Sharad Navratri": date(2024, 10, 3),
    "Durga Ashtami": date(2024, 10, 11),
    "Maha Navami": date(2024, 10, 12),
    "Dussehra": date(2024, 10, 13),
    "Karwa Chauth": date(2024, 10, 20),
    "Dhanteras": date(2024, 10, 29),
    "Diwali": date(2024, 10, 31),
    "Govardhan Puja": date(2024, 11, 2),
    "Bhai Dooj": date(2024, 11, 3),
    "Chhath Puja": date(2024, 11, 7),
    "Kartik Purnima": date(2024, 11, 15),
    "Dev Deepawali": date(2024, 11, 15),
}

# ---------------------------------------------------------------------------
# Fixed Gregorian-calendar-date observances.  These never depend on astronomy;
# the pairs are the statutory / calendar month and day.
# ---------------------------------------------------------------------------
NATIONAL_HOLIDAYS_FIXED = {
    "Republic Day": (1, 26),
    "Independence Day": (8, 15),
    "Gandhi Jayanti": (10, 2),
}

FIXED_DATES = {
    **NATIONAL_HOLIDAYS_FIXED,
    "New Year's Day": (1, 1),
    "Army Day": (1, 15),
    "National Science Day": (2, 28),
    "International Women's Day": (3, 8),
    "Ambedkar Jayanti": (4, 14),
    "Labour Day": (5, 1),
    "International Yoga Day": (6, 21),
    "National Sports Day": (8, 29),
    "Teachers' Day": (9, 5),
    "Children's Day": (11, 14),
    "Constitution Day": (11, 26),
    "Navy Day": (12, 4),
    "Christmas": (12, 25),
}

# ---------------------------------------------------------------------------
# Tabular (civil) Islamic calendar anchors: (hijri_year, month, day) ->
# Gregorian date.  These follow the standard arithmetic Islamic calendar
# (epoch 1 Muharram AH 1 = 16 July 622 CE); the locally observed date may be
# a day or two later because it depends on the crescent sighting.
# ---------------------------------------------------------------------------
HIJRI_TABULAR = {
    (1445, 1, 1): date(2023, 7, 19),    # Islamic New Year
    (1445, 9, 1): date(2024, 3, 11),    # Ramadan begins
    (1445, 10, 1): date(2024, 4, 10),   # Eid al-Fitr
    (1445, 12, 10): date(2024, 6, 17),  # Eid al-Adha
    (1446, 1, 1): date(2024, 7, 8),     # Islamic New Year
    (1446, 3, 12): date(2024, 9, 16),   # Milad-un-Nabi
    (1447, 9, 1): date(2026, 2, 18),    # Ramadan begins
    (1447, 10, 1): date(2026, 3, 20),   # Eid al-Fitr
    (1447, 12, 10): date(2026, 5, 27),  # Eid al-Adha
}

# Adhika masa years in 2010-2030, from published panchang records.
ADHIKA_MASA_YEARS = {
    2012: "Bhadrapada",   # UNVERIFIED name; year is well established
    2015: "Ashadha",
    2018: "Jyeshtha",
    2020: "Ashwin",
    2023: "Shravana",
    2026: "Jyeshtha",
}
