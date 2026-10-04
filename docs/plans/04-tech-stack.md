# 04 — Tech Stack (Decision Record)

## Decision

> **Recommendation: Astro (SSR/SSG + islands) for the frontend/PWA, plus a thin
> Python FastAPI service that imports the `kalagana` package.**

Fallbacks considered: **Next.js** and **HTMX**. The choice is reversible early
(it's the `master` branch's shell) but cheap to get right now.

## Why the app needs *both* a frontend build and a Python service

The engine is Python. Any JS framework still needs a Python process we control
that can `import kalagana`. So the real question is only: *which frontend shell*?

## Options compared

| Criterion | **Astro** ✅ | Next.js | HTMX (FastAPI + Jinja) |
|---|---|---|---|
| Content/SEO pages (festivals, deities, lyrics) | Excellent (SSG/MDX) | Good | Good |
| Islands for interactive tools | Excellent | Excellent | Limited |
| Ships minimal JS by default | Excellent | Okay | Excellent (tiny) |
| PWA / offline | Excellent (`@vite-pwa`) | Good | Good |
| Needs a JS runtime server | No (static/hybrid) | Yes (Node) | No (Python) |
| Single language | No (JS + Python) | No (JS + Python) | **Yes (Python only)** |
| Interactivity complexity | Medium | Medium | Low→Medium |
| Team/ergonomics for a content-heavy catalog | Best | Good | Good |
| Hosting cost | Lowest (edge/static) | Higher | Low |
| Risk | Low | Low | Medium (UX ceiling) |

## Recommendation: **Astro + FastAPI**

Rationale:
1. Kalagana's page inventory is **content-heavy and SEO-critical** (a page per
   festival, per tool, per year/city). Astro's content collections + SSG produce
   fast, crawlable pages with almost no client JS.
2. The interactive parts (panchang, muhurat, kundali) are **islands** — small
   hydrated components calling the JSON API. Astro handles this natively.
3. PWA is first-class (`@vite-pwa/astro`): precache the shell + last panchang,
   runtime-cache API GETs.
4. Static/hybrid output → **cheapest hosting** and the best Lighthouse scores,
   directly serving the "Performance/SEO ≥ 95" success metric.
5. We keep the **engine in Python**, matching the existing package — no rewrite.

**FastAPI** for the app API because it maps naturally onto the package, gives
OpenAPI docs for free (reuse for an eventual public API), and is easy to host as
a long-running service with warm caches.

## Decision details

| Concern | Choice |
|---|---|
| Frontend | Astro 5+, `output: "hybrid"` (static default, SSR where needed) |
| UI islands | Astro + a small amount of vanilla/`Preact` (or Svelte) — pick one, keep small |
| Styling | Plain CSS with design tokens (see `06-design-system.md`); no heavy UI kit |
| PWA | `@vite-pwa/astro` (Workbox) — precache shell, runtime cache API |
| App API | FastAPI + Uvicorn, Pydantic response models |
| Engine | `kalagana` from PyPI (pinned) |
| Frontend host | **Vercel** (Astro adapter, CDN, preview deploys; Hobby free tier) |
| API host | **Render** (long-running Python web service; free/paid tiers) |
| DB | none for v1 |
| i18n (later) | Astro i18n routing + message catalogs |

> Hosting picks are grounded via Gravity Index: Vercel is recommended for the
> Astro/PWA frontend (preview deploys, global CDN, free Hobby tier); Render is
> the better fit for the long-running Python API (vs serverless).

## When to revisit

- If interactivity dominates and the "islands" model gets awkward → consider
  SvelteKit/Next.
- If we want **one language only** and accept a lower UX ceiling → HTMX.
- If arbitrary-date **offline computation** is required (not just cached
  lookups) → evaluate compiling the engine to WASM (Pyodide/micropython) as a
  progressive enhancement, with the Python API as the authority.

## What we deliberately are *not* doing

- No microservices. One frontend, one API, one package.
- No database in v1.
- No client-side reimplementation of panchang math — ever.
