# Sprint 07 — Devotional Content & Depth

**Goal:** add the non-calculation content that keeps users on the site and
brings organic search: aarti/chalisa/stotram, deities, gurus, pilgrimage
places, and galleries.

## Scope
- **In:** devotional text collections, deity/guru/pilgrimage pages, puja vidhi,
  galleries. **App-only** (no package work).
- **Out:** any computation; licensed/third-party content.

## Package work (`PyPI-dev`)
- [ ] None expected. (Optional: expose festival→deity links as metadata.)

## App work (`master`)
- [ ] Content collections: `aarti`, `chalisa`, `stotram`, `ashtakam`, `mantra`,
      `deities`, `gurus`, `pilgrim-places`, `puja-vidhi`.
- [ ] Pages: `/lyrics/{slug}`, `/deities/{slug}`, `/gurus/{slug}`,
      `/pilgrim-places/{slug}`, `/puja-vidhi/{slug}`.
- [ ] Aarti/chalisa reader: clean typography, optional transliteration, print.
- [ ] Link devotional content to relevant festival/vrat pages.
- [ ] Gallery pages (rangoli, mehandi, greetings) with proper attribution OR
      original generated artwork — no third-party trademarks.
- [ ] Content QA: public-domain verification + source attribution field.

## Deliverables
- Browsable devotional section (public-domain subset first).
- Puja vidhi pages linked from festivals.

## Definition of Done
- [ ] Every content item has `source`/license frontmatter.
- [ ] No copyrighted text or trademarked imagery.
- [ ] Sitemap includes all content pages.

## Dependencies & risks
- **Licensing is the risk.** Start with a small, verifiably public-domain set;
  editorial review is mandatory before publishing.
- Volume is high → prioritize by search demand.
