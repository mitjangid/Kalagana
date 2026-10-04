# Kalagana — App Planning Docs

This folder is the **plan** for turning the `kalagana` Python package into a
complete, feature-comparable web application (a "Kalagana app"), benchmarked
against [drikpanchang.com](https://www.drikpanchang.com/).

> **Status:** planning only. No application code is written from these docs yet.
> See `docs/sprints/` for the executable breakdown.

## How to read these docs

| # | File | Answers |
|---|------|---------|
| 01 | [01-product-vision.md](01-product-vision.md) | What are we building, for whom, and why? |
| 02 | [02-feature-parity.md](02-feature-parity.md) | Every feature Drik Panchang has, and our status per feature. |
| 03 | [03-architecture-and-branches.md](03-architecture-and-branches.md) | How package + app fit together; branch & release model. |
| 04 | [04-tech-stack.md](04-tech-stack.md) | Which frontend stack, PWA, and hosting. |
| 05 | [05-data-model-and-api.md](05-data-model-and-api.md) | The data/API contract between package and app. |
| 06 | [06-design-system.md](06-design-system.md) | Hindu visual language, light mode, components, a11y. |
| 07 | [07-seo-content-growth.md](07-seo-content-growth.md) | URL/SEO strategy, content model, growth. |
| 08 | [08-roadmap.md](08-roadmap.md) | Phase → sprint map and milestones. |

## The one rule that governs everything

**The Python `kalagana` package is the single source of truth for every
calculation.** The app never reimplements panchang math. If the app needs a new
number, the package computes it first, and that change ships to PyPI from the
`PyPI-dev` branch before the app consumes it.

## Branch model (short version)

| Branch | Owns | Publishes to |
|--------|------|--------------|
| `PyPI-dev` | `kalagana/` package, `tests/`, packaging, `docs/` for the package | **PyPI** (via `release.yml`) |
| `master` | The web app (frontend + app backend), product docs | App hosting |

Full rationale in [03-architecture-and-branches.md](03-architecture-and-branches.md).

## Conventions used in these docs

- **Status tags:** `have` · `partial` · `missing` · `app-only` (content that is
  not a calculation, e.g. lyrics, images).
- **Owner:** `pkg` (must live in the `kalagana` package) or `app` (frontend /
  content only).
- **Priority:** `P0` (MVP), `P1` (parity-critical), `P2` (nice-to-have).
