"""Self-test runnable without pytest: ``python -m kalagana.selftest``.

Runs the astronomy and calendar checks and prints an accuracy table.  Exit
code is non-zero if any check fails.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from typing import Callable, List, Tuple

from . import julian, moon, sun
from .limbs import elongation
from .location import Location
from .solver import next_crossing
from .sunrise import sunrise_sunset

_Results = List[Tuple[str, int, float, str]]  # check, n, max_error, unit


def _check_meeus_positions() -> Tuple[str, int, float, str]:
    # Meeus, Astronomical Algorithms, worked examples.
    jd = julian.gregorian_to_jd(1992, 4, 12.0)
    lon, lat, dist = moon.moon_position(jd)
    err = max(abs(lon - 133.162655), abs(lat - (-3.229126)), abs((dist - 368409.7) / 1e5))
    jd2 = julian.gregorian_to_jd(1992, 10, 13.0)
    sun_err = abs(sun.sun_apparent_longitude(jd2) - 199.90895)
    return ("Meeus Sun/Moon examples", 2, max(err, sun_err), "deg")


def _check_new_moons() -> Tuple[str, int, float, str]:
    expected = [
        (2000, 1, 6, 18, 14), (2000, 2, 5, 13, 3), (2000, 3, 6, 5, 17),
        (2000, 4, 4, 18, 12), (2000, 5, 4, 4, 12), (2000, 6, 2, 12, 14),
        (2000, 7, 1, 19, 20), (2000, 7, 31, 2, 25), (2000, 8, 29, 10, 19),
        (2000, 9, 27, 19, 53), (2000, 10, 27, 7, 58), (2000, 11, 25, 23, 11),
        (2000, 12, 25, 17, 22),
    ]
    jd = julian.datetime_to_jd(datetime(2000, 1, 1, tzinfo=timezone.utc))
    worst = 0.0
    for (y, mo, d, h, mi) in expected:
        r = next_crossing(elongation, 0.0, jd, max_days=40.0)
        assert r is not None
        got = julian.jd_to_datetime(r)
        exp = datetime(y, mo, d, h, mi, tzinfo=timezone.utc)
        worst = max(worst, abs((got - exp).total_seconds()))
        jd = r + 1.0
    return ("New moon instants (2000)", len(expected), worst, "s")


def _check_sunrise() -> Tuple[str, int, float, str]:
    loc = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")
    # Published Drik Panchang values for New Delhi (IST).
    expected = {
        date(2024, 3, 20): ("06:24", "18:32"),
        date(2024, 6, 21): ("05:24", "19:22"),
        date(2024, 12, 21): ("07:09", "17:28"),
    }
    worst = 0.0
    n = 0
    for d, (rs, ss) in expected.items():
        r, s = sunrise_sunset(d, loc)
        assert r and s
        for got, want in ((r, rs), (s, ss)):
            hh, mm = (int(x) for x in want.split(":"))
            target = got.replace(hour=hh, minute=mm, second=0, microsecond=0)
            worst = max(worst, abs((got - target).total_seconds()))
            n += 1
    return ("Sunrise/sunset vs Drik (Delhi)", n, worst, "s")


def _check_festivals() -> Tuple[str, int, float, str]:
    from .festivals import festivals_for_year

    loc = Location("Delhi", 28.6139, 77.2090, "Asia/Kolkata")
    # A handful of well-known 2024 dates (Drik Panchang, New Delhi).
    known = {
        "Makar Sankranti": date(2024, 1, 14),
        "Maha Shivaratri": date(2024, 3, 8),
        "Holi": date(2024, 3, 25),
        "Rama Navami": date(2024, 4, 17),
        "Raksha Bandhan": date(2024, 8, 19),
        "Krishna Janmashtami": date(2024, 8, 26),
        "Ganesh Chaturthi": date(2024, 9, 7),
        "Dussehra": date(2024, 10, 13),
        "Diwali": date(2024, 10, 31),
    }
    occs = festivals_for_year(2024, loc, tradition="north", include_monthly=False)
    by_name = {}
    for o in occs:
        by_name.setdefault(o.name, o.date)
    worst = 0.0
    n = 0
    for name, want in known.items():
        got = by_name.get(name)
        assert got is not None, f"{name} not found"
        worst = max(worst, abs((got - want).days))
        n += 1
    return ("Festival dates vs Drik (Delhi 2024)", n, worst, "days")


def run() -> int:
    checks: List[Callable[[], Tuple[str, int, float, str]]] = [
        _check_meeus_positions,
        _check_new_moons,
        _check_sunrise,
        _check_festivals,
    ]
    print("kalagana self-test")
    print("-" * 68)
    print(f"{'check':<38}{'n':>4}{'max err':>14}  unit")
    failed = 0
    for fn in checks:
        label, n, worst, unit = fn()
        tol = {"deg": 0.01, "s": 300.0, "days": 1.0}[unit]
        ok = worst <= tol
        if not ok:
            failed += 1
        flag = "ok" if ok else "FAIL"
        print(f"{label:<38}{n:>4}{worst:>14.2f}  {unit}  [{flag}]")
    print("-" * 68)
    if failed:
        print(f"{failed} check(s) beyond tolerance")
    else:
        print("all checks within tolerance")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
