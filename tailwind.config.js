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
        // paleta herdada do tema da plataforma
        marca: {
          DEFAULT: "#FF2338",
          escuro: "#E32D47",
        },
        fundo: {
          DEFAULT: "#141417",
          card: "#1B1B1F",
          borda: "#2A2A30",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};
