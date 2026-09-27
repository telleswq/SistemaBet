from django.urls import path

from . import views

app_name = "contas"

urlpatterns = [
    path("cadastro/", views.CadastroView.as_view(), name="cadastro"),
    path("entrar/", views.LoginView.as_view(), name="login"),
    path("sair/", views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
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
