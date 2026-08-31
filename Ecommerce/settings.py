from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file for local development
load_dotenv(BASE_DIR / ".env")


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-development-key"
)

DEBUG = os.environ.get(
    "DEBUG",
    "True"
).lower() == "true"


# =========================================================
# RENDER HOSTNAME
# =========================================================

RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)


# =========================================================
# ALLOWED HOSTS
# =========================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    if host.strip()
]


if RENDER_EXTERNAL_HOSTNAME:

    ALLOWED_HOSTS.append(
        RENDER_EXTERNAL_HOSTNAME
    )


# =========================================================
# CSRF TRUSTED ORIGINS
# =========================================================

CSRF_TRUSTED_ORIGINS = []


if RENDER_EXTERNAL_HOSTNAME:

    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    )


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [

    # -----------------------------------------------------
    # Jazzmin
    # -----------------------------------------------------

    "jazzmin",


    # -----------------------------------------------------
    # Django
    # -----------------------------------------------------

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",


    # -----------------------------------------------------
    # Cloudinary
    # -----------------------------------------------------

    "cloudinary",
    "cloudinary_storage",


    # -----------------------------------------------------
    # Local Apps
    # -----------------------------------------------------

    "store",

]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    # -----------------------------------------------------
    # WhiteNoise
    # -----------------------------------------------------

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# =========================================================
# URL CONFIGURATION
# =========================================================

ROOT_URLCONF = "Ecommerce.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {

        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                # -------------------------------------------------
                # Django
                # -------------------------------------------------

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",


                # -------------------------------------------------
                # Store
                # -------------------------------------------------

                "store.context_processors.cart_count",

                "store.context_processors.customer_messages_count",

                "store.context_processors.store_settings",

            ],

        },

    },

]


# =========================================================
# WSGI / ASGI
# =========================================================

WSGI_APPLICATION = "Ecommerce.wsgi.application"

ASGI_APPLICATION = "Ecommerce.asgi.application"


# =========================================================
# DATABASE
# =========================================================
#
# LOCAL:
#     SQLite
#
# RENDER:
#     PostgreSQL through DATABASE_URL
#
# =========================================================

DATABASES = {

    "default": dj_database_url.config(

        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",

        conn_max_age=600,

        conn_health_checks=True,

    )

}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {

        "NAME":
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator",

    },

    {

        "NAME":
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator",

    },

    {

        "NAME":
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator",

    },

    {

        "NAME":
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator",

    },

]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================================================
# WHITENOISE
# =========================================================
#
# WhiteNoise serves static files in production.
#
# Manifest strict mode is disabled because some third-party
# packages, such as Jazzmin/Bootstrap assets, can reference
# optional source-map files.
#
# =========================================================

WHITENOISE_MANIFEST_STRICT = False


# =========================================================
# STORAGE
# =========================================================

STORAGES = {
    "default": {
        "BACKEND":
            "cloudinary_storage.storage.MediaCloudinaryStorage",
    },

    "staticfiles": {
        "BACKEND":
            "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# CLOUDINARY
# =========================================================

CLOUDINARY_STORAGE = {

    "CLOUD_NAME": os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    ),

    "API_KEY": os.environ.get(
        "CLOUDINARY_API_KEY"
    ),

    "API_SECRET": os.environ.get(
        "CLOUDINARY_API_SECRET"
    ),

}


# =========================================================
# AUTHENTICATION
# =========================================================

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/"


# =========================================================
# EMAIL
# =========================================================
#
# LOCAL DEVELOPMENT:
# Emails are printed in terminal.
#
# For production, replace this with an SMTP provider.
#
# =========================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = "info@mystore.com"


# =========================================================
# SECURITY - PRODUCTION
# =========================================================

if not DEBUG:

    # -----------------------------------------------------
    # Render / HTTPS
    # -----------------------------------------------------

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


    # -----------------------------------------------------
    # Secure Cookies
    # -----------------------------------------------------

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True


    # -----------------------------------------------------
    # Force HTTPS
    # -----------------------------------------------------

    SECURE_SSL_REDIRECT = True


    # -----------------------------------------------------
    # HSTS
    # -----------------------------------------------------

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)