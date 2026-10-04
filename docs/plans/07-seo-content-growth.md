# 07 — SEO, Content & Growth

## 1. Why SEO is a product feature

Drik Panchang's traffic is driven by **long-tail, location- and date-specific
pages** (festival dates per year, panchang per city, tool pages). To reach
parity we need the same crawlable surface — generated from computed data, not
hand-written.

## 2. URL strategy

```
/                                     home (today's panchang, saved city)
/panchang/{yyyy-mm-dd}/{city}         daily panchang
/panchang/{yyyy-mm}/{city}            month panchang
/calendar/{yyyy}/{city}               year calendar (festivals)
/calendar/hindu/{yyyy}/{city}         Hindu calendar
/festivals/{slug}                     festival detail
/festivals/{yyyy}/{city}              festival list for year+city
/vrat/{slug}                          vrat detail (katha, dates)
/muhurat/{tool}                       vivah, griha-pravesh, choghadiya, hora…
/jyotish/{tool}                       kundali, rashi, gemstone, baby-names…
/planets/{topic}                      positions, transit, retrograde, eclipses
/{section}/{slug}                     devotional content (aarti, chalisa, …)
/settings                             user settings
```

Rules:
- **Canonical, stable, lowercase, hyphenated.** No query strings for primary
  content.
- **City slug** from a canonical place id (`new-delhi`, `mumbai`), not raw lat/lon.
- **Pagination & archives** for year listings.
- `hreflang` when i18n lands.

## 3. Generated pages (the SEO engine)

Build-time generation from the package so dates are always correct:

1. **Festival × year** pages — one per P1 festival × current & next year.
2. **Tool** pages — one per muhurat/jyotish tool (evergreen).
3. **City** landing pages — top N cities × today's panchang (regenerate at build
   / ISR-style).
4. **Festival detail** pages — authored content + *computed* dates table.

Everything gets **JSON-LD** (`Event` for festivals, `FAQPage` for tool FAQs,
`BreadcrumbList`), OpenGraph images (generated per festival/date), and an XML
sitemap + RSS for upcoming festivals.

## 4. Content model & cadence

- Author **evergreen explainers**: "What is Tithi", "How Rahu Kalam is
  calculated", one per panchang element and per tool.
- **Festival pages**: significance + vidhi + tithi rule + computed dates.
- **Vrat katha / aarti / chalisa**: start with a public-domain subset.
- Cadence: publish tool pages first (evergreen, high intent), then festivals.

## 5. Performance targets

| Metric | Target |
|---|---|
| Lighthouse Performance | ≥ 95 (mobile) |
| SEO / Best Practices / A11y | ≥ 95 |
| LCP | < 2.5s on Slow 4G |
| CLS | < 0.1 |
| JS shipped on content pages | < 20 KB |

Achieved by static/hybrid Astro, minimal islands, edge caching of API JSON.

## 6. Accessibility & internationalization

- WCAG 2.1 AA.
- Plan locales: `en` (default), `hi`, and later regional (`ta`, `te`, `bn`,
  `mr`, `gu`, `kn`, `ml`). Numbers/dates via `Intl`.
- Language switcher; content fallback to `en`.

## 7. Distribution beyond search

- **PWA install** (the app itself).
- **Shareable deep links**: every date+city is a URL (share buttons).
- **Embeddable widget** (later): a 1-line `<iframe>` today-panchang badge that
  links back — free backlinks.
- **Open API + docs** (from the package) → developer mindshare.
- **RSS/calendar feeds**: upcoming festivals as `.ics` / RSS.

## 8. Analytics & measurement

- Privacy-friendly analytics (no PII). Track: tool usage, city distribution,
  offline usage, install events.
- Search Console: monitor index coverage and query→page mapping.
- Keep an internal **parity dashboard**: count of P1 features live vs `02`.

## 9. Legal & attribution

- Public-domain religious texts only, with source attribution.
- No drikpanchang.com trademarks, images, or scraped content.
- Clear disclaimer: unaffiliated; Drik Ganita conventions documented.
