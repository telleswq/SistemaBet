"""
Testes de fumaca da fundacao.

Nao testam regra de negocio (ainda nao existe) — testam que a aplicacao sobe,
responde e que as protecoes que nao podem ser desligadas continuam ligadas.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_responde(client):
    resposta = client.get(reverse("core:home"))
    assert resposta.status_code == 200


@pytest.mark.django_db
def test_health_reporta_banco_ok(client):
    resposta = client.get(reverse("core:health"))
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "banco": True}


def test_csrf_middleware_ativo(settings):
    """Foi desligado no sistema antigo. Aqui e regressao."""
    assert "django.middleware.csrf.CsrfViewMiddleware" in settings.MIDDLEWARE


def test_argon2_e_o_hasher_padrao(settings):
    """O sistema antigo usava MD5 sem salt."""
    assert settings.PASSWORD_HASHERS[0].endswith("Argon2PasswordHasher")


def test_producao_exige_secret_key(monkeypatch):
    """prod.py nao pode ter chave padrao: sem SECRET_KEY, deve recusar subir."""
    import importlib

    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "exemplo.com")

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        importlib.reload(importlib.import_module("config.settings.prod"))
