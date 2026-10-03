"""REST API tests: handler logic plus one real HTTP round-trip."""

from __future__ import annotations

import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalagana import config  # noqa: E402
from kalagana.server import ApiError, KalaganaAPI, create_server  # noqa: E402


class TestHandlers(unittest.TestCase):
    def setUp(self):
        self.api = KalaganaAPI(config.load_settings({"KALAGANA_CITY": "delhi"}))

    def test_health(self):
        self.assertEqual(self.api.health({})["status"], "ok")

    def test_cities(self):
        self.assertGreater(self.api.cities({})["count"], 20)

    def test_ayanamsas(self):
        self.assertIn("lahiri", self.api.ayanamsas({})["ayanamsas"])

    def test_day(self):
        out = self.api.day({"date": "2024-08-26", "city": "delhi"})
        self.assertEqual(out["date"], "2024-08-26")
        self.assertEqual(out["vara_en"], "Monday")
        self.assertTrue(any("Ashtami" in t["name"] for t in out["tithi"]))

    def test_day_missing_date(self):
        with self.assertRaises(ApiError) as ctx:
            self.api.day({"city": "delhi"})
        self.assertEqual(ctx.exception.status, 400)

    def test_location_falls_back_to_settings(self):
        # No city/lat/lon in the query -> uses KALAGANA_CITY.
        out = self.api.day({"date": "2024-08-26"})
        self.assertEqual(out["location"]["name"], "Delhi")

    def test_find_and_404(self):
        occ = self.api.find({"name": "Diwali", "after": "2025-01-01", "city": "delhi"})
        self.assertEqual(occ["date"], "2025-10-20")
        with self.assertRaises(ApiError) as ctx:
            self.api.find({"name": "Not A Festival", "city": "delhi"})
        self.assertEqual(ctx.exception.status, 404)


class TestHTTP(unittest.TestCase):
    def test_round_trip(self):
        settings = config.load_settings({"KALAGANA_CITY": "delhi", "KALAGANA_LOG_REQUESTS": "false"})
        httpd, _api = create_server("127.0.0.1", 0, settings)
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as resp:
                body = json.loads(resp.read())
                status = resp.status
            self.assertEqual(body["name"], "kalagana")
            self.assertEqual(status, 200)
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
