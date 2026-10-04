"""Festival engine tests (dates computed from rules, checked against Drik)."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kalagana import festivals_for_year, find_next  # noqa: E402
from kalagana.location import Location  # noqa: E402

from .data.reference_dates import FESTIVALS_2024_DELHI  # noqa: E402

DELHI = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")


class TestFestivals2024(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occs = festivals_for_year(2024, DELHI, tradition="north", include_monthly=False)
        cls.by_name = {}
        for o in cls.occs:
            cls.by_name.setdefault(o.name, o.date)

    def test_all_reference_dates(self):
        for name, want in FESTIVALS_2024_DELHI.items():
            got = self.by_name.get(name)
            self.assertIsNotNone(got, f"{name} not computed")
            self.assertEqual(got, want, f"{name}: got {got}, want {want}")

    def test_no_hardcoded_dates(self):
        # The engine must produce different dates in different years.
        d2025 = {
            o.name: o.date
            for o in festivals_for_year(2025, DELHI, tradition="north", include_monthly=False)
        }
        self.assertNotEqual(d2025.get("Diwali"), date(2024, 10, 31))


class TestFindNext(unittest.TestCase):
    def test_find_diwali(self):
        occ = find_next("Diwali", date(2024, 1, 1), DELHI)
        self.assertIsNotNone(occ)
        self.assertEqual(occ.date, date(2024, 10, 31))


if __name__ == "__main__":
    unittest.main()
