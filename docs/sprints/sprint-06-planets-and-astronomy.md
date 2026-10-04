# Sprint 06 — Planets & Astronomy

**Goal:** add planetary events and astronomical pages, and raise eclipse
accuracy from "approximate detector" to a proper eclipse page.

## Scope
- **In:** planetary positions, transits (gochara), retrograde/margi, combustion
  (asta), eclipse dates (solar/lunar) with better type/timing, seasons,
  solstices/equinoxes.
- **Out:** jyotish tools (previous sprint), content.

## Package work (`PyPI-dev`)
- [ ] Planetary longitude engine for all grahas (Sun, Moon, Mercury, Venus,
      Mars, Jupiter, Saturn, Rahu/Ketu) — reuse Sprint 05 ephemeris.
- [ ] `planetary_positions(date)` → sidereal longitudes, nakshatra/pada, rashi.
- [ ] `planet_transit(from, to)` (gochara) with pada-level granularity.
- [ ] `retrograde_windows(year)` (vakri/margi) and `combustion(year)` (asta/uday).
- [ ] Improve eclipse detection: types (total/annular/partial/penumbral),
      greatest-time, and visibility/location notes.
- [ ] Seasons, solstices, equinoxes as first-class data.

## App work (`master`)
- [ ] `/planets/positions?date=` — table + degree bars.
- [ ] `/planets/transit` — upcoming transit events.
- [ ] `/planets/retrograde`, `/planets/combustion`.
- [ ] `/eclipses/{yyyy}/{city}` — solar + lunar with type and greatest time.
- [ ] `/astronomy/seasons`, `/solstices`, `/equinoxes`.
- [ ] "Upcoming planetary events" widget (like Drik's home sidebar).

## Deliverables
- Planet & astronomy section.
- Eclipse pages with locality and caveats.

## Definition of Done
- [ ] Planetary positions verified against an authoritative ephemeris.
- [ ] Eclipse dates verified for a set of known eclipses.
- [ ] `02` Section H updated.

## Dependencies & risks
- Ephemeris accuracy is the hard part; keep the "approximate" caveat honest
  until verified, and always state the convention (sidereal, ayanamsa).
