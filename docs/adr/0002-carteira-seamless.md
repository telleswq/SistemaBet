# ADR 0002 — Carteira seamless

**Data:** 2026-09-28
**Status:** aceito
**Resolve:** a pendencia deixada em aberto no [ADR 0001](0001-stack.md)

## Contexto

O ADR 0001 deixou uma pergunta travando o modelo da carteira: **o provedor de
jogos suporta carteira seamless?**

O sistema anterior usava **carteira por transferencia** — para ajustar saldo,
zerava no provedor e depositava de novo. Dai vinham a dessincronizacao, a
corrida e o saque infinito descritos em
[`../auditoria-sistema-anterior.md`](../auditoria-sistema-anterior.md).

## Decisao

**Seamless.** A documentacao do provedor (Games2API) traz o modo explicitamente,
com dois callbacks que a API envia **para o nosso servidor**:

| Callback | O que faz |
|---|---|
| `user_balance` | o provedor PERGUNTA o saldo do jogador para nos |
| `transaction` | o provedor NOTIFICA aposta e premio, com `txn_id` |

Ou seja: **o saldo passa a ter fonte unica de verdade no nosso banco.** Some a
classe inteira de bug que quebrou o sistema anterior — nao existe mais "saldo
daqui" e "saldo de la" para conciliar.

## Consequencias

O ganho vem com uma troca: **passamos a estar no caminho critico da aposta.**
Se o nosso callback cair ou responder devagar, o jogo trava para o jogador.
Isso muda requisitos:

- o endpoint de callback precisa ser rapido e ter disponibilidade alta;
- nao pode depender de servico externo para responder;
- precisa de log suficiente para reconstruir qualquer sessao de jogo.

## Seguranca do callback — o ponto que exige cuidado

A documentacao publica **nao menciona assinatura, HMAC nem whitelist de IP**.
A autenticacao aparente e apenas o `agent_secret` no corpo do JSON.

Um segredo compartilhado no corpo, sozinho, nao basta para um endpoint que
credita dinheiro. Quem obtiver o segredo credita o que quiser, e nao ha
carimbo de tempo para impedir repeticao. Portanto, do nosso lado:

1. **Comparacao do segredo em tempo constante** — nunca `==`.
2. **Idempotencia obrigatoria em `txn_id`**, com constraint de unicidade no
   banco. Esta e a nossa defesa contra repeticao, ja que o provedor nao
   oferece nenhuma. Sem isso, reenviar o mesmo pacote credita de novo.
3. **Aposta so e aceita se o saldo cobrir** — o valor vem do provedor, mas
   quem decide se ha saldo somos nos. Debito atomico, como no resto do sistema.
4. **HTTPS obrigatorio** e, se o provedor publicar os IPs de saida, whitelist.
5. **Nunca confiar em `user_code`** sem resolver para um usuario existente e
   ativo.

> **Pendente:** obter a secao "Seguranca do Callback" do painel do provedor
> (o guia publico nao a renderiza). Se houver assinatura ou lista de IPs
> documentada, incorporar. Ate la, valem as regras acima.

## Estado da integracao

Credenciais validadas contra `https://api.games2api.xyz`:

- `agent_code` e o nome da conta; `agent_token` e a string **completa**,
  incluindo o prefixo antes dos dois-pontos (nao a parte depois);
- os valores vivem no `.env`, **nunca no repositorio**;
- a conta respondeu **"O Agente esta sem saldo"** — autenticacao passa, mas nao
  ha credito. A integracao nao pode ser exercitada ponta a ponta ate a conta
  ser creditada.
