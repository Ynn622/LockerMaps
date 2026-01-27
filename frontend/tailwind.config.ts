import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class', // 啟用 class-based dark mode
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
} satisfies Config
