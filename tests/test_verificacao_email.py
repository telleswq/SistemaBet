"""
Testes da verificacao de e-mail.

Cobrem o fluxo e, sobretudo, o que NAO pode acontecer: link expirado valendo,
link adulterado valendo, link de um jogador confirmando a conta de outro, mesmo
link valendo duas vezes, e reenvio sem teto (bombardeio de e-mail).
"""

import time
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import mail, signing
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.views import View

from apps.contas import servicos, tokens
from apps.contas.decorators import EmailVerificadoRequeridoMixin, exigir_email_verificado
from apps.contas.models import EnvioVerificacaoEmail

Usuario = get_user_model()

SENHA_DE_TESTE = "senha-de-teste-12345"  # gitleaks:allow
CPF_VALIDO = "52998224725"
CPF_VALIDO_2 = "12345678909"


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(
        email="jogador@exemplo.com",
        password=SENHA_DE_TESTE,
        nome_completo="Jogador de Teste",
        cpf=CPF_VALIDO,
        data_nascimento=date(1990, 5, 20),
    )


@pytest.fixture
def outro_usuario(db):
    return Usuario.objects.create_user(
        email="outro@exemplo.com",
        password=SENHA_DE_TESTE,
        nome_completo="Outro Jogador",
        cpf=CPF_VALIDO_2,
        data_nascimento=date(1988, 3, 10),
    )


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


def url_de(usuario):
    """URL de confirmacao valida para o estado atual do usuario."""
    return reverse("contas:verificacao_confirmar", kwargs={"token": tokens.gerar_token(usuario)})


def link_do_email(corpo):
    for linha in corpo.splitlines():
        linha = linha.strip()
        if "/contas/verificar/" in linha:
            return linha

    raise AssertionError("o e-mail nao traz link de verificacao")


def token_expirado(usuario, monkeypatch):
    """
    Token real, assinado com carimbo de tempo no passado.

    Mexe so no instante que o TimestampSigner grava — nao no relogio do
    processo — para exercitar o caminho de expiracao de verdade, com o mesmo
    `max_age` de producao.
    """
    atraso = tokens.VALIDADE_SEGUNDOS + 60
    monkeypatch.setattr(
        signing.TimestampSigner,
        "timestamp",
        lambda self: signing.b62_encode(int(time.time()) - atraso),
    )
    token = tokens.gerar_token(usuario)
    monkeypatch.undo()

    return token


# ------------------------------------------------------- envio no cadastro


@pytest.mark.django_db
def test_cadastro_envia_link_de_verificacao(client):
    resposta = client.post(reverse("contas:cadastro"), dados_cadastro())

    assert resposta.status_code == 302

    u = Usuario.objects.get(email="novo@exemplo.com")
    assert u.email_verificado is False
    assert u.email_verificado_em is None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [u.email]
    assert "/contas/verificar/" in mail.outbox[0].body
    assert EnvioVerificacaoEmail.objects.filter(usuario=u).count() == 1


@pytest.mark.django_db
def test_assunto_nao_tem_quebra_de_linha(usuario, rf):
    """Assunto com "\\n" permitiria injetar cabecalho no e-mail."""
    servicos.enviar_verificacao(usuario, rf.get("/"))

    assert "\n" not in mail.outbox[0].subject
    assert "\r" not in mail.outbox[0].subject


@pytest.mark.django_db
def test_cadastro_nao_falha_se_o_email_nao_sair(client, monkeypatch):
    """A conta ja foi criada: falha de SMTP nao pode virar erro 500."""

    def explode(*args, **kwargs):
        raise OSError("smtp fora do ar")

    monkeypatch.setattr(servicos, "send_mail", explode)

    resposta = client.post(reverse("contas:cadastro"), dados_cadastro())

    assert resposta.status_code == 302
    assert Usuario.objects.filter(email="novo@exemplo.com").exists()


@pytest.mark.django_db
def test_fluxo_completo_do_cadastro_ate_a_confirmacao(client):
    client.post(reverse("contas:cadastro"), dados_cadastro())
    u = Usuario.objects.get(email="novo@exemplo.com")

    resposta = client.get(link_do_email(mail.outbox[0].body))

    assert resposta.status_code == 200
    u.refresh_from_db()
    assert u.email_verificado is True


# -------------------------------------------------------------- link valido


@pytest.mark.django_db
def test_link_valido_verifica(usuario, client):
    resposta = client.get(url_de(usuario))

    assert resposta.status_code == 200
    usuario.refresh_from_db()
    assert usuario.email_verificado is True
    assert usuario.email_verificado_em is not None


@pytest.mark.django_db
def test_confirmar_nao_autentica_ninguem(usuario, client):
    """Link virar sessao faria de um e-mail vazado uma tomada de conta."""
    resposta = client.get(url_de(usuario))

    assert not resposta.wsgi_request.user.is_authenticated


# ------------------------------------------------------------ link invalido


@pytest.mark.django_db
def test_link_expirado_nao_verifica(usuario, client, monkeypatch):
    url = reverse(
        "contas:verificacao_confirmar",
        kwargs={"token": token_expirado(usuario, monkeypatch)},
    )

    resposta = client.get(url)

    assert resposta.status_code == 200
    assert "contas/verificacao/invalido.html" in [t.name for t in resposta.templates]
    usuario.refresh_from_db()
    assert usuario.email_verificado is False


@pytest.mark.django_db
def test_link_adulterado_nao_verifica(usuario, client):
    token = tokens.gerar_token(usuario)
    # troca o ultimo caractere: quebra o HMAC
    adulterado = token[:-1] + ("a" if token[-1] != "a" else "b")

    resposta = client.get(reverse("contas:verificacao_confirmar", kwargs={"token": adulterado}))

    assert resposta.status_code == 200
    usuario.refresh_from_db()
    assert usuario.email_verificado is False


@pytest.mark.django_db
def test_token_assinado_para_outro_contexto_nao_serve(usuario):
    """Mesma SECRET_KEY, salt diferente: o token de outro fluxo nao atravessa."""
    token = signing.dumps({"uid": usuario.pk, "fp": f"{usuario.email}|0"}, salt="outro-contexto")

    with pytest.raises(tokens.TokenInvalido):
        tokens.usuario_do_token(token)


@pytest.mark.django_db
def test_token_sem_assinatura_nao_serve(usuario, client):
    """Payload legivel nao basta: sem HMAC nao passa."""
    resposta = client.get(
        reverse("contas:verificacao_confirmar", kwargs={"token": f"uid-{usuario.pk}"})
    )

    assert resposta.status_code == 200
    usuario.refresh_from_db()
    assert usuario.email_verificado is False


@pytest.mark.django_db
def test_link_de_conta_inativa_nao_verifica(usuario, client):
    url = url_de(usuario)
    usuario.is_active = False
    usuario.save(update_fields=["is_active"])

    client.get(url)

    usuario.refresh_from_db()
    assert usuario.email_verificado is False


# ------------------------------------------------- o link e de um dono so


@pytest.mark.django_db
def test_link_de_um_usuario_nao_verifica_outro(usuario, outro_usuario, client):
    """O id do dono vai dentro da assinatura, nao na URL."""
    resposta = client.get(url_de(usuario))

    assert resposta.status_code == 200
    usuario.refresh_from_db()
    outro_usuario.refresh_from_db()
    assert usuario.email_verificado is True
    assert outro_usuario.email_verificado is False


@pytest.mark.django_db
def test_token_resolve_exatamente_o_dono(usuario, outro_usuario):
    assert tokens.usuario_do_token(tokens.gerar_token(usuario)).pk == usuario.pk
    assert tokens.usuario_do_token(tokens.gerar_token(outro_usuario)).pk == outro_usuario.pk


# ------------------------------------------------------------- uso unico


@pytest.mark.django_db
def test_mesmo_link_duas_vezes_nao_reverifica(usuario, client):
    url = url_de(usuario)

    client.get(url)
    usuario.refresh_from_db()
    primeiro_carimbo = usuario.email_verificado_em

    resposta = client.get(url)

    assert resposta.status_code == 200
    assert "contas/verificacao/invalido.html" in [t.name for t in resposta.templates]

    usuario.refresh_from_db()
    assert usuario.email_verificado is True
    # o carimbo intacto prova que o segundo acesso nao reprocessou nada
    assert usuario.email_verificado_em == primeiro_carimbo


@pytest.mark.django_db
def test_trocar_o_email_invalida_link_antigo(usuario, client):
    """Link emitido para um endereco nao confirma outro."""
    url = url_de(usuario)
    usuario.email = "trocado@exemplo.com"
    usuario.save(update_fields=["email"])

    client.get(url)

    usuario.refresh_from_db()
    assert usuario.email_verificado is False


# --------------------------------------------------------------- reenvio


@pytest.mark.django_db
def test_reenvio_exige_login(client):
    resposta = client.post(reverse("contas:verificacao_reenviar"))

    assert resposta.status_code == 302
    assert reverse("contas:login") in resposta.url
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_reenvio_por_get_nao_envia(usuario, client):
    """GET permitiria disparar e-mail com <img src=...>, fora do alcance do CSRF."""
    client.force_login(usuario)

    resposta = client.get(reverse("contas:verificacao_reenviar"))

    assert resposta.status_code == 405
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_reenvio_manda_novo_link_para_o_proprio_email(usuario, client):
    client.force_login(usuario)

    resposta = client.post(reverse("contas:verificacao_reenviar"))

    assert resposta.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [usuario.email]


@pytest.mark.django_db
def test_reenvio_nao_manda_para_quem_ja_confirmou(usuario, client):
    servicos.marcar_email_verificado(usuario)
    client.force_login(usuario)

    client.post(reverse("contas:verificacao_reenviar"))

    assert len(mail.outbox) == 0


# ---------------------------------------------------------- limite de reenvio


@pytest.mark.django_db
def test_limite_de_reenvio_para_o_bombardeio(usuario, client):
    client.force_login(usuario)
    url = reverse("contas:verificacao_reenviar")

    for _ in range(servicos.LIMITE_ENVIOS):
        client.post(url)

    assert len(mail.outbox) == servicos.LIMITE_ENVIOS

    # a partir daqui, nenhum e-mail sai mais na janela
    for _ in range(5):
        resposta = client.post(url)

    assert resposta.status_code == 302
    assert len(mail.outbox) == servicos.LIMITE_ENVIOS
    assert EnvioVerificacaoEmail.objects.filter(usuario=usuario).count() == (servicos.LIMITE_ENVIOS)


@pytest.mark.django_db
def test_envio_no_cadastro_conta_para_o_limite(client):
    """O link automatico do cadastro nao e cota extra."""
    client.post(reverse("contas:cadastro"), dados_cadastro())
    u = Usuario.objects.get(email="novo@exemplo.com")

    client.force_login(u)
    for _ in range(servicos.LIMITE_ENVIOS):
        client.post(reverse("contas:verificacao_reenviar"))

    assert len(mail.outbox) == servicos.LIMITE_ENVIOS


@pytest.mark.django_db
def test_limite_libera_depois_da_janela(usuario, client):
    """A janela e deslizante: envio velho nao segura o jogador para sempre."""
    client.force_login(usuario)
    url = reverse("contas:verificacao_reenviar")

    for _ in range(servicos.LIMITE_ENVIOS):
        client.post(url)

    assert servicos.pode_enviar(usuario) is False

    # empurra os envios para fora da janela (auto_now_add exige update direto)
    EnvioVerificacaoEmail.objects.filter(usuario=usuario).update(
        criado_em=timezone.now() - servicos.JANELA_ENVIOS - timedelta(minutes=1)
    )

    assert servicos.pode_enviar(usuario) is True

    client.post(url)

    assert len(mail.outbox) == servicos.LIMITE_ENVIOS + 1


@pytest.mark.django_db
def test_limite_e_por_usuario(usuario, outro_usuario, client):
    """Estourar a cota de uma conta nao bloqueia as outras."""
    client.force_login(usuario)
    for _ in range(servicos.LIMITE_ENVIOS + 2):
        client.post(reverse("contas:verificacao_reenviar"))

    assert servicos.pode_enviar(usuario) is False
    assert servicos.pode_enviar(outro_usuario) is True


# ------------------------------------------------------------ tela pendente


@pytest.mark.django_db
def test_tela_pendente_exige_login(client):
    resposta = client.get(reverse("contas:verificacao_pendente"))

    assert resposta.status_code == 302
    assert reverse("contas:login") in resposta.url


@pytest.mark.django_db
def test_tela_pendente_redireciona_quem_ja_confirmou(usuario, client):
    servicos.marcar_email_verificado(usuario)
    client.force_login(usuario)

    resposta = client.get(reverse("contas:verificacao_pendente"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("contas:perfil")


@pytest.mark.django_db
def test_tela_pendente_mostra_reenvio(usuario, client):
    client.force_login(usuario)

    resposta = client.get(reverse("contas:verificacao_pendente"))

    assert resposta.status_code == 200
    assert reverse("contas:verificacao_reenviar") in resposta.content.decode()


# ------------------------------------------------- guarda reutilizavel


def tela_protegida(request):
    return HttpResponse("liberado")


class TelaProtegidaCBV(EmailVerificadoRequeridoMixin, View):
    def get(self, request):
        return HttpResponse("liberado")


def pedido_de(usuario):
    request = RequestFactory().get("/carteira/deposito/")
    request.user = usuario

    return request


@pytest.mark.django_db
def test_guarda_manda_anonimo_para_o_login():
    resposta = exigir_email_verificado(tela_protegida)(pedido_de(AnonymousUser()))

    assert resposta.status_code == 302
    assert reverse("contas:login") in resposta.url
    assert "next=/carteira/deposito/" in resposta.url


@pytest.mark.django_db
def test_guarda_manda_nao_confirmado_para_a_tela_pendente(usuario):
    resposta = exigir_email_verificado(tela_protegida)(pedido_de(usuario))

    assert resposta.status_code == 302
    assert reverse("contas:verificacao_pendente") in resposta.url
    assert "next=/carteira/deposito/" in resposta.url


@pytest.mark.django_db
def test_guarda_libera_quem_confirmou(usuario):
    servicos.marcar_email_verificado(usuario)

    resposta = exigir_email_verificado(tela_protegida)(pedido_de(usuario))

    assert resposta.status_code == 200
    assert resposta.content == b"liberado"


@pytest.mark.django_db
def test_guarda_aceita_a_forma_com_parenteses(usuario):
    guardada = exigir_email_verificado(url_pendente="contas:verificacao_pendente")(tela_protegida)

    resposta = guardada(pedido_de(usuario))

    assert resposta.status_code == 302
    assert reverse("contas:verificacao_pendente") in resposta.url


@pytest.mark.django_db
def test_mixin_aplica_a_mesma_guarda(usuario):
    vista = TelaProtegidaCBV.as_view()

    assert vista(pedido_de(usuario)).status_code == 302

    servicos.marcar_email_verificado(usuario)

    assert vista(pedido_de(usuario)).status_code == 200


@pytest.mark.django_db
def test_nenhuma_tela_existente_passou_a_exigir_email_confirmado(usuario, client):
    """
    A guarda entra pronta, mas NAO ligada: perfil e home seguem como estavam.
    Se alguem aplicar sem combinar, este teste avisa.
    """
    client.force_login(usuario)

    assert usuario.email_verificado is False
    assert client.get(reverse("contas:perfil")).status_code == 200
    assert client.get(reverse("core:home")).status_code == 200
