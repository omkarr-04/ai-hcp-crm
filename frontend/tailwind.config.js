/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      colors: {
        'health-blue': '#0ea5e9',
        'health-dark': '#1e293b',
        'health-light': '#f1f5f9',
      }
    },
  },
  plugins: [],
}