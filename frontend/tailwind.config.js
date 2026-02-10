/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          600: '#4f46e5', // Indigo-600
        },
        emerald: {
          500: '#10b981',
        },
        rose: {
          500: '#f43f5e',
        },
        amber: {
          500: '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
