# Sprint 09 — Regional Panchang & Internationalization

**Goal:** add regional calendar conventions and multi-language support.

## Scope
- **In:** regional display conventions (Bengali/Tamil/Telugu/Odia/Malayalam/
  Marathi/Gujarati/Kannada/Nepali/ISKCON), i18n routing and catalogs.
- **Out:** new computational domains.

## Package work (`PyPI-dev`)
- [ ] Regional **display conventions**: month naming, calendar systems,
      epoch differences, regional variant rules per tradition.
- [ ] Bengali Panjika & Tamil Panchangam specifics (Surya Siddhanta caveats as
      documented by the package), Gowri Nalla Neram (if not done in Sprint 03).
- [ ] Nepali Patro (Bikram Sambat display).
- [ ] ISKCON Panchang / ISKCON Ekadashi variant flags.
- [ ] Graceful fallback when a convention is unsupported.

## App work (`master`)
- [ ] Astro i18n routing (`/en/...`, `/hi/...`) with locale switcher.
- [ ] Message catalogs for UI chrome; content collections carry `locale`.
- [ ] Regional calendar pickers/views; localized month & weekday names.
- [ ] `hreflang` + localized sitemaps.
- [ ] Number & date formatting via `Intl`.

## Deliverables
- Regional calendar modes selectable per user.
- At least `en` + `hi` UI locales; regional content where available.

## Definition of Done
- [ ] A regional calendar mode renders correctly for a golden date.
- [ ] i18n routing with fallback works; no missing-key strings visible.
- [ ] `02` Section B updated with real statuses.

## Dependencies & risks
- Regional conventions are subtle and vary; scope to the most-used first
  (Bengali, Tamil) and gate the rest behind `tradition=`.
- Translation quality needs native review.
