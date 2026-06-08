import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        soil: {
          50: "#f7f4ef",
          100: "#eee7da",
          400: "#9b8062",
          700: "#4c3728",
          900: "#211812"
        },
        leaf: {
          400: "#5f8d4e",
          600: "#2f5f3a",
          800: "#173d25"
        }
      },
      boxShadow: {
        sober: "0 24px 80px rgba(15, 23, 42, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
