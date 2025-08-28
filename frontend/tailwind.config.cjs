/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{svelte,ts,js}'],
  theme: {
    extend: {
      colors: { primary: 'var(--color-primary)' },
      borderRadius: { md: 'var(--radius-md)', lg: 'var(--radius-lg)' },
      boxShadow: { card: 'var(--shadow-sm)' }
    }
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
}
