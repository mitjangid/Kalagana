# Sprint 01 — Daily Panchang

**Goal:** deliver a complete, shareable daily panchang page (the site's most-used
surface), matching the Drik day-panchang field set we already support, plus the
first tranche of missing daily fields.

## Scope
- **In:** date navigation, full panchang render, time formats, muhurta blocks,
  shareable URLs, wordwide city search.
- **Out:** muhurat planning tools, jyotish.

## Package work (`PyPI-dev`)
- [ ] World city search/resolve (name → lat/lon/tz), beyond the compact table.
- [ ] Elevation input support for sunrise/sunset.
- [ ] Extend `/day` with: Dinamana, Ratrimana, Madhyahna, Drik/Vedic Ritu &
      Ayana, Pravishte/Gate.
- [ ] Add: Vijaya Muhurta, Godhuli Muhurta, Pratah/Sayahna Sandhya, Amrit Kalam,
      Nishita Muhurta.
- [ ] Add: Panchaka Rahita Muhurta + Udaya Lagna windows for a day.
- [ ] Add: Chandrabalam & Tarabalam tables.
- [ ] Add: Vinchudo windows.

## App work (`master`)
- [ ] `/panchang/{yyyy-mm-dd}/{city}` page (SSR/SSG + islands).
- [ ] Date nav: prev/next/today + date picker; "panchang day = sunrise→sunrise".
- [ ] Time format toggle: 12h / 24h / 24-plus; "past midnight → next day" suffix.
- [ ] Amanta/Purnimanta toggle; ayanamsa selector.
- [ ] Render sections: sunrise/moon, five limbs with end times, months/samvat,
      rashi/nakshatra, ritu/ayana/dinamana, auspicious & inauspicious timings,
      panchaka rahita, udaya lagna, chandrabalam/tarabalam.
- [ ] Share/deep-link button; OG image per date+city.
- [ ] JSON-LD `BreadcrumbList` + `FAQPage`.

## Deliverables
- Daily panchang page, fully navigable, shareable, cacheable.
- Matching CLI/REST output for parity verification.

## Definition of Done
- [ ] Golden-date tests in the package back every rendered field.
- [ ] Lighthouse ≥ 95; LCP < 2.5s.
- [ ] Page renders correctly for at least one non-IST city (DST check).
- [ ] `/day` docstring & `docs/api/README.md` updated.

## Dependencies & risks
- Many new fields → several package releases; sequence them, don't batch into
  one giant release.
- Field naming must match user expectations (parity review vs `02`).
