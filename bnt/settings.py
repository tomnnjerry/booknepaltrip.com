"""Django settings for booknepaltrip.com."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production" if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("Set DJANGO_SECRET_KEY when DJANGO_DEBUG=0")
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

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
                         "NAME": os.environ.get("BNT_DB_PATH", str(BASE_DIR / "db.sqlite3"))}}

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
# Every value can be set by environment variable on the server (see README.md).
SITE = {
    "name": "Book Nepal Trip",
    "url": os.environ.get("BNT_URL", "https://booknepaltrip.com"),
    "email": os.environ.get("BNT_EMAIL", "hello@booknepaltrip.com"),
    "phone": os.environ.get("BNT_PHONE", ""),        # as displayed, e.g. "+977 980-0000000"
    "whatsapp": os.environ.get("BNT_WHATSAPP", ""),  # digits with country code, e.g. 9779800000000
    "address": os.environ.get("BNT_ADDRESS", "Kathmandu, Nepal"),
    "hours": os.environ.get("BNT_HOURS", ""),        # e.g. "Sun–Fri, 9:00–18:00 Nepal time"
    "licence": os.environ.get("BNT_LICENCE", ""),    # e.g. "Department of Tourism licence no. 0000"
    "memberships": os.environ.get("BNT_MEMBERSHIPS", ""),  # e.g. "Member of TAAN and NATTA"
    "payments": os.environ.get("BNT_PAYMENTS", ""),  # e.g. "bank transfer · cards"
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

# New enquiries are emailed to BNT_NOTIFY_EMAIL when SMTP is configured (they are always saved in /admin/).
NOTIFY_EMAIL = os.environ.get("BNT_NOTIFY_EMAIL", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@booknepaltrip.com")
if not EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# HTTPS hardening in production (the site sits behind a TLS-terminating proxy such as nginx).
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("BNT_SSL_REDIRECT", "1") == "1"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("BNT_HSTS_SECONDS", "3600"))
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
