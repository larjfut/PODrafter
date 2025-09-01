/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        mint: { deep: '#2FB8AF' },
        coral: { DEFAULT: '#F16667' },
        purple: { deep: '#3D2B7B' },
        indigo: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81'
        },
        ink: '#0e1116',
        'muted-ink': '#475569',
        slate: '#94a3b8',
        saffron: '#E3B23C',
        moss: '#6A7F5F',
        brick: '#8B2E2F',
        cloud: '#f8fafc',
      },
      borderRadius: {
        card: '24px',
        control: '14px',
        pill: '9999px',
      },
      boxShadow: {
        e1: '0 1px 2px rgba(0,0,0,0.06), 0 1px 1px rgba(0,0,0,0.04)',
        e2: '0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)',
        e3: '0 12px 24px rgba(0,0,0,0.18), 0 4px 10px rgba(0,0,0,0.10)',
      },
      keyframes: {
        sheen: {
          '0%': { transform: 'translateX(-150%) skewX(-20deg)', opacity: '0' },
          '30%': { opacity: '0.6' },
          '100%': { transform: 'translateX(250%) skewX(-20deg)', opacity: '0' },
        },
        sweep: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        sheen: 'sheen 1.2s ease-in-out',
        sweep: 'sweep 12s ease-in-out infinite',
        shimmer: 'shimmer 1.6s linear infinite',
      },
      backdropBlur: {
        glass: '10px',
      },
      backgroundImage: {
        grain: 'radial-gradient(rgba(0,0,0,0.06) 0.5px, transparent 0.5px)',
      },
    },
  },
  plugins: [],
}
