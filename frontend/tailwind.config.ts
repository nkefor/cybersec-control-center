import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        sidebar: {
          DEFAULT: '#0F172A',
          hover: '#1E293B',
          active: '#1E3A5F',
          border: '#1E293B',
          text: '#94A3B8',
          'text-active': '#F8FAFC',
        },
        brand: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
          light: '#DBEAFE',
        },
        severity: {
          critical: '#DC2626',
          high: '#EA580C',
          medium: '#D97706',
          low: '#65A30D',
          info: '#2563EB',
        },
        status: {
          healthy: '#16A34A',
          warning: '#D97706',
          critical: '#DC2626',
          unknown: '#6B7280',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'score-fill': {
          '0%': { 'stroke-dashoffset': '339' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'score-fill': 'score-fill 1.2s ease-out forwards',
      },
    },
  },
  plugins: [],
}

export default config
