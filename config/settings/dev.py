"""Desenvolvimento local. Nunca usar em producao."""

from .base import *  # noqa: F403
from .base import env, env_bool, env_list

DEBUG = env_bool("DEBUG", True)

# Em dev existe um padrao para a aplicacao subir sem configuracao.
# Em producao (prod.py) a chave e obrigatoria e nao tem padrao.
SECRET_KEY = env("SECRET_KEY", "dev-inseguro-nao-use-fora-do-seu-computador")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")

INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
