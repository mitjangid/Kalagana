# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Jyotish (Vedic astrology) suite** — kundali (birth chart with grahas, whole-sign
  houses, 16 divisional charts, Avakhada and Vimshottari dasha), Ashtakoota
  marriage matching (Guna Milana) with Mangal dosha, and transit-based rashifal.
- REST endpoints `/kundali`, `/match` and `/rashifal`, plus `kundali`, `match`
  and `rashifal` CLI subcommands.
- Public API reference and matching OpenAPI, Postman, Insomnia and Bruno client
  collections under `docs/api/`.

### Changed
- Repository restructured to a `src/` layout; the package now lives in
  `src/kalagana/`.
- Test reference data moved to `tests/data/`.
- API reference, festival coverage and a docs index consolidated under `docs/`.
- Single canonical logo at `assets/logo.png`.

### Removed
- The bundled single-page web UI and the app product/planning docs moved to the
  `master` branch; `kalagana serve` now exposes only the JSON REST API.

## [0.1.1]

### Added
- Islamic (Hijri), national-holiday and secondary Hindu festival rules; the
  `/festivals`, `/find` and `/day` REST endpoints and the optional `.env`
  configuration.

## [0.1.0]

### Added
- Initial public release: the five panchang limbs, sunrise/sunset and
  moonrise/moonset, muhurta windows, eclipses, eras, a rule-driven festival
  calendar, the CLI and the offline REST server.
