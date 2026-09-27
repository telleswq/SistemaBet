# Design System — SistemaBet

Especificação de design para a reescrita. O objetivo é **paridade visual redesenhada**
com a plataforma anterior (`~/rs2`, PHP/CodeIgniter + CSS gerado por Webflow):
a mesma linguagem, a mesma estrutura de tela, a mesma sensação — reconstruída em
Tailwind/HTMX/Alpine, com os erros de contraste e de semântica corrigidos.

Este documento é **especificação**, não implementação. Ele define tokens, anatomia
e estados. Quem escreve o template, o componente e o CSS final é o time de frontend.

- Referência visual: `~/rs2` em `http://localhost:8090`
- Alvo: `~/SistemaBet` em `http://localhost:8010`
- Stack do alvo: Django 5 + Tailwind 3.4 + HTMX + Alpine
- Nada aqui inventa funcionalidade que o sistema antigo não tenha.

---

## 0. Como este documento foi levantado

Todos os valores de cor, tamanho, raio e breakpoint citados como "o antigo" foram
lidos diretamente de:

- `rs2/public/css/app.css` (86 KB, minificado, gerado por Webflow)
- `rs2/application/controllers/Style.php` — gera `:root{…}` em runtime a partir da
  tabela `tema`; é de lá que sai a cor de marca
- `rs2/application/views/pages/layout/header.php` e `footer.php`
- `rs2/application/views/pages/welcome/{home,cassino,game}.php`
- `rs2/application/views/pages/minhaconta/{minhaconta,editarconta,indique}.php`
- `rs2/admin/application/views/pages/**` (painel — Bootstrap 5.3 puro, sem marca)

Todos os contrastes citados foram **calculados** (WCAG 2.1, fórmula de luminância
relativa), inclusive compondo as cores com alpha sobre o fundo real. Não há
estimativa neste documento.

### Três descobertas que mudam o desenho

1. **A tipografia da referência nunca existiu.** O CSS declara
   `font-family: Gilroy, sans-serif` no `body`, mas Gilroy não é carregada em
   nenhum lugar. A referência renderizou a vida toda em Arial. Logo, **não há
   fidelidade tipográfica a preservar** — Inter (já em uso no novo) é ganho puro.

2. **Os ícones da referência nunca existiram.** Todos são `<div>` vazios com
   `font-family:"Fa sharp solid 900"` e nenhum `content`. O menu lateral, o rodapé
   e a navbar do antigo mostram apenas texto, com um buraco de 20–24px ao lado.
   Logo, **há liberdade total de iconografia** — e ganho imediato ao usar SVG real.

3. **O nome do jogo é invisível.** `.name-game { opacity: 0 }`. O catálogo do
   antigo mostra só a arte, sem título. O nome está no DOM (leitor de tela lê),
   mas o usuário vidente nunca vê. Isso não é estilo, é defeito: quebra
   reconhecimento em vez de memória. O redesenho mostra o nome.

---

## 1. Tokens

> **Correção (verificada após a entrega da especificação):** a afirmação de que
> a Gilroy nunca foi carregada está **errada**. O `public/css/app.css` do sistema
> antigo tem cinco `@font-face` de Gilroy apontando para a CDN da Webflow, e a
> CDN **ainda responde** (HTTP 200, ~145 KB). A referência tipográfica existe.
>
> Adotar Inter continua sendo defensável — a Gilroy é fonte comercial e a
> licença veio junto da assinatura Webflow; apontar para a CDN deles a partir de
> um Django próprio é frágil e provavelmente fora da licença. Mas é uma
> **decisão de marca**, não o preenchimento de um vazio. A família fica num
> único token para que a troca seja de uma linha.


### 1.1 Cor

#### De onde a paleta vem

`Style.php` injeta a cor do tenant em `--default`, `--yellow` e `--orange`
(os três são a mesma variável) e fixa o resto:

```
--black:     #141417                  → fundo da página
--211b38:    #1b1b1f                  → fim do gradiente de card/botão
--black-80:  rgba(20,20,23,.9)        → fundo de card
--white-5:   rgba(218,209,177,.05)    → fundo de campo e borda fina  = #1E1D1F
--white-10:  rgba(218,209,177,.1)     → borda de botão e de menu     = #282726
--white-50:  rgba(255,255,255,.3)     → COR DO TEXTO DO BODY         = #5A5A5D
--yellow:    #FF2338 (tenant)         → marca
--yellow10:  rgba(227,45,71,.1)       → wash de card "degrade"
--yellow25:  rgba(227,45,71,.25)      → wash da barra inferior mobile
```

Note que `yellow10`/`yellow25` estão *hardcoded* em `#E32D47`, enquanto a marca
é dinâmica. A paleta real da referência é portanto **dois vermelhos**: `#FF2338`
(marca) e `#E32D47` (washes). O `tailwind.config.js` atual já reflete isso
(`marca.DEFAULT` / `marca.escuro`) — o que confirma a leitura.

#### A decisão difícil: `#FF2338` não pode ser fundo de texto branco

| par | contraste | AA texto normal (4.5:1) |
|---|---|---|
| branco sobre `#FF2338` | **3,78:1** | ❌ |
| branco sobre `#E32D47` | **4,44:1** | ❌ (falta 0,06) |
| branco sobre `#E01B2F` | **4,81:1** | ✅ |
| `#FF2338` sobre `#141417` | **4,86:1** | ✅ |

O botão primário do antigo é `.btn-color-1` = fundo de marca com
`color: var(--gray100)` (branco) e rótulo de 13px/700 — **3,78:1**. Reprova.
E o `marca.escuro` que já está no config novo reprova por 0,06.

**Decisão:** a marca `#FF2338` permanece a cor da identidade e continua visível
em tudo que não seja fundo de texto pequeno — texto de destaque (4,86:1 ✅),
ícones, anel de foco, indicador de item ativo, círculos de categoria, washes de
gradiente, o "R$" do saldo. O **preenchimento do botão primário passa a
`#E01B2F`** (marca-600), que é imperceptivelmente mais profundo e resolve o
contraste. Lado a lado ninguém distingue; no medidor a diferença é aprovar ou não.

> **Alternativa se o dono quiser o `#FF2338` literal no botão:** é possível manter
> o fundo `#FF2338` com texto branco **se o rótulo for texto grande** pela
> definição do WCAG — ≥ 18,66px **e** bold (aí o mínimo cai para 3:1, e 3,78:1
> passa). Custa um rótulo de 19px/700 em botão de 40px, o que fica desproporcional.
> Recomendação: `#E01B2F`.

#### Rampa de marca

| token | hex | sobre `#141417` | branco em cima | uso |
|---|---|---|---|---|
| `marca-50` | `#FFF1F2` | 16,74:1 | 1,10:1 | nada no escuro; reservado |
| `marca-100` | `#FFDFE2` | 14,80:1 | 1,24:1 | reservado |
| `marca-200` | `#FFBEC5` | 11,75:1 | 1,56:1 | reservado |
| `marca-300` | `#FF8E9B` | 8,40:1 | 2,19:1 | texto sobre wash de marca |
| `marca-400` | `#FF5266` | 5,82:1 | 3,16:1 | link/hover de texto, "R$" do saldo |
| `marca-500` | `#FF2338` | **4,86:1** | 3,78:1 | **a marca.** Texto de destaque, ícone, anel de foco, indicador ativo |
| `marca-600` | `#E01B2F` | 3,82:1 | **4,81:1** | preenchimento do botão primário |
| `marca-700` | `#C4122A` | 3,04:1 | 6,06:1 | hover do botão primário |
| `marca-800` | `#9E0F20` | 2,23:1 | 8,26:1 | pressionado / desabilitado |
| `marca-900` | `#6B0B16` | 1,47:1 | 12,47:1 | wash profundo, fundo de gradiente |
| `marca-legado` | `#E32D47` | 4,14:1 | 4,44:1 | **só** wash e gradiente. Nunca fundo de texto. |

`marca-legado` existe para manter rastreabilidade com o antigo (`yellow10`,
`yellow25`, `slate-blue` todos derivam dele). Fica documentado como proibido
para fundo de texto.

#### Neutros

| token | hex | sobre `#141417` | sobre `#1B1B1F` | sobre `#202024` | uso |
|---|---|---|---|---|---|
| `fundo` | `#141417` | — | — | — | fundo da página (idêntico ao antigo) |
| `fundo-card` | `#1B1B1F` | 1,07:1 | — | — | card, painel, dropdown |
| `fundo-campo` | `#202024` | 1,13:1 | — | — | fundo de input/select/textarea |
| `fundo-elevado` | `#232329` | 1,18:1 | 1,10:1 | — | hover de linha/item, zebra de tabela |
| `borda` | `#2A2A30` | 1,29:1 | 1,20:1 | 1,14:1 | divisória **decorativa** (borda de card, régua) |
| `borda-forte` | `#6B6B78` | **3,50:1** | **3,27:1** | 3,09:1 | **limite de controle** (input, select, checkbox) — exigência de 1.4.11 |
| `texto` | `#F4F4F5` | 16,73:1 | 15,62:1 | 14,77:1 | texto primário, título |
| `texto-2` | `#A1A1AA` | 7,17:1 | 6,70:1 | 6,33:1 | texto secundário, rótulo, cabeçalho de tabela |
| `texto-3` | `#8A8A92` | **5,37:1** | **5,01:1** | **4,74:1** | **piso absoluto.** Placeholder, texto auxiliar. Nada abaixo disso. |

O antigo usa `#5A5A5D` (**2,67:1**) como cor de texto do `body` e `#666668`
(**3,21:1**) nos itens do menu lateral. Ambos reprovam. `texto-3` é o piso: não
existe token de texto mais apagado, e `text-white/30`, `text-white/35`,
`text-white/40` — todos presentes hoje em `templates/base.html` — ficam proibidos
para texto.

> **Por que `borda-forte` é tão claro.** O WCAG 1.4.11 pede 3:1 para a informação
> visual que identifica um controle. Num tema escuro o preenchimento do campo
> (`#202024`) está a 1,13:1 do fundo — invisível como fronteira. Sobra a borda,
> e para chegar a 3:1 ela precisa ser `#6B6B78`. É mais cinza do que o antigo
> (`#282726`, 1,23:1), e é o preço da conformidade. Se ficar visualmente pesado,
> a saída **não** é escurecer a borda: é aumentar o contraste do preenchimento
> (campo mais escuro que a página, ex. `#0F0F11`) — mas aí a borda ainda é o
> que marca o limite. Mantenha `#6B6B78`.

#### Semânticos

Cada estado semântico tem três tokens: texto, superfície e borda. A superfície é
a cor base a 18% sobre `fundo-card`; a borda, a 45%.

| estado | texto | contraste do texto sobre a superfície | superfície | borda |
|---|---|---|---|---|
| sucesso | `#6EE7B7` | **8,44:1** | `#193731` | `#16624B` |
| aviso | `#FCD34D` | **8,46:1** | `#42331B` | `#7D5616` |
| erro | `#FDA4AF` | **7,49:1** | `#42212A` | `#7D2B3B` |
| info | `#93C5FD` | **7,54:1** | `#212E46` | `#294980` |

**O erro não usa a marca.** A marca é vermelha; se o erro também for `#FF2338`,
"destaque da marca" e "deu errado" ficam indistinguíveis. O erro usa a família
rose (`#FDA4AF` texto, `#FB7185` borda de campo — 6,83:1 sobre o fundo) e
**sempre** vem acompanhado de ícone e de texto explícito, nunca só de cor
(WCAG 1.4.1). Isso corrige o `text-marca` que hoje está em
`templates/contas/_campo.html` e em `base.html` para mensagens de erro.

#### Fundo ambiente

O antigo tem uma camada decorativa fixa (`.eng-bg-wrapper`): padrão de pontos de
4px + um gradiente em imagem com `opacity:.5` e `hue-rotate(94deg)`, animado em
`translateX(-60%)` ao longo de **50 segundos**. Reproduza a *sensação* sem a
imagem e sem a animação infinita:

```
fundo da página: #141417
wash: radial-gradient(60% 50% at 50% 0%, rgba(255,35,56,.10), transparent 70%)
textura (opcional): radial-gradient(rgba(255,255,255,.035) 1px, transparent 1px) / 4px 4px
```

Nada de animação de 50s: é movimento contínuo sem controle de pausa
(WCAG 2.2.2) e custa bateria em celular.

---

### 1.2 Tipografia

**Família:** Inter (já carregada em `base.html`), com fallback de sistema.
Substitui a Gilroy declarada e nunca carregada do antigo.

**Escala.** A da referência, com três correções: corpo de 13px→14px, peso de
300→400, e rótulo de 11px→12px.

| token | tamanho / entrelinha | peso | equivale no antigo | uso |
|---|---|---|---|---|
| `text-2xs` | 11px / 14px | 500 | `.txt-label` (11/13) | apenas etiqueta em caixa alta com `tracking-widest` |
| `text-xs` | 12px / 16px | 400 | `.small-text`, `.text-size-small` (12) | legenda, texto legal, nome do provedor |
| `text-sm` | 14px / 20px | 400 | `body` (13/16, peso 300) | **corpo padrão** |
| `text-base` | 16px / 24px | 400 | `h4` (1rem) | corpo em leitura longa, valor em card |
| `text-lg` | 18px / 26px | 600 | — | título de card, `h3` de seção secundária |
| `text-xl` | 20px / 28px | 600 | — | título de seção |
| `text-2xl` | 24px / 32px | 600 | `h3` (1.5rem, peso 600) | `h1` de página interna |
| `text-3xl` | 30px / 36px | 700 | `h2` (2rem) | `h1` mobile de home |
| `text-4xl` | 40px / 44px | 700 | `h1` (2.5rem) | `h1` desktop de home |

**Pesos:** 400 corpo · 500 ênfase e rótulo · 600 subtítulo e botão · 700 título.
O peso 300 do antigo sai: 13px/300 em `#5A5A5D` sobre preto é a pior combinação
possível de tamanho, peso e contraste.

**Números de dinheiro:** `font-variant-numeric: tabular-nums` em saldo, valor de
transação e coluna de valor de tabela. Sem isso o saldo "pula" de largura a cada
atualização via HTMX.

**Hierarquia de heading.** O antigo está quebrado: a home não tem `h1`; o rodapé
abre a primeira coluna com `h6` ("Games") e as seguintes com `h5`
("Carteira", "Ajuda"); e `h4` é usado para valor de saldo, para título de seção
e para número de card de afiliado indistintamente. Regra nova: **um `h1` por
página**, descida sem pular nível, e valor numérico é `<p>`/`<span>` estilizado —
nunca heading.

---

### 1.3 Espaçamento

Base 4px, igual ao antigo (que usa `mb-1 mb-2 mt-4 mt-8 mb-16 mb-20 mt-24 mb-32`
e gaps de 8/16/24/48px). A escala padrão do Tailwind já cobre — não precisa
estender. Fixe o uso:

| contexto | valor | Tailwind | origem no antigo |
|---|---|---|---|
| gap interno de item (ícone↔rótulo) | 8px | `gap-2` | `grid-column-gap:8px` |
| gap de grade de catálogo | 16px | `gap-4` | `.eng-slots-int{gap:16px}` |
| padding de card | 24px | `p-6` | `.card{padding:24px}` |
| padding de card de destaque | 32px | `p-8` | `.card-affiliate{padding:2rem}` |
| padding lateral do conteúdo (desktop) | 24px | `px-6` | `.container-medium` ≤991 |
| padding lateral do conteúdo (mobile) | 16px | `px-4` | `.container-medium` ≤767 |
| padding do menu lateral | 24px | `p-6` | `.left-side-bar_navigation-wrapper` |
| espaço entre seções | 32px | `mb-8` | `.main_slots-wrapper{margin-bottom:32px}` |
| padding vertical de topo de conteúdo | 24px | `py-6` | `.container-medium{margin-top:24px}` |
| gap entre itens do menu | 8px | `space-y-2` | `.eng-sublinks-nav{grid-row-gap:8px}` |
| divisória do menu | 24px acima e abaixo | `my-6` | `.line-divisor-nav` |

**Largura de conteúdo.** O antigo usa `max-width:90%` centralizado — elástico e
sem teto, o que estica a grade de catálogo em monitor largo. Substitua por
`max-w-[1440px]`: preserva a densidade em 1440px (onde o antigo vira 7 colunas)
e para de crescer depois.

---

### 1.4 Raio

Os valores da referência, sem alteração:

| token | valor | uso | origem |
|---|---|---|---|
| `rounded` | 4px | moldura do iframe de jogo | `.eng-iframe-slot{border-radius:4px}` |
| `rounded-lg` | 8px | **botão, campo, badge, arte de jogo, alerta** | `.btn-small`, `.input`, `.slot-game`, `.alert` |
| `rounded-xl` | 10px | item de menu com arte (jogo no dropdown) | `.link-menu{border-radius:10px}` |
| `rounded-2xl` | 16px | **card, modal, painel** | `.card`, `.card-affiliate` |
| `rounded-full` | pill | avatar (42px), círculo de categoria (64px) | `.eng-letter-name`, `.eng-stroke-icon-sublink` |

Um só raio por nível de superfície. Botão e campo compartilham 8px — é o que
alinha visualmente um campo com o botão ao lado dele num formulário em linha.

---

### 1.5 Sombra e elevação

O antigo praticamente não usa sombra: separa superfícies por **borda de 1px** e
por gradiente. Mantenha isso — é o que dá o ar de "painel escuro" e evita a
sombra que não aparece em fundo preto.

| nível | superfície | borda | sombra |
|---|---|---|---|
| 0 — página | `bg-fundo` | — | — |
| 1 — card, painel | `bg-fundo-card` | `border border-borda` | — |
| 2 — dropdown, popover | `bg-fundo-card` | `border border-borda` | `shadow-lg shadow-black/40` |
| 3 — modal | `bg-fundo-card` | `border border-borda` | `shadow-2xl shadow-black/60` |
| overlay de modal | `bg-black/70 backdrop-blur-sm` | — | — |

O overlay do antigo é `rgba(22,22,37,.9)` — quase opaco, e o conteúdo atrás
desaparece. `black/70 + blur` mantém contexto e ainda garante que o modal domine.

---

### 1.6 Camadas

O antigo chega a `z-index: 99999` no menu lateral mobile. Fixe a escala:

| camada | z | elemento |
|---|---|---|
| base | 0 | conteúdo |
| ambiente | `-z-10` | wash/textura de fundo |
| sticky | 30 | barra superior |
| navegação fixa | 40 | barra inferior mobile |
| overlay | 50 | fundo escuro de gaveta/modal |
| gaveta / modal | 60 | painel do menu mobile, modal |
| toast | 70 | flash flutuante |

---

### 1.7 Movimento

| propriedade | duração | easing | uso |
|---|---|---|---|
| cor, borda, opacidade | 150ms | `ease-out` | hover e foco de botão, campo, item de menu |
| transformação pequena | 200ms | `ease-out` | elevação de card de jogo, rotação de seta |
| entrada de gaveta/modal | 250ms | `cubic-bezier(.2,.8,.2,1)` | translação do menu mobile, escala do modal |
| saída de gaveta/modal | 200ms | `ease-in` | — |
| skeleton | 1600ms | `linear infinite` | pulso de carregamento |

Os 200ms do antigo (`transition: opacity 200ms ease, transform 200ms ease` nos
modais) estão corretos e ficam. O que sai: a animação de 50s do fundo, a
marquee infinita de provedores de 45s e o carrossel em `data-ride="carousel"`
(auto-avanço sem controle).

**`prefers-reduced-motion: reduce` desliga tudo que se move sozinho** — marquee,
auto-avanço do carrossel, pulso de skeleton (vira estático), e reduz transições
a 0ms. Não é opcional: WCAG 2.3.3.

---

### 1.8 `tailwind.config.js` — configuração completa

Substitui o arquivo atual. É aditivo em relação ao que já existe: `marca.DEFAULT`
continua `#FF2338` e `fundo.DEFAULT` continua `#141417`, então nada do que já
está escrito em template quebra. `marca-escuro` é mantido como alias de
`marca-legado` para não quebrar `btn-marca`, mas está marcado como depreciado.

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./apps/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        // ---- marca -------------------------------------------------------
        // #FF2338 e a cor do tenant no sistema antigo (Style.php -> --yellow).
        // 500 e a marca; 600 e o preenchimento de botao (branco em cima:
        // 4,81:1). Nunca use 500 como fundo de texto pequeno (3,78:1).
        marca: {
          50:  "#FFF1F2",
          100: "#FFDFE2",
          200: "#FFBEC5",
          300: "#FF8E9B",
          400: "#FF5266",
          500: "#FF2338",
          DEFAULT: "#FF2338",
          600: "#E01B2F",
          700: "#C4122A",
          800: "#9E0F20",
          900: "#6B0B16",
          // rgba(227,45,71,*) do CSS antigo. SO wash e gradiente.
          legado: "#E32D47",
          escuro: "#E32D47", // @deprecated: use marca-600 (botao) ou marca-legado (wash)
        },

        // ---- superficie --------------------------------------------------
        fundo: {
          DEFAULT:  "#141417", // --black do antigo
          card:     "#1B1B1F", // --211b38 do antigo
          campo:    "#202024",
          elevado:  "#232329",
          borda:    "#2A2A30", // divisoria DECORATIVA (1,29:1)
        },

        // ---- fronteira de controle --------------------------------------
        // 3,50:1 sobre #141417. Exigido por WCAG 1.4.11 em input/select/
        // checkbox. Nao escureca.
        borda: {
          DEFAULT: "#2A2A30",
          forte:   "#6B6B78",
        },

        // ---- texto -------------------------------------------------------
        // texto-3 e o PISO. Nada de text-white/30, /35, /40 para texto.
        texto: {
          DEFAULT: "#F4F4F5", // 16,73:1
          2:       "#A1A1AA", //  7,17:1
          3:       "#8A8A92", //  5,37:1  <- piso
        },

        // ---- semanticos --------------------------------------------------
        // erro NAO usa a marca: vermelho de marca e vermelho de erro
        // precisam ser distinguiveis.
        sucesso: { DEFAULT: "#6EE7B7", forte: "#10B981", fundo: "#193731", borda: "#16624B" },
        aviso:   { DEFAULT: "#FCD34D", forte: "#F59E0B", fundo: "#42331B", borda: "#7D5616" },
        erro:    { DEFAULT: "#FDA4AF", forte: "#FB7185", fundo: "#42212A", borda: "#7D2B3B" },
        info:    { DEFAULT: "#93C5FD", forte: "#3B82F6", fundo: "#212E46", borda: "#294980" },
      },

      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },

      fontSize: {
        "2xs":  ["11px", { lineHeight: "14px" }],
        xs:     ["12px", { lineHeight: "16px" }],
        sm:     ["14px", { lineHeight: "20px" }],
        base:   ["16px", { lineHeight: "24px" }],
        lg:     ["18px", { lineHeight: "26px" }],
        xl:     ["20px", { lineHeight: "28px" }],
        "2xl":  ["24px", { lineHeight: "32px" }],
        "3xl":  ["30px", { lineHeight: "36px" }],
        "4xl":  ["40px", { lineHeight: "44px" }],
      },

      borderRadius: {
        DEFAULT: "4px",
        lg:  "8px",
        xl:  "10px",
        "2xl": "16px",
      },

      maxWidth: {
        conteudo: "1440px", // substitui o max-width:90% elastico do antigo
        menu:     "256px",  // .left-side-bar_page-padding: min 250 / max 280
      },

      spacing: {
        barra:       "64px", // altura da barra superior (desktop)
        "barra-sm":  "56px", // altura da barra superior (mobile)
        "tabbar":    "64px", // altura da barra inferior mobile
      },

      transitionTimingFunction: {
        gaveta: "cubic-bezier(.2,.8,.2,1)",
      },

      keyframes: {
        pulso:   { "0%,100%": { opacity: ".5" }, "50%": { opacity: "1" } },
        entrada: { from: { opacity: "0", transform: "translateY(4px)" },
                   to:   { opacity: "1", transform: "translateY(0)" } },
      },
      animation: {
        pulso:   "pulso 1600ms linear infinite",
        entrada: "entrada 200ms ease-out",
      },
    },
  },
  plugins: [],
};
```

**Screens:** não estenda. Os breakpoints padrão do Tailwind (`sm:640 md:768
lg:1024 xl:1280 2xl:1536`) mapeiam bem nos do Webflow — ver §2.1.

### 1.9 Camada de componentes (`static/src/input.css`)

Só entram aqui as classes que aparecem em **dezenas** de lugares e que o Django
precisa injetar por `widget.attrs["class"]` (é o caso de `campo`, usado pelo
`EstiloMixin` em `apps/contas/forms.py`). Todo o resto é utilitário no template.

```css
@layer components {
  /* ---- campo -------------------------------------------------------- */
  /* Injetado por EstiloMixin. Borda em borda-forte por 1.4.11.          */
  .campo {
    @apply w-full rounded-lg border border-borda-forte bg-fundo-campo
           px-4 py-2.5 text-sm text-texto placeholder:text-texto-3
           transition-colors duration-150 ease-out
           hover:border-texto-3
           focus:border-marca focus:outline-none
           focus-visible:ring-2 focus-visible:ring-marca
           focus-visible:ring-offset-2 focus-visible:ring-offset-fundo
           disabled:cursor-not-allowed disabled:border-borda
           disabled:bg-fundo-card disabled:text-texto-3
           aria-[invalid=true]:border-erro-forte;
  }
  .campo-com-icone { @apply pl-11; }   /* ícone de 20px + 16px de folga */

  /* ---- botão -------------------------------------------------------- */
  .btn {
    @apply inline-flex h-10 items-center justify-center gap-2 rounded-lg
           px-4 text-sm font-semibold whitespace-nowrap
           transition-colors duration-150 ease-out
           focus-visible:outline-none focus-visible:ring-2
           focus-visible:ring-offset-2 focus-visible:ring-offset-fundo
           disabled:cursor-not-allowed;
  }
  .btn-sm { @apply h-8 px-3 text-xs; }
  .btn-lg { @apply h-12 px-6 text-base; }

  .btn-marca {
    @apply btn bg-marca-600 text-white
           hover:bg-marca-700 active:bg-marca-800
           focus-visible:ring-white
           disabled:bg-marca-800 disabled:text-white/55;
  }
  .btn-vazado {
    @apply btn border border-borda-forte bg-fundo-card text-texto
           hover:border-marca hover:text-marca-400
           active:bg-fundo-elevado
           focus-visible:ring-marca
           disabled:border-borda disabled:text-texto-3;
  }
  .btn-fantasma {
    @apply btn text-texto-2
           hover:bg-fundo-elevado hover:text-texto
           active:bg-fundo-card
           focus-visible:ring-marca
           disabled:text-texto-3;
  }

  /* ---- item de menu lateral ------------------------------------------ */
  .item-menu {
    @apply flex h-11 items-center gap-3 rounded-lg px-4 text-sm font-medium
           text-texto-2 transition-colors duration-150 ease-out
           hover:bg-fundo-elevado hover:text-texto
           focus-visible:outline-none focus-visible:ring-2
           focus-visible:ring-marca focus-visible:ring-offset-2
           focus-visible:ring-offset-fundo;
  }
  .item-menu-ativo {
    @apply bg-marca/15 text-marca-300;
  }

  /* ---- utilitário de dinheiro ---------------------------------------- */
  .num { font-variant-numeric: tabular-nums; }
}
```

Diferenças em relação ao `input.css` atual, e por quê:

| hoje | passa a ser | motivo |
|---|---|---|
| `.campo` com `border-fundo-borda` (1,29:1) | `border-borda-forte` (3,50:1) | WCAG 1.4.11 |
| `.campo` com `placeholder-white/30` (2,67:1) | `placeholder:text-texto-3` (4,74:1) | placeholder é texto; WCAG 1.4.3 |
| `.campo` com `focus:ring-1` | `focus-visible:ring-2` + offset | 1px de anel sobre borda escura é invisível; 2.4.7 |
| `.btn-marca` com `bg-marca` (3,78:1) | `bg-marca-600` (4,81:1) | WCAG 1.4.3 |
| `.btn-marca` com `py-3` (altura variável) | `h-10` fixo | alinhamento com campo de 40px |
| `.btn-*` sem estado de foco | `focus-visible:ring-2` | 2.4.7 |
| `.item-menu` com borda e fundo de card | fundo transparente, hover em `fundo-elevado` | é o padrão do antigo (`.sublink-nav` só ganha fundo quando ativo) e reduz ruído visual numa lista de 8 itens |
| `.item-menu` com `text-white/80` | `text-texto-2` | consistência de token |

---

## 2. Layout

### 2.1 Breakpoints

O antigo usa os do Webflow. O mapeamento para Tailwind:

| antigo | Tailwind | comportamento |
|---|---|---|
| `≤479px` | abaixo de `sm` | catálogo 2 col (`.link-game{min-width:48%}`), gaveta em tela cheia |
| `≤767px` | abaixo de `md` | catálogo 3 col, `.no-mobile` esconde, padding lateral 16px |
| `≤991px` | abaixo de `lg` | **menu lateral vira gaveta**, barra inferior mobile aparece |
| 992–1279 | `lg` | 3 colunas de layout; catálogo 5 col |
| `≥1280px` | `xl` | catálogo 6 col |
| `≥1440px` | entre `xl` e `2xl` | catálogo 7 col |

Só os 1440px não têm breakpoint equivalente. Use `xl:` para 6 colunas e
`2xl:` (1536px) para 7 — ganha-se um ponto de corte padrão e perde-se muito
pouco (a faixa 1440–1535 fica com 6 em vez de 7 colunas). **Não crie um
breakpoint de 1440px** só para isso.

### 2.2 App shell

```
┌──────────────────────────────────────────────────────────────┐
│ barra superior (sticky, 64px)                                │ z-30
│  logo          [ Banca R$ 0,00 ] [+ Depositar] [avatar ▾]    │
├────────────┬─────────────────────────────────────────────────┤
│ menu       │  conteúdo                                       │
│ lateral    │                                                 │
│ 256px      │  max-w-conteudo, px-6                           │
│ sticky     │                                                 │
│ top-64px   │                                                 │
│            │                                                 │
├────────────┴─────────────────────────────────────────────────┤
│ rodapé                                                       │
└──────────────────────────────────────────────────────────────┘

< lg (991px):
┌──────────────────────────────────────────────────────────────┐
│ [≡] logo        [ R$ 0,00 ] [+]                        56px  │ z-30
├──────────────────────────────────────────────────────────────┤
│ conteúdo (largura total, px-4)                               │
│                                                              │
│                                pb-tabbar para não cobrir     │
├──────────────────────────────────────────────────────────────┤
│ [Menu] [Ao vivo] [Cassino] [Conta] [Sair]            64px    │ z-40
└──────────────────────────────────────────────────────────────┘
```

Estrutura de template:

```html
<body class="min-h-full bg-fundo font-sans text-sm text-texto antialiased">
  <a href="#conteudo" class="sr-only focus:not-sr-only focus:absolute focus:left-4
     focus:top-4 focus:z-[80] focus:rounded-lg focus:bg-fundo-card focus:px-4
     focus:py-2 focus:ring-2 focus:ring-marca">Pular para o conteúdo</a>

  <header class="sticky top-0 z-30 h-barra-sm border-b border-borda
                 bg-fundo/95 backdrop-blur lg:h-barra">…</header>

  <div class="mx-auto flex w-full max-w-conteudo gap-6 px-4 lg:px-6">
    <aside class="hidden w-menu shrink-0 lg:block">
      <nav class="sticky top-barra max-h-[calc(100vh-var(--barra))]
                  overflow-y-auto py-6" aria-label="Navegação principal">…</nav>
    </aside>
    <main id="conteudo" class="min-w-0 flex-1 py-6 pb-[calc(theme(spacing.tabbar)+24px)]
                               lg:pb-6">…</main>
  </div>

  <footer class="border-t border-borda">…</footer>
  <nav class="fixed bottom-0 left-0 right-0 z-40 h-tabbar border-t border-borda
              bg-fundo lg:hidden" aria-label="Navegação rápida">…</nav>
</body>
```

Pontos que o antigo erra e que essa estrutura corrige:

- `min-w-0 flex-1` no `<main>` — sem isso a grade de catálogo estica o flex e
  quebra o layout (o antigo contorna com `width:115%` + `padding-right:15%` em
  `.eng-sublinks-2`, que é um remendo de overflow).
- `.left-side_sticky-wrapper` do antigo tem `min-height:100vh` + `overflow:scroll`:
  em desktop o menu tem barra de rolagem própria sempre visível, mesmo com 8
  itens. Aqui: `max-h-[calc(100vh-barra)] overflow-y-auto` — só rola se precisar.
- `overflow:hidden` em `.main-content` do antigo corta dropdown e tooltip. Sai.
- Link de pular conteúdo: não existe no antigo. Com um menu lateral de ~15 links
  antes do conteúdo, é obrigatório (WCAG 2.4.1).

### 2.3 Grade de catálogo

A grade do antigo (`.eng-slots-int._6`), com o `2xl` substituindo os 1440px:

```html
<ul class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5
           xl:grid-cols-6 2xl:grid-cols-7">
```

| largura | colunas | origem |
|---|---|---|
| < 640 | 2 | `.link-game{min-width:48%}` em ≤479 |
| 640–1023 | 3 | `.eng-slots-int._6{…1fr 1fr 1fr}` em ≤767 |
| 1024–1279 | 5 | base `1fr ×5` |
| 1280–1535 | 6 | `@media (min-width:1280px)` |
| ≥ 1536 | 7 | `@media (min-width:1440px)` |

**Proporção do card:** a arte dos jogos é quadrada nos assets do antigo
(`.slot-game{width:100%}` sem altura, com `filter:saturate(130%)`). Fixe
`aspect-square` e `object-cover` para que uma arte fora do padrão não desalinhe
a linha, e mantenha `saturate-[1.15]` (130% é exagerado e distorce as artes
que já vêm saturadas).

### 2.4 Menu lateral no mobile

**Como o antigo faz.** Não é gaveta de verdade: é um `modal` do Bootstrap 4
(`#exampleModal`) com uma **cópia inteira** do menu dentro, duplicando todo o
markup — inclusive `id="balance"` e `id="email"`, que passam a existir duas
vezes no documento. O CSS é `.left-side-bar{position:fixed; max-width:80%;
background-color:#170001; transform:translate(-100%)}` em ≤991, e em ≤479 vira
`width:100vw; margin-top:7.5rem` (tela cheia, empurrada 120px para baixo —
deixando uma faixa morta no topo). O botão de fechar é um `<div>` com
`data-dismiss`, sem `tabindex`, sem `role`, inalcançável por teclado.

**Como fazer.** Um único markup de menu, renderizado uma vez, reposicionado por
CSS. Gaveta de verdade, com Alpine:

```
Repouso (< lg)          Aberta
┌──────────────┐        ┌───────────────┬──────────┐
│              │        │ logo      [×] │          │
│  conteúdo    │        │ ───────────── │ overlay  │
│              │   →    │ Início        │ black/70 │
│              │        │ Minha conta   │ blur-sm  │
└──────────────┘        │ …             │          │
                        └───────────────┴──────────┘
                         320px (max 85vw)
```

Especificação:

| aspecto | valor |
|---|---|
| gatilho | botão `≡` de 44×44px no canto esquerdo da barra superior |
| largura | `w-[320px] max-w-[85vw]` — 85% em vez dos 80% do antigo; nunca 100vw |
| lado | esquerda, `translate-x-0` aberta / `-translate-x-full` fechada |
| altura | `inset-y-0` — **tela cheia**, sem o `margin-top:7.5rem` do antigo |
| superfície | `bg-fundo border-r border-borda` (não `#170001`, que é uma cor órfã) |
| overlay | `bg-black/70 backdrop-blur-sm`, z-50, fecha ao clique |
| transição | 250ms `ease-gaveta` na entrada, 200ms `ease-in` na saída |
| cabeçalho | logo à esquerda + botão fechar `44×44px` (`<button>`, não `<div>`) |
| conteúdo | `overflow-y-auto overscroll-contain` |
| rolagem do fundo | travada enquanto aberta |
| semântica | `role="dialog" aria-modal="true" aria-label="Menu"` |
| foco | move para o botão fechar na abertura; **fica preso** dentro da gaveta; volta ao `≡` no fechamento |
| `Esc` | fecha |
| `prefers-reduced-motion` | sem translação, só troca de opacidade |

A gaveta mostra **os mesmos itens do menu desktop** — Início, Minha Conta,
Indique e Ganhe, Todos os jogos, divisória, Populares / Roletas / Cassino /
Cassino Ao vivo, divisória, Suporte, sociais, copyright. Não uma versão reduzida.
Quando deslogado, o topo da gaveta traz Entrar + Cadastrar; quando logado,
saldo + Depositar, exatamente como no antigo.

**A barra inferior mobile** (`.navbar-mobile`) continua existindo e é
complementar, não redundante: 5 destinos, `flex-1` cada, altura 64px, ícone de
20px + rótulo `text-2xs`, item ativo com `border-t-2 border-marca` (o antigo já
tem `border-top:2px solid transparent` reservado para isso) e `text-marca`.
Alvo real de toque: 64px de altura × ~20% da largura — passa folgado.
Cada item recebe `aria-current="page"` quando ativo.

---

## 3. Componentes

Notação de estados usada em todos: **repouso · hover · foco · ativo/pressionado ·
desabilitado · erro · carregando**. Quando um estado não se aplica ao componente,
está escrito "n/a" com o motivo.

---

### 3.1 Botão

**Anatomia**

```
┌────────────────────────────────┐
│  [ícone 16]  Rótulo  [ícone]   │  h-10 (40px), px-4, gap-2, rounded-lg
└────────────────────────────────┘
   └ opcional     └ text-sm/600   └ opcional (seta, chevron)
```

**Variantes** (o antigo tem duas: `.btn-small` neutro e `.btn-small.btn-color-1`
de marca; acrescento `fantasma` para ações terciárias que hoje viram link `<a
href="#">`)

| variante | repouso | hover | ativo | desabilitado |
|---|---|---|---|---|
| **primário** | `bg-marca-600` + `text-white` (**4,81:1**) | `bg-marca-700` (**6,06:1**) | `bg-marca-800` (**8,26:1**) | `bg-marca-800` + `text-white/55` (3,31:1 — isento por 1.4.3) |
| **secundário** | `bg-fundo-card` + `border-borda-forte` (3,50:1) + `text-texto` (15,62:1) | `border-marca` (4,86:1) + `text-marca-400` (5,44:1) | `bg-fundo-elevado` | `border-borda` + `text-texto-3`, `cursor-not-allowed` |
| **fantasma** | transparente + `text-texto-2` (7,17:1) | `bg-fundo-elevado` + `text-texto` | `bg-fundo-card` | `text-texto-3` |
| **destrutivo** | `bg-erro-fundo` + `border-erro-borda` + `text-erro` (7,49:1) | `bg-erro-forte` + `text-white` (branco sobre `#FB7185` = 2,69:1 → **use** `bg-[#B3213A]`, 6,57:1) | idem escurecido | como secundário |

**Tamanhos**

| tamanho | altura | padding | texto | uso |
|---|---|---|---|---|
| `sm` | 32px | `px-3` | `text-xs` | chip de valor no modal de depósito, ação em linha de tabela |
| `md` | 40px | `px-4` | `text-sm` | padrão — é o `.btn-small` de 42px do antigo, arredondado para a grade de 4px |
| `lg` | 48px | `px-6` | `text-base` | CTA primário de página, submit de formulário em mobile |

Em mobile, **todo botão de ação principal usa `lg` (48px)** ou recebe
`min-h-[44px]`. O antigo tem 42px em tudo, o que passa o mínimo de 24×24
(WCAG 2.5.8) mas fica abaixo dos 44px recomendados para o polegar.

**Foco:** `focus-visible:ring-2 ring-offset-2 ring-offset-fundo`. O anel é
`ring-marca` nas variantes de fundo escuro e **`ring-white`** no primário —
um anel `#FF2338` sobre `#E01B2F` tem 1,27:1 e simplesmente não existe.

**Carregando**

```
┌────────────────────────────────┐
│   ◌  Depositando…              │  aria-busy="true", disabled
└────────────────────────────────┘
```
- largura **travada** (`min-w-[valor de repouso]`) para o botão não pular
- spinner de 16px, `animate-spin`, `border-2 border-white/30 border-t-white`
- rótulo troca para gerúndio; `aria-live="polite"` num `<span>` irmão anuncia
- com `prefers-reduced-motion`: spinner vira `animate-pulso`
- HTMX: `hx-indicator` + `hx-disabled-elt="this"` (impede duplo clique — no
  antigo, `#enviarBotao` do depósito não trava e aceita reenvio)

**Erro:** n/a no botão. Erro pertence ao formulário ou ao alerta, não ao controle.

---

### 3.2 Campo de formulário

**Anatomia** — o antigo tem dois padrões e mistura os dois. Unifique no padrão
com rótulo visível.

```
Rótulo                             ← text-xs/500 text-texto-2, mb-1.5
┌──────────────────────────────┐
│ [ico] 000.000.000-00    [👁] │   ← h-10, rounded-lg, bg-fundo-campo,
└──────────────────────────────┘      border-borda-forte, text-sm text-texto
Somente números. Sem pontuação.    ← text-xs text-texto-3, mt-1  (dica)
⚠ CPF inválido.                    ← text-xs text-erro, mt-1    (erro)
```

- `[ico]` opcional à esquerda, 20px, em `text-texto-3`, com `pl-11` no input
  (o antigo usa `padding-left:44px` — mesmo valor)
- `[👁]` mostrar/ocultar senha: `<button type="button">` de 40×40px,
  `aria-pressed`, `aria-label="Mostrar senha"`/`"Ocultar senha"`.
  No antigo são dois `<div>` alternados por JS, sem foco e sem rótulo.

**O rótulo fica visível.** Hoje `EstiloMixin` em `apps/contas/forms.py` usa o
label como placeholder e esconde o rótulo — que é o padrão do antigo
(`placeholder="E-mail"`, sem `<label>`). Isso quebra três coisas: o rótulo
desaparece quando o campo é preenchido (memória em vez de reconhecimento), o
autofill do navegador escreve em cima, e leitor de tela em alguns
navegadores não anuncia placeholder como nome acessível. **Rótulo acima, sempre.**
O placeholder passa a ser *exemplo de formato* (`"000.000.000-00"`), não
repetição do rótulo. `editarconta.php` do antigo já acerta isso
(`<label class="txt-label with-input">`) — só está com 11px e sobreposto.

**Estados**

| estado | borda | fundo | texto | extra |
|---|---|---|---|---|
| repouso | `borda-forte` (3,50:1) | `fundo-campo` | `texto` (14,77:1) | placeholder `texto-3` (4,74:1) |
| hover | `texto-3` | `fundo-campo` | — | `cursor-text` |
| foco | `marca` (4,86:1) | `fundo-campo` | — | `ring-2 ring-marca ring-offset-2 ring-offset-fundo` |
| preenchido | `borda-forte` | `fundo-campo` | `texto` | sem diferença visual (evita o "campo que muda de cor sozinho") |
| desabilitado | `borda` | `fundo-card` | `texto-3` | `cursor-not-allowed`, sem `opacity` (o antigo usa `opacity:.85 !important`, que degrada o contraste de todo o conjunto) |
| somente leitura | `borda` | `fundo-card` | `texto-2` | `readonly`, cursor normal, texto selecionável |
| **erro** | `erro-forte` (`#FB7185`, 6,03:1 sobre o campo) | `fundo-campo` | `texto` | `aria-invalid="true"`, `aria-describedby` apontando para a mensagem, **ícone ⚠ + texto** |
| carregando | `borda-forte` | `fundo-campo` | `texto` | spinner 16px à direita; usado no autocompletar de CEP |

**Select.** O antigo deixa `.w-select{color:#828282 !important}` (4,78:1 — passa
raspando) e desenha a seta com um pseudo-elemento em `#666`. Padronize:
`appearance-none` + chevron SVG de 16px em `text-texto-2`, `pr-10`, e a mesma
caixa do input. O `<option>` herda o esquema do SO — declare
`color-scheme: dark` no `:root` para o dropdown nativo não abrir em branco.

**Grade de formulário.** `.form-account` do antigo é
`grid-template-columns: 1fr 1fr 1fr 1fr` com campos marcados `.full` para
ocupar a linha — em `editarconta.php` isso produz uma grade de 4 colunas com
campos de larguras irregulares. Substitua por **coluna única** até `md`, e
`md:grid-cols-2` com `md:col-span-2` nos campos longos (endereço, chave PIX).
Formulário de uma coluna tem taxa de conclusão maior; a exceção justificável é
o par CEP/cidade.

**Grupo de valores rápidos** (chips R$20 / R$40 / R$60 do modal de depósito):
`grid grid-cols-3 gap-2`, cada chip é um **`<button type="button">`** com
`aria-pressed` — no antigo são `<a class="btn-small" onclick="$('#valor').val(20)">`,
que não são botões, não recebem foco em ordem útil e não informam seleção.

---

### 3.3 Card de jogo

**Anatomia**

```
┌─────────────────┐
│                 │  arte quadrada, rounded-lg, object-cover
│   arte 1:1      │  saturate-[1.15]
│                 │
│  ┌───────────┐  │  ← overlay no hover/foco: bg-black/55
│  │  ▶ Jogar  │  │    + botão primário sm centralizado
│  └───────────┘  │
└─────────────────┘
Fortune Tiger        ← text-sm/500 text-texto, truncate  (NOVO: o antigo esconde)
PG Soft              ← text-xs text-texto-3
```

O link envolve o card inteiro (`<a>` com a arte + nome). O nome fica **visível** —
é a correção mais importante do catálogo. Sem ele, o usuário precisa reconhecer
~200 jogos pela arte.

**Estados**

| estado | efeito |
|---|---|
| repouso | arte a 100%, sem overlay, `border border-borda` |
| hover | `-translate-y-0.5`, `border-marca/40`, overlay `bg-black/55` + botão "▶ Jogar", 200ms |
| foco | **mesmo overlay do hover** + `ring-2 ring-marca ring-offset-2 ring-offset-fundo`. No antigo o efeito é só `:hover` — quem navega por teclado nunca vê o botão Jogar |
| pressionado | `scale-[.98]` |
| desabilitado / "Em breve" | arte em `grayscale opacity-60`; faixa `Em breve` centralizada em `bg-black/75 text-texto`; `aria-disabled="true"`; o link vira `<div>` ou `<a>` sem `href`. O antigo tem `.coming-soon-alert` com `rgba(22,22,37,.8)` — mantém o padrão |
| erro (arte não carrega) | bloco `bg-fundo-elevado` com as iniciais do jogo em `text-lg text-texto-2` centralizadas. Melhor que o ícone de imagem quebrada |
| carregando | skeleton: `aspect-square rounded-lg bg-fundo-elevado animate-pulso` + duas barras de texto (`h-3 w-3/4`, `h-2.5 w-1/2`) |

**Acessibilidade.** No antigo o link é `<a><img alt=""><div class="name-game"
style="opacity:0">Fortune Tiger</div></a>`. O nome acessível existe (leitor lê o
texto com `opacity:0`), mas é frágil e depende de um detalhe de CSS. Especifique
explicitamente: `alt=""` na arte (é decorativa quando o nome está em texto ao
lado) e o nome do jogo como texto real no link. Nome acessível resultante:
`"Fortune Tiger, PG Soft"`.

**Carregamento de imagem:** `loading="lazy"` + `decoding="async"` em tudo abaixo
da primeira dobra, `width`/`height` declarados para reservar espaço. O antigo usa
`loading="eager"` em **todas** as artes de **todas** as seções — dezenas de
requisições de imagem bloqueantes no primeiro paint.

---

### 3.4 Card de categoria

Equivale a `.sublink` do antigo: círculo com ícone + rótulo, em faixa rolável
horizontal (`.eng-sublinks-2`, 8 itens).

**Anatomia**

```
    ┌───────┐
   ╱  ┌───┐  ╲     anel externo 64px, rounded-full, border-borda-forte
  │   │ ◆ │   │    disco interno 48px, rounded-full, bg-marca/14
   ╲  └───┘  ╱     ícone 20px, text-marca
    └───────┘
    Roletas        text-xs/600 text-texto, centralizado, min-w-[88px]
```

Valores do antigo preservados: anel 64px (`.eng-stroke-icon-sublink`), disco 50px
(`.eng-icon-sublink`, com `background: --yellow10` = marca a 10%), ícone 20px,
largura mínima do item 90px (`.sublink{min-width:90px}`).

**Estados**

| estado | efeito |
|---|---|
| repouso | anel `border-borda-forte`, disco `bg-marca/14`, ícone `text-marca`, rótulo `text-texto` |
| hover | anel `border-marca`, disco `bg-marca/25`, rótulo `text-marca-400` (5,82:1). É o `.sublink:hover{color:var(--yellow)}` do antigo, com o token que passa contraste |
| foco | `ring-2 ring-marca ring-offset-2 ring-offset-fundo` no elemento inteiro |
| ativo (categoria da página atual) | disco `bg-marca`, ícone `text-white`, rótulo `text-texto`, `aria-current="page"` |
| desabilitado | n/a — categoria vazia não é renderizada |
| erro | n/a |
| carregando | círculo `bg-fundo-elevado animate-pulso` + barra `h-3 w-16` |

**Faixa rolável.** O antigo resolve com `width:115%; padding-right:15%;
overflow:scroll` — gambiarra que causa overflow horizontal no `<body>` em
algumas larguras. Especifique:

```html
<ul class="-mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4
           pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden
           sm:mx-0 sm:grid sm:grid-cols-4 sm:px-0 lg:grid-cols-8">
```

Cada item com `snap-start`. Em `sm` e acima vira grade e o scroll desaparece —
8 categorias cabem em 8 colunas em `lg`, em duas linhas de 4 em `sm`.
**O `<body>` nunca rola na horizontal**; só este contêiner.

---

### 3.5 Banner / carrossel

Vem do banco (tabela `banners`, campo `image`) e no antigo é um carrossel
Bootstrap 4 com `data-ride="carousel"` — auto-avanço, setas `carousel-control`
padrão (ícone branco sobre imagem arbitrária, contraste imprevisível) e sem
indicadores.

**Anatomia**

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  ‹                imagem do banner               ›   │  aspect-[21/9] lg
└──────────────────────────────────────────────────────┘  aspect-[16/9] md
              ● ○ ○   ← indicadores 8px, gap-2           aspect-[4/3] sm
   [⏸]  ← controle de pausa, visível quando há >1 slide
```

**Especificação**

| aspecto | valor |
|---|---|
| proporção | `aspect-[4/3]` < sm · `aspect-[16/9]` md · `aspect-[21/9]` lg — declarada, para não haver salto de layout |
| raio | `rounded-2xl` (é superfície de nível card) |
| imagem | `object-cover`, primeiro slide `loading="eager" fetchpriority="high"`, os demais `lazy` |
| setas | 44×44px, `rounded-full bg-black/60 backdrop-blur text-white`, `hover:bg-black/80`, posicionadas `inset-y-0 left-2 / right-2`. `<button>` com `aria-label="Banner anterior"` / `"Próximo banner"` |
| indicadores | `<button>` de 8px (alvo real 24×24 via `p-2`), ativo `w-6 bg-marca`, inativo `w-2 bg-white/40`. `aria-label="Ir para o banner 2 de 3"` |
| **pausa** | botão visível e persistente, 44×44px, `aria-label="Pausar rotação"` / `"Retomar rotação"` |
| intervalo | 6000ms; pausa em `hover`, em `focus-within` e enquanto a aba está oculta |
| transição | 250ms `ease-out` de opacidade + translação de 8px |
| teclado | `←`/`→` navegam quando o carrossel tem foco |
| semântica | `role="region" aria-roledescription="carrossel" aria-label="Destaques"`; cada slide `role="group" aria-roledescription="slide" aria-label="1 de 3"`; a região de slides com `aria-live="off"` (é troca a pedido, não conteúdo novo) |
| **reduced-motion** | **auto-avanço desligado por completo** e transição sem translação |
| `alt` | o banco não guarda texto alternativo. Enquanto não guardar: `alt=""` + `aria-hidden="true"` na imagem, com o link (se houver) carregando o texto. **Nunca** `alt="..."` como está hoje |

**Estados**

| estado | efeito |
|---|---|
| repouso | slide 1 visível, indicador 1 ativo |
| hover | setas passam de `bg-black/60` para `/80`; rotação pausada |
| foco | seta/indicador com `ring-2 ring-white ring-offset-2 ring-offset-black/60` (o anel de marca desaparece sobre imagem arbitrária) |
| ativo | seta com `scale-95` |
| desabilitado | com 1 banner: **sem** setas, **sem** indicadores, **sem** rotação — apenas a imagem |
| erro | banner que não carrega é removido do conjunto; se nenhum carregar, colapsa sem deixar buraco |
| carregando | `aspect-*` + `bg-fundo-elevado animate-pulso` |

Um só banner é o caso comum em operação. O antigo ainda assim renderiza as setas
e liga o `data-ride` — setas que não fazem nada.

---

### 3.6 Barra superior com saldo

**Anatomia (logado, ≥ lg)**

```
┌─────────────────────────────────────────────────────────────────────┐
│ [logo 32px]              ┌─────────────┐ ┌──────────────┐ ┌───┐     │
│                          │ BANCA       │ │ + Depositar  │ │ T ▾│    │
│                          │ R$ 1.250,00 │ └──────────────┘ └───┘     │
│                          └─────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
  h-barra (64px), border-b border-borda, bg-fundo/95 backdrop-blur, sticky z-30
```

**Bloco de saldo**

| parte | especificação |
|---|---|
| contêiner | `h-10 rounded-lg border border-borda bg-fundo-card px-4`, `flex flex-col justify-center` |
| rótulo | "Banca", `text-2xs font-medium uppercase tracking-widest text-texto-2` (6,70:1) |
| valor | `text-sm font-semibold text-texto num` (15,62:1), "R$" em `text-marca-400` (5,44:1) |
| atualização | `hx-get` + `hx-trigger="every 30s"` num `<span id="saldo">` com `aria-live="polite" aria-atomic="true"` |
| flash de mudança | 600ms de `bg-sucesso/15` quando sobe, `bg-erro/15` quando desce, e **texto explícito** ("+R$ 50,00 creditado") — cor sozinha não comunica (1.4.1) |
| carregando | `text-texto-3` + `animate-pulso` no valor, sem trocar a largura (é aqui que `tabular-nums` importa) |
| erro | valor vira `—` com `title`/tooltip "Saldo indisponível. Tentando novamente." Nunca mostre um saldo antigo como se fosse atual — **falha fechado**, alinhado à regra 3 do `CLAUDE.md` |

No antigo o saldo é `<h4 id="balance">` — heading usado como dado, e o **mesmo
`id` duplicado** na barra desktop e na cópia mobile do menu. Corrija os dois.

**Avatar / menu de conta**

- Botão de 40×40px, `rounded-full border border-borda-forte bg-fundo-card`,
  inicial do nome em `text-sm font-semibold text-texto`
- `aria-haspopup="menu" aria-expanded` + `aria-controls`
- Painel: `w-64 rounded-2xl border border-borda bg-fundo-card shadow-lg
  shadow-black/40`, ancorado à direita, `origin-top-right animate-entrada`
- Cabeçalho do painel: nome (`text-sm text-texto`) + e-mail (`text-xs
  text-texto-3 truncate`), sobre `bg-fundo-elevado`, clicável para "Minha conta"
- Itens: `h-11 px-4 text-sm text-texto-2 hover:bg-fundo-elevado hover:text-texto`,
  ícone 16px — Depositar, Sacar, Histórico, Sair (Sair em `text-erro`)
- `role="menu"` / `role="menuitem"`; `↑`/`↓` circulam, `Esc` fecha e devolve o
  foco ao botão, clique fora fecha
- **Sair é `<form method="post">` com CSRF**, não um `<a href=".../logout">`.
  Logout por GET é o que o antigo faz e é vulnerável a CSRF por link/imagem.

No antigo esse dropdown abre por `data-hover="true"` (hover), o que em touch
exige um toque que também navega, e some se o cursor cruza um vão de 1px.
**Abre por clique.** Hover pode pré-carregar, nunca abrir.

**Barra deslogada:** logo à esquerda, `[Entrar]` secundário + `[Cadastrar]`
primário à direita, `gap-2` (é o `.navbar-buttons-login-wrapper{grid-column-gap:8px}`
do antigo).

**Barra em < lg:** `h-barra-sm` (56px), `[≡ 44px] [logo]` à esquerda,
`[R$ 1.250,00] [+ 44px]` à direita. O rótulo "Banca" e a palavra "Depositar"
somem (é o `.no-mobile{display:none}` do antigo); o botão `+` mantém
`aria-label="Depositar"`.

---

### 3.7 Menu lateral

**Anatomia** — a estrutura do antigo, preservada seção por seção

```
┌────────────────────────┐  w-menu (256px), sticky top-barra
│ [+ Depositar]          │  ← só em < lg (é .btn-small.mobile do antigo)
│                        │
│ ⌂  Início              │  h-11, rounded-lg, gap-3, px-4
│ ⚇  Minha Conta         │  (só logado)
│ ⇥  Sair                │  (só logado)
│ ⇗  Indique e Ganhe     │
│ ▦  Todos os jogos      │
│ ────────────────────── │  ← divisória, my-6, border-borda
│ ▾  Populares           │  ← item expansível
│    ┌──┐ Fortune Ox     │     sub-item h-12, arte 32px rounded-lg
│    ┌──┐ Fortune Tiger  │
│       Ver todos     ›  │
│ ◎  Roletas             │
│ ♠  Cassino             │
│ ●  Cassino Ao vivo     │
│ ────────────────────── │
│ ?  Suporte             │
│ ────────────────────── │
│ [tg][ig][fb][wa]       │  ← sociais, 40×40px cada
│ SistemaBet © 2026      │  ← text-2xs text-texto-3
└────────────────────────┘
```

**Estados do item**

| estado | especificação |
|---|---|
| repouso | transparente, `text-texto-2` (**7,17:1** — no antigo é `rgba(255,255,255,.35)`, **3,21:1**), ícone `text-texto-3` |
| hover | `bg-fundo-elevado`, `text-texto` (14,22:1), ícone `text-texto-2`, 150ms |
| foco | `ring-2 ring-marca ring-offset-2 ring-offset-fundo`, sem `outline` do browser |
| **ativo** | `bg-marca/15` (superfície `#37161C`), `text-marca-300` (**7,41:1**), ícone `text-marca`, **barra de 3px `bg-marca` na borda esquerda** (4,86:1 contra a página, 4,29:1 contra a superfície do item — passa nos dois lados), `aria-current="page"` |
| desabilitado | `text-texto-3`, `cursor-not-allowed`, `aria-disabled="true"` — para categoria sem jogo |
| erro | n/a |
| carregando | 8 barras `h-11 rounded-lg bg-fundo-elevado animate-pulso` |

A barra de 3px existe porque cor sozinha não pode ser o único indicador de
estado (WCAG 1.4.1). O antigo marca o item ativo só com
`.sublink-nav.w--current{color:var(--yellow)}` — e pior, o caso
`.sublink-nav.btn-color-1.w--current` aplica `opacity:.5`, deixando o item
**ativo mais apagado** que os inativos.

**Item expansível** ("Populares")

- Botão com `aria-expanded` + `aria-controls`; chevron de 16px rotaciona
  `rotate-90` em 200ms (o antigo usa `.arrow-drop-menu.active{rotate(90deg)}`)
- Estado aberto/fechado persiste na sessão (`localStorage` via Alpine)
- Sub-itens com arte de 32px `rounded-lg` (`.icon-sublink-game` do antigo:
  `32×32, border-radius:8px`), nome em `text-xs truncate`, altura 48px
- "Ver todos ›" fecha a lista com `text-xs text-marca-400`
- Aberto por padrão no primeiro acesso — é o que o antigo faz
  (`.arrow-drop-menu.active` já vem no markup)

---

### 3.8 Modal

O antigo tem seis: Entrar, Cadastrar, Depósito, QR Code do PIX, Sucesso do
pagamento, Saque (+ o menu mobile, que é um sétimo modal). Todos Bootstrap 4.

> **Decisão de rota, não só de visual:** Entrar e Cadastrar deixam de ser modal e
> passam a ser **páginas** — o que o novo já fez em `contas/login.html` e
> `contas/cadastro.html`, e está certo: URL compartilhável, botão voltar
> funcional, gerenciador de senha do navegador funcionando, erro de validação
> sobrevivendo ao recarregamento. Permanecem modais os fluxos **transacionais**
> (depositar, sacar, QR, resultado), onde o contexto da página importa.

**Anatomia**

```
        ┌──────────────────────────────────────┐
        │  Faça agora seu depósito no PIX  [×] │  ← h2 text-xl/600, botão 40px
        │  Falta pouco para a diversão!        │  ← text-sm text-texto-2
        ├──────────────────────────────────────┤
        │                                      │
        │  corpo (rolável se passar de 70vh)   │
        │                                      │
        ├──────────────────────────────────────┤
        │  ⓘ aviso de segurança                │
        │              [Cancelar] [Depositar]  │  ← ações à direita
        └──────────────────────────────────────┘
  max-w-[480px] (form) / max-w-[600px] (QR), rounded-2xl,
  bg-fundo-card, border border-borda, shadow-2xl shadow-black/60
```

Larguras: 480px para formulário, 600px para QR/conteúdo largo — é o
`.card.windows{max-width:600px; min-width:380px; padding:48px}` do antigo, com o
padding reduzido de 48px para 24px (48px de padding em 380px de largura sobra
284px úteis; em mobile o antigo troca para padding 0 e o card perde a moldura
inteira).

| aspecto | valor |
|---|---|
| overlay | `bg-black/70 backdrop-blur-sm`, z-50, `grid place-items-center p-4` |
| painel | z-60, `w-full max-w-[480px] max-h-[85vh] overflow-y-auto` |
| entrada | 250ms: `opacity 0→1` + `scale .96→1` + `translate-y-2→0` |
| saída | 200ms `ease-in`, inverso |
| **mobile** (< sm) | **folha inferior**: `items-end`, `rounded-t-2xl rounded-b-none`, `max-h-[90vh]`, entrada por `translate-y-full → 0`. O antigo remove a moldura e o card vira tela cheia sem cabeçalho fixo — perde-se a saída |
| fechar | `<button>` 40×40px no canto superior direito, `aria-label="Fechar"`, `rounded-lg hover:bg-fundo-elevado`. No antigo é `<div class="eng-close-windows">` com `background-color: var(--orange)` — um quadrado vermelho de 40px, colado em `top:-1px right:-1px` (transbordando o card), sem `tabindex` |
| semântica | `role="dialog" aria-modal="true" aria-labelledby="<id do h2>" aria-describedby="<id da linha de apoio>"` |
| foco | entra no primeiro campo (ou no botão fechar se não houver campo), **preso** dentro do painel, volta ao gatilho no fechamento |
| `Esc` | fecha — **exceto** enquanto uma transação está em voo (`aria-busy`) |
| clique no overlay | fecha, com a mesma exceção |
| rolagem do fundo | travada (`overflow-hidden` no `<html>`), sem salto de scrollbar |

**Estados do modal como um todo**

| estado | especificação |
|---|---|
| repouso | formulário pronto, ação primária habilitada |
| carregando | ação primária em estado de carregamento, campos `readonly`, `[×]` **continua ativo** mas com confirmação ("Cancelar o depósito?"). `aria-busy="true"` no painel |
| erro | alerta de erro **no topo do corpo**, `role="alert"`, foco movido para ele; campos mantêm o valor digitado; erro por campo em `aria-describedby` |
| sucesso | troca de conteúdo no mesmo painel (não abre outro modal): ícone de sucesso 48px, título, valor, uma ação de saída. O antigo abre um `#successModal` separado, o que empilha dois overlays |
| desabilitado | n/a (modal não tem estado desabilitado) |

**Fluxo de depósito** — três etapas em **um** painel, com `hx-swap` no corpo:

```
1 valor          2 QR PIX                     3 resultado
┌───────────┐    ┌───────────────────────┐    ┌───────────────┐
│ R$ [____] │    │   ┌───────────────┐   │    │      ✓        │
│ [20][40]  │    │   │   QR 220px    │   │    │ Pagamento     │
│    [60]   │ →  │   │  fundo branco │   │ →  │ confirmado    │
│           │    │   └───────────────┘   │    │ R$ 50,00      │
│[Depositar]│    │ 00020126...  [Copiar] │    │ [Começar]     │
└───────────┘    │ ◌ Aguardando pagamento│    └───────────────┘
                 └───────────────────────┘
```

- QR: 220×220px sobre **fundo branco** com `p-2 rounded-lg` — o antigo já faz
  (`.img-qr-code{background:#f7f5fa}`) e é obrigatório: QR escuro sobre escuro
  não é lido por câmera
- `alt` do QR: `"QR Code PIX para pagamento de R$ 50,00"`
- Código copia-e-cola: `<input readonly>` com `break-all` + botão "Copiar";
  ao copiar, o botão mostra "Copiado ✓" por 2s **e** anuncia em `aria-live="polite"`
- Espera: `hx-get` no endpoint de status (é o `Ezze::statusPix` do antigo) com
  `hx-trigger="every 3s"`; texto "Aguardando pagamento…" em `aria-live="polite"`;
  **limite de 15 minutos**, depois oferece "Verificar novamente"
- Nunca feche o modal sozinho ao confirmar — o usuário precisa ver o resultado

**Fluxo de saque.** O modal de saque do antigo tem um defeito funcional para
corrigir no redesenho: o `<button type="submit">Sacar</button>` está **fora** do
`<form>` (o `</form>` fecha antes dele) — o botão não envia nada. A especificação
é trivial mas precisa estar dita: botão dentro do formulário.
O aviso "Saques permitidos apenas para contas bancárias de sua titularidade"
permanece, como alerta `info` acima da ação. E a chave PIX **não é campo
editável no modal**: é exibida em `readonly`, vinda do perfil, com link
"Alterar no perfil" — regra 5 do `CLAUDE.md`.

---

### 3.9 Alertas e flash

O antigo tem três padrões desconexos: `.alert` do Webflow
(`rgba(255,255,255,.04)`, centralizado, sem ícone e sem cor semântica),
`alert-<?= tipo ?>` do Bootstrap (cores do Bootstrap, fora da paleta) e
`.eng-alert`/`.ang-alert` (dois nomes, um deles com erro de digitação).
Unifique num componente.

**Anatomia**

```
┌──────────────────────────────────────────────────────┐
│ ⓘ  Depósito confirmado                          [×] │
│    R$ 50,00 creditados na sua banca.                 │
└──────────────────────────────────────────────────────┘
  rounded-lg, border, p-4, flex gap-3, ícone 20px shrink-0
  título text-sm/600 · corpo text-sm · fechar 32×32px opcional
```

**Variantes** (fundo, borda e texto vêm dos tokens semânticos)

| variante | superfície | borda | texto | contraste do texto | ícone |
|---|---|---|---|---|---|
| sucesso | `bg-sucesso-fundo` | `border-sucesso-borda` | `text-sucesso` | **8,44:1** | ✓ círculo |
| aviso | `bg-aviso-fundo` | `border-aviso-borda` | `text-aviso` | **8,46:1** | ⚠ triângulo |
| erro | `bg-erro-fundo` | `border-erro-borda` | `text-erro` | **7,49:1** | ✕ círculo |
| info | `bg-info-fundo` | `border-info-borda` | `text-info` | **7,54:1** | ⓘ círculo |

O título vai em `text-texto` (15,62:1 sobre a superfície escura) quando houver
duas linhas; a cor semântica fica no ícone e na borda. **Cada variante tem forma
de ícone distinta** — quem não distingue verde de vermelho ainda diferencia ✓ de ✕.

**Posicionamento e semântica**

| tipo | onde | semântica |
|---|---|---|
| flash de página (mensagens do Django) | topo do `<main>`, acima do `<h1>` | `role="status"` (sucesso/info) · `role="alert"` (erro/aviso) |
| erro de formulário | acima do primeiro campo, dentro do `<form>` | `role="alert"` + foco programático |
| erro de campo | sob o campo | `aria-describedby`, sem `role` |
| aviso permanente | in-loco (ex.: aviso de titularidade no saque) | sem `role` |
| toast | `fixed bottom-4 right-4 z-70`, `max-w-sm` | `role="status" aria-live="polite"` |

**Estados**

| estado | efeito |
|---|---|
| repouso | estático |
| entrada | `animate-entrada` (200ms, opacidade + 4px) |
| hover | só no `[×]`: `bg-white/10 rounded` |
| foco | `[×]` com `ring-2 ring-marca ring-offset-2 ring-offset-<superfície>` |
| descarte | 150ms de `opacity`+`scale-95`; toast sai por auto-descarte de 6s **pausado no hover/focus**; alerta de erro **nunca** se descarta sozinho |
| carregando | n/a |

Nunca use `text-marca` para mensagem — é o que `base.html` e `_campo.html` fazem
hoje, e confunde "erro" com "destaque da marca". Use `text-erro`.

---

### 3.10 Tabela

O front do antigo não tem tabela; o painel tem (`table table-bordered` do
Bootstrap, com `<th>` sem escopo e sem versão mobile). Esta especificação serve
para histórico de transações no front e para as listagens do painel.

**Anatomia (≥ md)**

```
┌───────────────────────────────────────────────────────────────┐
│ Movimentações                              [filtro ▾] [busca] │ cabeçalho do painel
├──────────┬──────────┬───────────┬─────────────┬───────────────┤
│ Data   ↕ │ Tipo     │ Status    │ Registrado  │        Valor  │ h-11, text-2xs
├──────────┼──────────┼───────────┼─────────────┼───────────────┤ uppercase tracking-widest
│ 27/09/26 │ Depósito │ ● Pago    │ 14:32       │    R$ 50,00   │ h-12, text-sm
│ 26/09/26 │ Saque    │ ● Pendente│ 09:11       │  − R$ 120,00  │
└──────────┴──────────┴───────────┴─────────────┴───────────────┘
   1–20 de 148                            ‹ 1 2 3 … 8 ›
```

| parte | especificação |
|---|---|
| contêiner | `rounded-2xl border border-borda bg-fundo-card overflow-hidden` |
| rolagem | `overflow-x-auto` no wrapper; **o `<body>` nunca rola na horizontal** |
| `<thead>` | `bg-fundo-elevado`, `text-2xs font-semibold uppercase tracking-widest text-texto-2` (6,70:1), `h-11`, `sticky top-0` em tabela longa |
| `<th>` | `scope="col"`; ordenável usa `<button>` interno + `aria-sort="ascending|descending|none"` |
| `<td>` | `h-12 px-4 text-sm text-texto` (13,53:1) |
| coluna de valor | `text-right num`, positivo em `text-sucesso`, negativo em `text-erro`, **com sinal explícito** (`+`/`−`) — cor não basta |
| zebra | `even:bg-fundo-elevado/50` (opcional; preferir só a divisória) |
| divisória | `divide-y divide-borda` |
| hover de linha | `hover:bg-fundo-elevado` — só se a linha for clicável |
| `<caption>` | presente e `sr-only` se já houver título visível |
| seleção | checkbox de 20px em célula de 44px |

**< md: a tabela vira lista de cards.** Não use rolagem horizontal como resposta
mobile — é o que o painel antigo faz e obriga a arrastar para ver o valor.

```
┌────────────────────────────────────┐
│ Depósito              + R$ 50,00   │  título text-sm/600 · valor num
│ 27/09/2026 14:32       ● Pago      │  meta text-xs text-texto-2 · badge
└────────────────────────────────────┘
```

**Badge de status** — `inline-flex items-center gap-1.5 h-6 rounded-lg px-2
text-xs font-medium`, com ponto de 6px:

| status | superfície | texto | contraste |
|---|---|---|---|
| Pago / Aprovado | `bg-sucesso-fundo` | `text-sucesso` | 8,44:1 |
| Pendente | `bg-aviso-fundo` | `text-aviso` | 8,46:1 |
| Recusado / Falhou | `bg-erro-fundo` | `text-erro` | 7,49:1 |
| Processando | `bg-info-fundo` | `text-info` | 7,54:1 |
| Cancelado | `bg-fundo-elevado` | `text-texto-2` | 6,33:1 |

O antigo usa `badge bg-success`/`badge bg-danger` com o texto "Pago"/"Não Pago"
na **coluna "Pago"**, enquanto a coluna "Status" mostra o mesmo dado em texto
cru. Uma coluna só.

**Estados da tabela**

| estado | especificação |
|---|---|
| repouso | dados renderizados |
| carregando (primeira carga) | 5 linhas de skeleton com a largura real das colunas |
| carregando (refiltro) | tabela atual a `opacity-60 pointer-events-none` + barra de progresso de 2px `bg-marca` no topo. Preserva contexto — melhor que trocar por skeleton |
| vazio | ver §3.12 |
| erro | alerta de erro no lugar do corpo, com botão "Tentar novamente" |
| linha desabilitada | `opacity-60`, ações removidas (não só desabilitadas) |

---

### 3.11 Paginação

O front do antigo esconde a paginação (`.pagination{display:none}`) e usa
carregamento infinito (`fs-cmsload-mode="infinite"`). O painel usa
`$this->pagination->create_links()` do CodeIgniter, sem estilo.

**Duas estratégias, cada uma no seu lugar**

| contexto | padrão | por quê |
|---|---|---|
| catálogo de jogos | **"Carregar mais"** explícito | preserva o comportamento do antigo sem os problemas do scroll infinito: rodapé alcançável, posição restaurada ao voltar, e teclado funciona. Scroll infinito automático não é uma opção acessível |
| tabela / histórico / painel | **paginação numérica** | o usuário precisa de "página 3 de 8" e de link estável |

**Carregar mais**

```
                 [ Carregar mais 24 jogos ]
                     60 de 148 jogos
```
- Botão secundário `lg`, centralizado, `mt-6`
- Contagem abaixo em `text-xs text-texto-2`
- Estados: repouso · carregando (spinner + "Carregando…", `aria-busy`) ·
  esgotado (botão sai, fica "148 de 148 jogos")
- Após inserir, foco vai para o **primeiro item novo** e `aria-live="polite"`
  anuncia "24 jogos carregados"
- HTMX: `hx-get` + `hx-swap="beforeend"` + `hx-indicator`

**Paginação numérica**

```
  1–20 de 148          ‹ Anterior   1  [2]  3  …  8   Próxima ›
```

| parte | especificação |
|---|---|
| contêiner | `<nav aria-label="Paginação">` com `flex items-center justify-between gap-4 border-t border-borda px-4 py-3` |
| contagem | `text-xs text-texto-2`, "1–20 de 148" |
| botão de página | 36×36px (área de toque 44px com `p-1`), `rounded-lg text-sm` |
| repouso | `text-texto-2 hover:bg-fundo-elevado hover:text-texto` |
| **atual** | `bg-marca-600 text-white` (4,81:1) + `aria-current="page"` |
| foco | `ring-2 ring-marca ring-offset-2 ring-offset-fundo` |
| desabilitado | primeira/última: `text-texto-3 cursor-not-allowed aria-disabled="true"` — **mantém o botão no layout**, não remove (evita o deslocamento dos vizinhos) |
| reticências | `<span aria-hidden="true">…</span>`, não focável |
| janela | 1 … atual−1, atual, atual+1 … última |
| mobile | só `‹ Anterior` / `Próxima ›` de largura total + "Página 2 de 8" no meio |
| carregando | como no refiltro de tabela: opacidade + barra de progresso |

---

### 3.12 Estado vazio

O antigo tem um só, no painel: `<h2>Nenhum registro encontrado.</h2>` — `h2` para
uma frase de sistema, sem explicação do que fazer. Front não tem nenhum: uma
seção de catálogo sem jogos renderiza um `<div class="grid">` vazio, e o usuário
vê um título seguido de nada.

**Anatomia**

```
        ┌────────────────────────────────────────┐
        │                                        │
        │              ┌────────┐                │  ilustração/ícone 64px
        │              │   ▦    │                │  em círculo bg-fundo-elevado
        │              └────────┘                │
        │                                        │
        │      Nenhuma movimentação ainda        │  text-lg/600 text-texto
        │                                        │
        │   Seus depósitos e saques aparecem     │  text-sm text-texto-2
        │   aqui. Comece com um depósito PIX.    │  max-w-sm, centralizado
        │                                        │
        │          [ + Depositar ]               │  ação primária (quando existe)
        │                                        │
        └────────────────────────────────────────┘
          rounded-2xl border border-borda border-dashed
          bg-fundo-card px-6 py-12, text-center
```

Borda tracejada distingue "vazio" de "card com conteúdo" sem precisar ler.

**Três tipos, com texto diferente** — o antigo trata os três como um só:

| tipo | título | apoio | ação |
|---|---|---|---|
| **primeiro uso** (nunca houve dado) | "Nenhuma movimentação ainda" | explica o que vai aparecer ali e como começar | ação primária que cria o primeiro dado |
| **filtro sem resultado** | "Nenhum jogo para «roleta ao vivo»" | "Tente outro termo ou remova os filtros." | secundária: "Limpar filtros" |
| **erro de carregamento** | "Não foi possível carregar" | "Verifique sua conexão." | secundária: "Tentar novamente" |

**Estados**

| estado | efeito |
|---|---|
| repouso | estático |
| hover/foco/ativo | só nos controles internos |
| desabilitado | n/a |
| erro | é o terceiro tipo acima; ícone em `text-erro`, borda `border-erro-borda` |
| carregando | **não existe**. Enquanto carrega, mostra-se skeleton; vazio só depois da resposta. Mostrar vazio durante o carregamento é o pior erro possível aqui — o usuário conclui que não há nada e sai |

Semântica: `<h2>`/`<h3>` conforme a posição na hierarquia da página (nunca
`<h2>` solto como no painel antigo). Ícone com `aria-hidden="true"`.
Em substituição de conteúdo via HTMX, o contêiner leva `aria-live="polite"`.

---

### 3.13 Skeleton

| onde | forma |
|---|---|
| card de jogo | `aspect-square rounded-lg` + `h-3 w-3/4` + `h-2.5 w-1/2` |
| linha de tabela | 5 barras `h-3` com a largura real de cada coluna |
| card de estatística | `h-3 w-24` (rótulo) + `h-7 w-32` (valor) |
| item de menu | `h-11 rounded-lg` |
| banner | `aspect-[21/9] rounded-2xl` |

Base `bg-fundo-elevado` (1,14:1 sobre o card — decorativo, sem exigência de
contraste), `animate-pulso` (1600ms). Com `prefers-reduced-motion`: estático.
Contêiner com `aria-busy="true"` e `aria-live="polite"`; os retângulos com
`aria-hidden="true"`.

**Skeleton, não spinner**, para lista e grade — preserva a forma da página e
elimina o salto de layout. O antigo faz o oposto em dois lugares e nos dois
custa caro:

- **`home.php`: um preloader de tela cheia com `setTimeout(…, 5000)`.** A home
  fica coberta por cinco segundos cravados, independentemente de a página já
  estar pronta. Pior: o script referencia `document.getElementById('content')`,
  que não existe em nenhum lugar do documento — então a linha
  `content.style.display = 'block'` lança `TypeError` **antes** de esconder o
  preloader em alguns navegadores. Remova o preloader por completo.
- **`game.php`: `.eng-loading-slot` com o logo sobre o iframe.** Aqui um
  indicador faz sentido (o `<iframe>` do provedor demora), mas ele nunca é
  removido — não há `onload`. Fica o logo atrás do iframe para sempre.
  Especificação: skeleton `aspect-video rounded` + `aria-busy`, removido no
  `load` do iframe, com limite de 20s que mostra "O jogo não carregou.
  [Tentar novamente]".

---

## 4. Telas que o antigo tem e o novo ainda não

O novo tem hoje: home (esqueleto), cadastro, login, recuperação de senha (4
telas), perfil, bloqueado. Tudo o mais abaixo falta.

Prioridade: **P0** = a plataforma não funciona sem isso · **P1** = paridade
essencial · **P2** = paridade completa · **P3** = pode esperar.

### Front

| # | tela | rota no antigo | o que é | prio | depende de |
|---|---|---|---|---|---|
| 1 | **Home completa** | `/` | banner/carrossel, faixa de 8 categorias, seções Populares / Cassino / Cassino ao vivo, faixa de provedores | **P0** | catálogo (Fase 4) |
| 2 | **Catálogo — Cassino** | `/cassino` | grade completa + faixa de provedores | **P0** | Fase 4 |
| 3 | **Catálogo — Ao vivo** | `/cassino/aovivo` | mesma grade, filtrada por `provedores.type='live'` | **P0** | Fase 4 |
| 4 | **Jogo (iframe)** | `/games/ver/{provedor}/{codigo}` | iframe do provedor + estado de carregamento | **P0** | Fase 4 |
| 5 | **App shell: menu lateral** | `header.php` | 11 destinos + expansível de Populares + sociais | **P0** | nenhuma — **pode ser feito já** |
| 6 | **App shell: barra com saldo** | `header.php` | bloco Banca + Depositar + menu de conta | **P0** | saldo real depende da Fase 2; a casca não |
| 7 | **App shell: barra inferior mobile** | `header.php` | 5 destinos | **P0** | nenhuma — **pode ser feito já** |
| 8 | **App shell: gaveta mobile** | `#exampleModal` | menu em gaveta | **P0** | nenhuma — **pode ser feito já** |
| 9 | **Modal de depósito** | `#modalDeposito` | valor + chips 20/40/60 | **P1** | Fase 3 |
| 10 | **Modal de QR PIX** | `#qrCodeModal` | QR + copia-e-cola + espera | **P1** | Fase 3 |
| 11 | **Modal de resultado** | `#successModal` | confirmação de pagamento | **P1** | Fase 3 |
| 12 | **Modal de saque** | `#modalSaque` | valor + tipo de chave + chave + aviso de titularidade | **P1** | Fase 3 |
| 13 | **Minha conta (visão geral)** | `/usuarios/minhaconta` | card de identidade + 4 cards (saldo total, saldo real, saldo bônus, indicações) | **P1** | Fase 2 para os valores |
| 14 | **Editar dados pessoais** | `/usuarios/editarconta` | e-mail, CPF, nome, nascimento, usuário, telefone, endereço, CEP, chave PIX | **P1** | parcialmente feito em `perfil.html`; faltam endereço/CEP |
| 15 | **Indique e Ganhe** | `/usuarios/indique` | 4 métricas + link de referência com copiar + 3 passos | **P2** | afiliados |
| 16 | **Rodapé completo** | `footer.php` | 3 colunas de links, sociais, 6 selos, texto de licença | **P2** | nenhuma — **pode ser feito já** |
| 17 | **Histórico de transações** | `#` no antigo | o link "Histórico" existe no menu de conta mas está `display:none` | **P2** | Fase 2. Não é feature nova: é o link morto do antigo |
| 18 | **Termos de uso / FAQ / Jogo Consciente** | `href="#"` | links do rodapé que não levam a nada | **P3** | conteúdo. Obrigatórios por regulação de aposta |
| 19 | **404 / 500** | `errors/html/*` | erro genérico do CodeIgniter | **P2** | nenhuma — **pode ser feito já** |

### Painel administrativo

O painel do antigo é Bootstrap 5.3 puro, sem marca, com temas claro/escuro/auto.
**Não é referência visual** — herda a marca do front no redesenho.
Corresponde à Fase 5 do roadmap.

| # | tela | rota | prio |
|---|---|---|---|
| 20 | Dashboard (lucro 24h/7d/1m/total) | `/dashboard` | P2 |
| 21 | Usuários: listar / criar / editar | `/usuarios{,/create,/edit/:id}` | P2 |
| 22 | Financeiro: resumo geral | `/financeiro` | P2 |
| 23 | Financeiro: saques (aprovar/recusar) | `/financeiro/saques` | **P1** (é operação de dinheiro) |
| 24 | Financeiro: depósitos | `/financeiro/depositos` | P2 |
| 25 | Financeiro: movimentações | `/financeiro/movimentacoes` | P2 |
| 26 | Gateway de pagamento | `/GatewayPagamento` | P2 |
| 27 | Configuração da API de jogos | `/Fiverscan` | P2 |
| 28 | Jogos: listar / editar | `/jogos{,/edit/:id}` | P2 |
| 29 | Tema (cor da marca, logo, favicon, redes) | `/tema` | P3 |
| 30 | Banners | `/tema/banners` | P2 |
| 31 | Configurações gerais | `/dashboard/config` | P2 |
| 32 | Configurações de afiliados | `/dashboard/afiliados` | P3 |
| 33 | Administradores | `/admin` | P2 |

### Ordem recomendada

**Onda 1 — nada bloqueia (itens 5, 6, 7, 8, 16, 19).** O app shell completo,
com o saldo em `R$ 0,00` e os destinos de catálogo apontando para uma tela de
"em breve". É a onda que dá ao dono a sensação de "é a mesma plataforma", e ela
não depende do provedor de jogos nem da carteira. **Comece por aqui.**

**Onda 2 — perfil (item 14).** Fecha a Fase 1, já em andamento.

**Onda 3 — catálogo (1, 2, 3, 4).** Assim que a Fase 4 destravar.

**Onda 4 — dinheiro (9, 10, 11, 12, 13, 17, 23).** Depende das Fases 2 e 3.

**Onda 5 — painel e conteúdo (o restante).**

> O item 29 (Tema) merece uma decisão explícita. O antigo gera `:root{…}` em
> runtime a partir da tabela `tema` (`Style.php`), o que só existe para
> revender a plataforma com outra cor. No novo, Tailwind compila o CSS em build.
> Tematização em runtime exigiria CSS custom properties em vez de valores
> literais em todos os tokens — decisão de arquitetura, não de design.
> **Se não há plano de revenda multi-tenant, não porte.**

---

## 5. Acessibilidade

Meta: **WCAG 2.1 AA**. As seções abaixo trazem o que medir e onde o antigo
reprova.

### 5.1 Contraste — todos os pares propostos

**Texto (1.4.3 — mínimo 4,5:1 normal, 3:1 grande)**

| par | contraste | AA |
|---|---|---|
| `texto` `#F4F4F5` sobre `fundo` `#141417` | **16,73:1** | ✅ |
| `texto` `#F4F4F5` sobre `fundo-card` `#1B1B1F` | **15,62:1** | ✅ |
| `texto-2` `#A1A1AA` sobre `fundo` | **7,17:1** | ✅ |
| `texto-2` `#A1A1AA` sobre `fundo-card` | **6,70:1** | ✅ |
| `texto-3` `#8A8A92` sobre `fundo` | **5,37:1** | ✅ |
| `texto-3` `#8A8A92` sobre `fundo-card` | **5,01:1** | ✅ |
| `texto-3` `#8A8A92` sobre `fundo-campo` `#202024` (placeholder) | **4,74:1** | ✅ |
| `marca-500` `#FF2338` sobre `fundo` (destaque, link) | **4,86:1** | ✅ |
| `marca-400` `#FF5266` sobre `fundo-card` (hover de link) | **5,44:1** | ✅ |
| `marca-300` `#FF8E9B` sobre wash `bg-marca/15` (item ativo) | **7,41:1** | ✅ |
| branco sobre `marca-600` `#E01B2F` (botão primário) | **4,81:1** | ✅ |
| branco sobre `marca-700` `#C4122A` (hover) | **6,06:1** | ✅ |
| branco sobre `marca-800` `#9E0F20` (pressionado) | **8,26:1** | ✅ |
| `sucesso` `#6EE7B7` sobre `sucesso-fundo` `#193731` | **8,44:1** | ✅ |
| `aviso` `#FCD34D` sobre `aviso-fundo` `#42331B` | **8,46:1** | ✅ |
| `erro` `#FDA4AF` sobre `erro-fundo` `#42212A` | **7,49:1** | ✅ |
| `info` `#93C5FD` sobre `info-fundo` `#212E46` | **7,54:1** | ✅ |
| `#E4E4E7` sobre `fundo-card` (célula de tabela) | **13,53:1** | ✅ |
| `#E4E4E7` sobre zebra `#202024` | **12,79:1** | ✅ |

**Componentes e estados (1.4.11 — mínimo 3:1)**

| par | contraste | AA |
|---|---|---|
| `borda-forte` `#6B6B78` sobre `fundo` (borda de campo) | **3,50:1** | ✅ |
| `borda-forte` `#6B6B78` sobre `fundo-card` | **3,27:1** | ✅ |
| `borda-forte` `#6B6B78` sobre `fundo-campo` | **3,09:1** | ✅ |
| `marca-500` `#FF2338` sobre `fundo` (anel de foco, indicador ativo) | **4,86:1** | ✅ |
| `marca-600` `#E01B2F` sobre `fundo` (limite do botão primário) | **3,82:1** | ✅ |
| `erro-forte` `#FB7185` sobre `fundo-campo` (borda de erro) | **6,03:1** | ✅ |
| branco sobre `marca-600` (anel de foco no botão primário) | **4,81:1** | ✅ |
| `borda` `#2A2A30` sobre `fundo` | 1,29:1 | ⚠️ **decorativo apenas** |

`borda` a 1,29:1 é legítima para divisória de card e régua de seção — não carrega
informação. Nunca use `borda` como único limite de um controle.

**Exceções declaradas**

| par | contraste | justificativa |
|---|---|---|
| botão desabilitado: `#FFFFFF/55` sobre `marca-800` | 3,31:1 | 1.4.3 isenta componente inativo. Ainda assim legível |
| skeleton `#26262C` sobre `fundo-card` | 1,14:1 | decorativo, `aria-hidden` |

### 5.2 Onde o antigo reprova — com número

| # | falha | medida | correção |
|---|---|---|---|
| 1 | **Texto do `body`** `rgba(255,255,255,.3)` = `#5A5A5D` sobre `#141417` | **2,67:1** (precisa 4,5) | `texto-2` `#A1A1AA` → 7,17:1 |
| 2 | **Itens do menu lateral** `rgba(255,255,255,.35)` = `#666668` | **3,21:1** | `texto-2` → 7,17:1 |
| 3 | **Placeholder** `.input::placeholder` a 30% de branco | **2,67:1** | `texto-3` sobre campo → 4,74:1 |
| 4 | **Botão primário** branco sobre `#FF2338` | **3,78:1** | `marca-600` → 4,81:1 |
| 5 | `.txt-label` a 11px em `--white-50` | **2,67:1** a 11px | 12px em `texto-2` → 6,70:1 |
| 6 | Corpo a **13px peso 300** | — | 14px peso 400 |
| 7 | `[disabled]{opacity:.85 !important}` global | reduz todo o contraste do controle | trocar cor de token, não opacidade |
| 8 | Item **ativo** do menu com `opacity:.5` (`.sublink-nav.btn-color-1.w--current`) | ativo menos visível que inativo | `bg-marca/15` + `text-marca-300` (7,41:1) + barra de 3px |
| 9 | Cores do Bootstrap nos flash (`alert-success` etc.) | fora da paleta, contraste não verificado | tokens semânticos, 7,49–8,46:1 |
| 10 | `.w-select{color:#828282}` | 4,78:1 — passa, mas é o piso acidental | `texto` `#F4F4F5` no valor, `texto-3` no placeholder |

### 5.3 Zoom e redimensionamento

**A falha mais grave do antigo, e é uma linha:**

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=0">
```

`maximum-scale=1.0` + `user-scalable=0` **bloqueiam o pinch-zoom no celular** —
reprovação direta de WCAG 1.4.4 (Resize Text). Para quem tem baixa visão, isso
torna a plataforma inutilizável num aparelho pequeno. Note que o `header.php`
declara `<meta name="viewport">` **duas vezes**, e é a segunda (a restritiva) que
vale.

O novo já está correto em `base.html`:
`<meta name="viewport" content="width=device-width, initial-scale=1">`.
**Nunca acrescente `maximum-scale` ou `user-scalable`.**

Além disso:
- layout íntegro a **200% de zoom** e em 320px de largura (1.4.10 Reflow) —
  nenhuma rolagem horizontal de página; só os contêineres declarados em
  §3.4 e §3.10
- unidades relativas (`rem`) para texto; `px` só para borda, raio e ícone
- `text-spacing` (1.4.12): nada de altura fixa em bloco de texto; use `min-h`

### 5.4 Foco visível (2.4.7)

O antigo **não tem** estilo de foco em nenhum componente — nem no botão, nem no
campo (só `border-color` no `:focus`, invisível a 1,23:1 de diferença), nem no
item de menu, nem no card de jogo. Quem navega por teclado não sabe onde está.

Padrão obrigatório:

```
focus-visible:outline-none
focus-visible:ring-2 focus-visible:ring-marca
focus-visible:ring-offset-2 focus-visible:ring-offset-<cor da superfície>
```

- **2px de anel + 2px de deslocamento.** 1px sobre fundo escuro desaparece;
  o `focus:ring-1` do `input.css` atual é insuficiente
- anel `ring-marca` (4,86:1 sobre o fundo) em superfície escura;
  **`ring-white`** sobre preenchimento de marca (4,81:1) e sobre imagem
- `focus-visible`, não `focus` — evita o anel no clique de mouse mantendo-o no
  teclado
- **nunca** `outline: none` sem substituto
- `ring-offset-<superfície>` tem de casar com a superfície real, senão o
  deslocamento aparece como um halo da cor errada

### 5.5 Alvos de toque (2.5.8 AA: 24×24 · 2.5.5 AAA: 44×44)

| elemento | antigo | novo |
|---|---|---|
| botão | 42px ✅ | 40px ✅ (`lg` 48px em mobile) |
| campo | 42px ✅ | 40px ✅ |
| item de menu | 42px ✅ | 44px ✅ |
| item da barra inferior | 64px alt. ✅ | 64px ✅ |
| fechar modal | 40px ✅ mas é `<div>` sem foco ❌ | 40px `<button>` ✅ |
| mostrar/ocultar senha | `<div>` sem foco ❌ | 40×40px `<button>` ✅ |
| seta do carrossel | padrão Bootstrap (~32px, sobreposta à borda) ⚠️ | 44px ✅ |
| indicador do carrossel | inexistente | 8px visual, **24×24 de alvo** ✅ |
| ícone social | 18px de fonte, sem área ❌ | 40×40px ✅ |
| link do rodapé | 12px de texto, sem altura ❌ | `py-2` → 32px ✅ |
| chip de valor no depósito | `<a>` de 42px ✅ mas não é botão ❌ | `<button>` 40px ✅ |

Regra: **nada interativo abaixo de 24×24px**, e em mobile nada de ação primária
abaixo de 44×44px. Alvos adjacentes com pelo menos 8px de separação.

### 5.6 Navegação por teclado

| requisito | estado no antigo | especificação |
|---|---|---|
| ordem de tabulação = ordem visual | quebrada: o menu mobile é uma **cópia completa** do menu no DOM, então tudo aparece duas vezes na tabulação, inclusive quando invisível | markup único; o que está escondido sai da árvore de acessibilidade |
| link de pular conteúdo | ausente; ~15 links antes do `<main>` | `Pular para o conteúdo` como primeiro elemento focável |
| armadilha de foco em modal | Bootstrap 4 faz parcialmente | foco preso; `Esc` fecha; retorna ao gatilho |
| dropdown por teclado | `data-hover="true"` — **impossível** abrir sem mouse | abre por clique/`Enter`/`Espaço`; `↑`/`↓` circulam; `Esc` fecha |
| `<div>` clicável | `.eng-close-windows`, `.icon-password-1/2`, chips de valor | `<button type="button">` |
| `<a href="#">` como ação | Depositar, Sacar, Copiar, categorias do rodapé | `<button>` quando é ação; `<a href>` só quando navega |
| `tabindex` positivo | não usado ✅ | manter: só `0` e `-1` |
| foco depois de troca HTMX | n/a | mover para o primeiro item novo (carregar mais) ou para o alerta (erro) |
| `aria-current` | só a classe `.w--current` do Webflow | `aria-current="page"` no item ativo do menu, da barra inferior e da paginação |

### 5.7 Semântica e leitor de tela

| problema no antigo | correção |
|---|---|
| `id` duplicado: `balance`, `email`, `senha`, `modalText` aparecem 2× (barra + cópia mobile) | markup único; `id` único por documento |
| home sem `<h1>` | um `<h1>` por página |
| hierarquia de heading quebrada (rodapé abre com `h6`, depois `h5`) | descida sem pular nível |
| `<h4>` usado para valor de saldo e `<h3>` para número de passo | valor é `<span>`/`<p>`; heading é título |
| `alt="..."` literal na imagem do carrossel | `alt=""` + `aria-hidden` enquanto o banco não guardar texto alternativo |
| `alt=""` na arte do jogo, com nome em `opacity:0` | nome como texto visível no link; `alt=""` na arte |
| `<input>` sem `<label>` (todos os modais) | `<label for>` visível |
| `aria-labelledby="exampleModalLabel"` apontando para elemento inexistente (em 4 modais) | apontar para o `id` do título real |
| ícone de status só por cor | ícone com forma distinta + texto |
| marquee de provedores em loop de 45s sem pausa | pausa obrigatória ou `animation` só sem `reduced-motion` |
| carrossel em auto-avanço sem pausa | botão de pausa + parada em hover/focus (2.2.2) |
| preloader que cobre a home por 5s | remover |
| `lang="en"` no `<html>` do painel, com conteúdo em português | `lang="pt-br"` |

### 5.8 Checklist de aceite por tela

- [ ] Nenhum par de texto abaixo de 4,5:1 (3:1 se ≥24px ou ≥18,66px bold)
- [ ] Nenhuma borda de controle abaixo de 3:1
- [ ] Todo elemento focável tem anel de 2px com deslocamento
- [ ] A tela inteira é operável só com teclado, e o foco nunca se perde
- [ ] Um `<h1>`; headings sem salto de nível
- [ ] Todo campo tem `<label>` visível associado por `for`
- [ ] Todo erro tem texto **e** ícone, e `aria-describedby` no campo
- [ ] Toda imagem informativa tem `alt`; decorativa tem `alt=""`
- [ ] Nenhum alvo interativo abaixo de 24×24px
- [ ] Layout íntegro a 200% de zoom e em 320px, sem rolagem horizontal de página
- [ ] `prefers-reduced-motion` desliga tudo que se move sozinho
- [ ] Nada de `maximum-scale` / `user-scalable` no viewport
- [ ] `id` único no documento
- [ ] Testado com VoiceOver (Safari) e NVDA (Firefox) nos fluxos de dinheiro

---

## 6. Handoff

### O que está definido aqui e o que não está

Definido: tokens (valores literais), anatomia de componente, todos os estados,
comportamento responsivo, contraste medido, semântica exigida.

Não definido, e é decisão de frontend: estrutura de template e de include, nomes
de bloco Django, onde entra HTMX e onde entra Alpine, componentização
(`{% include %}` vs template tag), estratégia de `hx-swap`, nomes de arquivo.

### Ordem de implementação

1. Substituir `tailwind.config.js` pelo §1.8 e `input.css` pelo §1.9.
   `marca.DEFAULT` e `fundo.DEFAULT` não mudam — nenhum template quebra.
2. Varrer os templates existentes trocando `text-white/30`, `/35`, `/40`, `/50`
   por `text-texto-2` / `text-texto-3`, e `border-fundo-borda` em campo por
   `border-borda-forte`. São 4 arquivos.
3. Trocar `text-marca` por `text-erro` nas mensagens de erro de
   `base.html` e `contas/_campo.html`.
4. Onda 1 das telas faltantes (§4): app shell completo.
5. `npm run css:build` e commit do `static/css/app.css` (é versionado).

### Ícones

O antigo não tem ícone nenhum que funcione (§0). Escolha **um** conjunto SVG
inline e não misture: Lucide é a recomendação (licença MIT, traço de 2px que
combina com o peso da Inter, cobertura completa do que é preciso aqui — casa,
usuário, carteira, dado, roleta, cartas, suporte, PIX/QR). Tamanhos: 16px em
linha de texto, 20px em item de menu e barra inferior, 24px em cabeçalho de
card, 48px em estado vazio. Ícone decorativo leva `aria-hidden="true"`; ícone
que é a única etiqueta de um botão exige `aria-label` no botão.

### Marca

`static/img/logo.png` (barra e modais, altura 32px), `logo-rodape.png` (rodapé,
altura 28px, `opacity-60` como no antigo), `favicon.png`, `logo.svg`.
Preferir o SVG onde houver: o antigo limita o logo a `max-height:42px;
max-width:120px` e um PNG nesse tamanho fica borrado em tela de alta densidade.
Todo logo que é link para a home leva `alt="SistemaBet — página inicial"`;
logo decorativo (o do rodapé, se o nome já estiver escrito ao lado)
leva `alt=""`.

---

## 7. Resumo das decisões

| decisão | motivo |
|---|---|
| Marca `#FF2338` preservada como identidade; botão primário em `#E01B2F` | branco sobre `#FF2338` dá 3,78:1 e reprova AA; `#E01B2F` dá 4,81:1 e é visualmente indistinguível |
| Piso de texto em `#8A8A92` (5,37:1); `white/30`–`/40` proibidos para texto | o antigo escreve o corpo a 2,67:1 e o menu a 3,21:1 |
| Borda de controle em `#6B6B78` (3,50:1), separada da borda decorativa | 1.4.11 exige 3:1 para o que identifica um controle; num tema escuro só a borda pode entregar isso |
| Erro em rose (`#FDA4AF`), nunca na marca | marca vermelha + erro vermelho = dois significados na mesma cor |
| Nome do jogo visível no card | `.name-game{opacity:0}` esconde o título de ~200 jogos |
| Entrar/Cadastrar como página; depósito/saque como modal | autenticação precisa de URL e de gerenciador de senha; transação precisa de contexto |
| Gaveta mobile com markup único | a cópia do menu duplica `id` e dobra a ordem de tabulação |
| "Carregar mais" em vez de scroll infinito | preserva o comportamento do antigo sem tornar o rodapé inalcançável |
| Viewport sem `maximum-scale`/`user-scalable` | o antigo bloqueia pinch-zoom — reprovação direta de 1.4.4 |
| Sem preloader; skeleton no lugar de spinner | o antigo cobre a home por 5s cravados, com um `TypeError` no caminho |
| Tematização em runtime (`Style.php`) não portada | Tailwind compila em build; só se houver plano de revenda multi-tenant |
