"""
Testes das telas de conta.

Cobrem o fluxo e, sobretudo, o que NAO pode acontecer: cadastro sem validacao,
login sem limite de tentativas, perfil aberto, logout por GET.
"""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

Usuario = get_user_model()

SENHA_DE_TESTE = "senha-de-teste-12345"  # gitleaks:allow
CPF_VALIDO = "52998224725"


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(
        email="jogador@exemplo.com",
        password=SENHA_DE_TESTE,
        nome_completo="Jogador de Teste",
        cpf=CPF_VALIDO,
        data_nascimento=date(1990, 5, 20),
    )


@pytest.fixture(autouse=True)
def limpa_bloqueios(db):
    """O axes guarda tentativas no banco; um teste nao pode travar o proximo."""
    from axes.models import AccessAttempt

    AccessAttempt.objects.all().delete()
    yield
    AccessAttempt.objects.all().delete()


def dados_cadastro(**extra):
    base = {
        "nome_completo": "Novo Jogador",
        "email": "novo@exemplo.com",
        "cpf": "529.982.247-25",
        "data_nascimento": "1990-05-20",
        "telefone": "(11) 99999-8888",
        "password1": SENHA_DE_TESTE,
        "password2": SENHA_DE_TESTE,
    }
    base.update(extra)
    return base


# ------------------------------------------------------------------- cadastro


@pytest.mark.django_db
def test_cadastro_cria_conta_e_normaliza_cpf(client):
    resposta = client.post(reverse("contas:cadastro"), dados_cadastro())

    assert resposta.status_code == 302
    u = Usuario.objects.get(email="novo@exemplo.com")
    assert u.cpf == CPF_VALIDO  # gravado sem pontuacao
    assert u.status_kyc == "pendente"


@pytest.mark.django_db
def test_cadastro_recusa_menor_de_idade(client):
    hoje = date.today()
    resposta = client.post(
        reverse("contas:cadastro"),
        dados_cadastro(data_nascimento=f"{hoje.year - 15}-01-01"),
    )

    assert resposta.status_code == 200
    assert not Usuario.objects.filter(email="novo@exemplo.com").exists()


@pytest.mark.django_db
def test_cadastro_recusa_cpf_invalido(client):
    resposta = client.post(reverse("contas:cadastro"), dados_cadastro(cpf="123.456.789-00"))

    assert resposta.status_code == 200
    assert not Usuario.objects.exists()


@pytest.mark.django_db
def test_cadastro_recusa_cpf_ja_usado_mesmo_com_pontuacao(usuario, client):
    """A normalizacao acontece antes da checagem de unicidade."""
    resposta = client.post(
        reverse("contas:cadastro"),
        dados_cadastro(cpf="529.982.247-25", email="outro@exemplo.com"),
    )

    assert resposta.status_code == 200
    assert Usuario.objects.count() == 1


@pytest.mark.django_db
def test_cadastro_ignora_campos_nao_declarados(client):
    """Atribuicao em massa: o formulario so aceita os campos que declara."""
    resposta = client.post(
        reverse("contas:cadastro"),
        dados_cadastro(is_staff="true", is_superuser="true", status_kyc="aprovado"),
    )

    assert resposta.status_code == 302
    u = Usuario.objects.get(email="novo@exemplo.com")
    assert u.is_staff is False
    assert u.is_superuser is False
    assert u.status_kyc == "pendente"


# ---------------------------------------------------------------------- login


@pytest.mark.django_db
def test_login_com_credenciais_corretas(usuario, client):
    resposta = client.post(
        reverse("contas:login"),
        {"username": usuario.email, "password": SENHA_DE_TESTE},
    )

    assert resposta.status_code == 302
    assert resposta.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_com_senha_errada_falha(usuario, client):
    resposta = client.post(
        reverse("contas:login"),
        {"username": usuario.email, "password": "errada-errada-1"},
    )

    assert resposta.status_code == 200
    assert not resposta.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_bloqueio_apos_cinco_tentativas(usuario, client, settings):
    """O sistema anterior permitia tentar senha indefinidamente."""
    url = reverse("contas:login")

    for _ in range(settings.AXES_FAILURE_LIMIT):
        client.post(url, {"username": usuario.email, "password": "errada-errada-1"})

    # mesmo com a senha CERTA, o acesso esta bloqueado
    resposta = client.post(url, {"username": usuario.email, "password": SENHA_DE_TESTE})

    assert resposta.status_code == 429
    assert not resposta.wsgi_request.user.is_authenticated


# --------------------------------------------------------------------- logout


@pytest.mark.django_db
def test_logout_por_get_nao_desloga(usuario, client):
    """Logout por GET permitiria deslogar alguem com um link ou <img>."""
    client.force_login(usuario)
    resposta = client.get(reverse("contas:logout"))

    assert resposta.status_code == 405


@pytest.mark.django_db
def test_logout_por_post_desloga(usuario, client):
    client.force_login(usuario)
    resposta = client.post(reverse("contas:logout"))

    assert resposta.status_code == 302
    assert not resposta.wsgi_request.user.is_authenticated


# --------------------------------------------------------------------- perfil


@pytest.mark.django_db
def test_perfil_exige_login(client):
    resposta = client.get(reverse("contas:perfil"))

    assert resposta.status_code == 302
    assert reverse("contas:login") in resposta.url


@pytest.mark.django_db
def test_perfil_salva_chave_pix(usuario, client):
    client.force_login(usuario)
    client.post(
        reverse("contas:perfil"),
        {
            "nome_completo": usuario.nome_completo,
            "telefone": "(11) 90000-0000",
            "chave_pix": "jogador@exemplo.com",
            "tipo_chave_pix": "EMAIL",
        },
    )

    usuario.refresh_from_db()
    assert usuario.chave_pix == "jogador@exemplo.com"


@pytest.mark.django_db
def test_perfil_nao_altera_cpf_nem_kyc(usuario, client):
    """Campos de identidade e verificacao nao sao editaveis pelo jogador."""
    client.force_login(usuario)
    client.post(
        reverse("contas:perfil"),
        {
            "nome_completo": usuario.nome_completo,
            "telefone": "",
            "chave_pix": "",
            "tipo_chave_pix": "",
            "cpf": "12345678909",
            "status_kyc": "aprovado",
            "email": "invasor@exemplo.com",
        },
    )

    usuario.refresh_from_db()
    assert usuario.cpf == CPF_VALIDO
    assert usuario.status_kyc == "pendente"
    assert usuario.email == "jogador@exemplo.com"


@pytest.mark.django_db
def test_chave_pix_do_tipo_cpf_precisa_ser_o_proprio_cpf(usuario, client):
    client.force_login(usuario)
    client.post(
        reverse("contas:perfil"),
        {
            "nome_completo": usuario.nome_completo,
            "telefone": "",
            "chave_pix": "12345678909",
            "tipo_chave_pix": "CPF",
        },
    )

    usuario.refresh_from_db()
    assert usuario.chave_pix == ""


# ------------------------------------------------------------- redefinir senha


@pytest.mark.django_db
def test_redefinicao_envia_email(usuario, client):
    resposta = client.post(reverse("contas:senha_redefinir"), {"email": usuario.email})

    assert resposta.status_code == 302
    assert len(mail.outbox) == 1
    assert usuario.email in mail.outbox[0].to


@pytest.mark.django_db
def test_redefinicao_nao_revela_se_email_existe(client):
    """Resposta identica para e-mail inexistente: evita enumeracao de contas."""
    resposta = client.post(reverse("contas:senha_redefinir"), {"email": "naoexiste@exemplo.com"})

    assert resposta.status_code == 302
    assert resposta.url == reverse("contas:senha_redefinir_enviado")
    assert len(mail.outbox) == 0


# ------------------------------------------------------ normalizacao de e-mail


@pytest.mark.django_db
def test_email_e_gravado_em_minusculas(client):
    """O normalize_email do Django so abaixa o dominio; a parte local tambem
    precisa ser normalizada, senao ha duas contas para o mesmo e-mail."""
    client.post(reverse("contas:cadastro"), dados_cadastro(email="Joao@Exemplo.com"))

    assert Usuario.objects.filter(email="joao@exemplo.com").exists()


@pytest.mark.django_db
def test_email_com_caixa_diferente_nao_cria_segunda_conta(usuario, client):
    resposta = client.post(
        reverse("contas:cadastro"),
        dados_cadastro(email="JOGADOR@EXEMPLO.COM", cpf="12345678909"),
    )

    assert resposta.status_code == 200
    assert Usuario.objects.count() == 1


@pytest.mark.django_db
def test_login_funciona_com_caixa_diferente(usuario, client):
    resposta = client.post(
        reverse("contas:login"),
        {"username": "JOGADOR@Exemplo.com", "password": SENHA_DE_TESTE},
    )

    assert resposta.status_code == 302
    assert resposta.wsgi_request.user.is_authenticated
