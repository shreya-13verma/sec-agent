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
          green: '#30ba78',
          dark: '#0c322c',
          pine: '#195144',
          gray: '#1f2937',
          light: '#f8fafc'
        }
      }
    },
  },
  plugins: [],
}
