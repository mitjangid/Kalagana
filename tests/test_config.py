"""Configuration (.env / environment) tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kalagana import config  # noqa: E402


class TestSettings(unittest.TestCase):
    def test_defaults(self):
        s = config.load_settings({})
        self.assertEqual(s.host, "127.0.0.1")
        self.assertEqual(s.port, 8765)
        self.assertEqual(s.city, "delhi")
        self.assertIsNone(s.lat)
        self.assertEqual(s.ayanamsa, "lahiri")
        self.assertTrue(s.include_monthly)

    def test_overrides(self):
        s = config.load_settings(
            {
                "KALAGANA_HOST": "0.0.0.0",
                "KALAGANA_PORT": "9000",
                "KALAGANA_CITY": "mumbai",
                "KALAGANA_LAT": "19.076",
                "KALAGANA_LON": "72.8777",
                "KALAGANA_AYANAMSA": "kp",
                "KALAGANA_INCLUDE_MONTHLY": "false",
                "KALAGANA_FIND_YEARS": "5",
            }
        )
        self.assertEqual(s.host, "0.0.0.0")
        self.assertEqual(s.port, 9000)
        self.assertEqual(s.city, "mumbai")
        self.assertAlmostEqual(s.lat, 19.076)
        self.assertAlmostEqual(s.lon, 72.8777)
        self.assertEqual(s.ayanamsa, "kp")
        self.assertFalse(s.include_monthly)
        self.assertEqual(s.find_years, 5)
        self.assertTrue(s.has_default_location())

    def test_invalid_values_fall_back_by_default(self):
        s = config.load_settings({"KALAGANA_PORT": "not-a-port", "KALAGANA_LAT": "x"})
        self.assertEqual(s.port, 8765)
        self.assertIsNone(s.lat)

    def test_strict_mode_raises(self):
        with self.assertRaises(config.ConfigError):
            config.load_settings({"KALAGANA_STRICT": "true", "KALAGANA_PORT": "nope"})


class TestEnvFile(unittest.TestCase):
    def test_parse_and_no_override(self):
        content = (
            "# a comment\n"
            "\n"
            "export KALAGANA_PORT=8123\n"
            'KALAGANA_CITY="Jaipur"\n'
            "IGNORED_LINE\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(content, encoding="utf-8")

            saved = dict(os.environ)
            try:
                os.environ.pop("KALAGANA_PORT", None)
                os.environ.pop("KALAGANA_CITY", None)
                # Pre-set one variable to prove it is NOT overwritten.
                os.environ["KALAGANA_PORT"] = "1111"

                loaded = config.load_env_file(str(path))

                self.assertEqual(loaded["KALAGANA_CITY"], "Jaipur")
                self.assertEqual(os.environ["KALAGANA_PORT"], "1111")  # preserved
                self.assertEqual(os.environ["KALAGANA_CITY"], "Jaipur")
            finally:
                os.environ.clear()
                os.environ.update(saved)

    def test_missing_file_is_empty(self):
        self.assertEqual(config.load_env_file("/no/such/.env"), {})


if __name__ == "__main__":
    unittest.main()
