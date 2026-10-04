# Sprint 10 — Launch & Growth

**Goal:** harden SEO, ship distribution surfaces (feeds, widget, public API
docs), and launch publicly.

## Scope
- **In:** SEO audit, sitemaps/feeds, embeddable widget, public API docs, launch
  checklist, monitoring.
- **Out:** new feature domains.

## Package work (`PyPI-dev`)
- [ ] Publish polished public API docs (`docs/api/README`, OpenAPI).
- [ ] Version & document the public REST surface for third-party use.
- [ ] (Optional) an embeddable "today" badge data endpoint.

## App work (`master`)
- [ ] Full SEO audit: titles/meta/OG/JSON-LD, canonical tags, sitemap index,
      robots, RSS/ICS feeds.
- [ ] Internal linking pass (festival ↔ vrat ↔ muhurat ↔ panchang).
- [ ] Embeddable widget: a small `<iframe>`/script today-panchang badge with a
      backlink (free-link acquisition).
- [ ] Public API landing page + docs (generated from OpenAPI).
- [ ] Monitoring & alerts (uptime, error rate, cache hit rate).
- [ ] Launch checklist: legal/privacy, 404s, redirects, analytics, backups of
      content.
- [ ] Announcement assets.

## Deliverables
- Public launch.
- Distribution: search + PWA installs + widget links + API users.

## Definition of Done
- [ ] Search Console index coverage healthy; no critical SEO errors.
- [ ] Feeds validate; widget renders on an external test page.
- [ ] Uptime/error alerts wired.
- [ ] Parity dashboard: ≥ 90% of P1 features live.

## Dependencies & risks
- Content depth (Sprint 07) and offline (08) gate a good launch.
- Widget/API must be stable and documented before promoting.
