<template>
  <view class="region-selector">
    <view class="selector-header">
      <text class="selector-title">圈选水印</text>
      <text class="selector-description">在图片上拖动框选，可连续选择多处</text>
    </view>
    <view
      class="selection-stage"
      @touchstart.stop.prevent="startSelection"
      @touchmove.stop.prevent="moveSelection"
      @touchend.stop.prevent="finishSelection"
      @touchcancel.stop.prevent="cancelDraft"
    >
      <text v-if="!imageFrame.width" class="loading-text">{{ loadError || '正在加载图片…' }}</text>
      <view v-if="imageFrame.width" class="selection-image" :style="frameStyle">
        <image class="source-image" :src="image" mode="aspectFit" :draggable="false" />
        <view v-for="(item, index) in regions" :key="index" class="selection-box" :style="regionStyle(item)">
          <text class="selection-number">{{ index + 1 }}</text>
        </view>
        <view v-if="draft" class="selection-box draft-box" :style="regionStyle(draft)" />
      </view>
    </view>
    <view class="selector-footer">
      <view class="selection-toolbar">
        <text class="selection-count">已选 {{ regions.length }} 处</text>
        <button class="selector-button toolbar-button" :class="{ 'is-disabled': !regions.length }" :disabled="!regions.length" @tap="undoSelection">撤销上一处</button>
        <button class="selector-button toolbar-button" :class="{ 'is-disabled': !regions.length }" :disabled="!regions.length" @tap="clearSelections">清空</button>
      </view>
      <text class="selection-tip">尽量只框住水印及少量周围背景，框得太大会改变原图细节。</text>
      <view class="selector-actions">
        <button class="selector-button cancel-button" @tap="emit('cancel')">取消</button>
        <button class="selector-button confirm-button" :class="{ 'is-disabled': !regions.length }" :disabled="!regions.length" @tap="confirmSelection">修复选区</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { clampImagePoint, fitImageFrame, normalizedRegion } from '../selection'
import type { RegionSelectorEmits, RegionSelectorProps, SelectionFrame, SelectionPoint, SelectionSize, SelectionTouchEvent, WatermarkRegion } from '@/types/watermark'

const props = defineProps<RegionSelectorProps>()
const emit = defineEmits<RegionSelectorEmits>()
const instance = getCurrentInstance()
const regions = ref<WatermarkRegion[]>([])
const draft = ref<WatermarkRegion | null>(null)
const imageSize = ref<SelectionSize>({ width: 0, height: 0 })
const imageFrame = ref<SelectionFrame>({ left: 0, top: 0, width: 0, height: 0 })
const loadError = ref('')
let stageFrame: SelectionFrame | null = null
let startPoint: SelectionPoint | null = null
let disposed = false

const frameStyle = computed(() => ({
  left: imageFrame.value.left + 'px',
  top: imageFrame.value.top + 'px',
  width: imageFrame.value.width + 'px',
  height: imageFrame.value.height + 'px',
}))

const regionStyle = (item: WatermarkRegion) => {
  return { left: item.x * 100 + '%', top: item.y * 100 + '%', width: item.width * 100 + '%', height: item.height * 100 + '%' }
}

const cancelDraft = () => {
  startPoint = null
  draft.value = null
}

const measureStage = async () => {
  await nextTick()
  if (disposed || !instance?.proxy || !imageSize.value.width) return
  uni.createSelectorQuery().in(instance.proxy).select('.selection-stage').boundingClientRect((result) => {
    if (disposed || !result || Array.isArray(result)) return
    const width = result.width || 0
    const height = result.height || 0
    stageFrame = { left: result.left || 0, top: result.top || 0, width, height }
    imageFrame.value = fitImageFrame({ width, height }, imageSize.value)
    cancelDraft()
  }).exec()
}

const eventPoint = (event: Event | SelectionTouchEvent): SelectionPoint | null => {
  if (!stageFrame || !imageFrame.value.width) return null
  // 编辑器可能将 view 的触摸事件识别为 Event，运行时按触摸事件读取并检查坐标。
  const touchEvent = event as SelectionTouchEvent
  const touch = touchEvent.touches?.[0] || touchEvent.changedTouches?.[0]
  if (!touch || typeof touch.clientX !== 'number' || typeof touch.clientY !== 'number') return null
  return {
    x: touch.clientX - stageFrame.left - imageFrame.value.left,
    y: touch.clientY - stageFrame.top - imageFrame.value.top,
  }
}

const startSelection = (event: Event | SelectionTouchEvent) => {
  const touchEvent = event as SelectionTouchEvent
  if ((touchEvent.touches?.length || 0) > 1) return
  if (regions.value.length >= 20) {
    uni.showToast({ title: '最多圈选20处，可先修复后再继续', icon: 'none' })
    return
  }
  const point = eventPoint(event)
  if (!point || point.x < 0 || point.y < 0 || point.x > imageFrame.value.width || point.y > imageFrame.value.height) return
  startPoint = point
  draft.value = null
}

const moveSelection = (event: Event | SelectionTouchEvent) => {
  if (!startPoint) return
  const point = eventPoint(event)
  if (!point) return
  draft.value = normalizedRegion(startPoint, clampImagePoint(point, imageFrame.value), imageFrame.value)
}

const finishSelection = (event: Event | SelectionTouchEvent) => {
  moveSelection(event)
  const item = draft.value
  if (item && item.width * imageFrame.value.width >= 6 && item.height * imageFrame.value.height >= 6) {
    regions.value.push(item)
  }
  cancelDraft()
}

const undoSelection = () => { regions.value.pop() }
const clearSelections = () => { regions.value = [] }
const confirmSelection = () => {
  if (regions.value.length) emit('confirm', regions.value.slice())
}

onMounted(() => {
  uni.onWindowResize(measureStage)
  uni.getImageInfo({
    src: props.image,
    success: (info) => {
      if (disposed) return
      const rotated = ['left', 'right', 'left-mirrored', 'right-mirrored'].includes(info.orientation || 'up')
      imageSize.value = { width: rotated ? info.height : info.width, height: rotated ? info.width : info.height }
      measureStage()
    },
    fail: () => { loadError.value = '图片加载失败，请返回后重新选择' },
  })
})

onUnmounted(() => {
  disposed = true
  uni.offWindowResize(measureStage)
})
</script>

<style lang="scss" scoped>
.region-selector {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  background: var(--dragon-page);
  color: var(--dragon-text);
}
.selector-header {
  padding: 28rpx 28rpx 12rpx;
  flex-shrink: 0;
}
.selector-title {
  display: block;
  font-size: 34rpx;
  font-weight: 600;
}
.selector-description {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: var(--dragon-muted);
}
.selection-stage {
  flex: 1;
  min-height: 0;
  margin: 20rpx 20rpx 0;
  position: relative;
  overflow: hidden;
  touch-action: none;
}
.loading-text {
  position: absolute;
  top: 45%;
  width: 100%;
  text-align: center;
  color: var(--dragon-muted);
}
.selection-image {
  position: absolute;
}
.source-image {
  width: 100%;
  height: 100%;
  display: block;
  pointer-events: none;
}
.selection-box {
  position: absolute;
  box-sizing: border-box;
  border: 2px solid #80aeff;
  background: rgba(40, 120, 255, 0.2);
  pointer-events: none;
}
.draft-box {
  border-style: dashed;
}
.selection-number {
  display: block;
  width: 30rpx;
  line-height: 30rpx;
  text-align: center;
  font-size: 20rpx;
  color: white;
  background: #2878ff;
}
.selector-footer {
  flex-shrink: 0;
  padding: 20rpx 24rpx calc(24rpx + env(safe-area-inset-bottom));
}
.selection-toolbar {
  display: flex;
  align-items: center;
  gap: 14rpx;
}
.selection-count {
  flex: 1;
  font-size: 25rpx;
  color: var(--dragon-muted);
}
.selector-button {
  margin: 0;
  border-radius: 16rpx;
  font-size: 26rpx;
}
.selector-button::after {
  border: none;
}
.toolbar-button {
  height: 60rpx;
  line-height: 60rpx;
  padding: 0 16rpx;
  background: var(--dragon-raised);
  color: var(--dragon-text);
  font-size: 23rpx;
}
.toolbar-button.is-disabled {
  color: var(--dragon-muted);
  background: var(--dragon-surface);
}
.selection-tip {
  display: block;
  margin: 20rpx 0;
  color: var(--dragon-muted);
  font-size: 22rpx;
  line-height: 1.7;
}
.selector-actions {
  display: flex;
  gap: 20rpx;
}
.selector-actions .selector-button {
  flex: 1;
}
.cancel-button {
  background: var(--dragon-raised);
  color: var(--dragon-text);
}
.confirm-button {
  background: var(--dragon-primary);
  color: white;
}
.confirm-button.is-disabled {
  background: var(--dragon-raised);
  color: var(--dragon-muted);
}
</style>
