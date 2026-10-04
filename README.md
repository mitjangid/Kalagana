<div align="center">

<img src="https://raw.githubusercontent.com/mitjangid/Kalagana/master/assets/logo.png" alt="Kalagana logo" width="160" />

# 🕉️ Kalagana — Official Drik Panchang & Panchangam for Python

**The official, offline, dependency-free Python library and CLI for the Hindu (Drik) Panchang, Panchangam and the Indian festival calendar.**

*Compute Tithi, Vara, Nakshatra, Yoga, Karana, sunrise/sunset, ayanamsa, muhurat (muhurta) and the dates of Hindu, Islamic and national festivals — for any city in India or worldwide — from first principles, with no network, no database and no downloaded ephemeris files.*

[![PyPI](https://img.shields.io/pypi/v/kalagana.svg)](https://pypi.org/project/kalagana/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](https://pypi.org/project/kalagana/)
[![Offline](https://img.shields.io/badge/network-100%25%20offline-success.svg)](https://pypi.org/project/kalagana/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## What is Kalagana?

**Kalagana** computes a complete **Drik Panchang** (also written *panchangam*, *panjika* or *Hindu calendar*) — the five traditional limbs of the Hindu calendar — together with the dates of **Hindu festivals, Islamic (Hijri) festivals and Indian national holidays**, for **any latitude, longitude and timezone**, in both **North (purnimanta)** and **South (amanta)** traditions.

Everything is derived from **positional astronomy implemented in the code itself**, using the algorithms from Jean Meeus' *Astronomical Algorithms*. There are:

- ❌ no network calls
- ❌ no database
- ❌ no downloaded ephemeris files
- ❌ no third-party packages
- ✅ just the Python standard library

The same inputs always produce the same outputs — the calculation core is **pure and deterministic**.

### What you can compute

Panchang (tithi, nakshatra, yoga, karana, vara), sunrise/sunset and moonrise/moonset, muhurat (Rahu Kalam, Yamaganda, Gulika, Abhijit, Choghadiya, Hora, Brahma Muhurta, Durmuhurta), Vikram Samvat / Shaka eras, ritu and ayana, and a rule-driven calendar of **Hindu festivals** (Diwali, Holi, Navratri, Dussehra, Ganesh Chaturthi, Krishna Janmashtami, Ekadashi, Karwa Chauth, Chhath Puja, Makar Sankranti, Pongal, Onam …), **Islamic festivals** (Eid al-Fitr, Eid al-Adha, Muharram, Milad-un-Nabi …) and **Indian national holidays** — for any date, past or decades ahead.

## ✨ Highlights

- 🌗 **Full five limbs** — Tithi (with paksha), Vara, Nakshatra (with pada), Yoga and Karana, each with exact **start and end times**.
- ☀️ **Rise & set** — sunrise, sunset, moonrise, moonset and solar noon, with refraction and disc-limb corrections.
- 🌐 **Location aware** — geodetic latitude/longitude + IANA timezone; ships with a built-in city table (no lookup service).
- 📐 **Multiple ayanamsa** — Lahiri (default), Raman, KP, Yukteshwar and Fagan–Bradley.
- 🧮 **Meeus-grade astronomy** — Sun to ~0.01°, Moon to ~10″, including nutation, aberration and ΔT.
- 🎉 **Festivals from rules, never stored** — Hindu (lunar + solar sankranti), Islamic (Hijri), national holidays and fixed-date observances, plus monthly vrats.
- 🐍 **Pure standard library** — targets Python **3.10+**.

## 🚀 Installation

```bash
pip install kalagana
```

On Windows, add the optional timezone database for full IANA support (India is exact either way):

```bash
pip install "kalagana[tz]"
```

Verify the install:

```bash
python -c "import kalagana; print(kalagana.__version__)"
```

No dependencies are pulled in — the runtime uses only the Python standard library.

## 🧑💻 Command line

Installing the package adds a `kalagana` command (equivalent to `python -m kalagana`). Every data subcommand takes a location (`--city`, or `--lat`/`--lon`) and `--format text|json|csv`.

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

Common options:

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
kalagana day 2026-11-08 --city delhi --format json

# National holidays only (kind filter)
kalagana festivals 2026 --kind national

# Recompute without Islamic festivals
kalagana festivals 2026 --no-islamic
```

## ⚡ Quick start (Python)

```python
from datetime import date
from kalagana import daily_panchang, festivals_for_year, city_lookup

loc = city_lookup("Delhi")

# The five limbs for the Hindu day beginning at sunrise
day = daily_panchang(date(2026, 11, 8), loc)
print(day.vara_en, "|", day.masa_purnimanta, day.paksha)
for t in day.tithi:
    print(f"Tithi    : {t.name:<22} {t.start:%H:%M} → {t.end:%H:%M}")

# Festival dates are computed from rules, not stored
for f in festivals_for_year(2026, loc, include_monthly=False, kinds=("national",)):
    print(f.date, f.name, f.kind)
```

**Real output** (Delhi, 8 November 2026 — Diwali day):

```text
Sunday | Kartika Krishna
Tithi    : Krishna Chaturdashi    06:39 → 11:30
Tithi    : Amavasya               11:30 → 06:40
2026-01-26 Republic Day national
2026-08-15 Independence Day national
2026-10-02 Gandhi Jayanti national
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
national_holidays(2026, delhi)                       # the three gazetted holidays
find_next("Eid al-Fitr", date(2026, 1, 1), delhi)    # 2026-03-20
```

Every occurrence carries a `kind` — `festival`, `national` or `observance`. Whole groups can be switched off with `include_islamic=False` / `include_fixed=False` (or the `KALAGANA_INCLUDE_*` environment variables).

> Islamic dates use the **tabular (arithmetic)** Islamic calendar, so they may differ by a day or two from the locally sighted date.

## 🌐 REST API

Kalagana ships a small **offline REST API** built on the standard-library `http.server` (no web framework, no network):

```bash
kalagana serve --port 8765      # or: python -m kalagana.server
```

```bash
curl -s "http://127.0.0.1:8765/day?date=2026-11-08&city=delhi"
curl -s "http://127.0.0.1:8765/festivals?year=2026&city=delhi&kind=national"
```

| Endpoint | Purpose |
|---|---|
| `GET /health` | status & version |
| `GET /cities` | built-in city table |
| `GET /ayanamsas` | supported ayanamsa models |
| `GET /day?date=&city=` | full panchang for one date |
| `GET /month?month=YYYY-MM` | day-by-day month summary |
| `GET /festivals?year=` | rule-derived festival dates |
| `GET /eclipses?year=` | approximate eclipses |
| `GET /muhurta?date=` | daily muhurta windows |
| `GET /find?name=&after=` | next occurrence of a festival |

Full reference: **[docs/api/README.md](https://github.com/mitjangid/Kalagana/blob/master/docs/api/README.md)**.

## ⚙️ Configuration

Kalagana needs **no configuration** to run, and defaults to **Delhi / Asia/Kolkata (IST)**. Optional settings are read from the environment and a local `.env` file (parsed by `kalagana/config.py`; no `python-dotenv` dependency):

```bash
cp .env.example .env
```

| Variable | Default | Effect |
|---|---|---|
| `KALAGANA_HOST` | `127.0.0.1` | Server bind address |
| `KALAGANA_PORT` | `8765` | Server port |
| `KALAGANA_CITY` | `delhi` | Default location when a request omits one |
| `KALAGANA_LAT` / `KALAGANA_LON` | — | Default coordinates (take precedence over `KALAGANA_CITY`) |
| `KALAGANA_TZ` | `Asia/Kolkata` | Default timezone |
| `KALAGANA_AYANAMSA` | `lahiri` | Default ayanamsa |
| `KALAGANA_TRADITION` | `north` | Default tradition |
| `KALAGANA_MONTH_SYSTEM` | `purnimanta` | Default month naming |
| `KALAGANA_INCLUDE_MONTHLY` | `true` | Include monthly vrats (Ekadashi, Purnima, …) |
| `KALAGANA_INCLUDE_ISLAMIC` | `true` | Include Islamic (Hijri) festivals |
| `KALAGANA_INCLUDE_FIXED` | `true` | Include fixed-date national/observance days |
| `KALAGANA_FIND_YEARS` | `3` | Look-ahead for `find` |
| `KALAGANA_LANG` | `en` | Preferred name language |
| `KALAGANA_ENV_FILE` | `.env` | Path of the env file to read |
| `KALAGANA_STRICT` | `false` | Raise on invalid values instead of falling back |

The full annotated list is in [`.env.example`](https://github.com/mitjangid/Kalagana/blob/master/.env.example).

## 🔬 Accuracy

| Quantity | Method / source | Rated accuracy |
|---|---|---|
| Julian Day / sidereal time | Meeus ch. 7 & 12 | ~0.1 s of time |
| Sun apparent longitude | Meeus ch. 25 (nutation + aberration) | ≈ 0.01° |
| Moon longitude / latitude / distance | Meeus ch. 47 full series | ≈ 10″ |
| Sunrise / sunset | Meeus ch. 15, altitude −0.833° | ≈ 1 minute |
| Ayanamsa | Lahiri at J2000 + IAU precession-in-longitude | across 1900–2100 |

Limb boundaries are located to **one second of time**. Eclipses are computed by an approximate detector (correct dates, rough type) — consult an authoritative ephemeris for exact circumstances, and always cross-check important dates against your local panchang.

## ⚠️ Disclaimer

Panchang calculations encode **tradition and convention** (ayanamsa choice, masa system, tie-break rules), and Islamic dates use a tabular calendar. Regional and sampradaya differences exist and are treated as first-class options rather than bugs.

Kalagana is an independent, open-source project. Here "official" means only that this is the project's canonical package on PyPI — Kalagana is **not** affiliated with, endorsed by, or connected to drikpanchang.com, any government body, or any religious institution.

## 📄 License

Released under the **MIT License** — see the [`LICENSE`](https://github.com/mitjangid/Kalagana/blob/master/LICENSE) file.

Copyright (c) 2026 [Amit K. Jangir](https://github.com/mitjangid).
