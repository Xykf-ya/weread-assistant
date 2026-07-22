/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parchment: {
          50: '#fdfbf7',
          100: '#f9f3e8',
          200: '#f3e9d5',
          300: '#e9dab8',
          400: '#dcc899',
          500: '#cfb57a',
          600: '#bfa062',
          700: '#9e8150',
          800: '#806944',
          900: '#675639',
        },
        ink: {
          50: '#f5f5f4',
          100: '#e7e5e4',
          200: '#d6d3d1',
          300: '#a8a29e',
          400: '#78716c',
          500: '#57534e',
          600: '#44403c',
          700: '#292524',
          800: '#1c1917',
          900: '#171514',
        },
        sepia: {
          50: '#f8f3eb',
          100: '#ede4d4',
          200: '#dcc5a8',
          300: '#c7a87b',
          400: '#b38b54',
          500: '#9f6f38',
          600: '#8a5a2e',
          700: '#6d4525',
          800: '#553720',
          900: '#422c19',
          950: '#2a1a0f',
        },
        gold: {
          50: '#fefce8',
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
          900: '#713f12',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
        handwriting: ['Dancing Script', 'cursive'],
      },
      boxShadow: {
        'paper': '0 1px 3px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',
        'paper-lifted': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.02)',
        'vintage': '2px 2px 0 rgba(66, 44, 25, 0.3), -1px -1px 0 rgba(255, 255, 255, 0.5) inset',
      },
      backgroundImage: {
        'parchment-texture': "url('data:image/svg+xml,%3Csvg viewBox=\"0 0 200 200\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noiseFilter\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"4\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25\" filter=\"url(%23noiseFilter)\"/%3E%3C/svg%3E')",
      },
      borderWidth: {
        'hairline': '1px',
      },
    },
  },
  plugins: [],
}
