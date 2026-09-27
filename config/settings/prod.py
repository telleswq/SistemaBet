"""
Producao. Falha ao subir se algo essencial estiver faltando —
e melhor nao subir do que subir inseguro.
"""

from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = False

SECRET_KEY = env("SECRET_KEY", obrigatorio=True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS e obrigatorio em producao.")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# --- HTTPS obrigatorio -------------------------------------------------

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 8

# --- Estaticos -------------------------------------------------------------
# Exige `python manage.py collectstatic` antes de subir.

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- E-mail ----------------------------------------------------------------
# Sem configuracao explicita o Django usa SMTP em localhost:25: o envio falha,
# e como a falha e capturada para nao derrubar o cadastro, ninguem receberia o
# link de verificacao e o problema passaria despercebido. Mesma filosofia do
# SECRET_KEY: melhor nao subir do que subir sem conseguir verificar e-mail.

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", obrigatorio=True)
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", obrigatorio=True)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", obrigatorio=True)
EMAIL_USE_TLS = True
# sem timeout, um SMTP travado prende o worker durante o cadastro
EMAIL_TIMEOUT = 10
