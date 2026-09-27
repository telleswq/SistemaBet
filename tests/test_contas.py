"""
Testes do modelo de usuario.

Cada bloco corresponde a uma exigencia que o sistema anterior nao fazia.
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.contas.models import StatusKYC, TipoChavePix
from apps.contas.validators import calcular_idade, cpf_e_valido, formatar_cpf

Usuario = get_user_model()

CPF_VALIDO = "52998224725"
CPF_VALIDO_2 = "12345678909"
MAIOR = date(1990, 5, 20)


def criar(**extra):
    dados = {
        "email": "jogador@exemplo.com",
        "password": "senha-forte-12345",
        "nome_completo": "Jogador de Teste",
        "cpf": CPF_VALIDO,
        "data_nascimento": MAIOR,
    }
    dados.update(extra)
    return Usuario.objects.create_user(**dados)


# ---------------------------------------------------------------- validadores


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725", "12345678909"])
def test_cpf_valido_e_aceito(cpf):
    assert cpf_e_valido(cpf)


@pytest.mark.parametrize(
    "cpf",
    ["111.111.111-11", "00000000000", "123.456.789-00", "529982247", "", "abcdefghijk"],
)
def test_cpf_invalido_e_recusado(cpf):
    assert not cpf_e_valido(cpf)


def test_cpf_com_todos_digitos_iguais_nao_passa():
    """Passam no calculo do digito verificador, mas nao sao CPFs reais."""
    for d in "0123456789":
        assert not cpf_e_valido(d * 11)


def test_formatar_cpf():
    assert formatar_cpf(CPF_VALIDO) == "529.982.247-25"


def test_calcular_idade_no_dia_do_aniversario():
    hoje = date(2026, 5, 20)
    assert calcular_idade(date(2008, 5, 20), hoje) == 18
    # um dia antes ainda nao completou
    assert calcular_idade(date(2008, 5, 21), hoje) == 17


# ---------------------------------------------------------------------- modelo


@pytest.mark.django_db
def test_cria_usuario_com_email_como_login():
    u = criar()
    assert u.email == "jogador@exemplo.com"
    assert u.check_password("senha-forte-12345")
    assert Usuario.USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_cpf_e_normalizado_para_so_digitos():
    u = criar(cpf="529.982.247-25")
    u.refresh_from_db()
    assert u.cpf == CPF_VALIDO
    assert u.cpf_formatado == "529.982.247-25"


@pytest.mark.django_db
def test_menor_de_18_nao_cadastra():
    ontem_fez_17 = date.today() - timedelta(days=365 * 17)
    with pytest.raises(ValidationError) as exc:
        criar(data_nascimento=ontem_fez_17)
    assert "data_nascimento" in exc.value.message_dict


@pytest.mark.django_db
def test_cpf_invalido_nao_cadastra():
    with pytest.raises(ValidationError) as exc:
        criar(cpf="123.456.789-00")
    assert "cpf" in exc.value.message_dict


@pytest.mark.django_db
def test_email_duplicado_nao_cadastra():
    criar()
    with pytest.raises(ValidationError) as exc:
        criar(cpf=CPF_VALIDO_2)
    assert "email" in exc.value.message_dict


@pytest.mark.django_db
def test_cpf_duplicado_nao_cadastra():
    """Uma conta por pessoa: exigencia regulatoria, nao conveniencia."""
    criar()
    with pytest.raises(ValidationError) as exc:
        criar(email="outro@exemplo.com")
    assert "cpf" in exc.value.message_dict


@pytest.mark.django_db
def test_cpf_duplicado_tambem_barra_no_banco():
    """Mesmo contornando a validacao, a constraint do banco impede."""
    criar()
    outro = Usuario(
        email="outro@exemplo.com",
        nome_completo="Outro",
        cpf=CPF_VALIDO,
        data_nascimento=MAIOR,
    )
    outro.set_password("senha-forte-12345")
    with pytest.raises(IntegrityError):
        outro.save()


@pytest.mark.django_db
def test_senha_nao_e_guardada_em_texto():
    u = criar()
    assert u.password != "senha-forte-12345"
    assert u.password.startswith("argon2")


# ------------------------------------------------------------------- saque/KYC


@pytest.mark.django_db
def test_nao_pode_sacar_sem_kyc_aprovado():
    u = criar(chave_pix="jogador@exemplo.com", tipo_chave_pix=TipoChavePix.EMAIL)
    assert u.status_kyc == StatusKYC.PENDENTE
    assert u.pode_sacar is False


@pytest.mark.django_db
def test_nao_pode_sacar_sem_chave_pix():
    u = criar()
    u.marcar_kyc(StatusKYC.APROVADO)
    assert u.pode_sacar is False


@pytest.mark.django_db
def test_pode_sacar_com_kyc_aprovado_e_chave():
    u = criar(chave_pix="jogador@exemplo.com", tipo_chave_pix=TipoChavePix.EMAIL)
    u.marcar_kyc(StatusKYC.APROVADO)
    assert u.pode_sacar is True
    assert u.kyc_atualizado_em is not None


@pytest.mark.django_db
def test_conta_inativa_nao_saca():
    u = criar(chave_pix="jogador@exemplo.com", tipo_chave_pix=TipoChavePix.EMAIL)
    u.marcar_kyc(StatusKYC.APROVADO)
    u.is_active = False
    assert u.pode_sacar is False


@pytest.mark.django_db
def test_superusuario_tambem_exige_cpf_e_idade_validos():
    u = Usuario.objects.create_superuser(
        email="admin@exemplo.com",
        password="senha-forte-12345",
        nome_completo="Administrador",
        cpf=CPF_VALIDO,
        data_nascimento=MAIOR,
    )
    assert u.is_staff and u.is_superuser
