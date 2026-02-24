from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound


def get_key_value() -> str:
    return str(getattr(settings, "INDEXNOW_API_KEY", "") or "").strip()


def get_key_response(key: str) -> HttpResponse:
    return HttpResponse(f"{key}\n", content_type="text/plain; charset=utf-8")


def key_txt(request: HttpRequest) -> HttpResponse:
    key = get_key_value()
    if not key:
        return HttpResponseNotFound()
    return get_key_response(key)
