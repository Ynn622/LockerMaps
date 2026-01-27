import { useDark, useToggle } from '@vueuse/core'

export function useDarkMode() {
  // useDark 會自動：
  // 1. 在 <html> 加上/移除 'dark' class
  // 2. 將狀態存到 localStorage
  const isDark = useDark({
    selector: 'html',
    attribute: 'class',
    valueDark: 'dark',
    valueLight: '',
    storageKey: 'locker-theme',
  })

  const toggleDark = useToggle(isDark)

  return {
    isDark,
    toggleDark,
  }
}
