/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vit: {
          maroon: "#800000",
          maroonDark: "#600000",
          maroonLight: "#991b1b",
          gold: "#D4AF37",
          goldDark: "#B8860B",
          navy: "#0B2545",
          slate: "#1E293B"
        }
      }
    },
  },
  plugins: [],
}
