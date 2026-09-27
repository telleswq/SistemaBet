"""
Token do link de verificacao de e-mail.

**Escolha: `django.core.signing`, e nao o gerador de token do reset de senha.**
Tres motivos concretos:

1. **Janela de validade propria.** O `PasswordResetTokenGenerator` le a validade
   de `settings.PASSWORD_RESET_TIMEOUT`, que e global. Redefinir senha e
   confirmar e-mail tem risco e urgencia diferentes; compartilhar a constante
   obrigaria a escolher uma janela ruim para um dos dois.

2. **Nenhum identificador solto na URL.** O fluxo de reset do Django leva o id
   do usuario em `uidb64`, fora da assinatura. Aqui o id vai DENTRO do payload
   assinado: a URL nao tem nenhum identificador que o cliente possa trocar. E a
   regra 8 do projeto ("nunca confiar em id vindo da URL") aplicada na raiz, e
   nao conferida depois.

3. **Uso unico sem tabela de tokens.** O payload carrega uma impressao do estado
   que a verificacao muda. Depois de confirmar, a impressao do usuario no banco
   deixa de casar com a do token e o mesmo link para de valer — sem precisar de
   tabela de tokens consumidos (que seria mais uma credencial em repouso).

O que continua igual ao Django: HMAC derivado da `SECRET_KEY`, salt proprio para
o token nao valer em outro contexto, e carimbo de tempo conferido na leitura.
"""

from django.core import signing
from django.utils.crypto import constant_time_compare

from .models import Usuario

# Salt proprio: um token assinado para outro proposito (ou o contrario) nao
# atravessa. Nao e segredo — o segredo e a SECRET_KEY.
SALT_VERIFICACAO = "apps.contas.verificacao-email"

# 24h. Tempo de sobra para quem so abre o e-mail no dia seguinte, e curto o
# bastante para um link esquecido em caixa de entrada nao valer para sempre.
VALIDADE_SEGUNDOS = 60 * 60 * 24


class TokenInvalido(Exception):
    """Token ausente, adulterado, expirado ou ja consumido."""


def _impressao(usuario: Usuario) -> str:
    """
    Estado do usuario que o link consome.

    Muda quando o e-mail e confirmado (o link vira de uso unico) e quando o
    e-mail e alterado (um link antigo nao confirma um endereco novo).
    """
    return f"{usuario.email}|{int(bool(usuario.email_verificado))}"


def gerar_token(usuario: Usuario) -> str:
    """Token assinado e com carimbo de tempo para o link de verificacao."""
    return signing.dumps(
        {"uid": usuario.pk, "fp": _impressao(usuario)},
        salt=SALT_VERIFICACAO,
    )


def usuario_do_token(token: str) -> Usuario:
    """
    Devolve o usuario do token, ou levanta `TokenInvalido`.

    Um unico tipo de erro para todos os casos: quem chama nao consegue (nem
    deve) distinguir "expirado" de "adulterado" de "ja usado". Distinguir na
    resposta informaria o atacante e abriria enumeracao de contas.
    """
    if not token:
        raise TokenInvalido("token ausente")

    try:
        # SignatureExpired herda de BadSignature: expirado e adulterado caem
        # no mesmo except, de proposito.
        dados = signing.loads(token, salt=SALT_VERIFICACAO, max_age=VALIDADE_SEGUNDOS)
    except signing.BadSignature as exc:
        raise TokenInvalido("assinatura invalida ou expirada") from exc

    if not isinstance(dados, dict):
        raise TokenInvalido("payload em formato inesperado")

    uid = dados.get("uid")
    impressao = dados.get("fp")

    if not isinstance(uid, int) or not isinstance(impressao, str):
        raise TokenInvalido("payload em formato inesperado")

    # conta inativa nao confirma e-mail: quem foi desativado nao volta por link
    usuario = Usuario.objects.filter(pk=uid, is_active=True).first()

    if usuario is None:
        raise TokenInvalido("usuario inexistente ou inativo")

    if not constant_time_compare(impressao, _impressao(usuario)):
        raise TokenInvalido("link ja usado, ou e-mail alterado depois do envio")

    return usuario
