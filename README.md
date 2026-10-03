<div align="center">

<img src="https://raw.githubusercontent.com/mitjangid/Kalagana/master/assets/logo.png" alt="Kalagana logo" width="160" />

# 🕉️ Kalagana

**An offline, dependency-free Hindu (Drik) Panchang & festival calculator written in pure Python.**

*Tithi, Vara, Nakshatra, Yoga, Karana, sunrise/sunset, ayanamsa and more — computed from first principles, with no internet, no database and no downloaded ephemeris files.*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#-requirements)
[![Offline](https://img.shields.io/badge/network-100%25%20offline-success.svg)](#-why-this-exists)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)](#-roadmap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<br/>

[![GitHub stars](https://img.shields.io/github/stars/mitjangid/Kalagana?style=social)](https://github.com/mitjangid/Kalagana/stargazers)
[![GitHub followers](https://img.shields.io/github/followers/mitjangid?style=social)](https://github.com/mitjangid?tab=followers)

</div>

---

## 📖 What is this?

**Kalagana** is a Python library and command-line tool that computes a complete **Drik Panchang** — the five traditional limbs of the Hindu calendar — together with (eventually) the dates of Hindu festivals, for **any latitude, longitude and timezone**, in both **North (purnimanta)** and **South (amanta)** traditions.

Everything is derived from **positional astronomy implemented in the code itself**, using the algorithms from Jean Meeus' *Astronomical Algorithms*. There are:

- ❌ no network calls
- ❌ no database
- ❌ no downloaded ephemeris files
- ❌ no third-party packages
- ✅ just the Python standard library

The same inputs always produce the same outputs — the calculation core is **pure and deterministic**.

> **New in this version:** a rule-driven **festival engine** for Hindu (lunar/solar), **Islamic (Hijri)** and **fixed-date national/observance** days — 80+ festival rules plus monthly vrats — with per-group on/off switches and a `kind` filter (`festival` / `national` / `observance`).

## ✨ Highlights

- 🌗 **Full five limbs** — Tithi (with paksha), Vara, Nakshatra (with pada), Yoga and Karana, each with exact **start and end times**.
- 🎉 **Festivals from rules, never stored** — Hindu (lunar + solar sankranti), Islamic (Hijri), national holidays and fixed-date observances, plus monthly vrats.
- ☀️ **Rise & set** — sunrise, sunset, moonrise, moonset and solar noon, with refraction and disc-limb corrections.
- 🌐 **Location aware** — geodetic latitude/longitude + IANA timezone; ships with a built-in city table (no lookup service).
- 📐 **Multiple ayanamsa** — Lahiri (default), Raman, KP, Yukteshwar and Fagan–Bradley.
- 🧮 **Meeus-grade astronomy** — Sun to ~0.01°, Moon to ~10″, including nutation, aberration and ΔT.
- 🐍 **Pure standard library** — targets Python **3.10+**.
- 🔁 **Deterministic** — no I/O in the astronomy core; ideal for testing and caching.

> **Status:** the astronomy foundation, panchang limbs, calendar structure, muhurta, the rule-driven festival engine and the CLI/API are implemented (Phases 1–4 and 6–7). Eclipses are an approximate detector (Phase 5, partial); precise Besselian-element circumstances and full planetary transits remain on the [roadmap](#-roadmap).

## 🎯 Why this exists

Most panchang software either phones home, ships megabytes of ephemeris tables, or hides its maths behind opaque data files. Kalagana takes the opposite approach:

| Principle | Meaning |
|---|---|
| **Offline by construction** | Every astronomical value is computed from formulas written in the source. |
| **Transparent** | Each module documents its formula and source (Meeus chapter, IAU polynomial, …). |
| **Data, not code, for rules** | Festival rules are plain Python data structures, evaluated by a generic engine. |
| **Deterministic & testable** | No randomness, no I/O in the core — the same inputs always yield the same result. |

## 🏗️ Architecture

The design keeps a clean separation between **astronomy**, the **calendar**, and **festival rules**:

```text
                   ┌───────────────────────────────────────────┐
                   │                  kalagana                  │
                   └───────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼───────────────────────────────┐
        │                              │                               │
   🌍 Astronomy                   📅 Calendar                    🎉 Festival rules
        │                              │                               │
  julian  (JD, ΔT, GMST)         calendar_month (masa…)          festivals/rules.py
  sun     (λ, δ, α, EoT)         eras (Vikram, Shaka…)           festivals/engine.py
  moon    (λ, β, distance)       muhurta (Rahu Kalam…)           festivals/regions.py
  planets (Merc…Saturn, nodes)   yogas (Siddhi…)
  ayanamsa (precession offset)   eclipses / transits
  solver  (root finding)
  sunrise (rise/set/transit)     ── these consume the ⬆ astronomy ⬆ ──
  limbs   (tithi, vara, …)              primitives above
```

Implemented today: `julian`, `sun`, `moon`, `ayanamsa`, `solver`, `sunrise`, `limbs`, `calendar_month`, `eras`, `muhurta`, `hijri`, `festivals` (rules + engine), `api`, `cli` and `location`.

## 📋 Requirements

- **Python 3.10 or newer** (developed and tested on 3.14).
- **No third-party packages.** The project uses only the standard library (`math`, `datetime`, `dataclasses`, `enum`, `argparse`, `json`, `functools`, `zoneinfo`).
- *Optional:* the [`tzdata`](https://pypi.org/project/tzdata/) package on Windows, where the stdlib `zoneinfo` needs it for full timezone-database support. Without it, Kalagana falls back to a built-in standard-offset table (exact for India, approximate for zones that observe DST).

## 🚀 Installation

**From PyPI** (recommended) — no dependencies are pulled in:

```bash
pip install kalagana
```

On Windows, add the optional timezone database for full IANA support (India is exact either way):

```bash
pip install "kalagana[tz]"
```

**From source** (development):

```bash
git clone https://github.com/mitjangid/Kalagana.git
cd Kalagana
```

There is nothing to build — it is pure Python. Verify either install:

```bash
python -c "import kalagana; print(kalagana.__version__)"
# 0.1.0
```

## 🏁 First-time setup in 60 seconds

Kalagana needs **no configuration and no network**. The three steps below are all you need:

```bash
# 1. Install
pip install kalagana

# 2. (optional) set your default city, so you can omit --city every time
cp .env.example .env          # then edit KALAGANA_CITY and friends

# 3. Run something
kalagana day 2026-11-08 --city delhi
```

That prints the full panchang for a date. Prefer festivals?

```bash
kalagana festivals 2026 --city delhi --major-only
```

> `.env` is optional and git-ignored; a variable already present in the real environment is never overwritten by it. See [Configuration](#-configuration).

## 🧑💻 Command line

Installing the package adds a `kalagana` command (equivalent to `python -m kalagana`). Every data subcommand takes a location (`--city`, or `--lat`/`--lon`) and `--format text|json|csv`.

```bash
kalagana --help
```

| Subcommand | What it does | Example |
|---|---|---|
| `day <date>` | Full panchang for one date | `kalagana day 2026-11-08 --city delhi` |
| `month <YYYY-MM>` | Day-by-day summary for a month | `kalagana month 2026-11 --city mumbai` |
| `festivals <year>` | Computed festivals for a year | `kalagana festivals 2026 --major-only` |
| `eclipses <year>` | Approximate eclipses | `kalagana eclipses 2026 --city delhi` |
| `muhurta <date>` | Rahu Kalam, Choghadiya, Hora, … | `kalagana muhurta 2026-11-08 --city delhi` |
| `find <name>` | Next date of a named festival | `kalagana find Diwali --date 2025-01-01` |
| `cities` | List the built-in city table | `kalagana cities` |
| `serve` | Start the offline REST API | `kalagana serve --port 8765` |

Common options (also accepted by `python -m kalagana`):

```bash
--city NAME            # built-in city key (see `kalagana cities`)
--lat D --lon D        # explicit coordinates instead of a city
--tz Asia/Kolkata      # override the timezone
--tradition north      # north | south | tamil | telugu | kannada | malayalam | bengali | odia | gujarati | marathi
--ayanamsa lahiri      # lahiri | raman | kp | yukteshwar | fagan_bradley
--format text|json|csv # output format
```

Examples:

```bash
# JSON output, piped to jq
kalagana day 2026-11-08 --city delhi --format json | jq .sunrise

# Festivals only for a region, skipping monthly observances
kalagana festivals 2026 --tradition tamil --major-only

# National holidays only (kind filter)
kalagana festivals 2026 --kind national

# Recompute without Islamic festivals
kalagana festivals 2026 --no-islamic
```

## ⚡ Quick start

```python
from datetime import date
from kalagana.location import Location
from kalagana.sunrise import sunrise_sunset, solar_noon
from kalagana.limbs import day_limbs

loc = Location(name="Delhi", lat=28.6139, lon=77.2090, tz="Asia/Kolkata")

# Sunrise / sunset / noon in local time
rise, setting = sunrise_sunset(date(2026, 11, 8), loc)
print("Sunrise:", rise.strftime("%H:%M:%S"))
print("Sunset :", setting.strftime("%H:%M:%S"))
print("Noon   :", solar_noon(date(2026, 11, 8), loc).strftime("%H:%M:%S"))

# The five limbs for the Hindu day beginning at sunrise
day = day_limbs(date(2026, 11, 8), loc)
print("Vara:", day["vara"], f"({day['vara_en']})")
for t in day["tithi"]:
    print(f"Tithi    : {t.name:<22} {t.start:%H:%M} → {t.end:%H:%M}")
for n in day["nakshatra"]:
    print(f"Nakshatra: {n.name:<22} {n.start:%H:%M} → {n.end:%H:%M}")
```

**Real output** (Delhi, 8 November 2026 — Diwali day):

```text
Sunrise: 06:38:07
Sunset : 17:31:21
Noon   : 12:04:44
Vara: Ravivara (Sunday)
Tithi    : Krishna Chaturdashi    06:39 → 11:30
Tithi    : Amavasya               11:30 → 06:40
Nakshatra: Swati                  06:39 → 06:40
```

## 🎉 Festivals

Festival dates are produced by a generic engine from a table of rules — never stored. Rules come in four groups:

| Group | `system` | Examples |
|---|---|---|
| Hindu lunar | `lunar` | Diwali, Holi, Janmashtami, Ganesh Chaturthi |
| Solar sankranti | `solar` | Makar Sankranti, Pongal, Vishu, Baisakhi |
| Islamic (Hijri) | `hijri` | Eid al-Fitr, Eid al-Adha, Milad-un-Nabi, Muharram |
| Fixed Gregorian | `fixed` | Republic Day, Independence Day, Teachers' Day |

```python
from datetime import date
from kalagana import festivals_for_year, national_holidays, find_next, city_lookup

delhi = city_lookup("Delhi")
for f in festivals_for_year(2026, delhi, include_monthly=False, kinds=("national",)):
    print(f.date, f.name, f.kind)
# 2026-01-26 Republic Day national
# 2026-08-15 Independence Day national
# 2026-10-02 Gandhi Jayanti national

national_holidays(2026, delhi)                       # the three gazetted holidays
find_next("Eid al-Fitr", date(2026, 1, 1), delhi)    # 2026-03-20
```

Every occurrence carries a `kind` — `festival`, `national` or `observance`. Whole groups can be switched off with `include_islamic=False` / `include_fixed=False` (or the `KALAGANA_INCLUDE_*` environment variables).

> Islamic dates use the **tabular (arithmetic)** Islamic calendar, so they may differ by a day or two from the locally sighted date.

## 🌐 REST API

Kalagana also ships a small **offline REST API** built on the standard-library `http.server` (no web framework, no network):

```bash
python -m kalagana.server --port 8765      # or: python -m kalagana serve
```

```bash
curl -s "http://127.0.0.1:8765/day?date=2024-08-26&city=delhi"
curl -s "http://127.0.0.1:8765/find?name=Diwali&after=2025-01-01&city=delhi"
```

| Endpoint | Purpose |
|---|---|
| `GET /health` | status & version |
| `GET /cities` | built-in city table |
| `GET /ayanamsas` | supported ayanamsa models |
| `GET /day?date=&city=` | full panchang for one date |
| `GET /month?month=YYYY-MM` | day-by-day month summary |
| `GET /festivals?year=` | rule-derived festival dates (`&kind=national`, `&no_islamic=true`, `&no_fixed=true`, `&major_only=true`) |
| `GET /eclipses?year=` | approximate eclipses |
| `GET /muhurta?date=` | daily muhurta windows |
| `GET /find?name=&after=` | next occurrence of a festival |

Full reference: **[API_README.md](API_README.md)**. Import files for Postman, Insomnia, Bruno and OpenAPI tooling live in [`api/`](api).

## 📚 Module reference

| Module | Purpose |
|---|---|
| `kalagana.julian` | Julian Day conversion (Gregorian/Julian), **ΔT** (Espenak & Meeus polynomials), Greenwich mean/apparent sidereal time. |
| `kalagana.sun` | Solar apparent longitude, right ascension, declination, equation of time (Meeus ch. 25 & 28). |
| `kalagana.moon` | Lunar longitude/latitude/distance via the full Meeus ch. 47 periodic-term tables, plus RA/dec. |
| `kalagana.ayanamsa` | Ayanamsa selection and propagation (Lahiri default) using the IAU general precession polynomial. |
| `kalagana.solver` | Generic angle root finder (`solve_angle`), zero finder (`find_crossing`), `bisect`, `next_crossing`. |
| `kalagana.sunrise` | Sunrise, sunset, moonrise, moonset, solar noon (scan + bisection on altitude). |
| `kalagana.limbs` | The five limbs: `elongation`, tithi, nakshatra (+pada), yoga, karana, vara, and `day_limbs()`. |
| `kalagana.calendar_month` | Lunar month (masa): new/full-moon finders, sankranti, adhika/kshaya detection, amanta vs purnimanta, paksha. |
| `kalagana.hijri` | Tabular (arithmetic) Islamic calendar: Hijri → Gregorian conversion for the Islamic festivals. |
| `kalagana.location` | `Location` dataclass, built-in `CITIES` table, timezone resolution with fallback. |

### Key entry points

```python
from kalagana.limbs import (
    tithi_number, tithi_name, nakshatra_number, nakshatra_pada,
    yoga_number, karana_number, karana_name, vara_name, day_limbs,
)
from kalagana.sunrise import sunrise_sunset, moonrise_moonset, solar_noon
from kalagana.calendar_month import masa_at, paksha_at, purnimanta_name
from kalagana.julian import gregorian_to_jd, datetime_to_jd, jd_to_datetime, delta_t
from kalagana.ayanamsa import ayanamsa_degrees, SUPPORTED
```

## 🔬 Accuracy & methodology

Every value is computed from a documented source:

| Quantity | Method / source | Rated accuracy |
|---|---|---|
| Julian Day / sidereal time | Meeus ch. 7 & 12 | ~0.1 s of time |
| ΔT | Espenak & Meeus polynomial expressions | — |
| Sun apparent longitude | Meeus ch. 25 (nutation + aberration) | ≈ 0.01° |
| Moon longitude / latitude / distance | Meeus ch. 47 full series (tables 47.A / 47.B) | ≈ 10″ |
| Sunrise / sunset | Meeus ch. 15, altitude −0.833° (upper limb + refraction) | ≈ 1 minute |
| Ayanamsa | Lahiri anchored at J2000 + IAU precession-in-longitude | across 1900–2100 |

**Limb boundaries** are located by turning *"when does this angle cross a multiple of 12° (or 13°20′, or 6°)?"* into a root-finding problem, solved to **one second of time**.

## 🧭 Ayanamsa

```python
from kalagana.ayanamsa import ayanamsa_degrees, SUPPORTED
print(SUPPORTED)
# ('fagan_bradley', 'kp', 'lahiri', 'raman', 'yukteshwar')

ayanamsa_degrees(2451545.0, "lahiri")   # ~23.8531° at J2000.0
```

**Lahiri (Chitrapaksha)** is the default — the convention of the Indian Government's *Rashtriya Panchang* and most North Indian panchangs. The Raman and KP epoch constants are documented approximations; confirm them against an authoritative ephemeris before relying on them for critical work.

## 🏙️ Built-in cities

`kalagana.location.CITIES` ships with **30+ ready-to-use locations** (Delhi, Mumbai, Chennai, Kolkata, Ujjain, Varanasi, Bikaner, Kota, Bengaluru, Hyderabad, Jaipur, and overseas reference points such as London, New York, Dubai, Singapore, Sydney, Toronto and Kathmandu). Look one up by name:

```python
from kalagana.location import city_lookup
loc = city_lookup("Varanasi")
```

## 🗓️ Calendar structure

`kalagana.calendar_month` resolves the **lunar month (masa)** and paksha, detecting **adhika** (extra) and **kshaya** (lost) months, in both the **amanta** (South) and **purnimanta** (North) conventions.

```python
from kalagana.julian import gregorian_to_jd
from kalagana.calendar_month import masa_at, paksha_at, purnimanta_name

jd = gregorian_to_jd(2026, 11, 8)            # Julian Day for 2026-11-08
m = masa_at(jd, ayanamsa="lahiri")
print(m.display)                             # 'Ashwin'  (amanta)
print(m.adhika, m.kshaya)                    # False False
print(paksha_at(jd))                         # 'Krishna'
print(purnimanta_name(jd, "lahiri"))         # 'Kartika' (North Indian)
```

**Real output** (Diwali, 2026-11-08):

```text
Ashwin
False False
Krishna
Kartika
```

## 🗺️ Roadmap

Kalagana is being built phase by phase against a detailed specification (`docs/hindu_panchang_prompt.md`).

| Phase | Scope | Status |
|---|---|---|
| **1. Astronomy foundation** | Julian Day, ΔT, sidereal time, Sun, Moon, Lahiri ayanamsa, generic solver | ✅ Done |
| **2. Panchang limbs** | Tithi, vara, nakshatra (+pada), yoga, karana, sunrise/sunset/moonrise | ✅ Done |
| **3. Calendar structure** | Masa, paksha, adhika/kshaya masa, amanta/purnimanta, ritu, ayana, samvat eras | ✅ Done |
| **4. Muhurta & yogas** | Rahu Kalam, Gulika, Abhijit, Brahma Muhurta, Choghadiya, Hora, Durmuhurta | ✅ Done |
| **5. Eclipses & transits** | Solar/lunar eclipse detector (dates & rough type); precise Besselian elements + planetary transits pending | 🚧 Partial |
| **6. Festival engine** | Data-driven `FestivalRule` table + tie-break policies + regional variants; Hindu, Islamic (Hijri), national-holiday and fixed-date rule groups | ✅ Done |
| **7. Interfaces** | Public API, `day` / `month` / `festivals` / `eclipses` / `muhurta` / `find` CLI, JSON/CSV | ✅ Done |

## 📂 Project structure

```text
Kalagana/
├── kalagana/               # the library (pure stdlib)
│   ├── __init__.py         # package metadata & re-exports
│   ├── julian.py           # JD conversion, ΔT, sidereal time
│   ├── sun.py              # solar coordinates & equation of time
│   ├── moon.py             # lunar coordinates (Meeus ch. 47)
│   ├── ayanamsa.py         # ayanamsa models
│   ├── solver.py           # root finding on angle functions
│   ├── sunrise.py          # rise / set / transit
│   ├── limbs.py            # tithi, vara, nakshatra, yoga, karana
│   ├── calendar_month.py   # masa, paksha, adhika/kshaya, amanta/purnimanta
│   ├── eras.py             # Vikram, Shaka, samvatsara, ritu, ayana
│   ├── muhurta.py          # Rahu Kalam, Choghadiya, Hora, Durmuhurta
│   ├── hijri.py            # tabular Islamic (Hijri) calendar conversion
│   ├── festivals/          # rule table + engine (data-driven dates)
│   ├── api.py              # Panchang object, daily_panchang, eclipses
│   ├── cli.py              # command line interface
│   ├── server.py           # offline REST API (stdlib http.server)
│   ├── config.py           # optional environment/.env configuration
│   ├── selftest.py         # python -m kalagana.selftest
│   └── location.py         # Location + built-in city table
├── api/                    # OpenAPI + Postman + Insomnia + Bruno import files
├── tests/                  # unittest suite + reference dates
├── scripts/
│   └── release.py          # version bump / build / tag / GitHub release
├── .github/workflows/      # CI, release and container automation
├── assets/
│   └── logo.png            # project logo
├── docs/
│   └── hindu_panchang_prompt.md   # full project specification
├── API_README.md           # detailed API reference
├── .env.example            # annotated configuration template
├── Dockerfile              # container image for the REST API
├── MANIFEST.in             # sdist contents
├── .gitignore
└── README.md
```

## ⚙️ Configuration

Kalagana needs **no configuration** to run. Optional settings are read from the environment and from a local `.env` file, parsed by [`kalagana/config.py`](kalagana/config.py) with **no** `python-dotenv` dependency:

```bash
cp .env.example .env
```

```dotenv
KALAGANA_HOST=127.0.0.1     # REST API bind address
KALAGANA_PORT=8765          # REST API port
KALAGANA_CITY=delhi         # default location (or KALAGANA_LAT / KALAGANA_LON)
KALAGANA_TZ=Asia/Kolkata
KALAGANA_AYANAMSA=lahiri    # lahiri | raman | kp | yukteshwar | fagan_bradley
KALAGANA_TRADITION=north
KALAGANA_INCLUDE_MONTHLY=true    # monthly vrats (Ekadashi, Purnima, ...)
KALAGANA_INCLUDE_ISLAMIC=true    # Islamic (Hijri) festivals
KALAGANA_INCLUDE_FIXED=true      # national holidays + fixed-date observances
```

The full annotated list — including `KALAGANA_LOG_REQUESTS`, `KALAGANA_FIND_YEARS`, `KALAGANA_LANG` and `KALAGANA_STRICT` — is in [`.env.example`](.env.example). Read from code with `kalagana.config.load_settings()`. A variable already present in the environment is never overwritten by `.env`, and `.env` itself is git-ignored.

## 🛠️ Development

Pure standard library, so there's nothing to compile. Run a module directly to explore, or use these smoke checks:

```bash
# sanity check: import + version
python -c "import kalagana; print(kalagana.__version__)"

# today's vara for a city
python -c "from datetime import date; from kalagana.location import city_lookup; from kalagana.limbs import day_limbs; print(day_limbs(date.today(), city_lookup('Delhi'))['vara'])"
```

### Conventions

- Type hints on every public function; docstrings state **units** (degrees, days, hours, km).
- The astronomy core is **pure** — no I/O, no global state.
- Units are explicit: longitudes in **degrees**, distances in **km**, times as **Julian Days (TT/UT)** or timezone-aware `datetime`.
- Functions stay small, and astronomy stays separate from calendar and festival rules.

## 🚀 Releasing

The version lives in `pyproject.toml` and `kalagana/__init__.py`; the helper keeps both in sync. It uses only the standard library.

```bash
python scripts/release.py current                  # show the current version
python scripts/release.py bump patch               # 0.1.0 -> 0.1.1 (rewrites both files)
python scripts/release.py build                    # sdist + wheel into dist/   (needs: pip install build)
python scripts/release.py tag --push               # annotated tag vX.Y.Z and push
python scripts/release.py gh-release               # GitHub Release with dist/ assets (needs: gh)
python scripts/release.py --dry-run release --bump patch --push --gh
```

`--dry-run` prints the commands instead of running them, and **nothing is pushed without `--push`**. The working tree must be clean before a bump or a tag (override with `--allow-dirty`).

### Automation

| Workflow | Trigger | Result |
|---|---|---|
| `ci.yml` | push / PR | self-test + unit tests on Ubuntu, Windows and macOS, Python 3.10 and 3.13 |
| `release.yml` | tag `v*` | builds sdist + wheel, creates the **GitHub Release**, publishes to **PyPI** (trusted publishing) |
| `container.yml` | push / tag | publishes the Docker image to **`ghcr.io/<owner>/kalagana`** |

> **Note on the GitHub “Packages” tab:** GitHub Packages does **not** host Python distributions, so the Python package is published to **PyPI**. The **Packages** section fills from the container image built by `container.yml`. PyPI publishing uses a [Trusted Publisher](https://docs.pypi.org/trusted-publishers/) — configure it for this repo, the `release.yml` workflow, and the `pypi` environment; no API token is stored. Use the workflow's manual `testpypi` option to rehearse first.

### Container

```bash
docker build -t kalagana .
docker run --rm -p 8765:8765 -e KALAGANA_CITY=mumbai kalagana
curl http://127.0.0.1:8765/health
```

## 🤝 Contributing

Contributions are welcome. Because accuracy is the whole point:

1. **Never hardcode a festival date** for a specific year — every date must fall out of computation.
2. **Cite your source** for any new formula (Meeus chapter, IAU resolution, …).
3. When traditions disagree, implement **both** as options, document the default, and say so.
4. Report measured accuracy honestly — **do not claim accuracy you have not tested**.

## 📚 References

- Jean Meeus, *Astronomical Algorithms*, 2nd edition — chapters 7, 12, 15, 22, 25, 28, 47.
- Fred Espenak & Jean Meeus, *Polynomial Expressions for Delta T* (NASA/GSFC).
- IAU 2006 general precession in longitude.
- *The Indian Astronomical Ephemeris* / **Rashtriya Panchang** (Lahiri / Chitrapaksha ayanamsa).

## ⚠️ Disclaimer

Panchang calculations encode **tradition and convention** (ayanamsa choice, masa system, tie-break rules). Kalagana aims to match published Drik Panchang values, but regional and sampradaya differences exist and are treated as first-class options rather than bugs. Always cross-check important dates (festivals, muhurta, vrat) against your local panchang before relying on them.

## 📄 License

Released under the **MIT License** — see the [`LICENSE`](LICENSE) file for the full text.

Copyright (c) 2026 [Amit K. Jangir](https://github.com/mitjangid).

You are free to use, modify, and distribute this software, including for commercial purposes, provided the copyright notice and permission notice are retained.

## ⭐ Show your support

If **Kalagana** helps you — or you just love an offline, transparent panchang — please consider giving a little back:

<p align="center">
  <a href="https://github.com/mitjangid/Kalagana/stargazers">
    <img src="https://img.shields.io/github/stars/mitjangid/Kalagana?style=for-the-badge&logo=github&label=Star%20this%20repo&color=yellow" alt="Star this repository">
  </a>
  <a href="https://github.com/mitjangid?tab=followers">
    <img src="https://img.shields.io/github/followers/mitjangid?style=for-the-badge&logo=github&label=Follow&color=blue" alt="Follow @mitjangid">
  </a>
</p>

- ⭐ **Star** this repository — a star helps more people discover the project.
- 👤 **Follow** [@mitjangid](https://github.com/mitjangid) for updates and new work.
- 🔁 **Share** it with someone who checks the panchang every day.

Thank you for your support! 🙏

---

<div align="center">

**Built with 🐍 and 📐 to be transparent, offline and correct.**

*Made for the Dharmic community, for astronomers-at-heart, and for anyone who likes their calendars deterministic.*

</div>
