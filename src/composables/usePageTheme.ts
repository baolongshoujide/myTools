import { watch } from 'vue'
import { onHide, onReady, onShow, onUnload } from '@dcloudio/uni-app'
import { useThemeStore } from '@/store/modules/theme'

export const usePageTheme = () => {
  const theme = useThemeStore()
  let visible = false

  const updateNavigation = () => {
    if (!visible) return
    uni.setNavigationBarColor({
      frontColor: theme.mode === 'light' ? '#000000' : '#ffffff',
      backgroundColor: theme.colors.base,
    })
    // #ifdef MP-WEIXIN
    uni.setBackgroundColor({ backgroundColor: theme.colors.base })
    // #endif
  }

  onShow(() => {
    visible = true
    updateNavigation()
  })
  onReady(updateNavigation)
  onHide(() => { visible = false })
  onUnload(() => { visible = false })
  watch(() => theme.mode, updateNavigation)

  return theme
}
