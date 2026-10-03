<div align="center">

# 🕉️ Kalagana · `panchang`

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

`panchang` (the package) / **Kalagana** (the project) is a Python library and command-line tool that computes a complete **Drik Panchang** — the five traditional limbs of the Hindu calendar — together with (eventually) the dates of Hindu festivals, for **any latitude, longitude and timezone**, in both **North (purnimanta)** and **South (amanta)** traditions.

Everything is derived from **positional astronomy implemented in the code itself**, using the algorithms from Jean Meeus' *Astronomical Algorithms*. There are:

- ❌ no network calls
- ❌ no database
- ❌ no downloaded ephemeris files
- ❌ no third-party packages
- ✅ just the Python standard library

The same inputs always produce the same outputs — the calculation core is **pure and deterministic**.

## ✨ Highlights

- 🌗 **Full five limbs** — Tithi (with paksha), Vara, Nakshatra (with pada), Yoga and Karana, each with exact **start and end times**.
- ☀️ **Rise & set** — sunrise, sunset, moonrise, moonset and solar noon, with refraction and disc-limb corrections.
- 🌐 **Location aware** — geodetic latitude/longitude + IANA timezone; ships with a built-in city table (no lookup service).
- 📐 **Multiple ayanamsa** — Lahiri (default), Raman, KP, Yukteshwar and Fagan–Bradley.
- 🧮 **Meeus-grade astronomy** — Sun to ~0.01°, Moon to ~10″, including nutation, aberration and ΔT.
- 🐍 **Pure standard library** — targets Python **3.10+**.
- 🔁 **Deterministic** — no I/O in the astronomy core; ideal for testing and caching.

> **Status:** the astronomy foundation and the panchang limbs are implemented (Phases 1–2), and the calendar layer (masa) is in progress (Phase 3). The festival engine, eclipses, transits and CLI are on the [roadmap](#-roadmap).

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
                   │                  panchang                  │
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

Implemented today: `julian`, `sun`, `moon`, `ayanamsa`, `solver`, `sunrise`, `limbs`, `calendar_month`, `location`.

## 📋 Requirements

- **Python 3.10 or newer** (developed and tested on 3.14).
- **No third-party packages.** The project uses only the standard library (`math`, `datetime`, `dataclasses`, `enum`, `argparse`, `json`, `functools`, `zoneinfo`).
- *Optional:* the [`tzdata`](https://pypi.org/project/tzdata/) package on Windows, where the stdlib `zoneinfo` needs it for full timezone-database support. Without it, `panchang` falls back to a built-in standard-offset table (exact for India, approximate for zones that observe DST).

## 🚀 Installation

The package is not yet published to PyPI. Clone and use it directly:

```bash
git clone https://github.com/mitjangid/Kalagana.git
cd Kalagana
```

There is nothing to build — it is pure Python. Verify the install:

```bash
python -c "import panchang; print(panchang.__version__)"
# 0.1.0
```

## ⚡ Quick start

```python
from datetime import date
from panchang.location import Location
from panchang.sunrise import sunrise_sunset, solar_noon
from panchang.limbs import day_limbs

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

## 📚 Module reference

| Module | Purpose |
|---|---|
| `panchang.julian` | Julian Day conversion (Gregorian/Julian), **ΔT** (Espenak & Meeus polynomials), Greenwich mean/apparent sidereal time. |
| `panchang.sun` | Solar apparent longitude, right ascension, declination, equation of time (Meeus ch. 25 & 28). |
| `panchang.moon` | Lunar longitude/latitude/distance via the full Meeus ch. 47 periodic-term tables, plus RA/dec. |
| `panchang.ayanamsa` | Ayanamsa selection and propagation (Lahiri default) using the IAU general precession polynomial. |
| `panchang.solver` | Generic angle root finder (`solve_angle`), zero finder (`find_crossing`), `bisect`, `next_crossing`. |
| `panchang.sunrise` | Sunrise, sunset, moonrise, moonset, solar noon (scan + bisection on altitude). |
| `panchang.limbs` | The five limbs: `elongation`, tithi, nakshatra (+pada), yoga, karana, vara, and `day_limbs()`. |
| `panchang.calendar_month` | Lunar month (masa): new/full-moon finders, sankranti, adhika/kshaya detection, amanta vs purnimanta, paksha. |
| `panchang.location` | `Location` dataclass, built-in `CITIES` table, timezone resolution with fallback. |

### Key entry points

```python
from panchang.limbs import (
    tithi_number, tithi_name, nakshatra_number, nakshatra_pada,
    yoga_number, karana_number, karana_name, vara_name, day_limbs,
)
from panchang.sunrise import sunrise_sunset, moonrise_moonset, solar_noon
from panchang.calendar_month import masa_at, paksha_at, purnimanta_name
from panchang.julian import gregorian_to_jd, datetime_to_jd, jd_to_datetime, delta_t
from panchang.ayanamsa import ayanamsa_degrees, SUPPORTED
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
from panchang.ayanamsa import ayanamsa_degrees, SUPPORTED
print(SUPPORTED)
# ('fagan_bradley', 'kp', 'lahiri', 'raman', 'yukteshwar')

ayanamsa_degrees(2451545.0, "lahiri")   # ~23.8531° at J2000.0
```

**Lahiri (Chitrapaksha)** is the default — the convention of the Indian Government's *Rashtriya Panchang* and most North Indian panchangs. The Raman and KP epoch constants are documented approximations; confirm them against an authoritative ephemeris before relying on them for critical work.

## 🏙️ Built-in cities

`panchang.location.CITIES` ships with **30+ ready-to-use locations** (Delhi, Mumbai, Chennai, Kolkata, Ujjain, Varanasi, Bikaner, Kota, Bengaluru, Hyderabad, Jaipur, and overseas reference points such as London, New York, Dubai, Singapore, Sydney, Toronto and Kathmandu). Look one up by name:

```python
from panchang.location import city_lookup
loc = city_lookup("Varanasi")
```

## 🗓️ Calendar structure (in progress)

`panchang.calendar_month` resolves the **lunar month (masa)** and paksha, detecting **adhika** (extra) and **kshaya** (lost) months, in both the **amanta** (South) and **purnimanta** (North) conventions.

```python
from panchang.julian import gregorian_to_jd
from panchang.calendar_month import masa_at, paksha_at, purnimanta_name

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

Kalagana is being built phase by phase against a detailed specification (`Docs/hindu_panchang_prompt.md`).

| Phase | Scope | Status |
|---|---|---|
| **1. Astronomy foundation** | Julian Day, ΔT, sidereal time, Sun, Moon, Lahiri ayanamsa, generic solver | ✅ Done |
| **2. Panchang limbs** | Tithi, vara, nakshatra (+pada), yoga, karana, sunrise/sunset/moonrise | ✅ Done |
| **3. Calendar structure** | Masa, paksha, adhika/kshaya masa, amanta/purnimanta, ritu, ayana, samvat eras | 🚧 In progress |
| **4. Muhurta & yogas** | Rahu Kalam, Gulika, Abhijit, Brahma Muhurta, Choghadiya, Hora, Siddhi yogas | ⏳ Planned |
| **5. Eclipses & transits** | Solar/lunar eclipses + Sutak, planetary ingresses, retrograde, combustion | ⏳ Planned |
| **6. Festival engine** | Data-driven `FestivalRule` table + tie-break policies + regional variants | ⏳ Planned |
| **7. Interfaces** | Public API, `day` / `month` / `year` / `festivals` / `eclipses` / `find` CLI, JSON/CSV, multi-language names | ⏳ Planned |

## 📂 Project structure

```text
Kalagana/
├── panchang/               # the library (pure stdlib)
│   ├── __init__.py         # package metadata & re-exports
│   ├── julian.py           # JD conversion, ΔT, sidereal time
│   ├── sun.py              # solar coordinates & equation of time
│   ├── moon.py             # lunar coordinates (Meeus ch. 47)
│   ├── ayanamsa.py         # ayanamsa models
│   ├── solver.py           # root finding on angle functions
│   ├── sunrise.py          # rise / set / transit
│   ├── limbs.py            # tithi, vara, nakshatra, yoga, karana
│   ├── calendar_month.py   # masa, paksha, adhika/kshaya, amanta/purnimanta
│   └── location.py         # Location + built-in city table
├── Docs/
│   └── hindu_panchang_prompt.md   # full project specification
├── .gitignore
└── README.md
```

## 🛠️ Development

Pure standard library, so there's nothing to compile. Run a module directly to explore, or use these smoke checks:

```bash
# sanity check: import + version
python -c "import panchang; print(panchang.__version__)"

# today's vara for a city
python -c "from datetime import date; from panchang.location import city_lookup; from panchang.limbs import day_limbs; print(day_limbs(date.today(), city_lookup('Delhi'))['vara'])"
```

### Conventions

- Type hints on every public function; docstrings state **units** (degrees, days, hours, km).
- The astronomy core is **pure** — no I/O, no global state.
- Units are explicit: longitudes in **degrees**, distances in **km**, times as **Julian Days (TT/UT)** or timezone-aware `datetime`.
- Functions stay small, and astronomy stays separate from calendar and festival rules.

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
