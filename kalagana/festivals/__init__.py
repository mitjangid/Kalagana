"""Festival rule engine: rules as data, dates computed from astronomy."""

from __future__ import annotations

from .rules import (
    FestivalRule,
    FESTIVAL_RULES,
    SECONDARY_RULES,
    FIXED_RULES,
    ISLAMIC_RULES,
    KINDS,
    rules_by_name,
)
from .engine import (
    festival_dates,
    festivals_for_year,
    national_holidays,
    find_next,
    FestivalOccurrence,
)

__all__ = [
    "FestivalRule",
    "FESTIVAL_RULES",
    "SECONDARY_RULES",
    "FIXED_RULES",
    "ISLAMIC_RULES",
    "KINDS",
    "rules_by_name",
    "festival_dates",
    "festivals_for_year",
    "national_holidays",
    "find_next",
    "FestivalOccurrence",
]
