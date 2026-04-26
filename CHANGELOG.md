# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-04-26

### Changed
- Renamed package from `fastapi-observer` to `fastapi-inspector`
- Renamed Python import from `fastapi_observer` to `fastapi_inspector`

## [0.1.0] - 2026-04-26

### Added
- FastAPI middleware for automatic request/response logging
- Structured `LogEvent` model with request metadata, response status, and latency
- Configurable event filtering pipeline (`ObserverFilter` protocol)
- Multiple storage backends: in-memory, JSON file, SQLite
- Console and file log handlers
- JSON and plain-text formatters
- Built-in dashboard for inspecting logged events (mountable as a sub-application)
- `ObserverConfig` for controlling log level, path filters, and storage
- Logger factory with structured output support
- Full test suite (69 tests, 87% coverage)
- MkDocs documentation site with quickstart, API reference, and best-practices guides
- CI/CD pipelines for testing (Python 3.10–3.14), coverage badge, and PyPI publishing

[Unreleased]: https://github.com/MehrazRumman/fastapi-inspector/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/MehrazRumman/fastapi-inspector/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/MehrazRumman/fastapi-inspector/releases/tag/v0.1.0
