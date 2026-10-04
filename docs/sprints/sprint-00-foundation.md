# Sprint 00 — Foundation & Scaffolding

**Goal:** stand up the app shell on `master`, wire it to the `kalagana` package
through a FastAPI service, and deploy a first "today's panchang" page.

## Scope
- **In:** repo layout, branch rules, Astro skeleton, FastAPI skeleton, CI,
  preview deploys, design tokens, one live page, package pinning.
- **Out:** any new calculations; full feature pages.

## Package work (`PyPI-dev`)
- [ ] Confirm the current released version and document the pin policy.
- [ ] Add `meta` (version/ayanamsa/tradition/location) to API responses if not
      already present, so the app can show provenance (`05-data-model-and-api`).
- [ ] Ensure `/health`, `/cities`, `/ayanamsas`, `/day` are stable contracts.

## App work (`master`)
- [ ] Create `app/` (Astro) and `server/` (FastAPI) in the repo layout below.
- [ ] FastAPI service importing `kalagana`; mirror `/day` (+ health/cities).
- [ ] Astro page `/` rendering today's panchang for a default city.
- [ ] Port the design tokens + components from `kalagana/web/` (see `06`).
- [ ] Location switcher (city dropdown) + ayanamsa + tradition controls.
- [ ] GitHub Actions: app CI (build + e2e smoke + Lighthouse budget).
- [ ] Vercel project (frontend) + Render service (API) + preview deploys.

## Proposed repo layout (master)
```
app/                      # Astro frontend + PWA
  src/pages/…
  src/components/…
  src/content/…
  src/lib/api.ts
server/                   # FastAPI app-API wrapper over kalagana
  main.py
  routers/…
  requirements.txt        # kalagana==X.Y.Z, fastapi, uvicorn
docs/                     # plans, sprints, product docs
kalagana/                 # (PyPI-dev only — not developed here)
```

## Deliverables
- Deployed preview: `/` shows today's panchang for one city.
- CI green with a Lighthouse budget.
- Documented pin: `kalagana==X.Y.Z`.

## Definition of Done
- [ ] `master` builds and deploys from CI.
- [ ] A PR produces a Vercel preview hitting the API.
- [ ] Design tokens match the existing web UI (light, Hindu palette).
- [ ] `docs/plans/*` and `docs/sprints/*` reviewed and accepted.

## Dependencies & risks
- Two-runtime deploy (JS + Python) coordination → keep API thin.
- Package coupling: app must not need an unreleased package version.
