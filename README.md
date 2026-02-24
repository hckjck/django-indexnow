# django-indexnow

**django-indexnow** is a lightweight Django app that makes it easy to notify search engines about changes on your site **immediately**.

Instead of waiting days or weeks for crawlers to discover updates, this app uses the [IndexNow](https://www.indexnow.org) protocol to proactively tell participating search engines when URLs are created, updated, or deleted.

The app is intentionally simple and designed for easy integration into existing Django projects.

---

## Features

* 🚀 Instant URL submission via IndexNow
* 🔔 Signal-based API (create, update, delete)
* 🧩 Minimal setup
* 🐍 Pure Django, no extra dependencies

---

## Installation

Install the package:

```bash
pip install django-indexnow
```

Add it to your installed apps:

```python
INSTALLED_APPS = [
    ...
    "indexnow",
]
```

---

## Configuration

### Create an IndexNow API key

IndexNow requires a unique API key that must be publicly accessible.

Create a new key (example):

```bash
openssl rand -hex 16
```

This will generate a random key like:

```
a1b2c3d4e5f67890abcdef1234567890
```

### Add the key to your Django settings

```python
INDEXNOW_API_KEY = "a1b2c3d4e5f67890abcdef1234567890"
```

---

## Verify setup

Start your Django project:

```bash
python manage.py runserver
```

Open the following URL in your browser:

```
http://localhost:8000/indexnow/key.txt
```

If everything is configured correctly, you should see your API key printed as plain text.

This file is required by IndexNow to verify site ownership.

---

## Usage

`django-indexnow` exposes a signal that you can dispatch whenever a URL should be indexed.

### Sending a URL to IndexNow

```python
from indexnow.signals import indexnow

indexnow.send(
    sender=BlogPost,
    url=blog_post.get_absolute_url(),
)
```

### Recommended integration

A common pattern is to dispatch the signal from Django model signals:

* `post_save` (create/update)
* `post_delete`

Example:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from indexnow.signals import indexnow
from .models import BlogPost


@receiver(post_save, sender=BlogPost)
def index_blogpost_save(sender, instance, **kwargs):
    indexnow.send(sender=sender, url=instance.get_absolute_url())


@receiver(post_delete, sender=BlogPost)
def index_blogpost_delete(sender, instance, **kwargs):
    indexnow.send(sender=sender, url=instance.get_absolute_url())
```

---

## Supported search engines

IndexNow is currently supported by:

* Bing
* Yandex
* Seznam
* Naver

Other search engines may adopt the protocol in the future.

---

## License

MIT License
