"""
Guarda reutilizavel para telas que exigem e-mail confirmado.

**Nao esta aplicada em nenhuma tela existente**, de proposito: entra pronta e
testada, e sera ligada quando a regra passar a valer (carteira, deposito, saque
— fases 2 e 3 do roadmap). Ligar agora mudaria o acesso de telas que nao fazem
parte desta tarefa.

A guarda cobre os dois casos, e nao so o segundo: usuario anonimo cai no login
como em qualquer tela autenticada. Assim ela SUBSTITUI o `login_required` em vez
de depender de alguem lembrar de empilhar os dois — foi esquecimento, um a um,
que deixou 14 metodos abertos no sistema anterior.
"""

from functools import wraps

from django.conf import settings
from django.contrib.auth.views import redirect_to_login

# Para onde vai quem esta logado mas ainda nao confirmou o e-mail.
URL_PENDENTE = "contas:verificacao_pendente"


def exigir_email_verificado(view=None, *, url_pendente=URL_PENDENTE):
    """
    Exige sessao ativa **e** `email_verificado`.

    Usa `redirect_to_login`, entao o destino original volta em `?next=` e o
    jogador retoma de onde parou depois de confirmar.

    Nao grava mensagem no `messages`: a guarda precisa rodar em qualquer
    contexto (inclusive sem o middleware de mensagens). Quem explica o que
    falta e a tela de destino.

    Aceita as duas formas::

        @exigir_email_verificado
        def deposito(request): ...

        @exigir_email_verificado(url_pendente="contas:verificacao_pendente")
        def saque(request): ...
    """

    def decorador(func):
        @wraps(func)
        def envelope(request, *args, **kwargs):
            usuario = getattr(request, "user", None)

            if usuario is None or not usuario.is_authenticated:
                # redirect_to_login resolve nome de rota sozinho
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

            if not usuario.email_verificado:
                return redirect_to_login(request.get_full_path(), url_pendente)

            return func(request, *args, **kwargs)

        return envelope

    if view is not None:
        return decorador(view)

    return decorador


class EmailVerificadoRequeridoMixin:
    """
    Mesma guarda, para views baseadas em classe. Dispensa o `LoginRequiredMixin`.

    Ajuste o destino com o atributo de classe::

        class Deposito(EmailVerificadoRequeridoMixin, FormView):
            url_pendente = "contas:verificacao_pendente"
    """

    url_pendente = URL_PENDENTE

    def dispatch(self, request, *args, **kwargs):
        guardada = exigir_email_verificado(
            super().dispatch,
            url_pendente=self.url_pendente,
        )

        return guardada(request, *args, **kwargs)
