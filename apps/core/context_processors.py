"""Dados da operacao disponiveis em todo template."""

from django.conf import settings


def operacao(request):
    """Razao social, licenca e agente de pagamento, para o rodape."""
    return {"operacao": settings.OPERACAO}
