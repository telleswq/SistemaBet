# Auditoria do sistema anterior

**Data:** 2026-09-27
**Alvo:** plataforma de apostas em PHP (CodeIgniter 3.1.13), pacote redistribuido
**Resultado:** reescrita. Este documento e o **porque**.

> Nao ha credencial, chave ou identificador de terceiro neste documento. As falhas
> sao descritas pela classe e pela licao que deixam, nao como roteiro de ataque.

## Por que isso importa aqui

Cada regra de desenvolvimento do projeto e cada decisao do
`docs/adr/0001-stack.md` vem de um item desta lista. Sem este contexto, as
regras parecem paranoia; com ele, sao cicatriz.

O padrao que emergiu **nao e "o codigo tem bugs"**. E ausencia sistematica de
garantias: nada verificava nada. Onde havia verificacao, era acidental.

## Metodo

A auditoria nao foi planejada. Comecou como "fazer o projeto rodar" e as falhas
apareceram sozinhas: a primeira ao abrir uma funcao por motivo alheio, a segunda
ao conferir um endpoint antes de responder a uma pergunta.

**Essa e a licao mais importante do dia.** As duas piores falhas foram achadas por
acaso, nao por busca dirigida. A densidade sugeria que o que foi visto era uma
fracao do que existia.

## Achados

### 1. Dinheiro — critico

**Saque sem verificacao de saldo.** Valor e destino chegavam do cliente. Nao havia
leitura de saldo, debito, nem aprovacao. Sem sessao exigida. Tres consequencias:
saque de valor arbitrario, saque para destino arbitrario, e saque repetido do
mesmo saldo (porque nada debitava).

**Credito de saldo exposto.** Rotinas que creditavam saldo eram metodos publicos de
controller — ou seja, URLs — sem autenticacao. O mesmo no painel administrativo.

**Deposito nunca creditava.** A rotina de credito era chamada com o numero errado de
argumentos: erro fatal, em codigo que nunca havia sido executado com sucesso. A
transacao era marcada como paga *antes* da tentativa de credito. O jogador pagava
e nao recebia.

**Sem idempotencia.** O identificador de transacao nao era unico e a confirmacao
dependia do navegador do cliente fazer polling — nao de webhook servidor-a-servidor.
Fechar a aba perdia o deposito.

**Trilha de auditoria quebrada.** Ajustes internos de saldo gravavam o valor a
partir de uma variavel inexistente: todo lancamento entrava sem valor.

> **Licoes:** regras de dinheiro (Decimal, atomicidade, falha fechada,
> idempotencia, validacao de destino, ledger append-only).

### 2. Controle de acesso — critico

**Metodos publicos sem guarda.** Um levantamento automatizado encontrou 14 metodos
de controller acessiveis sem sessao que deveriam exigir uma — inclusive de
administracao. Nao por decisao: por esquecimento, um a um.

**Identificador vindo da URL sem conferencia de dono.** Permitia editar a conta de
outra pessoa trocando um numero. Combinado com atribuicao em massa, permitia
assumir a conta.

**Atribuicao em massa.** O corpo inteiro da requisicao ia para o banco. Qualquer
campo que o atacante inventasse era gravado.

> **Licoes:** regras de acesso (autenticado por padrao, conferir dono do
> recurso, campos explicitos em vez de atribuicao em massa).

### 3. Autenticacao — alto

**Senhas em MD5 sem salt**, tanto de jogadores quanto de administradores.
**CSRF desligado** nos dois aplicativos. **Sem limite de tentativas** de login.

> **Licoes:** Argon2 e CSRF tem teste de regressao em `tests/test_smoke.py`.

### 4. Injecao — medio

Parametro de indicacao refletido cru no HTML (XSS refletido).

### 5. Cadeia de distribuicao — alto

O dump do banco distribuido com o pacote continha **credenciais ativas de dois
terceiros** — provedor de jogos e processador de pagamento. Verificado: nao estavam
expiradas; a API reconheceu o par e recusou apenas por IP nao autorizado.

Quem instalasse o pacote e configurasse o proprio servidor estaria operando com a
conta de outra pessoa, possivelmente sem perceber.

> **Licoes:** Gitleaks no CI; `.gitignore` testado arquivo por arquivo.

### 6. Arquitetura — a razao de fundo

O saldo real vivia na API do provedor, mas o saque saia do gateway de pagamento, e
**nada reconciliava os dois**. O saldo local era cache sobrescrito pela API, nao um
ledger. Para ajustar saldo, o sistema zerava no provedor e depositava de novo —
operacao nao atomica, sujeita a corrida.

Isso nao esta com bug. **Esta ausente.** Ledger, idempotencia, conciliacao e
aprovacao de saque nao sao correcoes: sao construcao.

## Conclusao

O sistema anterior recebeu correcoes emergenciais (autenticacao, hashing, ledger
minimo, fechamento dos endpoints) para nao ficar exposto enquanto existisse. Nao
e base para evoluir.

A decisao de reescrever esta em `docs/adr/0001-stack.md`.
