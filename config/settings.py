from pathlib import Path
import os
import environ

# --------------------------------------------------
# Base
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG") == "on"

ALLOWED_HOSTS = []


# --------------------------------------------------
# Applications
# --------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # 3rd party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "tailwind",
    "theme",
    "django_browser_reload",

    # Local apps
    "users.apps.UsersConfig",
    "portfolios.apps.PortfoliosConfig",
]

SITE_ID = 1
TAILWIND_APP_NAME = "theme"


# --------------------------------------------------
# Middleware
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # allauth
    "allauth.account.middleware.AccountMiddleware",

    # browser reload
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]


# --------------------------------------------------
# URLs / Templates
# --------------------------------------------------
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------
# Database
# --------------------------------------------------
DATABASES = {
    "default": env.db(),
}


# --------------------------------------------------
# Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# Static / Media
# --------------------------------------------------
STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------------
# Custom User
# --------------------------------------------------
AUTH_USER_MODEL = "users.User"


# --------------------------------------------------
# Auth / Redirect
# --------------------------------------------------
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)


# ==================================================
# 🔐 django-allauth (NEW STYLE – CORRECT & STABLE)
# ==================================================

# ใช้ Email + Password เท่านั้น
ACCOUNT_LOGIN_METHODS = {"email"}

# ❌ ปิด Login by Code ถาวร
ACCOUNT_LOGIN_BY_CODE_ENABLED = False

# บังคับใช้ Password
ACCOUNT_LOGIN_BY_PASSWORD_ENABLED = True

# Email
# ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# ไม่ใช้ username
# ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

# Signup fields (ต้องมี email* เพราะ verification = mandatory)
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "username",
    "password1*",
    "password2*",
]

# UX
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Smafolio] "


# --------------------------------------------------
# Email (Gmail SMTP)
# --------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "jokesittipong@gmail.com"
EMAIL_HOST_PASSWORD = env("EMAIL_AUTHEN")
DEFAULT_FROM_EMAIL = "Smafolio <jokesittipong@gmail.com>"
