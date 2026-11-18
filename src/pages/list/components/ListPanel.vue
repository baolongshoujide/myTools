<template>
  <view class="wheel-list">
    <text v-if="!wheelStore.wheels.length" class="empty">暂无转盘，点击下方加号创建，或到“我的”回收站恢复。</text>
    <WheelListItem v-for="item in wheelStore.wheels" :key="item.id" :prop="item" />
  </view>
</template>

<script lang="ts" setup>
import WheelListItem from './Item.vue'
import { useWheelStore } from '@/store/modules/wheel';

const wheelStore = useWheelStore()
</script>

<style lang="scss" scoped>
.wheel-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;

  .empty {
    padding: 60rpx 24rpx;
    color: var(--dragon-muted);
    font-size: 27rpx;
    line-height: 1.8;
  }
}
</style>
