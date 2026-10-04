# 08 — Roadmap

Phases → sprints. Each sprint has a file in `docs/sprints/`. Durations are rough
and assume a small team; treat them as ordering, not commitments.

## Phase 0 — Foundation (Sprint 00)
Set up the app branch, repo layout, Astro + FastAPI skeleton, CI, the package
dependency contract, and the initial design tokens. **Exit:** a deployed
"today's panchang for one city" page + working preview deploys.

## Phase 1 — Core Panchang MVP (Sprints 01–02)
Daily + monthly panchang, year/festival calendar, location switcher, time-format
toggles, PWA install + offline shell. **Exit:** the daily loops a diaspora user
needs, offline-capable and fast.

## Phase 2 — Muhurat & Vrat suite (Sprints 03–04)
Choghadiya/hora (done in package), plus the missing muhurat tools and the
vrat/upavas date pages and festival/vrat detail pages. **Exit:** the "when do I
do X" and "when do I fast" journeys complete.

## Phase 3 — Jyotish & astronomy (Sprints 05–06)
Kundali, match, rashi/gemstone/baby-name tools; planetary positions/transit/
retrograde; eclipse pages. Requires substantial package work on `PyPI-dev`.
**Exit:** astrology-curious journeys covered.

## Phase 4 — Content & depth (Sprint 07)
Devotional corpus (public-domain subset), deities/gurus/pilgrimages, galleries.

## Phase 5 — Offline & polish (Sprint 08)
True offline behavior, performance hardening, a11y pass, analytics.

## Phase 6 — Regional & i18n (Sprint 09)
Regional panchang conventions and localized UI.

## Phase 7 — Launch & growth (Sprint 10)
SEO hardening, sitemaps, feeds, widget, public API docs, launch.

---

## Sprint → plan map

| Sprint | Theme | Primary package work | Primary app work |
|---|---|---|---|
| 00 | Foundation | pin contract | Astro+FastAPI skeleton, tokens |
| 01 | Daily panchang | expose daily fields | panchang page, location, formats |
| 02 | Calendars & festivals | year/tradition polish | year calendar, festival pages |
| 03 | Muhurat suite | vivah/griha/vehicle/property/lagna/gowri/panchaka/do-ghati | muhurat tools |
| 04 | Vrat & festival depth | chandra darshan, shraddha dates | vrat pages, festival detail |
| 05 | Jyotish tools | kundali, match, rashi, gemstone, baby names | jyotish tool pages |
| 06 | Planets & astronomy | positions, transit, retrograde, eclipse accuracy | planet/eclipse pages |
| 07 | Devotional content | — | content collections, galleries |
| 08 | PWA & polish | — | offline, perf, a11y |
| 09 | Regional & i18n | regional conventions | i18n routing + catalogs |
| 10 | Launch & growth | public API docs | SEO, feeds, widget |

## Milestones

- **M0** — App skeleton deployed on `master` (end of Sprint 00).
- **M1** — Public MVP: daily panchang + calendar + PWA (end of Sprint 02).
- **M2** — Muhurat-ready (end of Sprint 03).
- **M3** — Astrology-capable (end of Sprint 06).
- **M4** — Content-complete + offline (end of Sprint 08).
- **M5** — Public launch (end of Sprint 10).

## Cross-cutting tracks (run in every sprint)

- **Package-first:** any new number → `PyPI-dev` → publish → pin in app.
- **Accuracy harness:** golden-date tests in the package back every app page.
- **Perf budget:** enforced in app CI (Lighthouse).
- **Parity dashboard:** P1 completion tracked against `02-feature-parity.md`.
