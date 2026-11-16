<template>
  <button class="button" @tap="selectWheel">
    <view class="flex-center" style="gap: 10rpx;">
      <image class="img" src="/static/转盘设置.png" />
      {{ prop.name }}
    </view>
    <uni-icons
      type="right"
      color=""
      size="20"
    />
  </button>
</template>
<script lang="ts" setup>
import type{ Wheel } from '@/types/wheel';
import { useWheelStore } from '@/store/modules/wheel';
import { useNavigationStore } from '@/store/modules/navigation';

const props = defineProps<{
   prop:Wheel
}>()

const wheelStore = useWheelStore()
const navigation = useNavigationStore()
const selectWheel = ()=>{
  wheelStore.selectWheel(props.prop.id)
  navigation.openTab('/pages/function/index')
}
</script>
<style lang="scss" scoped>
.button {
  width: 100%;
  box-sizing: border-box;
  height: 120rpx;
  padding-left: 60rpx;
  background-color: pink;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow:-9rpx 8rpx 10rpx 9rpx rgba(0, 0, 0, 0.45);
  border-radius: 16rpx;
  transition: all 0.15s;
  &:active {
    transform: translateY(6rpx);
    box-shadow: 0 2rpx 0 #d77d8d, 0 4rpx 8rpx rgba(0, 0, 0, 0.2);
  }
  .img{
    width: 50rpx;
    height: 50rpx;
  }
}
</style>
