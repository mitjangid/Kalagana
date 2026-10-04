"""Tabular (arithmetic) Hijri/Islamic calendar conversion.

Islamic dates are lunar and, in principle, begin with the *sighting* of the
new crescent.  That makes the observed civil date in India differ by a day or
two from a purely arithmetic calendar.  This module implements the standard
tabular (civil, "Kuwaiti") calendar so Islamic festival dates can still be
*computed* offline for any year -- no data files, no network.  Treat the
results as the tabular date; the actual observed date is typically within
+-1-2 days of it.

The epoch is 1 Muharram AH 1 = Friday 16 July 622 CE (Julian) = JD 1948439.5.
Months alternate 30/29 days and leap years add a day to Dhu al-Hijjah, giving
a mean year of 354 + 11/30 days (the 30-year cycle contains 11 leap years).
"""

from __future__ import annotations

import math
from datetime import date
from typing import Tuple

from . import julian

__all__ = [
    "HIJRI_MONTHS",
    "HIJRI_EPOCH_JD",
    "hijri_to_jd",
    "hijri_to_gregorian",
    "hijri_years_for_gregorian",
]

# JD (at midnight) of 1 Muharram AH 1, the civil/tabular epoch.
HIJRI_EPOCH_JD: float = 1948439.5

HIJRI_MONTHS: Tuple[str, ...] = (
    "Muharram",
    "Safar",
    "Rabi' al-Awwal",
    "Rabi' al-Thani",
    "Jumada al-Awwal",
    "Jumada al-Thani",
    "Rajab",
    "Sha'ban",
    "Ramadan",
    "Shawwal",
    "Dhu al-Qi'dah",
    "Dhu al-Hijjah",
)


def hijri_to_jd(hijri_year: int, hijri_month: int, hijri_day: int) -> float:
    """Julian Day (at midnight) of a tabular Hijri date.

    ``hijri_month`` is 1..12 and ``hijri_day`` is 1..30.
    """
    return (
        HIJRI_EPOCH_JD
        + (hijri_day - 1)
        + math.ceil(29.5 * (hijri_month - 1))
        + (hijri_year - 1) * 354
        + (3 + 11 * hijri_year) // 30
    )


def hijri_to_gregorian(hijri_year: int, hijri_month: int, hijri_day: int) -> date:
    """Convert a tabular Hijri date to a proleptic Gregorian ``date``."""
    jd = hijri_to_jd(hijri_year, hijri_month, hijri_day)
    year, month, day = julian.jd_to_calendar(jd, gregorian=True)
    return date(year, month, int(day))


def hijri_years_for_gregorian(gregorian_year: int) -> Tuple[int, ...]:
    """Return the Hijri years that (may) overlap a Gregorian year.

    A Gregorian year spans parts of two or three Hijri years; the returned
    window is generous enough to contain all of them.
    """
    estimate = int((gregorian_year - 622) * 33 / 32)
    return tuple(range(estimate - 2, estimate + 3))
