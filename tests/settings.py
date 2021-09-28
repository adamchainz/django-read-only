import os
from typing import List

import django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "NOTASECRET"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    },
    "other": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    },
}

ALLOWED_HOSTS: List[str] = []

INSTALLED_APPS = [
    "django_read_only",
    "django.contrib.sites",
]

MIDDLEWARE: List[str] = []

ROOT_URLCONF = "tests.urls"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True

if django.VERSION < (4, 0):
    USE_L10N = True

SITE_ID = 1

USE_TZ = True
