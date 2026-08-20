import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-secret")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tinymce",
    "tinycontent",
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

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

FIXTURE_DIRS = [BASE_DIR / "fixtures"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Showcases chaining filters, as documented in docs/filters.rst.
TINYCONTENT_FILTER = [
    "tinycontent.filters.md.markdown_filter",
    "tinycontent.filters.builtin.uploaded_file_filter",
]
TINYCONTENT_VERBOSE_NAME = "Demo Content"

# Showcases the optional TinyMCE admin editor - requires "tinymce" in
# INSTALLED_APPS above and the `tinymce` extra installed (see pyproject.toml).
TINYCONTENT_USE_TINYMCE = True
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "promotion": False,
    "height": 500,
    "menubar": True,
    "lineheight": 1,
    "plugins": "advlist,autolink,lists,link,image,charmap,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | lineheight | fontsizeselect |"
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "charmap | removeformat | help",
}

# Off so home.html's "footer_note" example keeps demonstrating the
# {% tinycontent %}...{% endtinycontent %} fallback live (a real content block
# would otherwise get autocreated for it the moment the dev server starts).
TINYCONTENT_AUTO_INDEX = False
