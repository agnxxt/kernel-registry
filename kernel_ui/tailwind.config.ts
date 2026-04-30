import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        kernel: {
          fast: "#3b82f6",
          slow: "#8b5cf6",
          rogue: "#ef4444",
        }
      },
    },
  },
  plugins: [],
};
export default config;
