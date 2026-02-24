## Prompt for Codex

You are implementing a new open-source Python package: **django-indexnow**.

Your task is to build a **production-ready Django app** that matches the specification below and is ready to be released on **PyPI**.
Provide **complete code**, **packaging**, **tests**, and **documentation**.

---

## Project goal

`django-indexnow` allows a Django project to notify **IndexNow-compatible search engines** whenever URLs are created, updated, or deleted.

The app is intentionally minimal, relies only on Django and the Python standard library, and integrates cleanly using signals.

---

## Core features

### 1. IndexNow key verification endpoints

Expose two key verification endpoints:

#### A) App endpoint

```
GET /indexnow/key.txt
```

* Returns the configured IndexNow API key as **plain text**
* UTF-8 encoded
* Exactly the key plus a trailing newline
* No HTML, no extra whitespace

#### B) Root key file (protocol-required)

```
GET /<INDEXNOW_API_KEY>.txt
```

* Served at the site root
* Returns the same plain-text key response
* Must not require the user to manually add a root URL pattern
* Implement using middleware

---

### 2. Django signal API

Expose a Django signal named:

```python
indexnow.signals.indexnow
```

Usage example:

```python
from indexnow.signals import indexnow

indexnow.send(sender=BlogPost, url=blog_post.get_absolute_url())
```

When the signal is dispatched, the app submits the URL to the IndexNow API.

---

## Enable / disable behavior

There is **no explicit enable switch**.

* If `INDEXNOW_API_KEY` is **set and non-empty**:

  * the app is enabled
  * endpoints are active
  * signal submissions are performed
* If `INDEXNOW_API_KEY` is **missing or empty**:

  * the app is disabled
  * key endpoints must return 404 (or 410)
  * signal receiver must no-op silently
  * no errors or warnings should be raised

---

## IndexNow submission protocol

Use the official IndexNow POST format:

* Endpoint (default):
  `https://api.indexnow.org/indexnow`

* Request:

  * Method: `POST`
  * Content-Type: `application/json; charset=utf-8`
  * JSON body:

    ```json
    {
      "host": "example.com",
      "key": "API_KEY",
      "urlList": ["https://example.com/path/"]
    }
    ```

Rules:

* `urlList` must contain **absolute URLs**
* Accept both absolute and relative URLs as input
* Network errors must be caught and logged
* Submissions must never crash the request/transaction that triggered them

Use **only Django and the Python standard library** (`urllib.request` preferred).

---

## URL + host resolution (IMPORTANT)

Do **not** introduce custom host/base-URL settings.

Instead, reuse the **Django Sites framework**.

### Requirements

* Use `django.contrib.sites`
* Resolve the current site using:

  ```python
  Site.objects.get_current()
  ```
* Use:

  * `site.domain` as the IndexNow `host`
  * `https://{site.domain}` as the base for building absolute URLs

### URL handling rules

* If the submitted URL is absolute:

  * use it as-is
* If the submitted URL is relative:

  * build an absolute URL using the current Site
* If Sites framework is not installed or misconfigured:

  * raise `ImproperlyConfigured` with a clear message

---

## Django settings

Support the following settings only:

* `INDEXNOW_API_KEY` (string, optional; absence disables app)
* `INDEXNOW_ENDPOINT` (optional, default `https://api.indexnow.org/indexnow`)
* `INDEXNOW_TIMEOUT` (optional, default `5`)
* `INDEXNOW_DEBUG_LOGGING` (optional bool, default `False`)
* `INDEXNOW_USER_AGENT` (optional, default `"django-indexnow/<version>"`)
* `INDEXNOW_DEDUPE_SECONDS` (optional int, default `60`; `0` disables dedupe)

Do **not** implement:

* `INDEXNOW_ENABLED`
* `INDEXNOW_BASE_URL`
* `INDEXNOW_HOST`

---

## Submission client

Create a small client module:

```python
submit_url(url: str) -> None
submit_urls(urls: list[str]) -> None
```

Responsibilities:

* Build correct IndexNow payload
* Apply timeout and headers
* Catch and log network errors
* Respect deduplication rules
* Never raise on submission failure

---

## Deduplication

Prevent repeated submissions of the same URL in a short window:

* Use an in-memory, per-process TTL cache
* Default TTL: `INDEXNOW_DEDUPE_SECONDS = 60`
* Setting value `0` disables deduplication entirely
* Cache does not need to be persistent or cross-process

---

## Signal receiver wiring

* Provide the signal object at `indexnow.signals.indexnow`
* Connect the default receiver in `AppConfig.ready()`
* The receiver:

  * no-ops if app is disabled
  * resolves absolute URL
  * submits via the client

---

## HTTP implementation

### URLs

`indexnow/urls.py`

```python
path("key.txt", views.key_txt, name="indexnow-key")
```

### Views

* Return `HttpResponse`
* Content-Type: `text/plain; charset=utf-8`
* Body: `<key>\n`

### Middleware

Implement `IndexNowKeyFileMiddleware`:

* Intercept requests to `/<API_KEY>.txt`
* Return the same plain-text response
* Respect enable/disable behavior

---

## Management command

Add:

```bash
python manage.py indexnow_generate_key
```

Behavior:

* Generate a secure 32-character hex key using:

  ```python
  secrets.token_hex(16)
  ```
* Print the key to stdout
* With `--set`, also print:

  ```python
  INDEXNOW_API_KEY = "<key>"
  ```

---

## Packaging (PyPI-ready)

Use **pyproject.toml + setuptools**.

Requirements:

* Package name: `django-indexnow`
* Import name: `indexnow`
* Provide `__version__` in `indexnow/__init__.py`
* Sync version with `pyproject.toml`
* Include:

  * `README.md`
  * `LICENSE`
  * `CHANGELOG.md`
* Django compatibility: `>=3.2`
* Python compatibility: `>=3.9`

---

## File layout

Generate the complete repository:

```
django-indexnow/
  indexnow/
    __init__.py
    apps.py
    signals.py
    client.py
    middleware.py
    views.py
    urls.py
    management/
      __init__.py
      commands/
        __init__.py
        indexnow_generate_key.py
  tests/
    __init__.py
    test_key_endpoint.py
    test_root_key_middleware.py
    test_client_payload.py
    test_signal_submission.py
  README.md
  LICENSE
  CHANGELOG.md
  pyproject.toml
  MANIFEST.in
```

---

## Tests

Use Django’s built-in test framework (no pytest).

Tests must verify:

1. `/indexnow/key.txt` returns correct content and content-type
2. `/<key>.txt` works via middleware
3. Client builds correct POST payload and headers (mock `urllib`)
4. Signal dispatch triggers submission
5. Deduplication prevents rapid duplicate submissions

Tests must be deterministic and make **no real network calls**.

---

## Documentation

Write a polished README including:

* Installation
* Configuration
* Key verification URLs
* Signal usage
* Example `post_save` / `post_delete` integration
* Supported search engines (brief)
* License

---

## Code quality requirements

* Clear, readable code
* Type hints on public functions
* Logging via `logging.getLogger(__name__)`
* Raise `ImproperlyConfigured` for configuration errors
* No unnecessary abstraction
* No optional dependencies

---

## Output instructions

Return the **full contents of all files**, clearly labeled by file path, using proper code blocks.

Do **not** omit any files.

