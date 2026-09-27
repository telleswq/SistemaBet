"""
Telas de conta.

Autenticacao usa as views prontas do Django sempre que possivel: sao revisadas
ha anos e ja tratam invalidacao de sessao, tokens de uso unico e enumeracao de
usuario. Escrever a nossa seria refazer trabalho e errar.
"""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView

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

        # mesma mensagem da plataforma anterior
        messages.success(
            self.request,
            f"Bem Vindo {form.instance.nome_completo}! Você já pode se logar na sua conta",
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


@login_required
def perfil(request):
    form = PerfilForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Foi atualizado com sucesso!")

        return redirect("contas:perfil")

    return render(request, "contas/perfil.html", {"form": form})
