# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2026-09-27

### Added
- `py.typed` marker so type checkers use the package's inline type hints (PEP 561)

### Changed
- Richer PyPI metadata: `Framework :: FastAPI`, `Framework :: Pydantic :: 2`, `Typing :: Typed`, and `OS Independent` classifiers, expanded keywords, and a clearer summary
- Stopped tracking macOS `.DS_Store` files

## [1.0.1] - 2026-09-09

### Added
- `fastapi_inspector.__version__` exposing the installed package version
- PyPI downloads badge in the README

### Changed
- Default dashboard title and example app titles now use the `FastAPI Inspector` name
- Test dependencies now include `httpx2`, which Starlette 1.x requires for its test client
- Pinned `mkdocs<2` in the docs extra ahead of the MkDocs 2.0 plugin-system rewrite
- Updated Black to 26.x and reformatted the code base
- Bumped GitHub Actions to current majors (`checkout@v7`, `setup-python@v7`, `upload-artifact@v7`, `download-artifact@v8`, `git-auto-commit-action@v7`)
- Docs workflow now only builds on pull requests and deploys on pushes to `main`

### Fixed
- Corrected repository links in `CONTRIBUTING.md` and the supported-versions table in `SECURITY.md`
- Corrected homepage and documentation URLs in package metadata and MkDocs configuration
- Updated author contact email in package metadata

## [1.0.0] - 2026-04-26

### Added
- First stable release
- Structured logging middleware for FastAPI (`ObserverMiddleware`)
- Typed event model (`LogEvent`) with method, path, status code, latency, correlation ID
- Configurable filter pipeline (`only_errors`, `min_duration_ms`, `exclude_paths`)
- Multiple storage backends: `InMemoryEventStore`, `JsonFileEventStore`, `JsonLinesEventStore`, `SQLiteEventStore`
- Built-in dashboard (`build_dashboard_app`) mountable at any path
- Console and file log handlers with JSON and plain-text formatters
- Full test suite (69 tests, 87% coverage across Python 3.10–3.14)
- MkDocs documentation site deployed to GitHub Pages

## [0.2.1] - 2026-04-26

### Fixed
- Corrected project URLs (homepage, documentation, repository) in package metadata

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

[Unreleased]: https://github.com/MehrazRumman/fastapi-observer/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/MehrazRumman/fastapi-observer/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/MehrazRumman/fastapi-observer/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/MehrazRumman/fastapi-observer/compare/v0.2.1...v1.0.0
[0.2.1]: https://github.com/MehrazRumman/fastapi-observer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/MehrazRumman/fastapi-observer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/MehrazRumman/fastapi-observer/releases/tag/v0.1.0
