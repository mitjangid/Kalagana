# Sprint 08 — PWA, Offline & Polish

**Goal:** make Kalagana a true installable, offline-capable PWA and hit the
performance/a11y bars site-wide.

## Scope
- **In:** service worker, offline data, install flow, performance, a11y,
  analytics, error/empty/loading states, settings.
- **Out:** new features; regional/i18n (next sprint).

## Package work (`PyPI-dev`)
- [ ] None required. (Optional: a tiny serialized "today" payload helper.)

## App work (`master`)
- [ ] `@vite-pwa/astro`: precache shell + fonts/icons; runtime-cache API GETs
      (stale-while-revalidate).
- [ ] Offline data: today's panchang for saved city + recently viewed dates;
      clear "offline" banner and last-synced indicator.
- [ ] Install flow: manifest, icons, iOS/Android prompts, `beforeinstallprompt`.
- [ ] Settings page: default city, time format, amanta/purnimanta, ayanamsa,
      theme note (light), language (stub). Persist in localStorage.
- [ ] Error/empty/loading states everywhere; retry on failure.
- [ ] Performance pass: image/OG optimization, code-splitting islands, edge
      cache headers.
- [ ] Accessibility pass: AA contrast, keyboard traps, focus order, aria-live.
- [ ] Privacy-friendly analytics (offline-aware).

## Deliverables
- Installable PWA that works offline for core views.
- Settings persisted locally.
- Documented perf/a11y audit results.

## Definition of Done
- [ ] Lighthouse PWA passes; Performance/SEO/A11y/Best-Practices ≥ 95.
- [ ] Airplane-mode test: today's panchang renders.
- [ ] Settings survive reload and offline.
- [ ] JS budget met on content pages.

## Dependencies & risks
- SW cache invalidation is error-prone → version caches, test upgrade paths.
- Caching API JSON must respect `past dates immutable / today volatile`.
