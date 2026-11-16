<template>
  <view />
</template>

<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { useNavigationStore } from '@/store/modules/navigation'

// 兼容原来的路由入口，实际内容统一由主页面的 swiper 展示。
onLoad(() => {
  useNavigationStore().selectTab(3)
  uni.redirectTo({ url: '/pages/index/index?tab=3' })
})
</script>
