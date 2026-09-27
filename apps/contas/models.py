"""
Modelo de usuario da plataforma.

Login por e-mail (nao por username): o jogador se identifica pelo e-mail, e o
CPF e a identidade legal, unica por conta.

A chave PIX vive AQUI, no perfil. O saque usa esta chave e nunca a que vier na
requisicao — foi assim que o sistema anterior permitia sacar para qualquer
destino.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import (
    calcular_idade,
    formatar_cpf,
    so_digitos,
    validar_cpf,
    validar_maioridade,
)


class UsuarioManager(BaseUserManager):
    """Manager sem username: a identificacao e o e-mail."""

    use_in_migrations = True

    def _criar(self, email, password, **extra):
        if not email:
            raise ValueError("E-mail e obrigatorio.")

        email = self.normalize_email(email)

        if extra.get("cpf"):
            extra["cpf"] = so_digitos(extra["cpf"])

        usuario = self.model(email=email, **extra)
        usuario.set_password(password)
        usuario.full_clean(exclude=["password"])
        usuario.save(using=self._db)

        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)

        return self._criar(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)

        if extra.get("is_staff") is not True:
            raise ValueError("Superusuario precisa de is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superusuario precisa de is_superuser=True.")

        return self._criar(email, password, **extra)


class StatusKYC(models.TextChoices):
    PENDENTE = "pendente", _("Pendente")
    EM_ANALISE = "em_analise", _("Em analise")
    APROVADO = "aprovado", _("Aprovado")
    RECUSADO = "recusado", _("Recusado")


class TipoChavePix(models.TextChoices):
    CPF = "CPF", _("CPF")
    EMAIL = "EMAIL", _("E-mail")
    PHONE = "PHONE", _("Telefone")
    EVP = "EVP", _("Chave aleatoria")


class Usuario(AbstractUser):
    # AbstractUser traz username; aqui a identificacao e o e-mail
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(_("e-mail"), unique=True)

    nome_completo = models.CharField(_("nome completo"), max_length=150)

    cpf = models.CharField(
        _("CPF"),
        max_length=11,
        unique=True,
        validators=[validar_cpf],
        help_text=_("Somente digitos."),
    )

    data_nascimento = models.DateField(
        _("data de nascimento"),
        validators=[validar_maioridade],
    )

    telefone = models.CharField(_("telefone"), max_length=20, blank=True)

    # --- destino de saque -------------------------------------------------
    chave_pix = models.CharField(_("chave PIX"), max_length=140, blank=True)
    tipo_chave_pix = models.CharField(
        _("tipo da chave PIX"),
        max_length=10,
        choices=TipoChavePix.choices,
        blank=True,
    )

    # --- verificacao ------------------------------------------------------
    email_verificado = models.BooleanField(_("e-mail verificado"), default=False)

    status_kyc = models.CharField(
        _("status do KYC"),
        max_length=12,
        choices=StatusKYC.choices,
        default=StatusKYC.PENDENTE,
    )
    kyc_atualizado_em = models.DateTimeField(_("KYC atualizado em"), null=True, blank=True)

    criado_em = models.DateTimeField(_("criado em"), auto_now_add=True)
    atualizado_em = models.DateTimeField(_("atualizado em"), auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome_completo", "cpf", "data_nascimento"]

    objects = UsuarioManager()

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome_completo} <{self.email}>"

    def clean(self):
        # guarda o CPF sempre so com digitos: a unicidade depende disso
        self.cpf = so_digitos(self.cpf)
        self.email = UsuarioManager.normalize_email(self.email)

        super().clean()

    def save(self, *args, **kwargs):
        self.cpf = so_digitos(self.cpf)

        super().save(*args, **kwargs)

    @property
    def cpf_formatado(self) -> str:
        return formatar_cpf(self.cpf)

    @property
    def idade(self) -> int:
        return calcular_idade(self.data_nascimento)

    @property
    def pode_sacar(self) -> bool:
        """Saque exige KYC aprovado e uma chave PIX cadastrada."""
        return (
            self.is_active
            and self.status_kyc == StatusKYC.APROVADO
            and bool(self.chave_pix)
            and bool(self.tipo_chave_pix)
        )

    def marcar_kyc(self, status: str) -> None:
        self.status_kyc = status
        self.kyc_atualizado_em = timezone.now()
        self.save(update_fields=["status_kyc", "kyc_atualizado_em", "atualizado_em"])
