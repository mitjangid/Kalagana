# 01 — Product Vision & Scope

## 1. One-liner

**Kalagana** is an offline-first, location-aware Hindu calendar and Panchang web
app — the full Drik Panchang experience (daily panchang, festivals, vrat,
muhurat, jyotish utilities and devotional content) built on top of our own
pure-Python `kalagana` engine, delivered as an installable PWA.

## 2. Why

- The `kalagana` package already computes accurate Drik Ganita panchang,
  festivals, vrat and muhurat for any location, fully offline, with no runtime
  data files.
- Drik Panchang proves the demand for a comprehensive, location-based Hindu
  almanac, but it is a single proprietary website/app with ads and no offline
  engine or open API.
- We can offer the same breadth with (a) an **offline-capable PWA** and (b) an
  **open, verifiable engine** (the package) that anyone can use.

## 3. Target users

| Persona | Need | Primary surface |
|---------|------|-----------------|
| **Daily practitioner (India)** | Today's tithi, rahu kalam, festivals, vrat timings | Home / daily panchang, PWA on phone |
| **Diaspora** | Same, for a foreign city + timezone/DST | Location-aware panchang, world cities |
| **Planner / event organizer** | "When is a good muhurat for marriage / griha pravesh?" | Muhurat suite |
| **Astrology-curious** | Kundali, rashi, rashifal, gemstone | Jyotish tools |
| **Developer** | Programmatic panchang via PyPI package | `pip install kalagana` |
| **Content reader** | Aarti, chalisa, vrat katha, festival meaning | Devotional / festival pages |

## 4. Product principles

1. **Correct before pretty.** Every displayed number traces to the package and
   has a documented convention (Drik Ganita; state the ayanamsa).
2. **Location is a first-class input.** Preset city, world search, lat/lon/tz,
   elevation. DST handled.
3. **Offline-first PWA.** Today's panchang and recent lookups work with no
   network.
4. **SEO is a product feature.** Festivals and tools must be crawlable,
   shareable, and fast.
5. **One engine, many surfaces.** Web app, PWA, CLI, REST, and eventually an
   embeddable widget all call the same package.
6. **No dark patterns.** Light, calm Hindu aesthetic; no popups.

## 5. Scope

### In scope (parity target — see 02)
- Daily + monthly panchang for any location.
- Festivals, vrat/upavas date lists, festival detail pages.
- Muhurat suite (choghadiya, hora, abhijit, vivah, griha pravesh, etc.).
- Calendars (yearly/monthly, regional variants).
- Jyotish utilities (kundali, rashi, gemstone, baby names, …).
- Planetary events and eclipse pages.
- Devotional content (aarti, chalisa, stotram, vrat katha).
- PWA install + offline.

### Explicitly out of scope (for now)
- Paid subscriptions / ad network integration.
- User accounts, social feed, comments (may revisit).
- Native iOS/Android apps (PWA first; wrap later only if needed).
- AI chat / predictions beyond rule-based rashifal.
- Storing any festival data as fixtures — everything is computed.

## 6. Success metrics

- **Parity:** ≥ 90% of the P1 feature list in `02-feature-parity.md` live.
- **Accuracy:** festival/panchang output matches the package's Meeus-verified
  selftest; zero stored dates.
- **Performance:** Lighthouse PWA + SEO ≥ 95; LCP < 2.5s on 3G.
- **Offline:** today's panchang + last-viewed city available offline.
- **Reach:** organic landing pages for every festival and tool.

## 7. Non-goals reminder

We are **not** affiliated with drikpanchang.com. "Parity" means feature
coverage for our users, not copying their content, trademarks or assets.
