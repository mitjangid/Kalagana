# Sprint 05 — Jyotish Tools

**Goal:** deliver the Vedic astrology toolbox: birth chart, matching, and the
calculator utilities. This is the largest package-expansion sprint.

## Scope
- **In:** kundali/janma kundali, horoscope match, rashi/sunsign/birthstar/lagna,
  gemstone, rudraksha, mangal dosha, kalasarpa yoga, shani sadesati, baby names,
  shraddha calculator.
- **Out:** rashifal predictions beyond a documented rules layer; planets sprint.

## Package work (`PyPI-dev`)
- [ ] Ayanamsa-aware **planetary positions** (needed by kundali) — shared with
      Sprint 06; build the ephemeris layer here first.
- [ ] `kundali(birth_datetime, loc)` — Lagna, houses, planetary placements,
      nakshatras/padas, North & South chart data.
- [ ] `horoscope_match(boy, girl)` — Ashtakoota (gun milan) with score & koota
      breakdown.
- [ ] `rashi/moonsign/sunsign/birthstar/lagna` calculators.
- [ ] `mangal_dosha`, `kalasarpa_yoga`, `shani_sadesati`.
- [ ] `gemstone` / `rudraksha` recommendation rules.
- [ ] `baby_names` finder (nakshatra-syllable based) + name initials.
- [ ] `shraddha_calculator`.

## App work (`master`)
- [ ] `/jyotish/kundali` — birth data form → chart (SVG North/South) + tables.
- [ ] `/jyotish/match` — two forms → score + koota table.
- [ ] `/jyotish/rashi`, `/sunsign`, `/birthstar`, `/lagna` calculators.
- [ ] `/jyotish/gemstone`, `/rudraksha`, `/mangal-dosha`, `/kalasarpa-yoga`,
      `/shani-sadesati`.
- [ ] `/jyotish/baby-names`.
- [ ] Privacy: **no PII stored**; all computation ephemeral; clear notice.

## Deliverables
- Working kundali + match + calculator pages.
- SVG chart components (North/South) with data-table fallback.

## Definition of Done
- [ ] Golden birth charts verified against reference charts.
- [ ] Charts accessible (labelled SVG + table).
- [ ] `02` Section G updated with real statuses.

## Dependencies & risks
- Accuracy of planetary positions is the crux → invest in the ephemeris layer
  and its tests before building tools on top.
- Astrology interpretation is sensitive → present as tradition, cite rules.
