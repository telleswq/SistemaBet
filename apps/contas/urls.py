from django.urls import path

from . import views

app_name = "contas"

urlpatterns = [
    path("cadastro/", views.CadastroView.as_view(), name="cadastro"),
    path("entrar/", views.LoginView.as_view(), name="login"),
    path("sair/", views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    # A rota com <token> vem DEPOIS das fixas: `str` casaria "pendente" e
    # "reenviar" como se fossem token.
    path(
        "verificar/pendente/",
        views.VerificacaoPendenteView.as_view(),
        name="verificacao_pendente",
    ),
    path(
        "verificar/reenviar/",
        views.ReenviarVerificacaoView.as_view(),
        name="verificacao_reenviar",
    ),
    path(
        "verificar/<str:token>/",
        views.VerificarEmailView.as_view(),
        name="verificacao_confirmar",
    ),
    path("senha/", views.RedefinirSenhaView.as_view(), name="senha_redefinir"),
    path(
        "senha/enviado/",
        views.RedefinirSenhaEnviadoView.as_view(),
        name="senha_redefinir_enviado",
    ),
    path(
        "senha/<uidb64>/<token>/",
        views.RedefinirSenhaConfirmaView.as_view(),
        name="senha_redefinir_confirma",
    ),
    path(
        "senha/concluido/",
        views.RedefinirSenhaConcluidoView.as_view(),
        name="senha_redefinir_concluido",
    ),
]
