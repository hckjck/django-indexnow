SECRET_KEY = "tests"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "tests.test_urls"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "indexnow",
]
MIDDLEWARE = [
    "indexnow.middleware.IndexNowKeyFileMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
