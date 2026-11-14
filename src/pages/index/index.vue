<template>
  <Layout class="home-layout">
    <view class="home">
      <view class="page-header">
        <text class="eyebrow">日常 · 效率 · 灵感</text>
        <text class="page-title">让小事，更简单</text>
        <text class="page-description">把顺手的小工具，装进你的口袋。</text>
      </view>
      <view class="section-heading">
        <text class="section-title">发现工具</text>
        <text class="section-note">每一件小事，都值得轻松一点</text>
      </view>
      <view class="tools">
        <view v-for="item in tools" :key="item.title" class="tool-item">
          <Items :tone="item.tone" @tap="openTool(item)">
            <template #image>
              <uni-icons :type="item.icon" size="28" :color="item.color" />
            </template>
            <view class="tool-title-row">
              <text class="tool-title">{{ item.title }}</text>
              <text v-if="!item.path" class="soon">待上线</text>
            </view>
            <text class="tool-description">{{ item.description }}</text>
          </Items>
        </view>
      </view>
      <view class="section-heading saved-heading">
        <text class="section-title">你的转盘</text>
        <view class="manage-link" @tap="openWheelList">管理 <uni-icons type="arrow-right" size="14" color="#72809a" /></view>
      </view>
      <view class="saved-wheel" hover-class="saved-wheel-pressed" @tap="openWheel">
        <view class="saved-icon"><uni-icons type="refresh" size="27" color="#2878ff" /></view>
        <view class="saved-details">
          <text class="saved-name">{{ wheelStore.currentWheel.name || '未命名转盘' }}</text>
          <text class="saved-meta">{{ wheelStore.currentWheel.prizes.length }} 个选项 · 旋转 {{ wheelStore.currentWheel.spinTime }} 秒</text>
        </view>
        <uni-icons type="arrow-right" size="19" color="#9aa7ba" />
      </view>
    </view>
  </Layout>
</template>

<script setup lang="ts">
import Items from './components/Items.vue'
import Layout from '@/compoents/Layout.vue'
import { useWheelStore } from '@/store/modules/wheel'
import type { Tool } from '@/types/home'

const wheelStore = useWheelStore()
const tools: Tool[] = [
  { title: '图片去水印', description: '自动识别，修复图片背景', tone: 'blue', color: '#2878ff', icon: 'image', path: '/pagesWatermark/index' },
  { title: '幸运转盘', description: '把纠结的选择交给转盘', tone: 'orange', color: '#ed9351', icon: 'refresh', path: '/pages/function/index' },
  { title: '转盘列表', description: '查看转盘列表', tone: 'purple', color: '#8a6ad8', icon: 'list', path: '/pages/list/index' },
  { title: '连点器', description: '更多顺手的工具正在准备', tone: 'green', color: '#4caa88', icon: 'hand-up' },
]
const openTool = (item: Tool) => {
  if (!item.path) {
    uni.showToast({ title: '这个工具还在准备中', icon: 'none' })
    return
  }
  if (item.path === '/pages/function/index' || item.path === '/pages/list/index') {
    uni.redirectTo({ url: item.path })
    return
  }
  uni.navigateTo({ url: item.path })
}
const openWheelList = () => { uni.redirectTo({ url: '/pages/list/index' }) }
const openWheel = () => { uni.redirectTo({ url: '/pages/function/index' }) }
</script>

<style lang="scss" scoped>
.home-layout {
  background: #f5f7fb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.home {
  padding-top: 42rpx;
}
.page-header {
  display: flex;
  flex-direction: column;
  padding: 0 8rpx 44rpx;
}
.eyebrow {
  font-size: 22rpx;
  letter-spacing: 4rpx;
  color: #8794aa;
}
.page-title {
  margin-top: 18rpx;
  font-size: 46rpx;
  line-height: 1.4;
  font-weight: 700;
  color: #24324b;
}
.page-description {
  margin-top: 12rpx;
  font-size: 26rpx;
  line-height: 1.6;
  color: #8b96a8;
}
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22rpx;
  padding: 0 4rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #2c3a52;
}
.section-note {
  font-size: 21rpx;
  color: #9aa5b6;
}
.tools {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}
.tool-item {
  width: calc((100% - 20rpx) / 2);
  min-width: 0;
  flex-shrink: 0;
}
.tool-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10rpx;
}
.tool-title {
  font-size: 29rpx;
  line-height: 1.5;
  font-weight: 600;
  color: #2c3a52;
}
.soon {
  font-size: 18rpx;
  color: #99a3b1;
  background: #f1f3f6;
  border-radius: 7rpx;
  padding: 2rpx 7rpx;
}
.tool-description {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #919bad;
  line-height: 1.6;
}
.saved-heading {
  margin-top: 44rpx;
}
.manage-link {
  display: flex;
  align-items: center;
  gap: 5rpx;
  padding: 8rpx 0 8rpx 20rpx;
  color: #72809a;
  font-size: 24rpx;
}
.saved-wheel {
  display: flex;
  align-items: center;
  gap: 22rpx;
  padding: 26rpx;
  background: #fff;
  border: 1rpx solid #e9edf5;
  border-radius: 25rpx;
}
.saved-wheel-pressed {
  background: #edf3ff;
}
.saved-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 78rpx;
  height: 78rpx;
  flex-shrink: 0;
  border-radius: 22rpx;
  background: #edf3ff;
}
.saved-details {
  flex: 1;
  min-width: 0;
}
.saved-name {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #34415a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.saved-meta {
  display: block;
  margin-top: 8rpx;
  color: #99a4b5;
  font-size: 23rpx;
}
</style>
