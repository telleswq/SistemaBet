"""
Formularios de conta.

Todo formulario declara os campos explicitamente. Nunca `fields = "__all__"`:
era por atribuicao em massa que o sistema anterior deixava o atacante gravar
qualquer coluna.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import TipoChavePix, Usuario, normalizar_email
from .validators import so_digitos, validar_cpf


class EstiloMixin:
    """
    Aplica a classe de input e usa o label como placeholder.

    O layout segue o da plataforma anterior: campos sem label visivel, com o
    texto dentro do proprio campo.
    """

    placeholders: dict[str, str] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nome, campo in self.fields.items():
            atuais = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = f"{atuais} campo".strip()
            campo.widget.attrs.setdefault("placeholder", self.placeholders.get(nome, campo.label))


class CadastroForm(EstiloMixin, UserCreationForm):
    placeholders = {
        "nome_completo": "Nome completo",
        "email": "E-mail",
        "cpf": "Digite seu CPF",
        "telefone": "Whatsapp",
        "password1": "Senha",
        "password2": "Confirme a senha",
    }

    # O campo do modelo tem max_length=11 e recusaria "529.982.247-25" (14)
    # antes de chegar na normalizacao. O formulario aceita a forma digitada;
    # o modelo continua guardando so digitos.
    cpf = forms.CharField(
        label=_("CPF"),
        max_length=14,
        widget=forms.TextInput(attrs={"inputmode": "numeric"}),
    )

    class Meta:
        model = Usuario
        fields = ["nome_completo", "email", "cpf", "data_nascimento", "telefone"]
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean_cpf(self):
        # normaliza antes da checagem de unicidade, senao a pontuacao
        # permitiria duas contas para o mesmo CPF
        cpf = so_digitos(self.cleaned_data["cpf"])
        validar_cpf(cpf)

        return cpf

    def clean_email(self):
        return normalizar_email(self.cleaned_data["email"])


class LoginForm(EstiloMixin, AuthenticationForm):
    placeholders = {"username": "E-mail", "password": "Senha"}

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _("E-mail ou senha invalidos, precisa de ajuda para lembrar seu login?."),
    }

    # O campo continua se chamando "username": e a convencao do
    # AuthenticationForm e o que o axes le do POST para contar tentativas.
    username = forms.EmailField(
        label=_("E-mail"),
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    def clean_username(self):
        # o e-mail e gravado em minusculas; sem normalizar aqui, quem digita
        # com maiuscula nao consegue entrar
        return normalizar_email(self.cleaned_data["username"])


class PerfilForm(EstiloMixin, forms.ModelForm):
    placeholders = {
        "nome_completo": "Nome completo",
        "telefone": "Whatsapp",
        "chave_pix": "Sua chave PIX",
    }

    """Dados que o proprio jogador edita. CPF e data de nascimento ficam de
    fora: mudam a identidade verificada e so a operacao altera."""

    class Meta:
        model = Usuario
        fields = ["nome_completo", "telefone", "chave_pix", "tipo_chave_pix"]

    def clean(self):
        dados = super().clean()
        chave = (dados.get("chave_pix") or "").strip()
        tipo = dados.get("tipo_chave_pix") or ""

        if chave and not tipo:
            self.add_error("tipo_chave_pix", _("Informe o tipo da chave."))

        if tipo and not chave:
            self.add_error("chave_pix", _("Informe a chave."))

        if tipo == TipoChavePix.CPF and so_digitos(chave) != self.instance.cpf:
            self.add_error(
                "chave_pix",
                _("A chave do tipo CPF precisa ser o CPF da propria conta."),
            )

        return dados
