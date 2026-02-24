from __future__ import annotations

from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import Signal

from .client import get_site_base_url, submit_url

indexnow = Signal()


_def_receiver_connected = False


def is_enabled() -> bool:
    key = getattr(settings, "INDEXNOW_API_KEY", "")
    return bool(str(key).strip())


def _default_receiver(sender, **kwargs) -> None:  # type: ignore[no-untyped-def]
    if not is_enabled():
        return

    url = kwargs.get("url")
    if not url:
        return

    url_str = str(url)
    if url_str.startswith(("http://", "https://")):
        absolute_url = url_str
    else:
        base = get_site_base_url()
        if not base:
            raise ImproperlyConfigured("Unable to resolve site base URL for IndexNow submission.")
        absolute_url = urljoin(f"{base.rstrip('/')}/", url_str.lstrip("/"))

    submit_url(absolute_url)


def connect_default_receiver() -> None:
    global _def_receiver_connected
    if _def_receiver_connected:
        return

    indexnow.connect(_default_receiver, dispatch_uid="indexnow.default_receiver")
    _def_receiver_connected = True
