"""Command line interface: ``python -m kalagana`` / ``kalagana``.

Subcommands
-----------
``day``        full panchang for one date
``month``      day-by-day summary for a Gregorian month
``festivals``  festivals for a year
``eclipses``   approximate eclipses for a year
``muhurta``    daily muhurta windows
``find``       next occurrence of a named festival
``cities``     list the built-in city table
``serve``      run the local REST API server
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional

from .api import daily_panchang, eclipses_for_year
from .festivals import find_next, festivals_for_year
from .location import CITIES, Location, city_lookup

__all__ = ["main", "build_parser"]


@lru_cache(maxsize=1)
def _settings():
    """Environment/.env settings, loaded once per process."""
    from .config import load_settings

    return load_settings()


def _resolve_location(args: argparse.Namespace) -> Location:
    st = _settings()
    tz = args.tz or st.tz
    if args.lat is not None and args.lon is not None:
        return Location(
            name=args.city or "Custom",
            lat=args.lat,
            lon=args.lon,
            tz=tz,
        )
    if args.city:
        try:
            loc = city_lookup(args.city)
        except KeyError as exc:
            raise SystemExit(str(exc))
        if args.tz:
            loc = Location(loc.name, loc.lat, loc.lon, args.tz)
        return loc
    # Fall back to configured defaults (KALAGANA_LAT/LON or KALAGANA_CITY).
    if st.lat is not None and st.lon is not None:
        return Location("Default", st.lat, st.lon, tz)
    if st.city:
        try:
            loc = city_lookup(st.city)
        except KeyError:
            pass
        else:
            if args.tz:
                loc = Location(loc.name, loc.lat, loc.lon, args.tz)
            return loc
    raise SystemExit("Provide --city NAME or both --lat and --lon.")


def _add_location_opts(p: argparse.ArgumentParser) -> None:
    st = _settings()
    p.add_argument("--city", help="built-in city name (e.g. delhi, mumbai)")
    p.add_argument("--lat", type=float, help="latitude in degrees (north +)")
    p.add_argument("--lon", type=float, help="longitude in degrees (east +)")
    p.add_argument("--tz", help=f"IANA timezone (default {st.tz})")
    p.add_argument(
        "--tradition",
        default=st.tradition,
        help="north|south|tamil|telugu|kannada|malayalam|bengali|odia|gujarati|marathi",
    )
    p.add_argument("--ayanamsa", default=st.ayanamsa, help="lahiri|raman|kp|yukteshwar|fagan_bradley")
    p.add_argument("--format", default="text", choices=["text", "json", "csv"])
    p.add_argument("--lang", default=st.lang, help="name language (en for now)")


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def _cmd_day(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    d = date.fromisoformat(args.date)
    p = daily_panchang(d, loc, ayanamsa=args.ayanamsa, month_system=args.month_system)
    if args.format == "json":
        _print_json(p.to_dict())
        return 0
    print(f"Panchang for {p.date.isoformat()}  ({p.vara_en} / {p.vara})")
    print(f"Place: {loc.name}  ({loc.lat:.4f}, {loc.lon:.4f})  {loc.tz}")
    print(f"Vikram Samvat {p.samvat}   Shaka {p.shaka}   {p.samvatsara}   "
          f"{p.masa_purnimanta} ({p.masa_amanta} amanta)  {p.paksha}")
    print(f"Ritu: {p.ritu}   Ayana: {p.ayana}")
    print(f"Sunrise: {_t(p.sunrise)}   Sunset: {_t(p.sunset)}")
    print(f"Moonrise: {_t(p.moonrise)}   Moonset: {_t(p.moonset)}")
    for label, segs in (("Tithi", p.tithi), ("Nakshatra", p.nakshatra),
                        ("Yoga", p.yoga), ("Karana", p.karana)):
        print(f"{label}:")
        for s in segs:
            print(f"  {s.name:<28} {_t(s.start)} -> {_t(s.end)}")
    if p.muhurta:
        print("Muhurta:")
        for key in ("rahu_kalam", "yamaganda", "gulika_kalam", "abhijit", "brahma_muhurta"):
            w = p.muhurta.get(key)
            if w is not None:
                print(f"  {w.name:<16} {_t(w.start)} -> {_t(w.end)}")
        for w in p.muhurta.get("durmuhurta", []):
            print(f"  {'Durmuhurta':<16} {_t(w.start)} -> {_t(w.end)}")
    return 0


def _t(dt) -> str:
    return dt.strftime("%H:%M:%S") if dt else "--:--"


def _cmd_month(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    year, month = (int(x) for x in args.month.split("-")) if "-" in args.month else (None, None)
    if year is None:
        year, month = date.today().year, int(args.month)
    d = date(year, month, 1)
    rows: List[str] = []
    while d.month == month:
        p = daily_panchang(d, loc, ayanamsa=args.ayanamsa, with_muhurta=False)
        tithi = p.tithi[0].name if p.tithi else ""
        nak = p.nakshatra[0].name if p.nakshatra else ""
        rows.append(f"{d.isoformat()}  {p.vara_en[:3]}  {tithi:<24} {nak:<16} "
                    f"SR {_t(p.sunrise)} SS {_t(p.sunset)}")
        d += timedelta(days=1)
    print("\n".join(rows))
    return 0


def _cmd_festivals(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    kinds = None
    if args.kind:
        kinds = tuple(k.strip() for k in args.kind.split(",") if k.strip())
    st = _settings()
    occs = festivals_for_year(
        args.year, loc, tradition=args.tradition, ayanamsa=args.ayanamsa,
        include_monthly=not args.major_only, kinds=kinds,
        include_islamic=st.include_islamic and not args.no_islamic,
        include_fixed=st.include_fixed and not args.no_fixed,
    )
    if args.format == "json":
        _print_json([
            {"name": o.name, "date": o.date.isoformat(), "month": o.month,
             "paksha": o.paksha, "tithi": o.tithi, "note": o.note, "kind": o.kind}
            for o in occs
        ])
    elif args.format == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["date", "name", "kind", "month", "paksha", "tithi"])
        for o in occs:
            w.writerow([o.date.isoformat(), o.name, o.kind, o.month or "",
                        o.paksha or "", o.tithi or ""])
        sys.stdout.write(buf.getvalue())
    else:
        for o in occs:
            print(str(o))
    return 0


def _cmd_eclipses(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    ecl = eclipses_for_year(args.year, loc)
    if args.format == "json":
        _print_json([
            {"kind": e.kind, "date": e.date.isoformat(), "greatest": e.greatest.isoformat(),
             "type": e.eclipse_type, "moon_latitude": e.moon_latitude}
            for e in ecl
        ])
    else:
        for e in ecl:
            print(str(e))
    return 0


def _cmd_muhurta(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    d = date.fromisoformat(args.date)
    p = daily_panchang(d, loc, ayanamsa=args.ayanamsa, with_muhurta=True)
    if args.format == "json":
        _print_json(p.to_dict()["muhurta"])
        return 0
    print(f"Muhurta for {d.isoformat()} ({loc.name})")
    for key in ("rahu_kalam", "yamaganda", "gulika_kalam", "abhijit", "brahma_muhurta"):
        w = p.muhurta.get(key)
        if w:
            print(f"  {w.name:<16} {_t(w.start)} -> {_t(w.end)}")
    for w in p.muhurta.get("durmuhurta", []):
        print(f"  {'Durmuhurta':<16} {_t(w.start)} -> {_t(w.end)}")
    chog = p.muhurta.get("choghadiya", {})
    print("  Day Choghadiya:")
    for w in chog.get("day", []):
        print(f"    {w.name:<8} {_t(w.start)} -> {_t(w.end)}")
    print("  Night Choghadiya:")
    for w in chog.get("night", []):
        print(f"    {w.name:<8} {_t(w.start)} -> {_t(w.end)}")
    return 0


def _cmd_find(args: argparse.Namespace) -> int:
    loc = _resolve_location(args)
    after = date.fromisoformat(args.date) if args.date else date.today()
    occ = find_next(args.name, after, loc, tradition=args.tradition, ayanamsa=args.ayanamsa)
    if occ is None:
        print(f"No occurrence of {args.name!r} found.")
        return 1
    print(str(occ))
    return 0


def _parse_dt(date_str: str, time_str: Optional[str]) -> datetime:
    """Build a naive local datetime from a date and optional HH:MM time."""
    d = date.fromisoformat(date_str)
    if not time_str:
        return datetime(d.year, d.month, d.day, 12, 0)
    hh, mm = (time_str.split(":") + ["0"])[:2]
    return datetime(d.year, d.month, d.day, int(hh), int(mm))


def _loc_from(city, lat, lon, tz):
    """Resolve a Location from explicit values, falling back to defaults."""
    st = _settings()
    if lat is not None and lon is not None:
        return Location(city or "Custom", lat, lon, tz or st.tz)
    if city:
        loc = city_lookup(city)
        if tz:
            return Location(loc.name, loc.lat, loc.lon, tz)
        return loc
    if st.city:
        try:
            return city_lookup(st.city)
        except KeyError:
            pass
    raise SystemExit("Provide a city or both lat and lon.")


def _cmd_kundali(args: argparse.Namespace) -> int:
    from .jyotish import kundali

    loc = _resolve_location(args)
    when = _parse_dt(args.date, args.time)
    k = kundali(when, loc, ayanamsa=args.ayanamsa, dasha_depth=args.dasha_depth)
    if args.format == "json":
        _print_json(k.to_dict())
        return 0
    print(f"Kundali for {when.isoformat()}  ({loc.name}, {loc.tz})  ayanamsa={args.ayanamsa}")
    print(f"Lagna: {k.ascendant.rashi_name} {k.ascendant.degree_in_rashi:.2f} deg"
          f"   Midheaven: {k.ascendant.midheaven:.2f} deg")
    print(f"{'Graha':<8} {'Rashi':<11} {'Deg':>6}  {'Nakshatra':<16} {'Pd':>2} {'H':>2}  Flags  Dignity")
    for name, p in k.grahas.items():
        flags = ("R" if p.retrograde else " ") + ("C" if p.combust else " ")
        print(f"{name:<8} {p.rashi_name:<11} {p.degree_in_rashi:6.2f}  {p.nakshatra_name:<16} "
              f"{p.pada:>2} {p.house:>2}  {flags}    {p.dignity}")
    av = k.avakhada
    print(f"Avakhada: rashi={av['rashi']} ({av['rashi_lord']}) nakshatra={av['nakshatra']} "
          f"pada={av['pada']} gana={av['gana']} yoni={av['yoni']} nadi={av['nadi']} "
          f"varna={av['varna']} vashya={av['vashya']}")
    print("Vimshottari dasha (mahadasha):")
    for d in k.dasha:
        info = d.to_dict(with_sub=False)
        print(f"  {d.lord:<8} {info['start'][:10]}  ->  {info['end'][:10]}")
    return 0


def _cmd_match(args: argparse.Namespace) -> int:
    from .jyotish import kundali, kundali_match

    boy_loc = _loc_from(args.boy_city, args.boy_lat, args.boy_lon, args.boy_tz)
    girl_loc = _loc_from(args.girl_city, args.girl_lat, args.girl_lon, args.girl_tz)
    boy = kundali(_parse_dt(args.boy_date, args.boy_time), boy_loc,
                  ayanamsa=args.ayanamsa, with_dasha=False)
    girl = kundali(_parse_dt(args.girl_date, args.girl_time), girl_loc,
                   ayanamsa=args.ayanamsa, with_dasha=False)
    result = kundali_match(boy, girl)
    if args.format == "json":
        _print_json(result)
        return 0
    ak = result["ashtakoota"]
    print(f"Ashtakoota (Guna Milana): {ak['total']} / {ak['maximum']}  -- {ak['verdict']}")
    for kk in ak["kootas"]:
        print(f"  {kk['name']:<13} {kk['score']:>4} / {kk['max']:<3}  {kk['detail']}")
    print(f"Boy:  Moon {result['boy']['moon_rashi']}, {result['boy']['moon_nakshatra']}, "
          f"Lagna {result['boy']['lagna']}, Mangal dosha={result['boy']['mangal_dosha']['present']}")
    print(f"Girl: Moon {result['girl']['moon_rashi']}, {result['girl']['moon_nakshatra']}, "
          f"Lagna {result['girl']['lagna']}, Mangal dosha={result['girl']['mangal_dosha']['present']}")
    return 0


def _cmd_rashifal(args: argparse.Namespace) -> int:
    from .jyotish import daily_rashifal, rashifal_for_all

    when = date.fromisoformat(args.date) if args.date else None
    if args.rashi:
        results = [daily_rashifal(args.rashi, when, args.ayanamsa, period=args.period)]
    else:
        results = rashifal_for_all(when, args.ayanamsa, period=args.period)
    if args.format == "json":
        payload = [r.to_dict() for r in results]
        _print_json(payload[0] if args.rashi else payload)
        return 0
    for r in results:
        print(f"{r.rashi_name} ({r.rashi_name_en}) -- {r.band}")
        print(f"  {r.headline}")
        print(f"  {r.summary}")
        if args.verbose and r.transits:
            for t in r.transits:
                print(f"    {t.graha:<8} in {t.rashi_name:<11} (H{t.house:<2}) {t.verdict}")
        if args.rashi:
            print(f"  {r.disclaimer}")
        print()
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    from .server import main as serve_main

    return serve_main(["--host", args.host, "--port", str(args.port)])


def _cmd_cities(args: argparse.Namespace) -> int:
    for key in sorted(CITIES):
        loc = CITIES[key]
        print(f"{key:<20} {loc.lat:>8.4f} {loc.lon:>9.4f}  {loc.tz}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kalagana", description="Kalagana -- offline Drik panchang & festival calculator"
    )
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("day", help="full panchang for one date")
    d.add_argument("date", help="YYYY-MM-DD")
    d.add_argument("--month-system", default="purnimanta", choices=["amanta", "purnimanta"])
    _add_location_opts(d)
    d.set_defaults(func=_cmd_day)

    m = sub.add_parser("month", help="day-by-day for a month (YYYY-MM or MM)")
    m.add_argument("month")
    _add_location_opts(m)
    m.set_defaults(func=_cmd_month)

    f = sub.add_parser("festivals", help="festivals for a year")
    f.add_argument("year", type=int)
    f.add_argument("--major-only", action="store_true", help="skip monthly observances")
    f.add_argument(
        "--kind",
        help="filter by kind (comma-separated): festival|national|observance",
    )
    f.add_argument("--no-islamic", action="store_true", help="exclude Islamic (Hijri) festivals")
    f.add_argument(
        "--no-fixed",
        action="store_true",
        help="exclude fixed-date national/observance days",
    )
    _add_location_opts(f)
    f.set_defaults(func=_cmd_festivals)

    e = sub.add_parser("eclipses", help="approximate eclipses for a year")
    e.add_argument("year", type=int)
    _add_location_opts(e)
    e.set_defaults(func=_cmd_eclipses)

    mm = sub.add_parser("muhurta", help="daily muhurta windows")
    mm.add_argument("date", help="YYYY-MM-DD")
    _add_location_opts(mm)
    mm.set_defaults(func=_cmd_muhurta)

    fi = sub.add_parser("find", help="next date of a named festival")
    fi.add_argument("name")
    fi.add_argument("--date", help="search on/after this date (default today)")
    _add_location_opts(fi)
    fi.set_defaults(func=_cmd_find)

    c = sub.add_parser("cities", help="list built-in cities")
    c.set_defaults(func=_cmd_cities)

    k = sub.add_parser("kundali", help="birth chart (kundali) for a date, time and place")
    k.add_argument("--date", required=True, help="birth date YYYY-MM-DD")
    k.add_argument("--time", help="birth time HH:MM (default 12:00)")
    k.add_argument("--dasha-depth", type=int, default=2, choices=[1, 2, 3],
                   help="1=mahadasha, 2=+antardasha, 3=+pratyantardasha")
    _add_location_opts(k)
    k.set_defaults(func=_cmd_kundali)

    mt = sub.add_parser("match", help="kundali matching (Guna Milana) for two people")
    mt.add_argument("--boy-date", required=True)
    mt.add_argument("--boy-time")
    mt.add_argument("--boy-city")
    mt.add_argument("--boy-lat", type=float)
    mt.add_argument("--boy-lon", type=float)
    mt.add_argument("--boy-tz")
    mt.add_argument("--girl-date", required=True)
    mt.add_argument("--girl-time")
    mt.add_argument("--girl-city")
    mt.add_argument("--girl-lat", type=float)
    mt.add_argument("--girl-lon", type=float)
    mt.add_argument("--girl-tz")
    mt.add_argument("--ayanamsa", default=_settings().ayanamsa)
    mt.add_argument("--format", default="text", choices=["text", "json"])
    mt.set_defaults(func=_cmd_match)

    rf = sub.add_parser("rashifal", help="transit-based daily rashifal for the 12 rashis")
    rf.add_argument("--rashi", help="one rashi by name (Mesha/Aries); default all 12")
    rf.add_argument("--date", help="date YYYY-MM-DD (default today)")
    rf.add_argument("--period", default="daily", help="label: daily|monthly|yearly")
    rf.add_argument("--ayanamsa", default=_settings().ayanamsa)
    rf.add_argument("--format", default="text", choices=["text", "json"])
    rf.add_argument("-v", "--verbose", action="store_true", help="show each transit")
    rf.set_defaults(func=_cmd_rashifal)

    srv = sub.add_parser("serve", help="run the local REST API server (offline)")
    srv.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    srv.add_argument("--port", type=int, default=8765, help="port (default 8765)")
    srv.set_defaults(func=_cmd_serve)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
