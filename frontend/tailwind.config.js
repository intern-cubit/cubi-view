/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Scan all JS, TS, JSX, TSX files in src/
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#3B82F6', // Example primary color
        'success-green': '#10B981',
        'danger-red': '#EF4444',
        'warning-yellow': '#F59E0B',
        'info-cyan': '#06B6D4',
        'dark-gray': '#1F2937',
        'light-gray': '#F3F4F6',
        'cubit-gold': '#b79d61', // From your About Us page
        'cubit-brown': '#83745c', // From your About Us page
      },
    },
  },
  plugins: [],
}