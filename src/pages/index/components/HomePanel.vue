<template>
  <view class="home">
    <!-- #ifdef APP-PLUS -->
    <view v-if="showPhonePermissionNote" class="permission-note">
      <uni-notice-bar
        text="如果提示设备识别码权限，对应的是系统「应用信息 → 权限 → 电话」。"
        :show-close="true"
        :color="theme.colors.muted"
        :background-color="theme.colors.surface"
        @close="dismissPhonePermissionNote"
      />
    </view>
    <!-- #endif -->
    <view class="page-header">
      <text class="eyebrow">日常 · 效率 · 灵感</text>
      <text class="page-title">让小事，更简单</text>
    </view>
    <view class="tools">
      <view v-for="item in tools" :key="item.title" class="tool-item">
        <Items :tone="item.tone" @tap="openTool(item)">
          <template #image>
            <uni-icons :type="item.icon" size="28" :color="theme.colors[item.color]" />
          </template>
          <template #arrow>
            <uni-icons type="arrow-right" :size="15" :color="theme.colors.muted" />
          </template>
          <text class="tool-title">{{ item.title }}</text>
          <text class="tool-description">{{ item.description }}</text>
        </Items>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Items from './Items.vue'
import { useNavigationStore } from '@/store/modules/navigation'
import type { Tool } from '@/types/home'
import { useThemeStore } from '@/store/modules/theme'

const theme = useThemeStore()

const navigation = useNavigationStore()
// #ifdef APP-PLUS
const phonePermissionNoteKey = 'mytools-phone-permission-note-dismissed'
const showPhonePermissionNote = ref(
  plus.os.name === 'Android' && !uni.getStorageSync(phonePermissionNoteKey)
)

const dismissPhonePermissionNote = () => {
  showPhonePermissionNote.value = false
  uni.setStorageSync(phonePermissionNoteKey, true)
}
// #endif
const tools: Tool[] = [
  { title: '幸运小转盘', description: '选择转盘或创建自己的转盘', tone: 'blue', color: 'accent', icon: 'refresh', destination: { list: 'wheel' } },
  { title: '连点器', description: '创建点击或滑动方案', tone: 'green', color: 'green', icon: 'hand-up', destination: { list: 'clicker' } },
  { title: '图片压缩', description: '按比例或目标体积压缩', tone: 'green', color: 'green', icon: 'image', destination: { url: '/pagesCompress/index' } },
  { title: '视频压缩', description: '按比例或目标体积压缩', tone: 'blue', color: 'accent', icon: 'videocam', destination: { url: '/pagesCompress/video' } },
  { title: '图片格式转换', description: '在 JPG 和 PNG 之间转换', tone: 'purple', color: 'purple', icon: 'loop', destination: { url: '/pagesCompress/index?mode=format' } },
  { title: '图片去水印', description: '自动识别或手动圈选', tone: 'purple', color: 'purple', icon: 'scan', destination: { url: '/pagesWatermark/index' } },
]
const openTool = (item: Tool) => {
  const { destination } = item
  if ('list' in destination) {
    navigation.openList(destination.list)
    return
  }
  uni.navigateTo({ url: destination.url })
}
</script>

<style lang="scss" scoped>
.home {
  padding-top: 32rpx;

  .permission-note {
    border-radius: 16rpx;
    overflow: hidden;
  }

  .page-header {
    display: flex;
    flex-direction: column;
    padding: 14rpx 6rpx 36rpx;

    .eyebrow {
      color: var(--dragon-accent);
      font-size: 22rpx;
      line-height: 1.5;
      letter-spacing: 4rpx;
    }

    .page-title {
      margin-top: 14rpx;
      color: var(--dragon-text);
      font-size: 50rpx;
      line-height: 1.25;
      font-weight: 700;
    }
  }

  .tools {
    display: flex;
    flex-wrap: wrap;
    gap: 20rpx;

    .tool-item {
      width: calc((100% - 20rpx) / 2);
      min-width: 0;
      flex-shrink: 0;

      .tool-title {
        display: block;
        color: var(--dragon-text);
        font-size: 30rpx;
        line-height: 1.5;
        font-weight: 600;
      }

      .tool-description {
        display: block;
        margin-top: 8rpx;
        color: var(--dragon-muted);
        font-size: 23rpx;
        line-height: 1.6;
      }
    }
  }
}
</style>
