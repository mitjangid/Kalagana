# 05 — Data Model & API Contract

## 1. Principle

The app API is a **thin, cacheable, versioned** JSON surface over the package.
Response shapes are derived from the package's existing dataclasses
(`Panchang`, `FestivalOccurrence`, `Eclipse`, muhurta windows) which already
serialize via `to_dict()` / `_occ()`.

## 2. Existing package surface (baseline)

| Route | Package |
|---|---|
| `GET /health` | `kalagana.__version__` |
| `GET /cities` | `kalagana.location.CITIES` |
| `GET /ayanamsas` | `kalagana.ayanamsa.SUPPORTED` |
| `GET /day?date=&city=` | `api.daily_panchang` |
| `GET /month?month=` | `api.daily_panchang` loop |
| `GET /festivals?year=` | `festivals.festivals_for_year` |
| `GET /eclipses?year=` | `api.eclipses_for_year` |
| `GET /muhurta?date=` | `muhurta.day_timings` |
| `GET /find?name=&after=` | `festivals.find_next` |

Common params: `city` | `lat`+`lon`(+`tz`), `ayanamsa`, `tradition`,
`month_system`, `kind`, `major_only`, `no_islamic`, `no_fixed`.

## 3. API additions needed for parity

New/extended endpoints the app will require (add on `PyPI-dev`, then consume):

| Route (proposed) | Purpose | Status |
|---|---|---|
| `/day` extended | add the bolded daily fields from `02` (dinamana, panchaka rahita, udaya lagna, chandrabalam, tarabalam, …) | extend |
| `/muhurat/vivah?year=` | marriage muhurat dates | new |
| `/muhurat/griha-pravesh?year=` | housewarming dates | new |
| `/muhurat/vehicle?year=` | vehicle purchase dates | new |
| `/muhurat/property?year=` | property purchase dates | new |
| `/muhurat/lagna?date=` | Lagna table / udaya lagna | new |
| `/muhurat/gowri?date=` | Gowri panchangam | new |
| `/muhurat/panchaka-rahita?date=` | Panchaka Rahita blocks | new |
| `/muhurat/do-ghati?date=` | Do Ghati muhurat | new |
| `/panchang/vinchudo?date=` | Vinchudo windows | new |
| `/chandrabalam?date=` / `/tarabalam?date=` | strength tables | new |
| `/vrat/ekadashi?year=` etc. | vrat lists (some exist via `/festivals`) | extend |
| `/planets/positions?date=` | planetary longitudes | new |
| `/planets/transit?from=&to=` | gochara | new |
| `/planets/retrograde?year=` | vakri/margi | new |
| `/kundali` (POST birth data) | birth chart | new |
| `/match` (POST two birth data) | horoscope match | new |
| `/rashi?date=&lat=&lon=` | rashi/moonsign/sunsign | extend |
| `/baby-names?...` | name finder | new |
| `/format` | time-format helpers | app-side |

> Naming: keep REST resources plural and stable; version under `/_v1` if we
> ever expose publicly.

## 4. Response envelope conventions

- Datetimes: ISO-8601 **with offset** (local to the requested place).
- Times intended for display come as ISO and are formatted client-side so the
  12h/24h/24-plus toggle is a pure UI concern.
- Every computed response includes `"meta": { ayanamsa, tradition, city/lat/lon,
  tz, version }` so the UI can show provenance and cache correctly.
- Errors: `{ "error": code, "message": ... }` (already the pattern in
  `kalagana/server.py`).

## 5. Caching model

| Key | TTL |
|---|---|
| `/day?date&city&ayanamsa&month_system` | long (immutable for a past date) → `s-maxage=86400, SWR` |
| `/month`, `/festivals?year` | long; invalidate never (dates are deterministic) |
| `/health`, `/cities`, `/ayanamsas` | short |
| `/today` convenience | until next local sunrise |

Server-side: an in-process LRU (already added for the festival day-info scan)
plus an HTTP cache layer. Edge caches the JSON.

## 6. Content data model (app-only)

Non-calculation content is authored as Markdown/MDX with frontmatter and
validated at build time.

```yaml
# festivals content, docs/content model (illustrative)
---
slug: diwali
name: Diwali
aliases: [Deepavali]
tradition: [north, south, west]
computed:                        # resolved by the package at build time
  rule: "Kartika Amavasya (purnimanta)"
  tithi: Amavasya
significance: "…"
vidhi: [ … ]
related: [Lakshmi Puja, Govardhan Puja, Bhai Dooj]
---
```

- **Content collections:** `festivals`, `vrat`, `deities`, `aarti`, `chalisa`,
  `stotram`, `puja-vidhi`, `pilgrim-places`, `gurus`.
- **Rule-first linking:** a festival page links to its *computed* date via a
  rule reference, so pages never hard-code dates.
- **Localization:** content carries a locale; fall back to `en`.

## 7. Package ↔ app version contract

- App pins `kalagana==X.Y.Z` in the API service.
- The app declares the **minimum package version** per feature (e.g. "muhurat
  suite requires kalagana ≥ 0.4"). CI on `master` verifies the pinned version
  resolves from PyPI.
- Package `MONTH`/minor bumps for new endpoints; app deploys independently.
