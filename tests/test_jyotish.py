"""Tests for :mod:`kalagana.jyotish` (kundali, varga, dasha, matching)."""

from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone

from kalagana import julian, limbs
from kalagana.jyotish import (
    RASHIS,
    angles,
    ashtakoota,
    daily_rashifal,
    dignity,
    kundali,
    kundali_match,
    planets,
    rashifal_for_all,
    varga,
    vimshottari,
)
from kalagana.location import city_lookup


def _jd(y, m, d, h=0, mi=0):
    dt = datetime(y, m, d, h, mi, tzinfo=timezone.utc)
    jd_ut = julian.datetime_to_jd(dt)
    jd_tt = jd_ut + julian.delta_t(y + (m - 0.5) / 12.0) / 86400.0
    return jd_ut, jd_tt


class TestPlanets(unittest.TestCase):
    def test_sun_matches_limbs(self):
        # The Keplerian Earth vector must reproduce the Meeus solar longitude.
        for y, m, d in ((2000, 1, 1), (2024, 8, 26), (2026, 10, 3), (1950, 6, 15)):
            _ju, jt = _jd(y, m, d, 12)
            diff = (planets.sun_sidereal_longitude(jt) - limbs.sidereal_sun_longitude(jt) + 180) % 360 - 180
            self.assertLess(abs(diff), 0.05, f"Sun mismatch on {y}-{m}-{d}")

    def test_known_grahas_2000(self):
        # Sanity anchors for 2000-01-01 12:00 UT (sidereal): Jupiter near the
        # start of Aries, Saturn in Aries, Rahu in Cancer.
        _ju, jt = _jd(2000, 1, 1, 12)
        self.assertEqual(int(planets.sidereal_longitude("Jupiter", jt) // 30), 0)  # Aries
        self.assertEqual(int(planets.sidereal_longitude("Saturn", jt) // 30), 0)   # Aries
        self.assertEqual(int(planets.sidereal_node_longitude(jt) // 30), 3)        # Cancer

    def test_retrograde_flags(self):
        _ju, jt = _jd(2026, 10, 3, 12)
        self.assertTrue(planets.is_retrograde("venus", jt))   # Venus retro Oct 2026
        self.assertTrue(planets.is_retrograde("saturn", jt))  # Saturn retro late 2026
        self.assertFalse(planets.is_retrograde("sun", jt))
        self.assertFalse(planets.is_retrograde("moon", jt))


class TestAngles(unittest.TestCase):
    def test_ascendant_lies_on_horizon(self):
        # The Lagna must be rising: altitude exactly zero, on the eastern side.
        for lat, lon in ((28.6139, 77.2090), (13.0827, 80.2707), (51.5074, -0.1278)):
            for y, m, d, h, mi in ((2000, 1, 1, 6, 0), (2024, 8, 26, 14, 30), (2026, 10, 3, 9, 15)):
                ju, jt = _jd(y, m, d, h, mi)
                asc = angles.ascendant(ju, jt, lat, lon)
                theta = angles.local_apparent_sidereal_time(ju, lon)
                eps = angles.true_obliquity(jt)
                lam = math.radians(asc.tropical)
                ra = math.degrees(math.atan2(math.cos(math.radians(eps)) * math.sin(lam), math.cos(lam))) % 360
                dec = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(lam)))
                hour = (theta - ra) % 360
                hour = hour - 360 if hour > 180 else hour
                alt = math.degrees(math.asin(
                    math.sin(math.radians(lat)) * math.sin(math.radians(dec))
                    + math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(math.radians(hour))
                ))
                self.assertLess(abs(alt), 0.01, "ascendant not on the horizon")
                self.assertLess(hour, 0, "ascendant should be rising (east)")

    def test_whole_sign_houses_are_consecutive(self):
        ju, jt = _jd(1990, 5, 15, 5, 0)
        asc = angles.ascendant(ju, jt, 28.6139, 77.2090)
        for i in range(12):
            self.assertEqual(angles.house_of_longitude(asc.sidereal + 30 * i, asc.sidereal), i + 1)


class TestVarga(unittest.TestCase):
    def test_navamsa(self):
        self.assertEqual(varga.varga_sign(0, 9), 0)     # Aries -> Aries
        self.assertEqual(varga.varga_sign(30, 9), 9)    # Taurus -> Capricorn
        self.assertEqual(varga.varga_sign(60, 9), 6)    # Gemini -> Libra
        self.assertEqual(varga.varga_sign(90, 9), 3)    # Cancer -> Cancer

    def test_other_vargas(self):
        self.assertEqual(varga.varga_sign(30, 3), 1)    # Taurus 1st drekkana = Taurus
        self.assertEqual(varga.varga_sign(30, 10), 9)   # Taurus (even) dasamsa 1st = Capricorn
        self.assertEqual(varga.varga_sign(0, 60), 0)    # Shashtiamsa starts Aries
        self.assertEqual(varga.varga_sign(0, 2), 4)     # odd sign hora 1st = Leo
        self.assertEqual(varga.varga_sign(30, 2), 3)    # even sign hora 1st = Cancer


class TestDasha(unittest.TestCase):
    def test_nakshatra_lord(self):
        from kalagana.jyotish import nakshatra_lord

        self.assertEqual(nakshatra_lord(1), "Ketu")      # Ashwini
        self.assertEqual(nakshatra_lord(2), "Venus")     # Bharani
        self.assertEqual(nakshatra_lord(3), "Sun")       # Krittika

    def test_cycle_totals_120_years(self):
        # Moon at 269.85 -> Uttara Ashadha -> Sun mahadasha.
        periods = vimshottari(269.847, 2448000.0, depth=1, count=9)
        self.assertEqual(periods[0].lord, "Sun")
        total = sum(p.years for p in periods)
        self.assertAlmostEqual(total, 120.0, places=6)
        # Periods are contiguous.
        for a, b in zip(periods, periods[1:]):
            self.assertAlmostEqual(a.end_jd, b.start_jd, places=9)

    def test_antardasha_subdivides(self):
        periods = vimshottari(100.0, 2448000.0, depth=2, count=1)
        maha = periods[0]
        self.assertEqual(len(maha.sub), 9)
        self.assertAlmostEqual(sum(s.years for s in maha.sub), maha.years, places=6)


class TestKundali(unittest.TestCase):
    def setUp(self):
        self.loc = city_lookup("delhi")

    def test_builds_full_chart(self):
        k = kundali(datetime(1990, 5, 15, 10, 30), self.loc)
        self.assertEqual(set(k.grahas), set(planets.GRAHAS))
        self.assertEqual(len(k.vargas), 16)
        self.assertEqual(len(k.houses), 12)
        # Houses are consecutive rashis starting from the Lagna.
        self.assertEqual(k.houses[0], k.ascendant.rashi)
        for i in range(12):
            self.assertEqual(k.houses[i], (k.ascendant.rashi + i) % 12)
        # Moon rashi is consistent with its longitude.
        self.assertEqual(k.moon.rashi, int(k.moon.longitude // 30))

    def test_naive_datetime_gets_location_zone(self):
        k = kundali(datetime(2000, 1, 1, 6, 0), self.loc)
        self.assertIsNotNone(k.when.tzinfo)

    def test_to_dict_serialisable(self):
        import json

        k = kundali(datetime(1985, 3, 3, 21, 45), self.loc, dasha_depth=1)
        blob = json.dumps(k.to_dict())
        self.assertIn("ascendant", blob)


class TestMatch(unittest.TestCase):
    def test_kootas_sum_to_total(self):
        result = ashtakoota(8, 21, 9, 22)
        self.assertAlmostEqual(sum(k.score for k in result.kootas), result.total, places=6)
        self.assertEqual(result.maximum, 36.0)
        self.assertEqual([k.name for k in result.kootas],
                         ["Varna", "Vashya", "Tara", "Yoni", "Graha Maitri", "Gana", "Bhakoot", "Nadi"])

    def test_same_nadi_scores_zero(self):
        # Same nakshatra -> same nadi -> 0 points and full Tara failure.
        result = ashtakoota(0, 1, 0, 1)
        nadi = next(k for k in result.kootas if k.name == "Nadi")
        self.assertEqual(nadi.score, 0.0)

    def test_kundali_match_end_to_end(self):
        loc = city_lookup("delhi")
        boy = kundali(datetime(1990, 5, 15, 10, 30), loc, with_dasha=False)
        girl = kundali(datetime(1992, 11, 3, 4, 15), loc, with_dasha=False)
        out = kundali_match(boy, girl)
        self.assertIn("ashtakoota", out)
        self.assertGreaterEqual(out["ashtakoota"]["total"], 0)
        self.assertLessEqual(out["ashtakoota"]["total"], 36)
        self.assertIn("mangal_dosha", out["boy"])


class TestDignity(unittest.TestCase):
    def test_exaltation_and_own(self):
        self.assertEqual(dignity.dignity("Sun", 10.0), "exalted")       # Sun in Aries
        self.assertEqual(dignity.dignity("Saturn", 271.0), "own")       # Saturn in Capricorn
        self.assertEqual(dignity.dignity("Venus", 348.0), "exalted")    # Venus in Pisces

    def test_combustion(self):
        self.assertTrue(dignity.is_combust("Mercury", 100.0, 108.0))
        self.assertFalse(dignity.is_combust("Mercury", 100.0, 140.0))


class TestCharts(unittest.TestCase):
    def setUp(self):
        from kalagana.jyotish import charts

        self.charts = charts
        self.rbg = {"Sun": 0, "Moon": 3, "Mars": 7}

    def test_all_three_formats(self):
        out = self.charts(3, self.rbg)  # Lagna = Cancer
        self.assertEqual(set(out), {"north", "south", "east"})
        for fmt, cells in out.items():
            self.assertEqual(len(cells), 12, fmt)
            # Every graha appears exactly once.
            seen = [g for c in cells for g in c["grahas"]]
            self.assertEqual(sorted(seen), ["Mars", "Moon", "Sun"], fmt)
            # Exactly one Lagna cell, always house 1.
            lagna = [c for c in cells if c["lagna"]]
            self.assertEqual(len(lagna), 1, fmt)
            self.assertEqual(lagna[0]["house"], 1, fmt)
            self.assertEqual(lagna[0]["rashi"], 3, fmt)

    def test_south_sign_positions_fixed(self):
        # Pisces top-left, then Aries, Taurus, Gemini clockwise.
        out = self.charts(0, {})["south"]
        by_pos = {(c["row"], c["col"]): c["rashi"] for c in out}
        self.assertEqual(by_pos[(0, 0)], 11)  # Pisces
        self.assertEqual(by_pos[(0, 1)], 0)   # Aries
        self.assertEqual(by_pos[(3, 3)], 5)   # Virgo

    def test_north_house_signs_rotate_with_lagna(self):
        out = self.charts(3, {})["north"]
        self.assertEqual([c["rashi"] for c in out], [(3 + i) % 12 for i in range(12)])

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            self.charts(0, {}, formats=("western",))

    def test_kundali_to_dict_has_charts(self):
        loc = city_lookup("delhi")
        k = kundali(datetime(1990, 5, 15, 10, 30), loc, with_dasha=False)
        d = k.to_dict()
        self.assertEqual(set(d["charts"]), {"north", "south", "east"})
        self.assertEqual(len(k.chart("east")), 12)


class TestRashifal(unittest.TestCase):
    def test_deterministic(self):
        from datetime import date

        a = daily_rashifal("Mesha", date(2026, 10, 3))
        b = daily_rashifal(0, date(2026, 10, 3))
        self.assertEqual(a.to_dict(), b.to_dict())  # name and index agree
        self.assertEqual(a.summary, b.summary)

    def test_all_twelve(self):
        from datetime import date

        out = rashifal_for_all(date(2026, 10, 3))
        self.assertEqual(len(out), 12)
        self.assertEqual({r.rashi for r in out}, set(range(12)))
        for r in out:
            self.assertEqual(len(r.transits), 9)
            self.assertIn(r.band, ("Excellent", "Good", "Average", "Mixed", "Challenging"))
            self.assertTrue(r.summary)

    def test_house_is_relative_to_moon_sign(self):
        # For a given transit, the house must differ by the rashi offset.
        from datetime import date

        a = daily_rashifal(0, date(2026, 10, 3))   # Mesha
        b = daily_rashifal(1, date(2026, 10, 3))   # Vrishabha
        sun_a = next(t for t in a.transits if t.graha == "Sun")
        sun_b = next(t for t in b.transits if t.graha == "Sun")
        # Houses are counted from the Moon sign, so advancing the Moon sign by
        # one rashi reduces every transit house by one.
        self.assertEqual((sun_a.house - sun_b.house) % 12, 1)

    def test_unknown_rashi_raises(self):
        with self.assertRaises(ValueError):
            daily_rashifal("Atlantis")


if __name__ == "__main__":
    unittest.main()
