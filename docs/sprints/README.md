# Kalagana App — Sprints

Executable breakdown of `docs/plans/08-roadmap.md`. Each file is one sprint.

| Sprint | Theme | Status |
|---|---|---|
| [00](sprint-00-foundation.md) | Foundation & scaffolding | planned |
| [01](sprint-01-daily-panchang.md) | Daily panchang | planned |
| [02](sprint-02-calendars-and-festivals.md) | Calendars & festivals | planned |
| [03](sprint-03-muhurat-suite.md) | Muhurat suite | planned |
| [04](sprint-04-vrat-and-festival-depth.md) | Vrat & festival depth | planned |
| [05](sprint-05-jyotish-tools.md) | Jyotish tools | planned |
| [06](sprint-06-planets-and-astronomy.md) | Planets & astronomy | planned |
| [07](sprint-07-devotional-content.md) | Devotional content | planned |
| [08](sprint-08-pwa-and-polish.md) | PWA, offline & polish | planned |
| [09](sprint-09-regional-and-i18n.md) | Regional & i18n | planned |
| [10](sprint-10-launch-and-growth.md) | Launch & growth | planned |

## Rules of engagement

1. **Package-first.** Any new computed value ships to PyPI from `PyPI-dev`
   before the app consumes it. App PRs record the minimum package version.
2. **Branch discipline.** Package work on `PyPI-dev`; app work on `master`
   (feature branches → PR). Never cross-edit.
3. **No stored calendar data.** Everything is computed by the package.
4. **Every sprint ends deployable** on `master` behind the current version.

## Sprint template

```
# Sprint NN — Theme

Goal: one sentence.

## Scope
- In: …
- Out: …

## Package work (PyPI-dev)
- [ ] …

## App work (master)
- [ ] …

## Deliverables
- …

## Definition of Done
- [ ] …

## Dependencies & risks
- …
```
