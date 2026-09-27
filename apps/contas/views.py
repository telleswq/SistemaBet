"""
Telas de conta.

Autenticacao usa as views prontas do Django sempre que possivel: sao revisadas
ha anos e ja tratam invalidacao de sessao, tokens de uso unico e enumeracao de
usuario. Escrever a nossa seria refazer trabalho e errar.
"""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, TemplateView

from . import servicos, tokens
from .forms import CadastroForm, LoginForm, PerfilForm


class CadastroView(CreateView):
    form_class = CadastroForm
    template_name = "contas/cadastro.html"
    success_url = reverse_lazy("contas:login")

    @method_decorator(sensitive_post_parameters("password1", "password2"))
    def dispatch(self, request, *args, **kwargs):
        # ja autenticado nao cadastra outra conta
        if request.user.is_authenticated:
            return redirect("core:home")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        resposta = super().form_valid(form)

        # Link de confirmacao logo apos criar a conta. `enviar_verificacao` nao
        # propaga falha de SMTP: a conta ja existe e o link e reenviavel — virar
        # erro 500 aqui deixaria o jogador sem conta aparente e com conta criada.
        servicos.enviar_verificacao(form.instance, self.request)

        # mesma mensagem da plataforma anterior
        messages.success(
            self.request,
            f"Bem Vindo {form.instance.nome_completo}! Você já pode se logar na sua conta",
        )
        messages.info(
            self.request,
            "Enviamos um link de confirmação para o seu e-mail. "
            "Confirme para liberar sua conta por completo.",
        )

        return resposta


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "contas/login.html"
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    """Só aceita POST: logout por GET permitiria deslogar alguem com um link."""


class RedefinirSenhaView(auth_views.PasswordResetView):
    template_name = "contas/senha_redefinir.html"
    email_template_name = "contas/email/senha_redefinir.txt"
    subject_template_name = "contas/email/senha_redefinir_assunto.txt"
    success_url = reverse_lazy("contas:senha_redefinir_enviado")


class RedefinirSenhaEnviadoView(auth_views.PasswordResetDoneView):
    template_name = "contas/senha_redefinir_enviado.html"


class RedefinirSenhaConfirmaView(auth_views.PasswordResetConfirmView):
    template_name = "contas/senha_redefinir_confirma.html"
    success_url = reverse_lazy("contas:senha_redefinir_concluido")


class RedefinirSenhaConcluidoView(auth_views.PasswordResetCompleteView):
    template_name = "contas/senha_redefinir_concluido.html"


# --------------------------------------------------- verificacao de e-mail


class VerificarEmailView(View):
    """
    Consome o link de verificacao.

    **Publica por excecao** (regra 7): o link chega por e-mail e o jogador abre
    onde puder — outro navegador, outro aparelho, sem sessao. A autorizacao aqui
    e o token assinado, nao a sessao.

    Nao autentica ninguem ao confirmar. Transformar o link em sessao faria de um
    e-mail vazado (ou de uma caixa de entrada compartilhada) uma tomada de conta
    sem senha.
    """

    def get(self, request, token):
        try:
            usuario = tokens.usuario_do_token(token)
        except tokens.TokenInvalido:
            # Mesma tela para expirado, adulterado e ja usado. Distinguir diria
            # ao atacante qual parte ele acertou e permitiria sondar contas.
            return render(request, "contas/verificacao/invalido.html")

        servicos.marcar_email_verificado(usuario)

        return render(request, "contas/verificacao/confirmado.html")


class VerificacaoPendenteView(LoginRequiredMixin, TemplateView):
    """
    Tela de quem ainda nao confirmou o e-mail, e de onde sai o reenvio.

    Exige sessao: um formulario publico com campo de e-mail permitiria mirar
    endereco alheio (bombardeio) e descobrir quais e-mails tem conta
    (enumeracao). Com sessao, o unico destino possivel e o e-mail da propria
    conta — nao ha id nem endereco vindo do cliente.
    """

    template_name = "contas/verificacao/pendente.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.email_verificado:
            return redirect("contas:perfil")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            pode_reenviar=servicos.pode_enviar(self.request.user),
            limite_envios=servicos.LIMITE_ENVIOS,
            janela_minutos=int(servicos.JANELA_ENVIOS.total_seconds() // 60),
            **kwargs,
        )


class ReenviarVerificacaoView(LoginRequiredMixin, View):
    """
    Reenvia o link para o e-mail da conta da sessao.

    So POST (sem `get`, o `View` responde 405): por GET, um `<img src=...>` num
    site qualquer dispararia e-mail a cada visita do jogador, e o CSRF nao cobre
    GET. Mesmo raciocinio do logout.
    """

    def post(self, request):
        usuario = request.user

        if usuario.email_verificado:
            messages.info(request, "Seu e-mail já está confirmado.")

            return redirect("contas:perfil")

        if not servicos.pode_enviar(usuario):
            messages.error(
                request,
                "Você já pediu o link de confirmação várias vezes. "
                "Aguarde alguns minutos antes de tentar de novo.",
            )
        elif servicos.enviar_verificacao(usuario, request):
            messages.success(
                request,
                "Enviamos um novo link de confirmação para o seu e-mail.",
            )
        else:
            messages.error(
                request,
                "Não foi possível enviar o e-mail agora. Tente novamente mais tarde.",
            )

        return redirect("contas:verificacao_pendente")


# ----------------------------------------------------------------- perfil


@login_required
def perfil(request):
    form = PerfilForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Foi atualizado com sucesso!")

        return redirect("contas:perfil")

    return render(request, "contas/perfil.html", {"form": form})
