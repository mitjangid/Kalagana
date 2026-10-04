# Sprint 02 — Calendars & Festivals

**Goal:** ship the year & month calendars and a crawlable page per festival
plus per year+city — the SEO backbone.

## Scope
- **In:** year calendar, month grid, festival list pages, festival detail pages,
  festival date tables computed per year.
- **Out:** muhurat tools, jyotish, devotional corpus.

## Package work (`PyPI-dev`)
- [ ] Ensure `/festivals?year=` returns `kind`, lunar refs, and stable ordering.
- [ ] Add `major` flag / curated "top festivals" grouping.
- [ ] Regional festival sets polish (Tamil/Malayalam/Sankranti) where cheap.
- [ ] Provide a "festival slug + aliases" registry so content can link to rules.

## App work (`master`)
- [ ] `/calendar/{yyyy}/{city}` year calendar (12 month cards) — reuse current UI.
- [ ] `/panchang/{yyyy-mm}/{city}` month grid with tithi + festival per cell.
- [ ] `/festivals/{yyyy}/{city}` list with kind/major/islamic/fixed filters.
- [ ] `/festivals/{slug}` detail page: significance, vidhi, tithi rule, computed
      dates for current + next year, related festivals.
- [ ] `Event` JSON-LD for each festival occurrence; sitemap entries.
- [ ] ICS/RSS feed of upcoming festivals.

## Deliverables
- Year calendar + month grid.
- One detail page per P1 festival with computed dates.
- Sitemap + feeds.

## Definition of Done
- [ ] Festival pages build from content collections + package data.
- [ ] Diwali 2024 = 2024-10-31 and other golden dates verified on-page.
- [ ] `02-feature-parity.md` Section C/F updated to `have`.

## Dependencies & risks
- Content authoring is the bottleneck → ship a subset, link the rest.
- Slug stability (SEO) → freeze slugs once published.
