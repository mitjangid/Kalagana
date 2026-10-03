"""Astronomy foundation tests (runnable with ``python -m unittest`` or pytest)."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalagana import julian, moon, sun  # noqa: E402
from kalagana.limbs import elongation  # noqa: E402
from kalagana.solver import next_crossing  # noqa: E402

from .reference_dates import MEEUS_MOON, MEEUS_SUN, NEW_MOONS_2000  # noqa: E402


class TestJulian(unittest.TestCase):
    def test_roundtrip(self):
        jd = julian.gregorian_to_jd(2000, 1, 1.5)
        self.assertAlmostEqual(jd, 2451545.0, places=6)
        y, m, d = julian.jd_to_calendar(jd)
        self.assertEqual((y, m), (2000, 1))
        self.assertAlmostEqual(d, 1.5, places=6)

    def test_delta_t_reasonable(self):
        # Measured Delta T is ~64 s in 2000 and ~69 s in 2020.
        self.assertTrue(60.0 < julian.delta_t(2000.0) < 66.0)
        self.assertTrue(66.0 < julian.delta_t(2020.0) < 72.0)


class TestSun(unittest.TestCase):
    def test_meeus_example(self):
        jd = MEEUS_SUN["jd"]
        self.assertAlmostEqual(
            sun.sun_apparent_longitude(jd), MEEUS_SUN["apparent_longitude"], places=4
        )
        self.assertAlmostEqual(
            sun.sun_right_ascension(jd), MEEUS_SUN["right_ascension"], places=4
        )
        self.assertAlmostEqual(
            sun.sun_declination(jd), MEEUS_SUN["declination"], places=4
        )


class TestMoon(unittest.TestCase):
    def test_meeus_example(self):
        jd = MEEUS_MOON["jd"]
        lon, lat, dist = moon.moon_position(jd)
        self.assertAlmostEqual(lon, MEEUS_MOON["longitude"], places=4)
        self.assertAlmostEqual(lat, MEEUS_MOON["latitude"], places=4)
        self.assertAlmostEqual(dist, MEEUS_MOON["distance"], delta=1.0)


class TestPhases(unittest.TestCase):
    def test_new_moons_2000(self):
        jd = julian.datetime_to_jd(datetime(2000, 1, 1, tzinfo=timezone.utc))
        for expected in NEW_MOONS_2000:
            r = next_crossing(elongation, 0.0, jd, max_days=40.0)
            self.assertIsNotNone(r)
            got = julian.jd_to_datetime(r)
            self.assertLess(abs((got - expected).total_seconds()), 300.0)
            jd = r + 1.0


if __name__ == "__main__":
    unittest.main()
