from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    ordering = ["-criado_em"]
    list_display = ["email", "nome_completo", "cpf_formatado", "status_kyc", "is_active"]
    list_filter = ["status_kyc", "email_verificado", "is_active", "is_staff"]
    search_fields = ["email", "nome_completo", "cpf"]
    readonly_fields = ["criado_em", "atualizado_em", "last_login", "kyc_atualizado_em"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Identidade"), {"fields": ("nome_completo", "cpf", "data_nascimento", "telefone")}),
        (_("Recebimento"), {"fields": ("chave_pix", "tipo_chave_pix")}),
        (_("Verificacao"), {"fields": ("email_verificado", "status_kyc", "kyc_atualizado_em")}),
        (
            _("Permissoes"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Datas"), {"fields": ("last_login", "criado_em", "atualizado_em")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nome_completo",
                    "cpf",
                    "data_nascimento",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description=_("CPF"), ordering="cpf")
    def cpf_formatado(self, obj):
        return obj.cpf_formatado
