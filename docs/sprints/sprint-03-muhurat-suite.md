# Sprint 03 — Muhurat Suite

**Goal:** cover the full muhurat toolbox — the "when should I do X" journeys —
including the missing ceremony muhurats.

## Scope
- **In:** choghadiya/hora/abhijit (already computed), plus vivah, griha pravesh,
  vehicle purchase, property purchase, lagna table, gowri panchangam, panchaka
  rahita, do ghati, auspicious yogas.
- **Out:** jyotish, planets, content.

## Package work (`PyPI-dev`)
- [ ] `vivah_muhurat(year, loc)` — marriage muhurat dates per classical rules.
- [ ] `griha_pravesh(year, loc)` — housewarming dates.
- [ ] `vehicle_purchase(year, loc)` and `property_purchase(year, loc)`.
- [ ] `lagna_table(date, loc)` + udaya lagna windows.
- [ ] `gowri_panchangam(date, loc)` — Gowri Nalla Neram.
- [ ] `panchaka_rahita(date, loc)` and `do_ghati_muhurat(date, loc)`.
- [ ] Auspicious yogas scanner: Sarvarthasiddhi, Amritsiddhi, Dwipushkar,
      Tripushkar, Ravi Pushya, Guru Pushya, Ravi Yoga, plus Aadal/Vidaal,
      Jwalamukhi (random daily yogas).
- [ ] New REST routes per `05-data-model-and-api`.

## App work (`master`)
- [ ] `/muhurat/choghadiya`, `/muhurat/hora`, `/muhurat/abhijit` (may be islands
      on the panchang page too).
- [ ] `/muhurat/vivah`, `/griha-pravesh`, `/vehicle`, `/property` — year lists
      with filters (month, weekday).
- [ ] `/muhurat/lagna`, `/muhurat/gowri`, `/muhurat/panchaka-rahita`,
      `/muhurat/do-ghati`.
- [ ] `/muhurat/auspicious-yogas` — upcoming yoga windows.
- [ ] Calendar export (ICS) of chosen muhurat dates.

## Deliverables
- Complete muhurat section matching the Drik taxonomy.
- Cross-links: panchang page → today's choghadiya/hora/abhijit.

## Definition of Done
- [ ] Golden tests for vivah/griha-pravesh against reference dates.
- [ ] Every muhurat tool has a page + API + CLI parity.
- [ ] `02` Section D updated to `have`.

## Dependencies & risks
- Rules vary by tradition → document the convention used; allow `tradition=`.
- Vivah/griha rules are the most complex; budget extra package time.
