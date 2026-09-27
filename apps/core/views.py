from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def health(request):
    """Usado pelo Docker e pelo CI para saber se a aplicacao esta de pe."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "degradado", "banco": False}, status=503)

    return JsonResponse({"status": "ok", "banco": True})
