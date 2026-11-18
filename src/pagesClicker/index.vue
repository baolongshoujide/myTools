<template>
  <view />
</template>

<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'

// 兼容以前打开连点器的链接。
onLoad(() => {
  uni.redirectTo({ url: '/pages/index/index?tab=2&list=clicker' })
})
</script>
