"""Secondary / regional Hindu festivals and named vrats.

``SECONDARY_RULES`` fills the gap against the published Drik Panchang Hindu
calendar.  Dates are still computed from astronomy; this module checks the
rule table is well-formed, that a curated set of 2026 dates matches, and that
the aliases resolve by name.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kalagana import festivals_for_year, find_next  # noqa: E402
from kalagana.festivals import FESTIVAL_RULES, SECONDARY_RULES  # noqa: E402
from kalagana.location import Location  # noqa: E402

DELHI = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")

# A representative set that agrees with the Drik Panchang 2026 list.
SECONDARY_2026_DELHI = {
    "Sakat Chauth": date(2026, 1, 6),
    "Shattila Ekadashi": date(2026, 1, 14),
    "Mauni Amavas": date(2026, 1, 18),
    "Bhishma Ashtami": date(2026, 1, 26),
    "Jaya Ekadashi": date(2026, 1, 29),
    "Vijaya Ekadashi": date(2026, 2, 13),
    "Amalaki Ekadashi": date(2026, 2, 27),
    "Chhoti Holi": date(2026, 3, 3),
    "Sheetala Ashtami": date(2026, 3, 11),
    "Yamuna Chhath": date(2026, 3, 24),
    "Kamada Ekadashi": date(2026, 3, 29),
    "Varuthini Ekadashi": date(2026, 4, 13),
    "Vat Savitri Vrat": date(2026, 5, 16),
    "Shani Jayanti": date(2026, 5, 16),
    "Narada Jayanti": date(2026, 5, 2),
    "Jagannath Rathyatra": date(2026, 7, 16),
    "Hariyali Teej": date(2026, 8, 15),
    "Rakhi": date(2026, 8, 28),
    "Radha Ashtami": date(2026, 9, 19),
    "Navratri Begins": date(2026, 10, 11),
    "Lakshmi Puja": date(2026, 11, 8),
    "Kalabhairav Jayanti": date(2026, 12, 1),
    "Vivah Panchami": date(2026, 12, 14),
}


class TestSecondaryRuleData(unittest.TestCase):
    def test_unique_names_and_merged_in(self):
        names = [r.name for r in SECONDARY_RULES]
        self.assertEqual(len(names), len(set(names)), "duplicate rule names")
        merged = {r.name for r in FESTIVAL_RULES}
        for name in names:
            self.assertIn(name, merged)

    def test_ekadashi_windows_are_arunodaya(self):
        for r in SECONDARY_RULES:
            if r.name.endswith("Ekadashi"):
                self.assertEqual(r.window, "arunodaya", r.name)


class TestSecondaryDates(unittest.TestCase):
    def test_2026_reference_dates(self):
        by_name = {
            o.name: o.date
            for o in festivals_for_year(2026, DELHI, include_monthly=False)
        }
        for name, want in SECONDARY_2026_DELHI.items():
            self.assertEqual(by_name.get(name), want, name)

    def test_alias_find_next(self):
        occ = find_next("Rakhi", date(2026, 1, 1), DELHI)
        self.assertIsNotNone(occ)
        self.assertEqual(occ.date, date(2026, 8, 28))


if __name__ == "__main__":
    unittest.main()
