/** @type {import('tailwindcss').Config} */
// Tokens da secao 1 de docs/design-system.md. Os valores sao literais de
// proposito: quem mudar cor aqui precisa refazer a conta de contraste que esta
// documentada na especificacao, lado a lado com cada token.
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
          50: "#FFF1F2",
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
          DEFAULT: "#141417", // --black do antigo
          card: "#1B1B1F", // --211b38 do antigo
          campo: "#202024",
          elevado: "#232329",
          borda: "#2A2A30", // divisoria DECORATIVA (1,29:1)
        },

        // ---- fronteira de controle ---------------------------------------
        // 3,50:1 sobre #141417. Exigido por WCAG 1.4.11 em input/select/
        // checkbox. Nao escureca.
        borda: {
          DEFAULT: "#2A2A30",
          forte: "#6B6B78",
        },

        // ---- texto -------------------------------------------------------
        // texto-3 e o PISO. Nada de text-white/30, /35, /40 para texto.
        texto: {
          DEFAULT: "#F4F4F5", // 16,73:1
          2: "#A1A1AA", //  7,17:1
          3: "#8A8A92", //  5,37:1  <- piso
        },

        // ---- semanticos --------------------------------------------------
        // erro NAO usa a marca: vermelho de marca e vermelho de erro
        // precisam ser distinguiveis.
        sucesso: { DEFAULT: "#6EE7B7", forte: "#10B981", fundo: "#193731", borda: "#16624B" },
        aviso: { DEFAULT: "#FCD34D", forte: "#F59E0B", fundo: "#42331B", borda: "#7D5616" },
        erro: { DEFAULT: "#FDA4AF", forte: "#FB7185", fundo: "#42212A", borda: "#7D2B3B" },
        info: { DEFAULT: "#93C5FD", forte: "#3B82F6", fundo: "#212E46", borda: "#294980" },
      },

      fontFamily: {
        // Troca de familia e uma linha: ver a nota de Gilroy na secao 1 da spec.
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },

      fontSize: {
        "2xs": ["11px", { lineHeight: "14px" }],
        xs: ["12px", { lineHeight: "16px" }],
        sm: ["14px", { lineHeight: "20px" }],
        base: ["16px", { lineHeight: "24px" }],
        lg: ["18px", { lineHeight: "26px" }],
        xl: ["20px", { lineHeight: "28px" }],
        "2xl": ["24px", { lineHeight: "32px" }],
        "3xl": ["30px", { lineHeight: "36px" }],
        "4xl": ["40px", { lineHeight: "44px" }],
      },

      borderRadius: {
        DEFAULT: "4px",
        lg: "8px",
        xl: "10px",
        "2xl": "16px",
      },

      maxWidth: {
        conteudo: "1440px", // substitui o max-width:90% elastico do antigo
        menu: "256px", // .left-side-bar_page-padding: min 250 / max 280
      },

      spacing: {
        barra: "64px", // altura da barra superior (desktop)
        "barra-sm": "56px", // altura da barra superior (mobile)
        tabbar: "64px", // altura da barra inferior mobile
        // A secao 2.2 usa `w-menu`, e largura sai de `spacing`, nao de
        // `maxWidth`. Mesmo valor do token `maxWidth.menu`.
        menu: "256px",
        gaveta: "320px", // largura da gaveta mobile (secao 2.4)
      },

      zIndex: {
        // escala da secao 1.6, para nao voltar ao z-index:99999 do antigo
        30: "30", // barra superior
        40: "40", // barra inferior mobile
        50: "50", // overlay
        60: "60", // gaveta / modal
        70: "70", // toast
        80: "80", // link de pular conteudo
      },

      transitionTimingFunction: {
        gaveta: "cubic-bezier(.2,.8,.2,1)",
      },

      transitionDuration: {
        250: "250ms", // entrada de gaveta/modal (secao 1.7)
      },

      keyframes: {
        pulso: { "0%,100%": { opacity: ".5" }, "50%": { opacity: "1" } },
        entrada: {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        pulso: "pulso 1600ms linear infinite",
        entrada: "entrada 200ms ease-out",
      },
    },
  },
  plugins: [],
};
