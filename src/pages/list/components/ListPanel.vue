<template>
  <view>
    <view class="wheel-list">
      <Item :prop = item v-for="item in wheelStore.wheels" :key="item.id" />
    </view>
  </view>
</template>

<script lang="ts" setup>
import Item from './Item.vue'
import { useWheelStore } from '@/store/modules/wheel';

const wheelStore = useWheelStore()



</script>

<style scoped>
.wheel-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding-top: 24rpx;
}
</style>
