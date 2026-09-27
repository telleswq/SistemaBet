# SistemaBet

Plataforma de apostas online. Reescrita em Python, do zero.

> **Estado:** fundacao. A aplicacao sobe, tem CI e testes — ainda sem regra de negocio.

## Stack

| Camada | Escolha |
|---|---|
| Backend | Django 5 (Python 3.12) |
| Banco | PostgreSQL 16 |
| Front | Templates Django + Tailwind + HTMX + Alpine.js |
| Infra | Docker Compose |
| Qualidade | Ruff, pytest, Gitleaks no CI |

O porque de cada escolha esta em [`docs/adr/0001-stack.md`](docs/adr/0001-stack.md).

## Rodando

```bash
cp .env.example .env          # ajuste se quiser
docker compose up -d --build
docker compose exec web python manage.py migrate
```

- Aplicacao: http://localhost:8010
- Admin: http://localhost:8010/admin/ (crie o usuario com `createsuperuser`)
- Estado: http://localhost:8010/health/

```bash
docker compose exec web python manage.py createsuperuser
```

### CSS

O Tailwind e compilado para `static/css/app.css`, que **e versionado**.
Ao mexer em template ou classe, recompile:

```bash
npm install
npm run css:build     # ou: npm run css  (modo watch)
```

### Testes e lint

```bash
docker compose exec web pytest
docker compose exec web ruff check .
```

## Seguranca

Este repositorio e **publico**. Nenhum segredo pode ser commitado:

- credenciais ficam em `.env` (ignorado pelo git); o modelo e o `.env.example`
- uploads de KYC vao para `media/` (ignorado) e nunca para o repo
- o CI roda Gitleaks em todo push e PR
- `config/settings/prod.py` se recusa a subir sem `SECRET_KEY` e `ALLOWED_HOSTS`

Se um segredo for commitado, considere-o **vazado**: reescrever o historico nao
apaga clones, forks nem o cache do GitHub. Rotacione a credencial.
