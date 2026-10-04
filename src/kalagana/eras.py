"""Hindu eras and year numbers.

All conversions are approximate at the boundary of a year because different
eras begin on different days (Chaitra Shukla Pratipada for Vikram, Kartika
Shukla Pratipada for the Gujarati new year, the solar new year for the Shaka
and Kollam eras).  The conventions below follow the widely published panchang
usage and are documented so they can be adjusted.
"""

from __future__ import annotations

from datetime import date
from typing import Tuple

__all__ = [
    "SAMVATSARA_NAMES",
    "vikram_samvat",
    "shaka_year",
    "samvatsara_name",
    "kali_year",
    "kollam_year",
    "bengali_year",
    "gujarati_year",
    "ritu",
    "ayana",
]

# The 60-year Jovian (Brihaspati) cycle.
SAMVATSARA_NAMES = (
    "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angirasa",
    "Shrimukha", "Bhava", "Yuva", "Dhata", "Ishvara", "Bahudhanya",
    "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu", "Svabhanu", "Tarana",
    "Parthiva", "Vyaya", "Sarvajit", "Sarvadharin", "Virodhi", "Vikriti",
    "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
    "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava", "Shubhakrit",
    "Shobhakrit", "Krodhi", "Vishvavasu", "Parabhava", "Plavanga", "Kilaka",
    "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadi", "Ananda",
    "Rakshasa", "Anala", "Pingala", "Kalayukta", "Siddharthi", "Raudra",
    "Durmati", "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya",
)

# Anchor: the year beginning with Chaitra Shukla Pratipada of Shaka 1946
# (2024-25) carries the samvatsara "Krodhi" (index 37).  This matches the
# widely published Rashtriya Panchang listing.
_SHAKA_ANCHOR_YEAR = 1946
_SHAKA_ANCHOR_INDEX = 37


def _approx_gregorian_year(d: date) -> int:
    """Gregorian year shifted so the Hindu new year boundary is roughly Chaitra."""
    # Before ~mid-April the Hindu year is still the previous Gregorian year.
    if (d.month, d.day) < (3, 22):
        return d.year - 1
    return d.year


def vikram_samvat(d: date) -> int:
    """Vikram Samvat year (Chaitra Shukla Pratipada reckoning, North India)."""
    return _approx_gregorian_year(d) + 57


def shaka_year(d: date) -> int:
    """Shaka (Saka) era year, reckoned from the solar Chaitra new year."""
    return _approx_gregorian_year(d) - 78


def samvatsara_name(shaka: int) -> str:
    """Name of the 60-year samvatsara for a Shaka year."""
    idx = (shaka - (_SHAKA_ANCHOR_YEAR - _SHAKA_ANCHOR_INDEX)) % 60
    return SAMVATSARA_NAMES[idx]


def kali_year(d: date) -> int:
    """Kali (Kaliyuga) year."""
    return _approx_gregorian_year(d) + 3102


def kollam_year(d: date) -> int:
    """Kollam (Malayalam) era year; the Kollam era began in 825 CE."""
    y = d.year
    # Kollam year increments around the solar new year in August/September.
    if (d.month, d.day) < (8, 17):
        y -= 1
    return y - 824


def bengali_year(d: date) -> int:
    """Bengali (Bangabda) year; Poila Boishakh marks the new year (mid-April)."""
    y = _approx_gregorian_year(d)
    return y - 593


def gujarati_year(d: date) -> int:
    """Gujarati Samvat year (Kartika Shukla Pratipada new year, Oct/Nov)."""
    y = d.year
    if (d.month, d.day) < (10, 20):
        y -= 1
    return y + 57


# Ritu (season) and Ayana, computed from the sidereal solar longitude.
_RITUS = (
    "Vasanta", "Grishma", "Varsha", "Sharad", "Hemanta", "Shishira",
)


def ritu(sidereal_sun_longitude: float) -> str:
    """Season (ritu) for a sidereal Sun longitude in *degrees*."""
    # Vasanta begins when the Sun enters Mesha (0 deg), each ritu spanning 2 signs.
    return _RITUS[int((sidereal_sun_longitude % 360.0) // 60.0) % 6]


def ayana(sidereal_sun_longitude: float) -> str:
    """Uttarayana (Sun in 270..360..90) or Dakshinayana (90..270)."""
    lon = sidereal_sun_longitude % 360.0
    return "Uttarayana" if (lon >= 270.0 or lon < 90.0) else "Dakshinayana"
