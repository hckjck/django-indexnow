from __future__ import annotations

import json
import logging
import threading
import time
from typing import Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured

from . import __version__

logger = logging.getLogger(__name__)

_DEDUPE_LOCK = threading.Lock()
_DEDUPE_CACHE: dict[str, float] = {}


DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
DEFAULT_TIMEOUT = 5
DEFAULT_DEDUPE_SECONDS = 60


def get_api_key() -> str:
    return str(getattr(settings, "INDEXNOW_API_KEY", "") or "").strip()


def is_enabled() -> bool:
    return bool(get_api_key())


def get_site() -> Site:
    apps = getattr(settings, "INSTALLED_APPS", [])
    if "django.contrib.sites" not in apps:
        raise ImproperlyConfigured(
            "django.contrib.sites must be in INSTALLED_APPS to use django-indexnow."
        )

    try:
        return Site.objects.get_current()
    except Exception as exc:
        raise ImproperlyConfigured(
            "Could not resolve current Site via Site.objects.get_current(). "
            "Check SITE_ID and Sites configuration."
        ) from exc


def get_site_base_url() -> str:
    site = get_site()
    domain = str(site.domain or "").strip()
    if not domain:
        raise ImproperlyConfigured("Current Site has an empty domain.")
    return f"https://{domain}"


def _normalize_url(url: str) -> str:
    if url.startswith(("http://", "https://")):
        return url

    base = get_site_base_url().rstrip("/") + "/"
    return urljoin(base, url.lstrip("/"))


def _should_submit(url: str) -> bool:
    ttl = int(getattr(settings, "INDEXNOW_DEDUPE_SECONDS", DEFAULT_DEDUPE_SECONDS))
    if ttl <= 0:
        return True

    now = time.monotonic()
    with _DEDUPE_LOCK:
        # Periodically remove expired entries opportunistically.
        expired = [u for u, expires in _DEDUPE_CACHE.items() if expires <= now]
        for expired_url in expired:
            _DEDUPE_CACHE.pop(expired_url, None)

        expires_at = _DEDUPE_CACHE.get(url)
        if expires_at and expires_at > now:
            return False

        _DEDUPE_CACHE[url] = now + ttl
        return True


def _build_payload(urls: Iterable[str]) -> dict[str, object]:
    absolute_urls = [_normalize_url(u) for u in urls]

    for abs_url in absolute_urls:
        parsed = urlparse(abs_url)
        if not parsed.scheme or not parsed.netloc:
            raise ImproperlyConfigured(
                f"IndexNow URL must be absolute after normalization: {abs_url}"
            )

    site = get_site()
    key = get_api_key()
    key_location = f"https://{site.domain}/{key}.txt"
    return {
        "host": site.domain,
        "key": key,
        "keyLocation": key_location,
        "urlList": absolute_urls,
    }


def _submit_payload(payload: dict[str, object]) -> None:
    endpoint = getattr(settings, "INDEXNOW_ENDPOINT", DEFAULT_ENDPOINT)
    timeout = int(getattr(settings, "INDEXNOW_TIMEOUT", DEFAULT_TIMEOUT))
    user_agent = getattr(settings, "INDEXNOW_USER_AGENT", f"django-indexnow/{__version__}")
    debug_logging = bool(getattr(settings, "INDEXNOW_DEBUG_LOGGING", False))

    body = json.dumps(payload).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": str(user_agent),
        },
    )

    try:
        with urlopen(request, timeout=timeout):
            if debug_logging:
                logger.debug("IndexNow submission succeeded for %s", payload.get("urlList"))
    except Exception:
        logger.exception("IndexNow submission failed")


def submit_url(url: str) -> None:
    submit_urls([url])


def submit_urls(urls: list[str]) -> None:
    if not is_enabled():
        return

    normalized_urls = [_normalize_url(url) for url in urls]
    filtered_urls = [url for url in normalized_urls if _should_submit(url)]

    if not filtered_urls:
        return

    payload = _build_payload(filtered_urls)
    _submit_payload(payload)
