# 03 — Architecture & Branch Model

## 1. Two products, one engine

```
                    ┌───────────────────────────────────────────┐
                    │        kalagana  (Python package)          │
                    │  pure stdlib · offline · no data files     │
                    │  panchang · festivals · vrat · muhurat     │
                    │  jyotish · astronomy · CLI · REST server   │
                    └───────────────────────────────────────────┘
                          ▲                        ▲
              pip install │                        │ import
                          │                        │
        ┌─────────────────┴──────┐      ┌──────────┴──────────────────┐
        │  Third-party users     │      │   Kalagana App (master)      │
        │  (scripts, notebooks)  │      │   frontend + app API service │
        └────────────────────────┘      │   Astro PWA  ⇄  FastAPI     │
                                        └──────────────────────────────┘
```

**Invariant:** the app computes *nothing* itself. It calls the package (in
process, via the app API service) for every number.

## 2. Repository & branch strategy

One repository, two deployables, two branches.

| Branch | Contents | CI | Publishes |
|---|---|---|---|
| **`PyPI-dev`** | `kalagana/` package, `tests/`, `pyproject.toml`, `scripts/`, package docs | `.github/workflows/ci.yml`, `release.yml` | **PyPI** on tag |
| **`master`** | Web app: `app/` (frontend), `server/` (app API), product docs, content | CI (build + e2e + lighthouse) | App hosting (Vercel + API host) |

### Why two branches (not two repos)
- Keeps the package history and the app history from fighting over one HEAD.
- `master` is the **app** branch; `PyPI-dev` is the **package** branch.
- The package is consumed by the app as a **pinned dependency**
  (`kalagana==X.Y.Z`) or, for local dev, an editable path. Either way, the app
  targets a *released* version so `master` always builds.

### Flow of change (package)
1. Work on `PyPI-dev`.
2. `scripts/release.py bump <patch|minor|major> --commit`.
3. `build` → `twine check` → `tag --push` → GitHub `release.yml` publishes to
   **PyPI** (trusted publishing).
4. Bump the version pinned in the app on `master`.

### Flow of change (app)
1. Work on `master` (feature branches → PR → `master`).
2. Preview deploy per PR (Vercel preview).
3. Merge to `master` → production deploy.

### Keeping them in sync
- **Never** edit the package on `master`; **never** build the app on `PyPI-dev`.
- A change that needs a new computation is **two commits**: package first (ship
  to PyPI), then app (pin the new version). The app PR notes the required
  package version.
- CI on `master` fails fast if the pinned `kalagana` version is not on PyPI.

## 3. Runtime components

| Component | Where | Responsibility |
|---|---|---|
| **Frontend (Astro + PWA)** | edge/CDN | Pages, SEO, islands, service worker, offline shell |
| **App API (FastAPI)** | container host | Thin JSON wrapper over `kalagana`; caching; rate-limit |
| **`kalagana` engine** | imported by the API | All computation |
| **Static/derived pages** | build step | Festival/tool landing pages pre-rendered (SEO) |

The app API is intentionally a **thin** layer: routes map 1:1 onto package
functions and mirror `kalagana/server.py`. The existing stdlib server stays as
the zero-dependency local/self-host option.

## 4. Deployment

- **Frontend:** Vercel (Astro adapter, global CDN, preview deploys, free Hobby
  tier). Alternatives: Cloudflare Pages, Netlify.
- **App API:** Render (long-running Python web service — better than serverless
  for warm caches of computed years). Alternatives: Fly.io, Railway, a VPS.
- **No database required for v1.** All output is computed. Optional later:
  Postgres only for analytics/caching of pre-rendered pages, never for source
  data.
- **CDN caching:** panchang/festival responses are cacheable per
  (date|year, city, ayanamsa, params) → aggressive `s-maxage` + SWR.

## 5. Environments

| Env | Frontend | API | Package |
|---|---|---|---|
| Local | `astro dev` | `uvicorn server:app --reload` | editable `kalagana` |
| Preview (per PR) | Vercel preview | Render preview / branch | pinned from PyPI |
| Production | `master` | Render prod | pinned from PyPI |

## 6. Non-functional requirements

- **Offline:** service worker caches app shell + last N panchang responses;
  today's panchang for the saved city always available.
- **Determinism:** same inputs → same output across platforms (package is
  stdlib-only; tz via `zoneinfo` with a documented fallback).
- **Performance budget:** API p95 < 300 ms for cached, < 2 s cold for a year
  scan (mitigated by the engine's `infos` cache + server cache).
- **No runtime data files / no network** inside the package.
