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

# ถ้าใน .env เป็น 'on' จะได้ True, ถ้าเป็น 'off' จะได้ False
DEBUG = env("DEBUG") == "on"

# รับค่าเป็น list คั่นด้วยจุลภาค (เช่น localhost,127.0.0.1)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

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

    # Local apps
    "users.apps.UsersConfig",
    "portfolios.apps.PortfoliosConfig",
]



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

]

# ถ้าอยู่ในโหมด Debug ให้เปิด Browser Reload
if DEBUG:
    INSTALLED_APPS.append("django_browser_reload")
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")
else:
    # ถ้าขึ้น Production แนะนำให้ใช้ Whitenoise ช่วยเสิร์ฟไฟล์ Static (Optional)
    # MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    pass


# ==========================================
# 3. Security Settings (Production Only)
# ==========================================
if not DEBUG:
    # 1. บังคับใช้ HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # 2. ป้องกัน XSS และ Sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True  # (Browser รุ่นใหม่เริ่มเลิกใช้แล้ว แต่ใส่กันไว้ก่อนได้)

    # 3. HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = 31536000  # 1 ปี
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False  # ✅ เริ่มต้น False ตามที่คุณแนะนำ (ปลอดภัยกว่า)

    # 4. Proxy Handling (สำคัญมากสำหรับ Nginx, Railway, Render)
    # บอก Django ว่าถ้า Header นี้มาเป็น https ให้ถือว่าปลอดภัยแล้ว
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ==========================================
# Global Security (ใช้ทั้ง Dev และ Prod)
# ==========================================
# ป้องกันการถูกฝัง Iframe จากเว็บอื่น (แต่ยังให้ YouTube ฝังได้ถ้าเราเขียนโค้ดถูก)
X_FRAME_OPTIONS = "SAMEORIGIN"

# จัดการ Referrer เมื่อกดลิงก์ออกไปข้างนอก (เพื่อให้ YouTube ตรวจสอบสิทธิ์ได้)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# --------------------------------------------------
# 4. URLs & Templates
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
# 5 Database
# --------------------------------------------------
DATABASES = {
    "default": env.db(),
}


# --------------------------------------------------
# 6 Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------------
# 7 Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# 8 Static / Media
# --------------------------------------------------
STATIC_URL = "/static/"
# จำเป็นสำหรับ Production (คำสั่ง collectstatic จะรวมไฟล์มาที่นี่)
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------------
# Custom User
# --------------------------------------------------
AUTH_USER_MODEL = "users.User"


# --------------------------------------------------
#9  Auth / Redirect
# --------------------------------------------------
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)


SITE_ID = 1
TAILWIND_APP_NAME = "theme"


# ==================================================
# 10 django-allauth (NEW STYLE – CORRECT & STABLE)
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

# ดึงค่าจาก .env แทนการ Hardcode (ปลอดภัยกว่า)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_AUTHEN")
DEFAULT_FROM_EMAIL = f"Smafolio <{EMAIL_HOST_USER}>"