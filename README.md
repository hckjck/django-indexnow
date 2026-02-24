# django-indexnow

`django-indexnow` is a minimal Django app that submits updated URLs to IndexNow-compatible search engines.

It is designed to stay small: Django + Python standard library only.

## Installation

```bash
pip install django-indexnow
```

Add the app and middleware:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "indexnow",
]

MIDDLEWARE = [
    # ...
    "indexnow.middleware.IndexNowKeyFileMiddleware",
]
```

Expose the app endpoint:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("indexnow/", include("indexnow.urls")),
]
```

## Configuration

Supported settings:

```python
INDEXNOW_API_KEY = "your-32-char-hex-key"  # optional; missing/empty disables app
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"  # optional
INDEXNOW_TIMEOUT = 5  # optional
INDEXNOW_DEBUG_LOGGING = False  # optional
INDEXNOW_USER_AGENT = "django-indexnow/0.1.0"  # optional
INDEXNOW_DEDUPE_SECONDS = 60  # optional; 0 disables dedupe
```

Behavior is automatic:

- If `INDEXNOW_API_KEY` is set and non-empty, endpoints and submissions are active.
- If it is missing or empty, endpoints return 404 and signal submission silently no-ops.

## Key Verification URLs

When enabled, the package serves both required verification endpoints:

- `/indexnow/key.txt`
- `/<INDEXNOW_API_KEY>.txt` (served by middleware at site root)

Both return plain text with exactly:

```text
<your_key>\n
```

## Signal API

Dispatch `indexnow.signals.indexnow` whenever a URL should be submitted:

```python
from indexnow.signals import indexnow

indexnow.send(sender=BlogPost, url=blog_post.get_absolute_url())
```

Relative URLs are resolved against `https://<site.domain>` from `Site.objects.get_current()`.
Absolute URLs are submitted as-is.

## post_save / post_delete Integration Example

```python
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from indexnow.signals import indexnow
from .models import BlogPost


@receiver(post_save, sender=BlogPost)
def on_blogpost_saved(sender, instance, **kwargs):
    indexnow.send(sender=sender, url=instance.get_absolute_url())


@receiver(post_delete, sender=BlogPost)
def on_blogpost_deleted(sender, instance, **kwargs):
    indexnow.send(sender=sender, url=instance.get_absolute_url())
```

## Management Command

Generate a key:

```bash
python manage.py indexnow_generate_key
```

Generate and print settings assignment:

```bash
python manage.py indexnow_generate_key --set
```

## Supported Search Engines

IndexNow is currently supported by engines including Bing, Yandex, Seznam, and Naver.

## License

MIT. See [LICENSE](LICENSE).
