import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { ThemeMode } from '@/types/theme'

const storageKey = 'mytools-theme'

const palettes = {
  dark: {
    base: '#0a213d',
    page: 'linear-gradient(165deg, #0a213d 0%, #103760 66%, #175493 100%)',
    surface: '#102d50',
    raised: '#17416c',
    highlight: '#235885',
    border: '#28517b',
    text: '#eef8ff',
    muted: '#afc9e3',
    accent: '#78dcff',
    primary: '#175da0',
    danger: '#ffb2ad',
    dangerSurface: '#452839',
    dangerPressed: '#5c3244',
    green: '#7de4db',
    purple: '#b3c7ff',
    greenSurface: '#134655',
    purpleSurface: '#263d68',
    wheelTrim: '#78dcff',
  },
  light: {
    base: '#fff5e9',
    page: '#fff5e9',
    surface: '#fffdfa',
    raised: '#f8e9da',
    highlight: '#f2daca',
    border: '#e9d5c4',
    text: '#332419',
    muted: '#6e5446',
    accent: '#a34721',
    primary: '#a34721',
    danger: '#9b3932',
    dangerSurface: '#ffe9e4',
    dangerPressed: '#f9d9d2',
    green: '#25665e',
    purple: '#58488b',
    greenSurface: '#e4f1e6',
    purpleSurface: '#efe8f5',
    wheelTrim: '#ffb52e',
  },
}

export const useThemeStore = defineStore('theme', () => {
  const mode = ref<ThemeMode>('dark')
  try {
    if (uni.getStorageSync(storageKey) === 'light') mode.value = 'light'
  } catch {
    // 读取失败时沿用默认深色。
  }

  const colors = computed(() => palettes[mode.value])
  const pageStyle = computed(() => ({
    ...Object.fromEntries(Object.entries(colors.value).map(([key, value]) => ['--dragon-' + key, value])),
    color: colors.value.text,
  }))

  const setMode = (value: ThemeMode) => {
    if (value === mode.value) return
    try {
      uni.setStorageSync(storageKey, value)
      mode.value = value
    } catch {
      uni.showToast({ title: '主题保存失败，请重试', icon: 'none' })
    }
  }

  return { mode, colors, pageStyle, setMode }
})
