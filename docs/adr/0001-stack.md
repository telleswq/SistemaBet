# ADR 0001 — Escolha de stack

**Data:** 2026-09-27
**Status:** aceito

## Contexto

Este projeto substitui uma plataforma existente em PHP (CodeIgniter 3). Antes de
comecar, o sistema antigo foi auditado. Os achados foram:

- senhas em MD5 sem salt;
- CSRF desligado nos dois aplicativos;
- endpoints de credito de saldo publicos, sem autenticacao;
- saque que nao verificava saldo, nao debitava e aceitava a chave PIX do POST;
- deposito que nunca creditava (erro de aridade nunca detectado);
- mass assignment e IDOR permitindo tomada de conta;
- ausencia total de idempotencia em operacoes de dinheiro;
- credenciais ativas de terceiros distribuidas no dump do banco.

O padrao comum nao e "bugs": e **ausencia de garantias**. A stack nova precisa
tornar o caminho seguro o caminho mais facil.

## Decisao

### Django 5, e nao FastAPI/Flask

Cada falha grave da auditoria corresponde a algo que o Django ja traz ligado:
CSRF por padrao, hashing forte, ORM parametrizado, sistema de permissoes, e um
admin pronto — o painel que consumiu horas de correcao no sistema antigo.

FastAPI e excelente, mas entregaria mais liberdade justamente onde a liberdade
foi o problema.

### PostgreSQL

Precisamos de `SELECT ... FOR UPDATE`, constraints de integridade e `NUMERIC`
confiavel para dinheiro.

### Templates + Tailwind + HTMX + Alpine, e nao SPA

O produto e grid de jogos, filtros, modais e saldo atualizando. HTMX cobre isso
sem um segundo aplicativo, sem duplicar API e sem build separado. Se surgir app
mobile, expomos DRF; nao antes.

## Consequencias

- Ganhamos seguranca por padrao e velocidade inicial.
- Abrimos mao de interatividade rica de SPA. Aceitavel para o escopo atual.
- Um `runserver` nao serve producao: sera gunicorn atras de proxy com TLS.

## ~~Pendente~~ — RESOLVIDO em 2026-09-28

O provedor **suporta carteira seamless**. Ver
[`0002-carteira-seamless.md`](0002-carteira-seamless.md).

O texto original desta secao dizia que o sistema anterior usava carteira por
transferencia e que era dai que vinham a dessincronizacao, a corrida e o saque
infinito — e que confirmar o suporte a seamless era pre-requisito para modelar
a carteira. A confirmacao veio: o modelo e seamless.
