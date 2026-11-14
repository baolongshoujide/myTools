<template>
  <view class="tool-card" :class="'tone-' + tone" hover-class="tool-card-pressed" :hover-stay-time="100" @tap="emit('tap')">
    <view class="icon-box"><slot name="image" /></view>
    <view class="card-content"><slot /></view>
  </view>
</template>

<script setup lang="ts">
import type { ToolCardEmits, ToolCardProps } from '@/types/home'

withDefaults(defineProps<ToolCardProps>(), { tone: 'blue' })
const emit = defineEmits<ToolCardEmits>()
</script>

<style lang="scss" scoped>
.tool-card {
  width: 100%;
  height: 280rpx;
  padding: 28rpx;
  box-sizing: border-box;
  background: #fff;
  border: 1rpx solid #e9edf5;
  border-radius: 28rpx;
  box-shadow: 0 6rpx 24rpx rgba(37, 55, 91, 0.035);
  transition: transform 0.15s ease, background-color 0.15s ease;
}
.tool-card-pressed {
  transform: scale(0.98);
  background: #f8faff;
}
.icon-box {
  width: 88rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 25rpx;
  background: #edf3ff;
}
.tone-orange .icon-box {
  background: #fff2e8;
}
.tone-purple .icon-box {
  background: #f1edff;
}
.tone-green .icon-box {
  background: #eaf6f2;
}
.card-content {
  margin-top: 24rpx;
}
</style>
