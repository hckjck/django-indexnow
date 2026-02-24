from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from .views import get_key_response, get_key_value


class IndexNowKeyFileMiddleware:
    def __init__(self, get_response):  # type: ignore[no-untyped-def]
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        key = get_key_value()
        if key:
            if request.path == f"/{key}.txt":
                return get_key_response(key)
        return self.get_response(request)
