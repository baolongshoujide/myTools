<template>
  <view class="button" @tap="selectWheel">
    <view class="flex-center" style="gap: 10rpx;">
      <image class="img" src="/static/wheel-settings.png" />
      <text>{{ prop.name }}</text>
    </view>
    <view class="delete-button" hover-class="delete-pressed" @tap.stop="deleteWheel">
      <uni-icons type="trash" :color="theme.colors.danger" :size="23" />
    </view>
  </view>
</template>
<script lang="ts" setup>
import type{ Wheel } from '@/types/wheel';
import { useWheelStore } from '@/store/modules/wheel';
import { useNavigationStore } from '@/store/modules/navigation';
import { useThemeStore } from '@/store/modules/theme';

const props = defineProps<{
   prop:Wheel
}>()

const wheelStore = useWheelStore()
const navigation = useNavigationStore()
const theme = useThemeStore()
const deleteWheel = () => {
  uni.showModal({
    title: '删除转盘',
    content: '将「' + props.prop.name + '」移入回收站？7天内可以恢复。',
    confirmText: '删除',
    confirmColor: '#df655b',
    success: (result) => {
      if (result.confirm && wheelStore.deleteWheel(props.prop.id)) {
        uni.showToast({ title: '已移入回收站', icon: 'none' })
      }
    },
  })
}
const selectWheel = ()=>{
  if (!wheelStore.selectWheel(props.prop.id)) {
    uni.showToast({ title: '转盘不存在，请重新选择', icon: 'none' })
    return
  }
  navigation.openTab('/pages/function/index')
}
</script>
<style lang="scss" scoped>
.button {
  width: 100%;
  box-sizing: border-box;
  height: 120rpx;
  padding-left: 60rpx;
  background-color: var(--dragon-surface);
  border: 1rpx solid var(--dragon-border);
  color: var(--dragon-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(3, 16, 32, 0.25);
  border-radius: 16rpx;
  transition: all 0.15s;
  &:active {
    transform: translateY(6rpx);
    box-shadow: 0 2rpx 0 var(--dragon-border), 0 4rpx 8rpx rgba(0, 0, 0, 0.2);
  }
  .img{
    width: 50rpx;
    height: 50rpx;
  }
  .delete-button {
    flex-shrink: 0;
    padding: 24rpx;
  }
  .delete-pressed {
    transform: scale(0.85);
  }
}
</style>
