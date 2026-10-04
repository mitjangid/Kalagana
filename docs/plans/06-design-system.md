# 06 — Design System

The current `kalagana/web/` UI already establishes the direction; this doc makes
it a reusable system for the Astro app.

## 1. Visual language — Hindu, warm, light-only

- **Mode:** light only (per product decision). Cream paper, saffron/marigold,
  vermilion (sindoor), turmeric gold, deep maroon ink.
- **Motifs (subtle):** a gold top rule on cards, a `❖` bullet before headings, a
  circular logo chip on the saffron header. Avoid loud religious iconography in
  chrome; reserve imagery for content pages.

### Tokens (from current `styles.css`)

```
--bg        #fdf6e9   cream page
--bg-2      #f8ecd5   subtle fills / pre
--panel     #fffdf7   cards
--ink       #3b2412   brown-black text
--muted     #8a7355   secondary text
--line      #ecdab8   hairlines
--saffron   #ff9933   primary accent
--saffron-deep #e8730c buttons
--vermilion #d7351b   alerts / gradients
--maroon    #7a1f1f   headings
--gold      #c8952a   rules / borders
--good      #1f7a44 / --bad #c1272d
```

**Header gradient:** `linear-gradient(120deg,#ff9933,#ef7d0d 42%,#d7351b)` with a
`4px` gold bottom border.

## 2. Layout & components

| Component | Purpose |
|---|---|
| App header | logo, title, tagline, global controls (city, ayanamsa, tradition) |
| Location bar | city search / lat-lon-tz, elevation, "use my location" |
| Tab nav | top-level sections (Panchang, Calendars, Muhurat, Vrat, Festivals, Jyotish) |
| Card | one tool per card; gold top rule; heading with `❖` |
| KV list | panchang summary rows |
| Window table | muhurta/timing tables (name, from, to) |
| Month grid | calendar month with tithi/festival per day cell |
| Year calendar | 12 month cards with festival lists |
| Pill | kind labels (festival / national / observance / islamic) |
| Toolbar | 12h/24h toggle, amanta/purnimanta, prev/next/today, share |
| Result panel | output area with skeleton/loading + error states |

## 3. Time & number formatting

- Time formats: **12h**, **24h**, and **24-plus** ("24:10" instead of "00:10") —
  a documented panchang convention; the toggle is client-side.
- Times after local midnight are suffixed "… , Oct 04" as Drik does.
- Use tabular numerals for all timing tables.

## 4. Accessibility

- AA contrast minimum on the cream palette (verify maroon-on-cream and
  saffron-deep-on-cream).
- Full keyboard nav for tabs, date pickers, tables.
- `aria-live` on result panels; status chip announced.
- Respect `prefers-reduced-motion`; no animation required to read data.
- Tables use real `<th>` scopes.

## 5. Responsive & mobile

- Mobile-first: header controls collapse; tabs scroll horizontally; tables
  become stacked key/value cards under ~560px.
- PWA install prompt; offline state banner.
- Touch targets ≥ 44px.

## 6. Iconography & imagery

- Minimal inline SVG icons (sun, moon, calendar, location, share).
- Content imagery (festival art, rangoli, greetings) lives in content pages with
  proper attribution/licensing; **never** reuse third-party trademarks.

## 7. Charts

- Lagna kundali: North/South Indian square diagrams as SVG.
- Planetary positions: simple degree bars / wheel.
- Keep charts accessible with a data-table fallback.

## 8. Deliverables to formalize

- A `tokens.css` + component styles shared with the current static UI.
- A small Storybook-like page (`/design`) rendering every component in both
  dense and comfortable spacing — for visual QA.
