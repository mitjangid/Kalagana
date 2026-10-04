# Kalagana documentation

Documentation for the **Kalagana** project. This branch (`master`) is the
**feature-rich / app** branch: it carries the package source, the web UI and the
product documentation.

## Package documentation

| Document | Contents |
|---|---|
| [`api/README.md`](api/README.md) | Full REST + Python API reference: every endpoint, parameter and response. |
| [`api/clients.md`](api/clients.md) | Ready-to-import OpenAPI, Postman, Insomnia and Bruno client collections. |
| [`festival-coverage.md`](festival-coverage.md) | Festival coverage and gap analysis vs. Drik Panchang. |

## App / product documentation

| Document | Contents |
|---|---|
| [`plans/`](plans/) | Product vision, feature parity, architecture and the app roadmap. |
| [`sprints/`](sprints/) | The executable sprint breakdown. |

## Top-level documents

- [`../README.md`](../README.md) — the package landing page.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — development, architecture and release process.
- [`../CHANGELOG.md`](../CHANGELOG.md) — version history.

> The installable package (library + CLI + REST API) is published to PyPI from
> the `PyPI-dev` branch. The web UI lives here under [`../web`](../web).
