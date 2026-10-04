# Sprint 04 — Vrat & Festival Depth

**Goal:** complete the fasting (vrat/upavas) date coverage and deepen festival
pages with content and detail.

## Scope
- **In:** all vrat date lists, vrat detail pages with katha, festival detail
  enrichment (vidhi, related, regional variants).
- **Out:** jyotish, planets.

## Package work (`PyPI-dev`)
- [ ] Chandra Darshan dates.
- [ ] Satyanarayana Puja dates.
- [ ] Dwadashi dates (complete), Skanda Sashti / Karthigai dates.
- [ ] Shraddha (Pitru Paksha) dates + Sarvapitru Amavasya.
- [ ] Satyanarayana / pradosham / chaturthi consistency pass.
- [ ] "Nakshatra-vrat" mappings (e.g. Karthigai, Skanda Sashti) where relevant.

## App work (`master`)
- [ ] `/vrat/{slug}` pages (ekadashi, purnima, amavasya, sankashti chaturthi,
      pradosham, shivaratri, durgashtami, kalashtami, ganesha chaturthi,
      chandra darshan, satyanarayana puja, skanda sashti, shraddha).
- [ ] Each vrat page: meaning + katha (content) + computed dates table +
      parana/next-day info where applicable.
- [ ] Cross-link every vrat to the festival it belongs to.
- [ ] Add vrat badge/highlight on the daily panchang and month grid.

## Deliverables
- Full vrat/upavas section with dates and katha.
- Panchang ↔ vrat cross-linking.

## Definition of Done
- [ ] Every vrat in `02` Section E has a page with computed dates.
- [ ] Parana times verified against package output.
- [ ] `02` Section E updated to `have`.

## Dependencies & risks
- Vrat Katha content is app-only and copyright-sensitive → public-domain subset.
- Some regional vrats differ by tradition → gate with `tradition=`.
