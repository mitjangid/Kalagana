"""Islamic (Hijri) festivals: tabular calendar conversion and rule wiring.

The engine uses the arithmetic (tabular) Islamic calendar, so the dates are
deterministic.  These tests pin the converter to standard tabular anchors and
check that each ``ISLAMIC_RULES`` entry emits exactly one date per year that
agrees with the converter.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalagana import festivals_for_year, find_next  # noqa: E402
from kalagana.festivals import ISLAMIC_RULES  # noqa: E402
from kalagana.hijri import (  # noqa: E402
    hijri_to_gregorian,
    hijri_years_for_gregorian,
)
from kalagana.location import Location  # noqa: E402

from .reference_dates import HIJRI_TABULAR  # noqa: E402

DELHI = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")


class TestHijriConverter(unittest.TestCase):
    def test_tabular_anchors(self):
        for key, want in HIJRI_TABULAR.items():
            self.assertEqual(hijri_to_gregorian(*key), want, key)

    def test_year_window_is_five_consecutive_years(self):
        for gy in (2020, 2024, 2026, 2030):
            years = hijri_years_for_gregorian(gy)
            self.assertEqual(len(years), 5)
            self.assertEqual(list(years), list(range(years[0], years[0] + 5)))

    def test_window_contains_the_new_year_starting_in_that_gregorian_year(self):
        for gy in (2020, 2024, 2026, 2030):
            # Exactly one Hijri new year (1 Muharram) falls in a Gregorian year.
            target = next(
                h for h in range(1400, 1500)
                if hijri_to_gregorian(h, 1, 1).year == gy
            )
            self.assertIn(target, hijri_years_for_gregorian(gy))


class TestIslamicFestivalRules(unittest.TestCase):
    def test_each_rule_matches_the_converter(self):
        occs = festivals_for_year(2026, DELHI, include_monthly=False)
        by_name = {o.name: o.date for o in occs}
        for rule in ISLAMIC_RULES:
            want = None
            for hy in hijri_years_for_gregorian(2026):
                gd = hijri_to_gregorian(hy, rule.hijri_month, rule.hijri_day)
                if gd.year == 2026:
                    want = gd
            self.assertIsNotNone(want, rule.name)
            self.assertEqual(by_name.get(rule.name), want, rule.name)

    def test_known_2026_eids(self):
        by_name = {
            o.name: o.date
            for o in festivals_for_year(2026, DELHI, include_monthly=False)
        }
        self.assertEqual(by_name["Eid al-Fitr"], hijri_to_gregorian(1447, 10, 1))
        self.assertEqual(by_name["Eid al-Adha"], hijri_to_gregorian(1447, 12, 10))

    def test_toggle_removes_islamic(self):
        names = {
            o.name
            for o in festivals_for_year(
                2026, DELHI, include_monthly=False, include_islamic=False
            )
        }
        for rule in ISLAMIC_RULES:
            self.assertNotIn(rule.name, names)

    def test_find_next_eid(self):
        occ = find_next("Eid al-Fitr", date(2026, 1, 1), DELHI)
        self.assertIsNotNone(occ)
        self.assertEqual(occ.date, hijri_to_gregorian(1447, 10, 1))


if __name__ == "__main__":
    unittest.main()
