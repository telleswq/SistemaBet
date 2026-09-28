# Roadmap

Estado em 2026-09-27. Atualize conforme as fases forem fechando.

## Fase 0 — Fundacao ✅

Django 5.2, PostgreSQL 16, Tailwind/HTMX/Alpine, Docker, CI com lint, testes e
varredura de segredos. Seguranca por padrao (Argon2, CSRF, prod que recusa subir
sem `SECRET_KEY`). Sem regra de negocio.

## Fase 1 — Contas e identidade 🔄 em andamento

Nao depende de nada externo.

- ✅ Modelo de usuario proprio: login por e-mail, CPF unico e validado,
  maioridade barrada no cadastro, chave PIX no perfil, status de KYC
- Cadastro, login, recuperacao de senha, limite de tentativas
- Verificacao de e-mail
- Perfil: dados pessoais, chave PIX (o saque usa a cadastrada, nunca a do request)
- KYC: CPF validado, idade minima 18, upload de documento em `media/` (fora do repo)
- Log de auditoria de acoes sensiveis

## Fase 2 — Carteira e ledger ✅ desbloqueada

O provedor **suporta seamless**. Decisao registrada em
[`adr/0002-carteira-seamless.md`](adr/0002-carteira-seamless.md).

O saldo tem fonte unica de verdade no nosso banco; o provedor chama a nossa API
a cada aposta (`transaction`) e para consultar saldo (`user_balance`).

Duas consequencias que mudam requisito:

- passamos a estar no **caminho critico da aposta**. Se o callback cair ou
  demorar, o jogo trava para o jogador.
- a autenticacao do callback e so um segredo compartilhado no corpo, sem
  assinatura nem carimbo de tempo. A **idempotencia em `txn_id`** deixa de ser
  boa pratica e passa a ser a unica defesa contra repeticao.

O que construir:

- Ledger append-only, dupla entrada, `DECIMAL` sempre
- Saldo derivado de lancamentos, nunca campo editavel solto
- Debito com `select_for_update()` ou `UPDATE ... WHERE saldo >= valor`
- Idempotencia com constraint de unicidade no banco
- Estorno por lancamento novo, nunca por edicao

## Fase 3 — Pagamentos (PIX)

Depende da fase 2.

- Deposito: cobranca, webhook **servidor-a-servidor** com assinatura verificada
- Credito idempotente (webhook e polling repetem)
- Saque: valida saldo, debita, so entao paga; devolve o saldo se o pagamento falhar
- Fila de aprovacao de saque acima de um limite
- Conciliacao diaria com o extrato do gateway

## Fase 4 — Catalogo e jogos

Depende da fase 2.

- Sincronizacao de provedores e jogos
- Lancamento de sessao de jogo (exige sessao autenticada)
- Se seamless: endpoints de aposta/premio/rollback com idempotencia

## Fase 5 — Painel administrativo

Django admin como base, com telas proprias para operacao financeira.

- Perfis de acesso separados (suporte ≠ financeiro ≠ administrador)
- Aprovacao de saque, com registro de quem aprovou
- Ajuste manual de saldo sempre como lancamento identificado
- 2FA obrigatorio

## Fase 6 — Afiliados

- Codigo de indicacao, atribuicao, comissao, extrato

## Fase 7 — Jogo responsavel e conformidade

Afeta o modelo de dados — **nao deixar para o fim**.

- Limites de deposito, perda e tempo, definidos pelo jogador
- Autoexclusao e pausa
- Relatorios de transacao para a autoridade reguladora
- Segregacao contabil de recursos de jogadores
- Trilha de auditoria imutavel

> A autorizacao da SPA/Ministerio da Fazenda e pre-requisito legal para operar
> apostas no Brasil (Lei 14.790/2023). Nao e trabalho de engenharia, mas define
> prazo e alguns requisitos de dados — por isso aparece aqui.

## Ordem sugerida

1. Fase 1 (livre)
2. Responder a pergunta do seamless **em paralelo**
3. Fase 2 assim que a resposta chegar
4. Fases 3 e 4
5. Fase 5, depois 6
6. Fase 7 permeia tudo: cada fase ja nasce com o que lhe cabe
