<template>
  <view class="tool-card" :class="'tone-' + tone" hover-class="tool-card-pressed" :hover-stay-time="100" @tap="emit('tap')">
    <view class="card-header">
      <view class="icon-box"><slot name="image" /></view>
      <view class="card-arrow"><slot name="arrow" /></view>
    </view>
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
  --tool-tint: var(--dragon-raised);
  width: 100%;
  height: 260rpx;
  padding: 24rpx;
  box-sizing: border-box;
  background: linear-gradient(150deg, var(--tool-tint), var(--dragon-surface) 65%);
  border: 1rpx solid var(--dragon-border);
  border-radius: 28rpx;
  box-shadow: 0 8rpx 18rpx rgba(14, 30, 52, 0.12);
  transition: transform 0.15s ease, opacity 0.15s ease;

  &.tool-card-pressed {
    transform: scale(0.98);
    opacity: 0.84;
  }

  &.tone-purple {
    --tool-tint: var(--dragon-purpleSurface);
  }

  &.tone-green {
    --tool-tint: var(--dragon-greenSurface);
  }

  .card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;

    .icon-box,
    .card-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1rpx solid var(--dragon-border);
    }

    .icon-box {
      width: 80rpx;
      height: 80rpx;
      box-sizing: border-box;
      border-radius: 22rpx;
      background: var(--tool-tint);
    }

    .card-arrow {
      width: 42rpx;
      height: 42rpx;
      border-radius: 50%;
      background: var(--dragon-surface);
    }
  }

  .card-content {
    margin-top: 16rpx;
  }
}
</style>
