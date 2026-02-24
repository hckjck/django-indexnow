from django.http import HttpResponse
from django.urls import include, path


urlpatterns = [
    path("indexnow/", include("indexnow.urls")),
    path("", lambda request: HttpResponse("ok")),
]
