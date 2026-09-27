"""
Validacao de identidade.

Numa plataforma de apostas isto nao e formalidade: CPF valido e maioridade sao
exigencias regulatorias, e precisam ser barradas no cadastro — nao depois.
"""

from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

IDADE_MINIMA = 18


def so_digitos(valor: str) -> str:
    """Remove pontuacao: "123.456.789-09" -> "12345678909"."""
    return "".join(c for c in str(valor) if c.isdigit())


def cpf_e_valido(cpf: str) -> bool:
    """Confere os dois digitos verificadores do CPF."""
    cpf = so_digitos(cpf)

    if len(cpf) != 11:
        return False

    # 00000000000, 11111111111, ... passam no calculo mas nao existem
    if cpf == cpf[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        digito = 0 if resto == 10 else resto

        if digito != int(cpf[tamanho]):
            return False

    return True


def validar_cpf(valor: str) -> None:
    if not cpf_e_valido(valor):
        raise ValidationError(_("CPF invalido."), code="cpf_invalido")


def calcular_idade(nascimento: date, hoje: date | None = None) -> int:
    hoje = hoje or date.today()
    completou = (hoje.month, hoje.day) >= (nascimento.month, nascimento.day)
    return hoje.year - nascimento.year - (0 if completou else 1)


def validar_maioridade(valor: date) -> None:
    hoje = date.today()

    if valor > hoje:
        raise ValidationError(_("Data de nascimento no futuro."), code="data_futura")

    if calcular_idade(valor, hoje) < IDADE_MINIMA:
        raise ValidationError(
            _("E necessario ter ao menos %(idade)d anos."),
            code="menor_de_idade",
            params={"idade": IDADE_MINIMA},
        )


def formatar_cpf(cpf: str) -> str:
    """ "12345678909" -> "123.456.789-09". So para exibicao."""
    cpf = so_digitos(cpf)

    if len(cpf) != 11:
        return cpf

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
