# Contributing to Kalagana

Thanks for your interest! Kalagana is a pure-standard-library project, so there
is nothing to compile — clone, run the checks, and edit.

## 🛠️ Development

No dependencies are needed to run the library. For the test/build tooling:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows;  source .venv/bin/activate elsewhere
pip install -e ".[dev]"
```

Smoke checks:

```bash
python -m kalagana.selftest            # accuracy self-test
python -m pytest -q                    # unit tests
python -m kalagana day 2026-11-08 --city delhi
```

### Conventions

- Type hints on every public function; docstrings state **units** (degrees, days, hours, km).
- The astronomy core is **pure** — no I/O, no global state.
- Units are explicit: longitudes in **degrees**, distances in **km**, times as **Julian Days (TT/UT)** or timezone-aware `datetime`.
- Functions stay small; astronomy stays separate from calendar and festival rules.

### Ground rules

1. **Never hardcode a festival date** for a specific year — every date must fall out of computation.
2. **Cite your source** for any new formula (Meeus chapter, IAU resolution, …).
3. When traditions disagree, implement **both** as options, document the default, and say so.
4. Report measured accuracy honestly — **do not claim accuracy you have not tested**.

## 🏗️ Architecture

The design keeps a clean separation between **astronomy**, the **calendar**, and **festival rules**:

```text
   🌍 Astronomy                 📅 Calendar                 🎉 Festival rules
  julian  (JD, ΔT, GMST)       calendar_month (masa…)       festivals/rules.py
  sun     (λ, δ, α, EoT)       eras (Vikram, Shaka…)        festivals/engine.py
  moon    (λ, β, distance)     muhurta (Rahu Kalam…)        hijri (tabular)
  ayanamsa (precession)        eclipses / transits
  solver  (root finding)
  sunrise (rise/set/transit)
  limbs   (tithi, vara, …)
```

## 📂 Project structure

```text
Kalagana/
├── kalagana/               # the library (pure stdlib)
│   ├── julian.py           # JD conversion, ΔT, sidereal time
│   ├── sun.py  moon.py     # solar / lunar coordinates (Meeus)
│   ├── ayanamsa.py         # ayanamsa models
│   ├── solver.py           # root finding on angle functions
│   ├── sunrise.py          # rise / set / transit
│   ├── limbs.py            # tithi, vara, nakshatra, yoga, karana
│   ├── calendar_month.py   # masa, paksha, adhika/kshaya, amanta/purnimanta
│   ├── eras.py             # Vikram, Shaka, samvatsara, ritu, ayana
│   ├── muhurta.py          # Rahu Kalam, Choghadiya, Hora, Durmuhurta
│   ├── hijri.py            # tabular Islamic (Hijri) calendar
│   ├── festivals/          # rule table + engine (data-driven dates)
│   ├── api.py  cli.py      # public API and command line
│   ├── server.py           # offline REST API (stdlib http.server)
│   ├── config.py           # optional environment/.env configuration
│   └── location.py         # Location + built-in city table
├── api/                    # OpenAPI + Postman + Insomnia + Bruno import files
├── tests/                  # unittest suite + reference dates
├── scripts/release.py      # version bump / build / tag / GitHub release
├── .github/workflows/      # CI, release and container automation
├── FESTIVAL_COVERAGE.md    # coverage vs. Drik Panchang
└── API_README.md           # detailed API reference
```

## 📚 Module reference

| Module | Purpose |
|---|---|
| `kalagana.julian` | Julian Day conversion, **ΔT** (Espenak & Meeus), sidereal time. |
| `kalagana.sun` / `kalagana.moon` | Solar and lunar coordinates (Meeus ch. 25 & 47). |
| `kalagana.ayanamsa` | Ayanamsa selection and propagation (Lahiri default). |
| `kalagana.solver` | Angle root finder, crossing finders, bisection. |
| `kalagana.sunrise` | Sunrise, sunset, moonrise, moonset, solar noon. |
| `kalagana.limbs` | The five limbs: tithi, nakshatra (+pada), yoga, karana, vara. |
| `kalagana.calendar_month` | Lunar month (masa), sankranti, adhika/kshaya, amanta/purnimanta. |
| `kalagana.hijri` | Tabular Islamic calendar conversion. |
| `kalagana.festivals` | `FestivalRule` table + engine (Hindu, Islamic, fixed-date). |
| `kalagana.api` / `kalagana.server` | `Panchang`, `daily_panchang`, `eclipses_for_year`; REST API. |
| `kalagana.location` | `Location` dataclass, built-in `CITIES`, timezone resolution. |

## 🚀 Releasing

The version lives in `pyproject.toml` and `kalagana/__init__.py`; the helper keeps both in sync (standard library only).

```bash
python scripts/release.py current                  # show the current version
python scripts/release.py bump patch               # 0.1.0 -> 0.1.1 (rewrites both files)
python scripts/release.py build                    # sdist + wheel into dist/   (needs: pip install build)
python scripts/release.py tag --push               # annotated tag vX.Y.Z and push
python scripts/release.py --dry-run release --bump patch --push
```

`--dry-run` prints the commands instead of running them, and **nothing is pushed without `--push`**.

### Automation

| Workflow | Trigger | Result |
|---|---|---|
| `ci.yml` | push / PR | self-test + unit tests on Ubuntu, Windows and macOS, Python 3.10 and 3.13 |
| `release.yml` | tag `v*` | builds sdist + wheel, creates the **GitHub Release**, publishes to **PyPI** (trusted publishing) |

> **Packaging note:** the package is published to **PyPI**. Publishing uses a [Trusted Publisher](https://docs.pypi.org/trusted-publishers/) — configure it for this repo, the `release.yml` workflow and the `pypi` environment; no API token is stored.

## 📚 References

- Jean Meeus, *Astronomical Algorithms*, 2nd edition — chapters 7, 12, 15, 22, 25, 28, 47.
- Fred Espenak & Jean Meeus, *Polynomial Expressions for Delta T* (NASA/GSFC).
- IAU 2006 general precession in longitude.
- *The Indian Astronomical Ephemeris* / **Rashtriya Panchang** (Lahiri / Chitrapaksha ayanamsa).
