import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { ListMode } from '@/types/navigation'

// 顺序与主页面中的 swiper-item 一致；route 用于兼容原来的页面入口。
export const mainTabs = [
  { route: '/pages/index/index', title: '首页' },
  { route: '/pages/function/index', title: '功能' },
  { route: '/pages/list/index', title: '列表' },
  { route: '/pages/my/index', title: '我的' },
]

export const useNavigationStore = defineStore('navigation', () => {
  const nowTab = ref(0)
  const listMode = ref<ListMode>('wheel')
  const locked = ref(false)
  const nowRoute = computed(() => mainTabs[nowTab.value].route)

  const selectTab = (index: number) => {
    if (locked.value || !Number.isInteger(index) || index < 0 || index >= mainTabs.length) return false
    nowTab.value = index
    return true
  }

  const openTab = (route: string) => {
    return selectTab(mainTabs.findIndex((item) => item.route === route))
  }

  const openList = (mode: ListMode) => {
    if (openTab('/pages/list/index')) listMode.value = mode
  }

  const setLocked = (value: boolean) => {
    locked.value = value
  }

  return { nowTab, nowRoute, listMode, locked, selectTab, openTab, openList, setLocked }
})
