"""Fixed Gregorian-date rules: national holidays and observance days.

These rules do not depend on astronomy, so their dates must be identical in
every year and place.  The tests also cover the ``kind`` categories and the
``national_holidays`` convenience helper.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalagana import festivals_for_year, find_next, national_holidays  # noqa: E402
from kalagana.festivals import FIXED_RULES, KINDS  # noqa: E402
from kalagana.location import Location  # noqa: E402

from .reference_dates import FIXED_DATES, NATIONAL_HOLIDAYS_FIXED  # noqa: E402

DELHI = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")
CHENNAI = Location("Chennai", 13.0827, 80.2707, "Asia/Kolkata")

YEARS = (2020, 2024, 2026, 2030)


class TestFixedRuleData(unittest.TestCase):
    def test_rule_data_is_well_formed(self):
        for rule in FIXED_RULES:
            self.assertEqual(rule.system, "fixed", rule.name)
            self.assertIsNotNone(rule.fixed_month, rule.name)
            self.assertIsNotNone(rule.fixed_day, rule.name)
            self.assertIn(rule.kind, KINDS, rule.name)
            # Validating by construction catches a slipped month/day.
            date(2025, rule.fixed_month, rule.fixed_day)

    def test_national_holidays_are_gazetted(self):
        national = [r.name for r in FIXED_RULES if r.kind == "national"]
        self.assertEqual(
            set(national),
            {"Republic Day", "Independence Day", "Gandhi Jayanti"},
        )


class TestFixedDates(unittest.TestCase):
    def test_reference_dates_every_year(self):
        for year in YEARS:
            by_name = {
                o.name: o.date
                for o in festivals_for_year(
                    year, DELHI, tradition="north", include_monthly=False
                )
            }
            for name, (month, day) in FIXED_DATES.items():
                self.assertEqual(
                    by_name.get(name), date(year, month, day),
                    f"{name} in {year}",
                )

    def test_every_fixed_rule_emits(self):
        emitted = {
            o.name
            for o in festivals_for_year(2026, DELHI, include_monthly=False)
        }
        for rule in FIXED_RULES:
            self.assertIn(rule.name, emitted, rule.name)

    def test_place_independent(self):
        delhi = {o.name: o.date for o in festivals_for_year(2026, DELHI, include_monthly=False)}
        chennai = {o.name: o.date for o in festivals_for_year(2026, CHENNAI, include_monthly=False)}
        for rule in FIXED_RULES:
            self.assertEqual(delhi[rule.name], chennai[rule.name], rule.name)


class TestKinds(unittest.TestCase):
    def test_kind_filter(self):
        occs = festivals_for_year(2026, DELHI, include_monthly=False, kinds=("national",))
        self.assertTrue(occs)
        self.assertTrue(all(o.kind == "national" for o in occs))
        self.assertEqual({o.name for o in occs}, set(NATIONAL_HOLIDAYS_FIXED))

    def test_national_holidays_helper(self):
        occs = national_holidays(2026, DELHI)
        self.assertEqual(len(occs), 3)
        self.assertEqual(
            {o.name for o in occs},
            {"Republic Day", "Independence Day", "Gandhi Jayanti"},
        )

    def test_observances_kind(self):
        occs = festivals_for_year(
            2026, DELHI, include_monthly=False, kinds=("observance",)
        )
        self.assertTrue(all(o.kind == "observance" for o in occs))
        self.assertIn("National Science Day", {o.name for o in occs})


class TestFixedToggle(unittest.TestCase):
    def test_toggle_removes_fixed_rules(self):
        names = {
            o.name
            for o in festivals_for_year(
                2026, DELHI, include_monthly=False, include_fixed=False
            )
        }
        for rule in FIXED_RULES:
            self.assertNotIn(rule.name, names)
        # Ordinary lunar/solar festivals are unaffected.
        self.assertIn("Diwali", names)


class TestFindFixed(unittest.TestCase):
    def test_find_next_republic_day(self):
        occ = find_next("Republic Day", date(2026, 1, 1), DELHI)
        self.assertIsNotNone(occ)
        self.assertEqual(occ.date, date(2026, 1, 26))

    def test_find_next_rolls_to_next_year(self):
        occ = find_next("Independence Day", date(2026, 9, 1), DELHI)
        self.assertIsNotNone(occ)
        self.assertEqual(occ.date, date(2027, 8, 15))


if __name__ == "__main__":
    unittest.main()
