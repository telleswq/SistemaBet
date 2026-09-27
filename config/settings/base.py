"""
Configuracao comum a todos os ambientes.

Nada de segredo aqui: tudo que e sensivel vem de variavel de ambiente.
Este arquivo vai para um repositorio publico.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(nome: str, padrao: str | None = None, *, obrigatorio: bool = False) -> str:
    valor = os.environ.get(nome, padrao)
    if obrigatorio and not valor:
        raise RuntimeError(f"Variavel de ambiente obrigatoria ausente: {nome}")
    return valor or ""


def env_bool(nome: str, padrao: bool = False) -> bool:
    return env(nome, str(int(padrao))).strip().lower() in {"1", "true", "yes", "on"}


def env_list(nome: str, padrao: str = "") -> list[str]:
    return [item.strip() for item in env(nome, padrao).split(",") if item.strip()]


# --- Aplicacoes --------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "axes",
]

LOCAL_APPS = [
    "apps.core",
    "apps.contas",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # CSRF ligado por padrao. Nao remover.
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # precisa ser o ultimo: conta as tentativas depois da autenticacao
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

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
                "apps.core.context_processors.operacao",
            ],
        },
    },
]

# --- Banco -------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "sistemabet"),
        "USER": env("POSTGRES_USER", "sistemabet"),
        "PASSWORD": env("POSTGRES_PASSWORD", "sistemabet"),
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "ATOMIC_REQUESTS": False,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modelo de usuario proprio desde o inicio: trocar depois de existir dado
# significa migrar chaves estrangeiras em toda a base.
AUTH_USER_MODEL = "contas.Usuario"

# --- Autenticacao ------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    # o backend do axes vem primeiro: bloqueia antes de conferir a senha
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "contas:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

# Bloqueio de tentativas. O sistema anterior nao tinha nenhum: dava para
# testar senha indefinidamente.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
# trava a combinacao usuario+IP: nao derruba todos os usuarios de um mesmo IP,
# e nao deixa um atacante trocar de IP para continuar no mesmo usuario
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
# O axes assume por padrao o USERNAME_FIELD do modelo ("email"), mas o campo
# que chega no POST se chama "username" (convencao do AuthenticationForm).
# Sem isto o usuario e gravado como None e o bloqueio vira bloqueio de IP —
# pior ainda, a consulta por (username, ip) nao casa e a senha CORRETA passa.
AXES_USERNAME_FORM_FIELD = "username"
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "contas/bloqueado.html"
AXES_VERBOSE = True

# --- Senhas ------------------------------------------------------------
# Argon2 primeiro. O sistema antigo usava MD5 sem salt; aqui isso nao se repete.

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Localizacao -------------------------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- Estaticos ---------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# O storage com manifest exige collectstatic previo; e comportamento de
# producao e fica em prod.py. Aqui, o storage simples.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Sessao e cookies --------------------------------------------------

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"

# --- Licenca e dados da operacao ---------------------------------------
# Ficam aqui, e nao no template, porque mudam com a empresa e com a
# autorizacao — e porque exibir licenca errada e afirmacao falsa.
# Os valores padrao sao os que a plataforma anterior exibia.

OPERACAO = {
    "razao_social": env("OPERACAO_RAZAO_SOCIAL", "Nexus"),
    "registro": env("OPERACAO_REGISTRO", "150731"),
    "endereco": env("OPERACAO_ENDERECO", "Groot Kwartierweg 10, Curacao"),
    "licenca": env(
        "OPERACAO_LICENCA",
        "Master License of Gaming Services Provider, N.V. #365/JAZ "
        "License Number: GLH-OCCHKTW0709172018",
    ),
    "licenciador": env("OPERACAO_LICENCIADOR", "Governo de Curacao"),
    "agente_pagamento": env(
        "OPERACAO_AGENTE_PAGAMENTO",
        "Horangi Trading Limited, Chytron 30, 2nd floor, Flat/Office A22, "
        "1075, Nicosia, Chipre — registro HE 411494",
    ),
}

# --- E-mail ------------------------------------------------------------

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "nao-responda@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# --- Log ---------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simples": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simples"},
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
}
