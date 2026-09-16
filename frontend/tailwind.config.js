/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1E40AF', // A deep, professional blue
        'secondary': '#DB2777', // A vibrant pink for accents
        'neutral': '#4B5563', // A neutral gray for text
        'light-gray': '#F3F4F6', // A light gray for backgrounds
      },
    },
  },
  plugins: [require('daisyui')],
}