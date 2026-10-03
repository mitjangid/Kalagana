"""Observer location and a small built-in city table (no lookup service)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, timezone, tzinfo
from typing import Dict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = ["Location", "CITIES", "city_lookup", "resolve_tzinfo"]

# Fixed UTC offsets used only when the IANA tz database is unavailable.
# On Windows the stdlib ``zoneinfo`` needs the ``tzdata`` package; without it
# we fall back to these standard (non-DST) offsets.  India has no DST, so the
# panchang's primary domain is exact; overseas DST periods are approximate.
_FALLBACK_OFFSETS: Dict[str, float] = {
    "UTC": 0.0,
    "Asia/Kolkata": 5.5,
    "Asia/Calcutta": 5.5,
    "Asia/Kathmandu": 5.75,
    "Asia/Dubai": 4.0,
    "Asia/Singapore": 8.0,
    "Asia/Colombo": 5.5,
    "Asia/Dhaka": 6.0,
    "Europe/London": 0.0,
    "America/New_York": -5.0,
    "America/Toronto": -5.0,
    "Australia/Sydney": 10.0,
}


def resolve_tzinfo(name: str) -> tzinfo:
    """Resolve an IANA timezone name, falling back to a fixed offset.

    Uses :mod:`zoneinfo` when the tz database is present (Linux/macOS, or
    Windows with the ``tzdata`` package).  Otherwise a built-in standard
    offset is used; see :data:`_FALLBACK_OFFSETS` for the DST caveat.
    """
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, KeyError):
        pass
    if name in _FALLBACK_OFFSETS:
        return timezone(timedelta(hours=_FALLBACK_OFFSETS[name]), name)
    raise ZoneInfoNotFoundError(
        f"No timezone data for {name!r}. Install the 'tzdata' package or use a "
        f"built-in zone such as: {', '.join(sorted(_FALLBACK_OFFSETS))}."
    )


@dataclass(frozen=True)
class Location:
    """An observing place.

    ``lat`` is geodetic latitude in *degrees* (north positive), ``lon`` is
    longitude in *degrees* (**east positive**), and ``tz`` is an IANA timezone
    name resolved with :mod:`zoneinfo` (e.g. ``"Asia/Kolkata"``).
    """

    name: str
    lat: float
    lon: float
    tz: str = "Asia/Kolkata"

    @property
    def zoneinfo(self) -> tzinfo:
        return resolve_tzinfo(self.tz)


# A compact built-in list of Indian cities plus a few overseas centres.
# Coordinates are approximate city centres; elevations are ignored.
CITIES: Dict[str, Location] = {
    "delhi": Location("Delhi", 28.6139, 77.2090),
    "new delhi": Location("New Delhi", 28.6139, 77.2090),
    "mumbai": Location("Mumbai", 19.0760, 72.8777),
    "kolkata": Location("Kolkata", 22.5726, 88.3639),
    "chennai": Location("Chennai", 13.0827, 80.2707),
    "bengaluru": Location("Bengaluru", 12.9716, 77.5946),
    "bangalore": Location("Bengaluru", 12.9716, 77.5946),
    "hyderabad": Location("Hyderabad", 17.3850, 78.4867),
    "pune": Location("Pune", 18.5204, 73.8567),
    "ahmedabad": Location("Ahmedabad", 23.0225, 72.5714),
    "jaipur": Location("Jaipur", 26.9124, 75.7873),
    "lucknow": Location("Lucknow", 26.8467, 80.9462),
    "kanpur": Location("Kanpur", 26.4499, 80.3319),
    "ujjain": Location("Ujjain", 23.1765, 75.7885),
    "varanasi": Location("Varanasi", 25.3176, 82.9739),
    "bikaner": Location("Bikaner", 28.0229, 73.3119),
    "kota": Location("Kota", 25.2138, 75.8648),
    "patna": Location("Patna", 25.5941, 85.1376),
    "bhopal": Location("Bhopal", 23.2599, 77.4126),
    "thiruvananthapuram": Location("Thiruvananthapuram", 8.5241, 76.9366),
    "kochi": Location("Kochi", 9.9312, 76.2673),
    "guwahati": Location("Guwahati", 26.1445, 91.7362),
    "bhubaneswar": Location("Bhubaneswar", 20.2961, 85.8245),
    "amritsar": Location("Amritsar", 31.6340, 74.8723),
    "srinagar": Location("Srinagar", 34.0837, 74.7973),
    "noida": Location("Noida", 28.5355, 77.3910),
    "gurugram": Location("Gurugram", 28.4595, 77.0266),
    # Overseas reference points (useful for accuracy tests).
    "london": Location("London", 51.5074, -0.1278, "Europe/London"),
    "new york": Location("New York", 40.7128, -74.0060, "America/New_York"),
    "dubai": Location("Dubai", 25.2048, 55.2708, "Asia/Dubai"),
    "singapore": Location("Singapore", 1.3521, 103.8198, "Asia/Singapore"),
    "sydney": Location("Sydney", -33.8688, 151.2093, "Australia/Sydney"),
    "toronto": Location("Toronto", 43.6532, -79.3832, "America/Toronto"),
    "kathmandu": Location("Kathmandu", 27.7172, 85.3240, "Asia/Kathmandu"),
}


def city_lookup(name: str) -> Location:
    """Look up a built-in city by (case-insensitive) name."""
    key = name.strip().lower()
    if key in CITIES:
        return CITIES[key]
    raise KeyError(f"Unknown city {name!r}; try one of: {', '.join(sorted(CITIES))}")
