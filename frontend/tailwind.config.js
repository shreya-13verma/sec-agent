/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        suse: {
          dark: '#0c322c',
          green: '#30ba78',
          pine: '#195144',
          mint: '#86e4b8',
          accent: '#fe7c3f'
        }
      }
    },
  },
  plugins: [],
}
