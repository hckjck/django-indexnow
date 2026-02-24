# Changelog

## 0.1.0 - 2026-02-24

- Initial release of `django-indexnow`.
- Added key verification endpoint at `/indexnow/key.txt`.
- Added middleware support for root key file at `/<INDEXNOW_API_KEY>.txt`.
- Added `indexnow.signals.indexnow` and default receiver wiring.
- Added submission client with URL normalization, Site-based host resolution, and in-memory deduplication.
- Added management command: `indexnow_generate_key`.
- Added Django test suite for endpoint behavior, middleware behavior, payload generation, signal submission, and dedupe.
