"""Limb, sunrise and calendar-structure tests."""

from __future__ import annotations

import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalagana import calendar_month, julian, limbs, muhurta  # noqa: E402
from kalagana.location import Location  # noqa: E402
from kalagana.sunrise import sunrise_sunset  # noqa: E402

from .reference_dates import ADHIKA_MASA_YEARS, DELHI_SUNRISE_SUNSET  # noqa: E402

DELHI = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")


class TestSunrise(unittest.TestCase):
    def test_delhi_against_drik(self):
        for d, (rs, ss) in DELHI_SUNRISE_SUNSET.items():
            r, s = sunrise_sunset(d, DELHI)
            self.assertIsNotNone(r)
            self.assertIsNotNone(s)
            for got, want in ((r, rs), (s, ss)):
                hh, mm = (int(x) for x in want.split(":"))
                target = got.replace(hour=hh, minute=mm, second=0, microsecond=0)
                self.assertLess(abs((got - target).total_seconds()), 120.0)


class TestLimbs(unittest.TestCase):
    def test_janmashtami_is_krishna_ashtami(self):
        # 2024-08-26 sunrise should carry Krishna Ashtami (Janmashtami).
        info = limbs.day_limbs(date(2024, 8, 26), DELHI)
        names = [s.name for s in info["tithi"]]
        self.assertIn("Krishna Ashtami", names)
        self.assertEqual(info["vara_en"], "Monday")

    def test_tithi_name_ranges(self):
        self.assertEqual(limbs.tithi_name(1), "Shukla Pratipada")
        self.assertEqual(limbs.tithi_name(15), "Purnima")
        self.assertEqual(limbs.tithi_name(30), "Amavasya")
        self.assertEqual(limbs.tithi_name(16), "Krishna Pratipada")

    def test_karana_counts(self):
        # 60 karanas; 1 fixed + 56 movable + 3 fixed.
        self.assertEqual(limbs.karana_name(1), "Kimstughna")
        self.assertEqual(limbs.karana_name(2), "Bava")
        self.assertEqual(limbs.karana_name(58), "Shakuni")
        self.assertEqual(limbs.karana_name(60), "Naga")


class TestMasa(unittest.TestCase):
    def test_known_month(self):
        # 2024-08-26 is amanta Shravana (purnimanta Bhadrapada).
        jd = julian.datetime_to_jd(datetime(2024, 8, 26, 6, 0, tzinfo=timezone.utc))
        m = calendar_month.masa_at(jd)
        self.assertEqual(m.name, "Shravana")
        self.assertFalse(m.adhika)

    def test_adhika_years(self):
        for year, name in ADHIKA_MASA_YEARS.items():
            found = False
            jd = julian.datetime_to_jd(datetime(year, 1, 1))
            end = julian.datetime_to_jd(datetime(year + 1, 1, 1))
            nm = calendar_month.next_new_moon(jd)
            while nm < end:
                m = calendar_month.masa_at(nm + 0.5)
                if m.adhika:
                    found = True
                    self.assertEqual(m.name, name)
                nm = calendar_month.next_new_moon(nm + 1.0)
            self.assertTrue(found, f"no adhika masa found in {year}")


class TestMuhurta(unittest.TestCase):
    def test_rahu_kalam_matches_reference(self):
        # Rahu Kalam is the 8th of 8 daylight kalas on a Sunday.
        d = date(2024, 3, 24)  # a Sunday
        r, s = sunrise_sunset(d, DELHI)
        self.assertEqual(r.weekday(), 6)  # Sunday
        w = muhurta.rahu_kalam(d, DELHI)
        span = (s - r) / 8
        self.assertAlmostEqual(
            (w.start - r).total_seconds(), span.total_seconds() * 7, delta=1
        )


if __name__ == "__main__":
    unittest.main()
