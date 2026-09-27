from .base import *  # noqa: F403,F401

DEBUG = True
SECRET_KEY = "!cym7z#4rvc7ld)x52&)9igx=-y^yz=l$9m(=9^jzbp@ugdb9o"
ALLOWED_HOSTS = ["testplatform.farmingo.com.tr", "localhost", "127.0.0.1",]
CSRF_TRUSTED_ORIGINS = ["https://testplatform.farmingo.com.tr",]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "notification_minimal",
        "USER": "pushdemo",
        "PASSWORD": "pushdemo",
        "HOST": "172.40.0.1",
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
