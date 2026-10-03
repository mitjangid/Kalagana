"""Offline REST API for Kalagana, using only the standard library.

Run it with::

    python -m kalagana.server --host 127.0.0.1 --port 8765

or via the CLI::

    python -m kalagana serve --port 8765

Endpoints (all GET, JSON)

==========================  ==================================================
``/health``                  service status and version
``/cities``                  built-in city table
``/ayanamsas``               supported ayanamsa models
``/day?date=&city=``         full panchang for one date and place
``/month?month=YYYY-MM``     day-by-day summary for a Gregorian month
``/festivals?year=``         computed festival dates for a year
``/eclipses?year=``          approximate eclipses for a year
``/muhurta?date=``           daily muhurta windows
``/find?name=&after=``       next occurrence of a named festival
==========================  ==================================================

Location is chosen with ``city=`` (a built-in name) or ``lat=`` + ``lon=``
(optionally ``tz=``).  All endpoints accept ``ayanamsa=``; the festival and
find endpoints accept ``tradition=`` and ``major_only=``.

Configuration is read from the environment (see ``kalagana.config`` and
``.env.example``); ``KALAGANA_HOST`` / ``KALAGANA_PORT`` set the defaults and
``KALAGANA_CITY`` / ``KALAGANA_LAT`` / ``KALAGANA_LON`` provide a fallback
location when a request omits one.

The server performs no network I/O of its own; it is a thin JSON wrapper over
the pure calculation core, so it stays usable in fully offline environments.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from . import __version__
from .api import daily_panchang, eclipses_for_year
from .ayanamsa import SUPPORTED as AYANAMSAS
from .config import Settings, load_settings
from .festivals import FestivalOccurrence, festivals_for_year, find_next
from .location import CITIES, Location, city_lookup
from .muhurta import day_timings

__all__ = ["KalaganaAPI", "create_server", "main", "DEFAULT_HOST", "DEFAULT_PORT"]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


class ApiError(Exception):
    """An error that maps to an HTTP status code and JSON message."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def _require(params: Dict[str, str], key: str) -> str:
    val = params.get(key)
    if not val:
        raise ApiError(400, f"Missing required parameter: {key}")
    return val


def _bool(params: Dict[str, str], key: str, default: bool = False) -> bool:
    val = params.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ApiError(400, f"Invalid date {value!r}; expected YYYY-MM-DD") from exc


def _occ(o: FestivalOccurrence) -> Dict[str, Any]:
    return {
        "name": o.name,
        "date": o.date.isoformat(),
        "month": o.month,
        "paksha": o.paksha,
        "tithi": o.tithi,
        "note": o.note,
        "kind": o.kind,
    }


class KalaganaAPI:
    """Holds the request handlers; kept separate from the HTTP transport."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or load_settings()
        self.routes: Dict[str, Callable[[Dict[str, str]], Dict[str, Any]]] = {
            "/health": self.health,
            "/cities": self.cities,
            "/ayanamsas": self.ayanamsas,
            "/day": self.day,
            "/month": self.month,
            "/festivals": self.festivals,
            "/eclipses": self.eclipses,
            "/muhurta": self.muhurta,
            "/find": self.find,
        }

    # --- helpers ----------------------------------------------------------
    def _location(self, params: Dict[str, str]) -> Location:
        """Resolve a location from the query, falling back to configured defaults."""
        lat, lon, tz = params.get("lat"), params.get("lon"), params.get("tz")
        city = params.get("city")
        tz = tz or self.settings.tz

        if lat is not None and lon is not None:
            try:
                return Location(city or "Custom", float(lat), float(lon), tz)
            except ValueError as exc:
                raise ApiError(400, f"Invalid lat/lon: {exc}") from exc

        if city:
            try:
                loc = city_lookup(city)
            except KeyError as exc:
                raise ApiError(400, str(exc)) from exc
            if params.get("tz"):
                loc = Location(loc.name, loc.lat, loc.lon, tz)
            return loc

        # Fall back to configured defaults.
        if self.settings.lat is not None and self.settings.lon is not None:
            return Location("Default", self.settings.lat, self.settings.lon, tz)
        if self.settings.city:
            try:
                loc = city_lookup(self.settings.city)
            except KeyError:
                loc = None
            if loc is not None:
                return Location(loc.name, loc.lat, loc.lon, tz) if params.get("tz") else loc

        raise ApiError(400, "Provide 'city', or both 'lat' and 'lon'.")

    def _ayanamsa(self, params: Dict[str, str]) -> str:
        return params.get("ayanamsa") or self.settings.ayanamsa

    def _tradition(self, params: Dict[str, str]) -> str:
        return params.get("tradition") or self.settings.tradition

    # --- meta -------------------------------------------------------------
    def health(self, _p: Dict[str, str]) -> Dict[str, Any]:
        return {"status": "ok", "name": "kalagana", "version": __version__}

    def cities(self, _p: Dict[str, str]) -> Dict[str, Any]:
        return {
            "count": len(CITIES),
            "cities": [
                {"key": k, "name": v.name, "lat": v.lat, "lon": v.lon, "tz": v.tz}
                for k, v in sorted(CITIES.items())
            ],
        }

    def ayanamsas(self, _p: Dict[str, str]) -> Dict[str, Any]:
        return {"default": self.settings.ayanamsa, "ayanamsas": list(AYANAMSAS)}

    # --- panchang ---------------------------------------------------------
    def day(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        d = _parse_date(_require(p, "date"))
        pan = daily_panchang(
            d,
            loc,
            ayanamsa=self._ayanamsa(p),
            month_system=p.get("month_system", self.settings.month_system),
            with_muhurta=not _bool(p, "no_muhurta"),
        )
        return pan.to_dict()

    def month(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        raw = _require(p, "month")
        try:
            year, mon = (int(x) for x in raw.split("-"))
        except ValueError as exc:
            raise ApiError(400, f"Invalid month {raw!r}; expected YYYY-MM") from exc
        d = date(year, mon, 1)
        days = []
        while d.month == mon:
            pan = daily_panchang(d, loc, ayanamsa=self._ayanamsa(p), with_muhurta=False)
            days.append(
                {
                    "date": d.isoformat(),
                    "vara": pan.vara,
                    "vara_en": pan.vara_en,
                    "paksha": pan.paksha,
                    "tithi": pan.tithi[0].name if pan.tithi else None,
                    "nakshatra": pan.nakshatra[0].name if pan.nakshatra else None,
                    "sunrise": pan.sunrise.isoformat() if pan.sunrise else None,
                    "sunset": pan.sunset.isoformat() if pan.sunset else None,
                }
            )
            d += timedelta(days=1)
        return {"month": raw, "count": len(days), "days": days}

    def festivals(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        year = int(_require(p, "year"))
        if _bool(p, "major_only"):
            include_monthly = False
        else:
            include_monthly = self.settings.include_monthly
        kinds = None
        if p.get("kind"):
            kinds = tuple(k.strip() for k in p["kind"].split(",") if k.strip())
        occs = festivals_for_year(
            year,
            loc,
            tradition=self._tradition(p),
            ayanamsa=self._ayanamsa(p),
            include_monthly=include_monthly,
            include_islamic=self.settings.include_islamic and not _bool(p, "no_islamic"),
            include_fixed=self.settings.include_fixed and not _bool(p, "no_fixed"),
            kinds=kinds,
        )
        return {"year": year, "count": len(occs), "festivals": [_occ(o) for o in occs]}

    def eclipses(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        year = int(_require(p, "year"))
        ecl = eclipses_for_year(year, loc)
        return {
            "year": year,
            "note": "Approximate detector; dates and rough type only.",
            "count": len(ecl),
            "eclipses": [
                {
                    "kind": e.kind,
                    "date": e.date.isoformat(),
                    "greatest": e.greatest.isoformat(),
                    "type": e.eclipse_type,
                    "moon_latitude": e.moon_latitude,
                }
                for e in ecl
            ],
        }

    def muhurta(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        d = _parse_date(_require(p, "date"))
        windows = day_timings(d, loc)
        from .api import _muhurta_dict

        return {"date": d.isoformat(), "muhurta": _muhurta_dict(windows)}

    def find(self, p: Dict[str, str]) -> Dict[str, Any]:
        loc = self._location(p)
        name = _require(p, "name")
        after = _parse_date(p["after"]) if p.get("after") else date.today()
        occ = find_next(
            name,
            after,
            loc,
            tradition=self._tradition(p),
            ayanamsa=self._ayanamsa(p),
            max_years=self.settings.find_years,
        )
        if occ is None:
            raise ApiError(404, f"No occurrence of {name!r} found")
        return _occ(occ)


class _Handler(BaseHTTPRequestHandler):
    server_version = f"Kalagana/{__version__}"
    api_instance: KalaganaAPI

    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 (http.server API)
        self._send(204, {})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        handler = self.api_instance.routes.get(path)
        if handler is None:
            self._send(404, {"error": "not_found", "message": f"Unknown path {path!r}",
                             "endpoints": sorted(self.api_instance.routes)})
            return
        try:
            self._send(200, handler(params))
        except ApiError as exc:
            self._send(exc.status, {"error": "bad_request", "message": exc.message})
        except Exception as exc:  # noqa: BLE001 - return a clean JSON error
            self._send(500, {"error": "internal_error", "message": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        if getattr(self.api_instance.settings, "log_requests", True):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def create_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> Tuple[ThreadingHTTPServer, KalaganaAPI]:
    """Create (but do not start) a Kalagana HTTP server.

    ``host``/``port`` default to ``KALAGANA_HOST``/``KALAGANA_PORT`` (or the
    built-in defaults) through :class:`~kalagana.config.Settings`.
    """
    api = KalaganaAPI(settings)
    handler = type("_BoundHandler", (_Handler,), {"api_instance": api})
    httpd = ThreadingHTTPServer((host or api.settings.host, port or api.settings.port), handler)
    return httpd, api


def main(argv: Optional[list] = None) -> int:
    settings = load_settings()
    parser = argparse.ArgumentParser(
        prog="kalagana-server", description="Serve the Kalagana REST API (offline, stdlib only)"
    )
    parser.add_argument("--host", default=settings.host, help=f"bind address (default {settings.host})")
    parser.add_argument("--port", type=int, default=settings.port, help=f"port (default {settings.port})")
    args = parser.parse_args(argv)

    httpd, api = create_server(args.host, args.port, settings)
    host, port = httpd.server_address[0], httpd.server_address[1]
    print(f"Kalagana API v{__version__} listening on http://{host}:{port}", file=sys.stderr)
    print("Endpoints:", " ".join(sorted(api.routes)), file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down", file=sys.stderr)
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
