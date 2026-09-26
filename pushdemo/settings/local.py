from .base import *  # noqa: F403,F401

DEBUG = True
SECRET_KEY = "local-secret-key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "notification_minimal",
        "USER": "pushdemo",
        "PASSWORD": "pushdemo",
        "HOST": "host.docker.internal",
        "PORT": "5432",
    }
}
