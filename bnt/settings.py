"""Django settings for booknepaltrip.com."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,booknepaltrip.com,www.booknepaltrip.com").split(",")
CSRF_TRUSTED_ORIGINS = ["https://booknepaltrip.com", "https://www.booknepaltrip.com"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "yatra",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

try:  # optional: serves /static/ efficiently in production
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
except ImportError:
    pass

ROOT_URLCONF = "bnt.urls"
WSGI_APPLICATION = "bnt.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "yatra.context.site",
    ]},
}]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = False
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CONTENT_DIR = BASE_DIR / "content"

# Business details. Fill these before launch; placeholders render as-is.
SITE = {
    "name": "Book Nepal Trip",
    "url": "https://booknepaltrip.com",
    "email": os.environ.get("BNT_EMAIL", "[YOUR EMAIL]"),
    "phone": os.environ.get("BNT_PHONE", "[YOUR PHONE]"),
    "whatsapp": os.environ.get("BNT_WHATSAPP", ""),  # digits with country code, e.g. 9779800000000
    "address": "[YOUR OFFICE ADDRESS, KATHMANDU]",
    "byline": "Book Nepal Trip Desk",
}

# Optional Google Analytics 4 measurement ID (e.g. G-XXXXXXX). Leave empty to load no analytics.
GA4_ID = os.environ.get("BNT_GA4", "")

# Production: hashed file names so every deploy busts browser caches.
# Set BNT_HASHED_STATIC=1 on the server AFTER `python manage.py collectstatic`.
if os.environ.get("BNT_HASHED_STATIC") == "1":
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
                        if "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE
                        else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
    }
