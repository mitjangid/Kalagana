# Kalagana API Reference

*Offline **Drik Panchang / Panchangam**, tithi, nakshatra, muhurat and Hindu, Islamic & national festival calculations — as a Python library and a local REST API.*

Kalagana exposes **two** APIs over the same pure, offline calculation core:

1. a **Python library** (`import kalagana`) —
2. a **local REST API** (`python -m kalagana.server`), which is a thin JSON wrapper around #1.

Both compute an **offline Drik panchang**: tithi, vara, nakshatra, yoga, karana, sunrise/sunset, moonrise/moonset, muhurta windows, eclipses, the lunar calendar structure, and **festival dates derived from rules** (never stored).

> Nothing here uses the network, a database, or downloaded ephemeris files. The HTTP server performs no outbound I/O — it only answers local requests.

---

## 1. Running the REST API

```bash
# Module form
python -m kalagana.server --host 127.0.0.1 --port 8765

# CLI form (equivalent)
python -m kalagana serve --port 8765
```

Once started:

```text
Kalagana API v0.1.0 listening on http://127.0.0.1:8765
Endpoints: /ayanamsas /cities /day /eclipses /festivals /find /health /month /muhurta
```

All responses are `application/json; charset=utf-8`. CORS is enabled (`Access-Control-Allow-Origin: *`) so a browser page can call the local server.

### Import files for API tools

| Tool | File |
|---|---|
| **OpenAPI 3.1** (Postman, Insomnia, Swagger UI, Bruno, codegen) | [`api/openapi.json`](api/openapi.json) |
| **Postman** collection | [`api/postman/Kalagana.postman_collection.json`](api/postman/Kalagana.postman_collection.json) |
| **Postman** environment | [`api/postman/Kalagana.postman_environment.json`](api/postman/Kalagana.postman_environment.json) |
| **Insomnia** export | [`api/insomnia/Kalagana.insomnia.json`](api/insomnia/Kalagana.insomnia.json) |
| **Bruno** collection | [`api/bruno/`](api/bruno) |

Import them, set the `baseUrl` variable to `http://127.0.0.1:8765`, start the server, and every request is ready to send.

### Configuration

Kalagana runs with no configuration. Optional settings come from the environment and a local `.env` file (parsed by [`kalagana/config.py`](kalagana/config.py); no `python-dotenv` dependency). Copy the annotated template and edit it:

```bash
cp .env.example .env
```

| Variable | Default | Effect |
|---|---|---|
| `KALAGANA_HOST` | `127.0.0.1` | Server bind address |
| `KALAGANA_PORT` | `8765` | Server port |
| `KALAGANA_LOG_REQUESTS` | `true` | Log each request to stderr |
| `KALAGANA_CITY` | `delhi` | Fallback location when a request omits one |
| `KALAGANA_LAT` / `KALAGANA_LON` | — | Fallback coordinates (take precedence over `KALAGANA_CITY`) |
| `KALAGANA_TZ` | `Asia/Kolkata` | Fallback timezone |
| `KALAGANA_AYANAMSA` | `lahiri` | Default ayanamsa |
| `KALAGANA_TRADITION` | `north` | Default tradition |
| `KALAGANA_MONTH_SYSTEM` | `purnimanta` | Default month naming |
| `KALAGANA_INCLUDE_MONTHLY` | `true` | Include monthly observances in `/festivals` |
| `KALAGANA_INCLUDE_ISLAMIC` | `true` | Include Islamic (Hijri) festivals |
| `KALAGANA_INCLUDE_FIXED` | `true` | Include fixed-date national/observance days |
| `KALAGANA_FIND_YEARS` | `3` | Look-ahead for `/find` |
| `KALAGANA_LANG` | `en` | Preferred name language |
| `KALAGANA_ENV_FILE` | `.env` | Path of the env file to read |
| `KALAGANA_STRICT` | `false` | Raise on invalid values instead of falling back |

The full annotated list is in [`.env.example`](.env.example). A variable already set in the real environment is never overwritten by `.env`. Read them in code via `kalagana.config.load_settings()`.

---

## 2. Conventions

### Location

Every data endpoint needs a place. Supply **either**:

- `city=<built-in name>` — see [`/cities`](#cities); e.g. `delhi`, `mumbai`, `london`.
- **or** `lat=<deg>&lon=<deg>` (and optionally `tz=<IANA zone>`). Longitude is **east-positive**.

`tz` overrides the city's default timezone (default `Asia/Kolkata`).

If a request supplies **neither**, the server falls back to `KALAGANA_LAT`/`KALAGANA_LON`, or `KALAGANA_CITY` (see [Configuration](#configuration)).

### Common query parameters

| Parameter | Type | Default | Applies to | Meaning |
|---|---|---|---|---|
| `city` | string | — | all data endpoints | Built-in city key |
| `lat` | float | — | all data endpoints | Latitude, north positive |
| `lon` | float | — | all data endpoints | Longitude, east positive |
| `tz` | string | `Asia/Kolkata` | all data endpoints | IANA timezone |
| `ayanamsa` | string | `lahiri` | day, month, festivals, find | `lahiri`, `raman`, `kp`, `yukteshwar`, `fagan_bradley` |
| `tradition` | string | `north` | festivals, find | `north`, `south`, `tamil`, `telugu`, `kannada`, `malayalam`, `bengali`, `odia`, `gujarati`, `marathi` |
| `major_only` | bool | `false` | festivals | Skip monthly observances (Ekadashi, Purnima, …) |
| `kind` | csv | — | festivals | Keep only these categories: `festival`, `national`, `observance` |
| `no_islamic` | bool | `false` | festivals | Exclude the Islamic (Hijri) festivals |
| `no_fixed` | bool | `false` | festivals | Exclude the fixed-date national/observance days |
| `no_muhurta` | bool | `false` | day | Skip muhurta windows for a faster response |

Booleans accept `1`, `true`, `yes`, `on` (case-insensitive).

### Timestamps and times

- Instants are ISO-8601 **with offset**, in the location's timezone, e.g. `2024-08-26T05:56:20.712569+05:30`.
- Dates are `YYYY-MM-DD`; months are `YYYY-MM`.
- Limb segments carry `start` and `end` (the limb is *active* over that interval).

### Errors

Errors return a JSON body and an appropriate status:

```json
{ "error": "bad_request", "message": "Missing required parameter: date" }
```

| Status | `error` | Cause |
|---|---|---|
| `400` | `bad_request` | Missing/invalid parameter, unknown city, bad date |
| `404` | `not_found` | Unknown path, or `find` produced no occurrence |
| `500` | `internal_error` | Unexpected failure |

---

## 3. Endpoint reference

### `GET /health`

Liveness and version.

```bash
curl -s http://127.0.0.1:8765/health
```

```json
{ "status": "ok", "name": "kalagana", "version": "0.1.0" }
```

### `GET /cities`

The built-in city table used for `city=`.

```bash
curl -s http://127.0.0.1:8765/cities
```

```json
{
  "count": 33,
  "cities": [
    { "key": "delhi", "name": "Delhi", "lat": 28.6139, "lon": 77.209, "tz": "Asia/Kolkata" }
  ]
}
```

### `GET /ayanamsas`

Supported ayanamsa models and the default.

```json
{ "default": "lahiri", "ayanamsas": ["fagan_bradley", "kp", "lahiri", "raman", "yukteshwar"] }
```

### `GET /day`

Full panchang for one date and place.

**Required:** `date` (`YYYY-MM-DD`). **Plus** a location (`city` or `lat`+`lon`).

```bash
curl -s "http://127.0.0.1:8765/day?date=2024-08-26&city=delhi"
```

```json
{
  "date": "2024-08-26",
  "location": { "name": "Delhi", "lat": 28.6139, "lon": 77.209, "tz": "Asia/Kolkata" },
  "sunrise": "2024-08-26T05:56:20.712569+05:30",
  "sunset": "2024-08-26T18:49:03.588124+05:30",
  "moonrise": "2024-08-26T23:21:04.429455+05:30",
  "moonset": "2024-08-26T12:56:58.199109+05:30",
  "vara": "Somavara",
  "vara_en": "Monday",
  "paksha": "Krishna",
  "masa_amanta": "Shravana",
  "masa_purnimanta": "Bhadrapada",
  "samvat": 2081,
  "shaka": 1946,
  "samvatsara": "Krodhi",
  "ritu": "Varsha",
  "ayana": "Dakshinayana",
  "tithi": [
    { "name": "Krishna Ashtami", "number": 23,
      "start": "2024-08-26T05:57:34.479404+05:30",
      "end": "2024-08-27T02:21:48.479404+05:30" }
  ],
  "nakshatra": [ { "name": "Krittika", "number": 3, "start": "...", "end": "..." } ],
  "yoga": [ { "name": "Vyaghata", "number": 13, "start": "...", "end": "..." } ],
  "karana": [ { "name": "Balava", "number": 3, "start": "...", "end": "..." } ],
  "muhurta": {
    "rahu_kalam":   { "name": "Rahu Kalam",   "start": "...", "end": "..." },
    "yamaganda":    { "name": "Yamaganda",    "start": "...", "end": "..." },
    "gulika_kalam": { "name": "Gulika Kalam", "start": "...", "end": "..." },
    "abhijit":      { "name": "Abhijit",      "start": "...", "end": "..." },
    "brahma_muhurta": { "name": "Brahma Muhurta", "start": "...", "end": "..." },
    "durmuhurta":  [ { "name": "Durmuhurta", "start": "...", "end": "..." } ],
    "choghadiya":  { "day": [ ... ], "night": [ ... ] },
    "hora":        { "day": [ ... ], "night": [ ... ] }
  }
}
```

`tithi`, `nakshatra`, `yoga` and `karana` are **lists** because two segments can occur within one Hindu day, and a segment can span two sunrises.

Add `&no_muhurta=true` to omit the `muhurta` object.

### `GET /month`

Day-by-day summary for a Gregorian month.

**Required:** `month` (`YYYY-MM`). **Plus** a location.

```bash
curl -s "http://127.0.0.1:8765/month?month=2024-10&city=delhi"
```

```json
{
  "month": "2024-10",
  "count": 31,
  "days": [
    { "date": "2024-10-01", "vara": "Mangalavara", "vara_en": "Tuesday",
      "paksha": "Krishna", "tithi": "Amavasya", "nakshatra": "Hasta",
      "sunrise": "2024-10-01T06:14:00+05:30", "sunset": "2024-10-01T18:13:00+05:30" }
  ]
}
```

### `GET /festivals`

Festival dates for a year — computed from the rule table, not stored.

**Required:** `year`. **Plus** a location.

```bash
curl -s "http://127.0.0.1:8765/festivals?year=2026&city=delhi&major_only=true"

# Only the three gazetted national holidays
curl -s "http://127.0.0.1:8765/festivals?year=2026&city=delhi&kind=national"
```

```json
{
  "year": 2026,
  "count": 78,
  "festivals": [
    { "name": "Republic Day", "date": "2026-01-26", "month": null, "paksha": null,
      "tithi": null, "note": "Gazetted national holiday.", "kind": "national" },
    { "name": "Makar Sankranti", "date": "2026-01-15", "month": null, "paksha": null,
      "tithi": null, "note": "Sun enters Makara (sidereal).", "kind": "festival" },
    { "name": "Eid al-Fitr", "date": "2026-03-20", "month": null, "paksha": null,
      "tithi": null, "note": "1 Shawwal (Id-ul-Fitr). Tabular Hijri date…", "kind": "festival" }
  ]
}
```

Each festival carries a **`kind`** — `festival`, `national` or `observance`. The three rule groups (Hindu lunar/solar, Islamic `hijri`, and fixed Gregorian) can be toggled with `include_monthly`, `no_islamic` and `no_fixed` (server defaults come from `KALAGANA_INCLUDE_*`).

> **Islamic dates** use the tabular (arithmetic) Hijri calendar, so they may differ by a day or two from the locally sighted date.

### `GET /eclipses`

Approximate solar/lunar eclipses for a year (dates and rough type).

**Required:** `year`. **Plus** a location.

```json
{
  "year": 2024,
  "note": "Approximate detector; dates and rough type only.",
  "count": 4,
  "eclipses": [
    { "kind": "lunar", "date": "2024-03-25", "greatest": "2024-03-25T12:30:00+05:30",
      "type": "penumbral", "moon_latitude": -1.02 }
  ]
}
```

> This is an indicator, not a Besselian-element solution. Use it to know *when* an eclipse window occurs; consult an authoritative ephemeris for exact circumstances.

### `GET /muhurta`

Daily muhurta windows for one date.

**Required:** `date`. **Plus** a location.

```bash
curl -s "http://127.0.0.1:8765/muhurta?date=2024-08-26&city=delhi"
```

```json
{
  "date": "2024-08-26",
  "muhurta": {
    "rahu_kalam": { "name": "Rahu Kalam", "start": "...", "end": "..." },
    "abhijit": { "name": "Abhijit", "start": "...", "end": "..." },
    "choghadiya": { "day": [ ... ], "night": [ ... ] }
  }
}
```

### `GET /find`

The next occurrence of a named festival on/after a date.

**Required:** `name`. **Optional:** `after` (default today), `tradition`, `ayanamsa`. **Plus** a location.

```bash
curl -s "http://127.0.0.1:8765/find?name=Diwali&after=2025-01-01&city=delhi"
```

```json
{ "name": "Diwali", "date": "2025-10-20", "month": "Kartika",
  "paksha": "Krishna", "tithi": "Amavasya", "note": "Amavasya at pradosh (Lakshmi Puja)." }
```

Returns `404` if no occurrence is found within three years.

---

## 4. Python library API

The HTTP layer wraps these directly.

### Top level

```python
from datetime import date
from kalagana import (
    Location, CITIES, city_lookup,
    daily_panchang, festivals_for_year, festival_dates, find_next,
    eclipses_for_year,
    Panchang, Eclipse, FestivalOccurrence, FestivalRule,
    tithi_name, AYANAMSAS,
)
```

### `Location`

```python
Location(name, lat, lon, tz="Asia/Kolkata")   # lon east-positive; tz = IANA name
city_lookup("Varanasi")                        # -> Location from the built-in table
```

### `daily_panchang(day, loc, ayanamsa="lahiri", month_system="purnimanta", with_muhurta=True) -> Panchang`

Returns a [`Panchang`](#panchang-object) with `sunrise`, `sunset`, `moonrise`, `moonset`, `vara`, `tithi`, `nakshatra`, `yoga`, `karana`, era fields, and `muhurta`. Call `panchang.to_dict()` for the exact JSON shown for `GET /day`.

### `festivals_for_year(year, loc, tradition="north", ayanamsa="lahiri", include_monthly=True, include_islamic=True, include_fixed=True, kinds=None) -> list[FestivalOccurrence]`

`festival_dates` is an alias. Each occurrence has `name`, `date`, `month`, `paksha`, `tithi`, `note` and `kind` (`festival` / `national` / `observance`). Pass `kinds=("national",)` to filter, or `include_islamic=False` / `include_fixed=False` to drop a whole rule group.

```python
from datetime import date
from kalagana import festivals_for_year, national_holidays, city_lookup

delhi = city_lookup("Delhi")
festivals_for_year(2026, delhi, include_monthly=False, kinds=("national",))
national_holidays(2026, delhi)          # the three gazetted holidays
```

### `national_holidays(year, loc, tradition="north", kinds=("national",), **kwargs) -> list[FestivalOccurrence]`

Fixed-date national holidays (Republic Day, Independence Day, Gandhi Jayanti). Pass `kinds=("national", "observance")` to include the commemorative days too.

### `find_next(name, after, loc, tradition="north", ayanamsa="lahiri") -> FestivalOccurrence | None`

### `eclipses_for_year(year, loc) -> list[Eclipse]`

Each `Eclipse` has `kind` (`"solar"`/`"lunar"`), `date`, `greatest`, `eclipse_type`, `moon_latitude`.

### Lower-level modules

| Module | Key functions |
|---|---|
| `kalagana.julian` | `gregorian_to_jd`, `datetime_to_jd`, `jd_to_datetime`, `delta_t`, `greenwich_apparent_sidereal_time` |
| `kalagana.sun` / `kalagana.moon` | `sun_apparent_longitude`, `sun_declination`, `moon_longitude`, `moon_latitude`, `moon_distance`, `moon_ra_dec` |
| `kalagana.ayanamsa` | `ayanamsa_degrees`, `SUPPORTED` |
| `kalagana.solver` | `solve_angle`, `find_crossing`, `next_crossing`, `bisect` |
| `kalagana.sunrise` | `sunrise_sunset`, `moonrise_moonset`, `solar_noon` |
| `kalagana.limbs` | `tithi_number`, `tithi_name`, `nakshatra_number`, `nakshatra_pada`, `yoga_number`, `karana_number`, `karana_name`, `vara_name`, `day_limbs` |
| `kalagana.calendar_month` | `masa_at`, `paksha_at`, `purnimanta_name`, `next_new_moon`, `prev_new_moon`, `next_full_moon`, `prev_full_moon`, `sankranti_rashis_between` |
| `kalagana.eras` | `vikram_samvat`, `shaka_year`, `samvatsara_name`, `kollam_year`, `bengali_year`, `ritu`, `ayana` |
| `kalagana.muhurta` | `rahu_kalam`, `yamaganda`, `gulika_kalam`, `abhijit_muhurta`, `brahma_muhurta`, `durmuhurta`, `choghadiya`, `hora`, `day_timings` |
| `kalagana.festivals` | `FestivalRule`, `FESTIVAL_RULES`, `FIXED_RULES`, `ISLAMIC_RULES`, `KINDS`, `rules_by_name`, `festival_dates`, `national_holidays`, `find_next` |
| `kalagana.hijri` | `hijri_to_gregorian`, `hijri_to_jd`, `hijri_years_for_gregorian`, `HIJRI_MONTHS` (tabular Islamic calendar) |
| `kalagana.server` | `KalaganaAPI`, `create_server`, `main` |
| `kalagana.config` | `Settings`, `load_settings`, `load_env_file` |

### `Panchang` object

| Field | Type | Notes |
|---|---|---|
| `date` | `datetime.date` | |
| `location` | `Location` | |
| `sunrise`, `sunset`, `moonrise`, `moonset` | `datetime \| None` | `None` at polar locations |
| `vara`, `vara_en` | `str` | e.g. `Somavara`, `Monday` |
| `tithi`, `nakshatra`, `yoga`, `karana` | `list[Limb]` | Each `Limb` has `name`, `number`, `start`, `end` |
| `paksha` | `str` | `Shukla` / `Krishna` |
| `masa_amanta`, `masa_purnimanta` | `str` | Lunar month in each convention |
| `samvat`, `shaka` | `int` | Vikram Samvat, Shaka year |
| `samvatsara` | `str` | 60-year cycle name |
| `ritu`, `ayana` | `str` | Season, half-year |
| `muhurta` | `dict` | Windows (see `GET /day`) |

### Embedding the server

```python
from kalagana.server import create_server

httpd, api = create_server("127.0.0.1", 8765)
httpd.serve_forever()          # or run it in a thread
```

`api.routes` maps paths to callables that take a `dict[str, str]` of query params.

---

## 5. Accuracy & limits

| Quantity | Method | Rated accuracy |
|---|---|---|
| Sun apparent longitude | Meeus ch. 25 | ≈ 0.01° |
| Moon longitude/lat/dist | Meeus ch. 47 full series | ≈ 10″ |
| Sunrise / sunset | Meeus ch. 15, altitude −0.833° | ≈ 1 minute |
| New-moon instants | root finder on the Moon–Sun elongation | within ~2 minutes |
| Ayanamsa | Lahiri at J2000 + IAU precession | across 1900–2100 |

Known limits: eclipses are approximate; Raman/KP ayanamsa constants are documented approximations; on Windows without the `tzdata` package, non-Indian timezones fall back to fixed standard offsets (India is exact).

## 6. License

MIT — see [`LICENSE`](LICENSE). Festival rules encode tradition and convention; regional differences are options, not bugs.
