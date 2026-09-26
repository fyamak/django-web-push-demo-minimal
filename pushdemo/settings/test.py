from .base import *  # noqa: F403,F401

DEBUG = False
SECRET_KEY = "replace-this-test-secret-key"
ALLOWED_HOSTS = ["testplatform.farmingo.com.tr"]
CSRF_TRUSTED_ORIGINS = ["https://testplatform.farmingo.com.tr"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "notification",
        "USER": "pushdemo",
        "PASSWORD": "pushdemo",
        "HOST": "172.31.40.1",
        "PORT": "5432",
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}
