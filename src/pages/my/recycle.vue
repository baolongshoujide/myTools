<template>
  <view class="recycle-page" :style="theme.pageStyle">
    <text class="notice">删除的转盘保留7天，到期后彻底删除。恢复后可在转盘列表中找到。</text>
    <view v-if="!wheelStore.recycleBin.length" class="empty">
      <uni-icons type="trash" :size="48" :color="theme.colors.accent" />
      <text>回收站是空的</text>
    </view>
    <view v-for="item in wheelStore.recycleBin" :key="item.id" class="recycle-card">
      <text class="name">{{ item.name }}</text>
      <text class="date">删除日期：{{ formatDate(item.deletedAt) }}</text>
      <text class="date">彻底删除：{{ formatDate(item.deletedAt + retentionTime) }}</text>
      <view class="actions">
        <button class="restore" @tap="restoreWheel(item.id)">恢复转盘</button>
        <button class="erase" @tap="eraseWheel(item.id)">彻底删除</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow, onHide, onUnload } from '@dcloudio/uni-app'
import { useWheelStore } from '@/store/modules/wheel'
import { usePageTheme } from '@/composables/usePageTheme'

const theme = usePageTheme()

const wheelStore = useWheelStore()
const retentionTime = 7 * 24 * 60 * 60 * 1000
let cleanupTimer: ReturnType<typeof setInterval> | undefined

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp)
  const pad = (value: number) => String(value).padStart(2, '0')
  return date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate())
    + ' ' + pad(date.getHours()) + ':' + pad(date.getMinutes())
}

const restoreWheel = (id: string) => {
  const previousName = wheelStore.recycleBin.find((item) => item.id === id)?.name
  const restored = wheelStore.restoreWheel(id)
  const restoredName = restored ? wheelStore.wheels.find((item) => item.id === id)?.name : undefined
  if (restoredName && restoredName !== previousName) {
    uni.showModal({ title: '转盘已恢复', content: '已恢复为「' + restoredName + '」。', showCancel: false })
    return
  }
  uni.showToast({ title: restored ? '转盘已恢复' : '该转盘已过期或不存在', icon: 'none' })
}

const eraseWheel = (id: string) => {
  uni.showModal({
    title: '彻底删除',
    content: '彻底删除后无法恢复，确定继续吗？',
    confirmText: '彻底删除',
    confirmColor: '#df655b',
    success: (result) => {
      if (result.confirm) wheelStore.eraseWheel(id)
    },
  })
}

const stopCleanup = () => {
  if (cleanupTimer) clearInterval(cleanupTimer)
  cleanupTimer = undefined
}

onShow(() => {
  stopCleanup()
  wheelStore.cleanRecycleBin()
  cleanupTimer = setInterval(wheelStore.cleanRecycleBin, 60000)
})
onHide(stopCleanup)
onUnload(stopCleanup)
</script>

<style lang="scss" scoped>
.recycle-page {
  min-height: 100vh;
  padding: 32rpx 24rpx;
  box-sizing: border-box;
  background: var(--dragon-page);

  .notice {
    display: block;
    margin-bottom: 28rpx;
    color: var(--dragon-muted);
    font-size: 25rpx;
    line-height: 1.8;
  }
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 140rpx 0;
    gap: 24rpx;
    color: var(--dragon-muted);
  }
  .recycle-card {
    padding: 28rpx;
    margin-bottom: 24rpx;
    border-radius: 24rpx;
    background: var(--dragon-surface);

    .name {
      display: block;
      margin-bottom: 20rpx;
      color: var(--dragon-text);
      font-size: 32rpx;
      font-weight: 600;
    }
    .date {
      display: block;
      margin-top: 8rpx;
      color: var(--dragon-muted);
      font-size: 24rpx;
    }
    .actions {
      display: flex;
      gap: 20rpx;
      margin-top: 24rpx;

      .restore,
      .erase {
        flex: 1;
        padding: 0 12rpx;
        margin: 0;
        font-size: 26rpx;
        border-radius: 16rpx;

        &::after {
          border: none;
        }
      }
      .restore {
        color: var(--dragon-accent);
        background: var(--dragon-raised);
      }
      .erase {
        color: var(--dragon-danger);
        background: var(--dragon-dangerSurface);
      }
    }
  }
}
</style>
