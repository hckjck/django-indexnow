from django.urls import path

from . import views

app_name = "indexnow"

urlpatterns = [
    path("key.txt", views.key_txt, name="indexnow-key"),
]
