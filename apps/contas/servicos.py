"""
Envio do link de verificacao de e-mail, limite de reenvio e marcacao no banco.

O limite existe porque um endpoint que dispara e-mail e um vetor de bombardeio:
sem teto, qualquer um transforma a plataforma em ferramenta de flood contra uma
caixa de entrada — e queima a reputacao do nosso remetente no caminho.

Duas barreiras, nesta ordem:

1. O reenvio exige sessao (ver `views.ReenviarVerificacaoView`). Sem campo de
   e-mail publico nao ha como mirar um endereco alheio, nem enumerar contas.
2. Teto por usuario em janela deslizante, contado no banco.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import EnvioVerificacaoEmail, Usuario
from .tokens import VALIDADE_SEGUNDOS, gerar_token

logger = logging.getLogger(__name__)

LIMITE_ENVIOS = 3
JANELA_ENVIOS = timedelta(hours=1)


def envios_na_janela(usuario: Usuario) -> int:
    """Quantos links foram disparados para este usuario na janela atual."""
    return EnvioVerificacaoEmail.objects.filter(
        usuario=usuario,
        criado_em__gte=timezone.now() - JANELA_ENVIOS,
    ).count()


def pode_enviar(usuario: Usuario) -> bool:
    if usuario.email_verificado:
        return False

    return envios_na_janela(usuario) < LIMITE_ENVIOS


def url_verificacao(usuario: Usuario, request: HttpRequest) -> str:
    caminho = reverse("contas:verificacao_confirmar", kwargs={"token": gerar_token(usuario)})

    # build_absolute_uri monta a URL a partir do Host da requisicao. Quem
    # protege isso e ALLOWED_HOSTS, que em producao e obrigatorio e explicito
    # (config/settings/prod.py). Sem ele, um Host forjado apontaria o link para
    # o servidor do atacante e o token sairia junto.
    return request.build_absolute_uri(caminho)


def enviar_verificacao(usuario: Usuario, request: HttpRequest) -> bool:
    """
    Dispara o link de verificacao. Devolve True se o e-mail saiu.

    Registra o pedido ANTES de tentar entregar: o teto conta pedidos, nao
    entregas. Se o SMTP falhar, o pedido ja consumiu cota — e o lado seguro para
    um vetor de bombardeio, e o usuario tem o reenvio como saida.

    Nunca propaga excecao de envio: o cadastro nao pode virar erro 500 porque o
    servidor de e-mail piscou. A conta ja existe e o link e reenviavel.
    """
    if not pode_enviar(usuario):
        return False

    EnvioVerificacaoEmail.objects.create(usuario=usuario)

    contexto = {
        "nome": usuario.nome_completo,
        "link": url_verificacao(usuario, request),
        "validade_horas": VALIDADE_SEGUNDOS // 3600,
    }

    # splitlines/join: assunto com "\n" permitiria injetar cabecalho no e-mail.
    # E o mesmo cuidado que o PasswordResetForm do Django toma.
    assunto = "".join(
        render_to_string("contas/email/verificacao_assunto.txt", contexto).splitlines()
    )
    # O template do corpo usa `{% autoescape off %}`: e texto puro, e escapar
    # HTML ali transformaria o apostrofo de um nome em "&#x27;". Sem HTML nao ha
    # XSS a prevenir, e o assunto ja foi higienizado acima.
    corpo = render_to_string("contas/email/verificacao.txt", contexto)

    try:
        send_mail(assunto, corpo, settings.DEFAULT_FROM_EMAIL, [usuario.email])
    except Exception:
        # Sem e-mail e sem token no log: um e dado pessoal, o outro e
        # credencial de uso unico. So o id interno.
        logger.exception("falha ao enviar verificacao de e-mail (usuario %s)", usuario.pk)
        return False

    return True


def marcar_email_verificado(usuario: Usuario) -> bool:
    """
    Marca o e-mail como verificado. Devolve True se esta chamada foi a que mudou.

    UPDATE condicional em vez de ler-depois-gravar: dois cliques simultaneos no
    mesmo link nao verificam duas vezes, e o UPDATE toca so estas colunas — nao
    regrava o usuario inteiro a partir de um objeto em memoria, que e a forma de
    um `save()` desavisado desfazer alteracao concorrente.
    """
    agora = timezone.now()

    linhas = Usuario.objects.filter(pk=usuario.pk, email_verificado=False).update(
        email_verificado=True,
        email_verificado_em=agora,
        # `update()` nao dispara auto_now; sem isto o registro ficaria com
        # atualizado_em antigo
        atualizado_em=agora,
    )

    if linhas:
        usuario.email_verificado = True
        usuario.email_verificado_em = agora

    return bool(linhas)
