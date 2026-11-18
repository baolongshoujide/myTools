<template>
  <view class="compress-page" :style="theme.pageStyle">
    <view class="heading">
      <text class="title">{{ mode === 'format' ? '图片格式转换' : '图片压缩' }}</text>
      <text class="subtitle">本地处理，无需上传图片</text>
    </view>
    <view class="image-card" @tap="chooseImage">
      <image v-if="source" class="preview" :src="source.path" mode="aspectFit" />
      <view v-else class="empty">
        <uni-icons type="image" :size="44" :color="theme.colors.accent" />
        <text>点击选择一张图片</text>
      </view>
      <text v-if="source" class="meta">原图 {{ formatSize(source.size) }} · {{ source.width }} × {{ source.height }} · 点击更换</text>
    </view>

    <view class="mode-tabs">
      <view class="mode-tab" :class="{ active: mode === 'ratio' }" @tap="selectMode('ratio')">按比例</view>
      <view class="mode-tab" :class="{ active: mode === 'target' }" @tap="selectMode('target')">目标体积</view>
      <view class="mode-tab" :class="{ active: mode === 'format' }" @tap="selectMode('format')">格式转换</view>
    </view>

    <view class="settings-card">
      <view v-if="mode === 'ratio'">
        <view class="label-row"><text>保留原图体积</text><text>{{ ratio }}%</text></view>
        <slider :value="ratio" :min="10" :max="95" :step="5" :disabled="busy" :activeColor="theme.colors.accent" @change="changeRatio" />
        <text class="hint">例如选择 25%，4 MB 的图片会以 1 MB 为目标。</text>
      </view>
      <view v-else-if="mode === 'target'">
        <text class="field-label">目标文件大小</text>
        <view class="target-row">
          <input v-model="targetSize" class="target-input" type="digit" placeholder="例如 0.5" :disabled="busy" />
          <view class="unit" :class="{ selected: targetUnit === 'MB' }" @tap="selectUnit('MB')">MB</view>
          <view class="unit" :class="{ selected: targetUnit === 'KB' }" @tap="selectUnit('KB')">KB</view>
        </view>
        <text class="hint">尽量贴近你填写的大小。实际体积受图片内容和编码影响。</text>
      </view>
      <view v-else class="format-options">
        <button
          v-for="option in formats"
          :key="option.value"
          class="format-option"
          :class="{ selected: outputFormat === option.value }"
          :disabled="busy || saving"
          @tap="outputFormat = option.value"
        >
          <text class="format-name">{{ option.value.toUpperCase() }}</text>
          <text class="hint">{{ option.description }}</text>
        </button>
      </view>
      <text class="format-note">{{ mode === 'format'
        ? '转换后体积可能增加。最长边限制为 2400 像素。'
        : '输出为静态 JPG，透明区域填充白色。最长边限制为 2400 像素。' }}</text>
    </view>

    <button class="primary" :disabled="!source || busy || saving" :loading="busy" @tap="startCompress">{{ actionLabel }}</button>
    <text v-if="message" class="message" :class="{ error: failed }">{{ message }}</text>

    <view v-if="result" class="result-card">
      <view class="label-row"><text class="result-title">处理结果</text><text>{{ result.format.toUpperCase() }} · {{ formatSize(result.size) }}</text></view>
      <image class="preview" :src="result.path" mode="aspectFit" @tap="previewResult" />
      <text class="meta">{{ result.width }} × {{ result.height }} · {{ resultSummary }}</text>
      <button class="primary" :loading="saving" :disabled="saving || busy" @tap="saveResult">保存到相册</button>
    </view>

    <canvas canvas-id="compressCanvas" id="compressCanvas" class="work-canvas" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }" />
  </view>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, ref } from 'vue'
import { onLoad, onReady, onUnload } from '@dcloudio/uni-app'
import { compressToTarget, formatSize } from './compressor'
import type { CompressImageFile, ImageMode, ImageFormat, CompressResult, CompressSliderEvent } from '@/types/compress'
import { usePageTheme } from '@/composables/usePageTheme'

const theme = usePageTheme()

const instance = getCurrentInstance()
const source = ref<CompressImageFile | null>(null)
const result = ref<CompressResult | null>(null)
const mode = ref<ImageMode>('ratio')
const outputFormat = ref<ImageFormat>('jpg')
const formats = [
  { value: 'jpg', description: '适合照片，通常体积更小。会损失少量细节，透明区域会填成白色。' },
  { value: 'png', description: '无损编码，保留透明背景，适合图标和截图。照片转成 PNG 后通常会变大。' },
] as const
const ratio = ref(50)
const targetSize = ref('0.5')
const targetUnit = ref('MB')
const busy = ref(false)
const saving = ref(false)
const failed = ref(false)
const message = ref('')
const canvasWidth = ref(1)
const canvasHeight = ref(1)
let disposed = false
let drawnWidth = 0
let drawnHeight = 0

const resultSummary = computed(() => {
  if (!source.value || !result.value) return ''
  const percent = (1 - result.value.size / source.value.size) * 100
  if (percent > 0) return '体积减少 ' + percent.toFixed(1) + '%'
  if (percent < 0) return '体积增加 ' + Math.abs(percent).toFixed(1) + '%'
  return '体积不变'
})

const actionLabel = computed(() => {
  if (mode.value === 'format') return busy.value ? '正在转换…' : '开始转换'
  return busy.value ? '正在压缩…' : '开始压缩'
})

const updateTitle = () => {
  uni.setNavigationBarTitle({ title: mode.value === 'format' ? '图片格式转换' : '图片压缩' })
}

onLoad((options) => {
  if (options?.mode === 'format') mode.value = 'format'
})
onReady(updateTitle)

const selectMode = (value: ImageMode) => {
  if (busy.value || saving.value || mode.value === value) return
  mode.value = value
  updateTitle()
}
const selectUnit = (value: string) => { if (!busy.value) targetUnit.value = value }
const changeRatio = (event: Event | CompressSliderEvent) => { ratio.value = (event as CompressSliderEvent).detail.value }

const fileSize = (path: string): Promise<number> => new Promise((resolve, reject) => {
  uni.getFileInfo({ filePath: path, success: (info) => resolve(info.size), fail: () => reject(new Error('无法读取图片体积，请重新选择')) })
})

const chooseImage = () => {
  if (busy.value || saving.value) return
  uni.chooseImage({
    count: 1,
    sizeType: ['original'],
    success: async (response) => {
      const path = response.tempFilePaths[0]
      if (!path || disposed) return
      busy.value = true
      message.value = ''
      failed.value = false
      result.value = null
      try {
        const size = await fileSize(path)
        if (size > 20 * 1024 * 1024) throw new Error('请选择20MB以内的图片')
        const info = await new Promise<UniApp.GetImageInfoSuccessData>((resolve, reject) => {
          uni.getImageInfo({ src: path, success: resolve, fail: () => reject(new Error('图片读取失败，请更换图片')) })
        })
        if (disposed) return
        source.value = { path: info.path || path, size, width: info.width, height: info.height }
      } catch (error) {
        if (!disposed) { failed.value = true; message.value = error instanceof Error ? error.message : '选图失败' }
      } finally {
        busy.value = false
      }
    },
  })
}

const encodeImage = async (width: number, height: number, outputQuality: number, format: ImageFormat = 'jpg'): Promise<CompressResult> => {
  if (disposed || !source.value) throw new Error('页面已关闭')
  if (width !== drawnWidth || height !== drawnHeight) {
    canvasWidth.value = width
    canvasHeight.value = height
    await nextTick()
    if (disposed) throw new Error('页面已关闭')
    const context = uni.createCanvasContext('compressCanvas', instance?.proxy)
    if (format === 'jpg') {
      context.setFillStyle('#ffffff')
      context.fillRect(0, 0, width, height)
    }
    context.drawImage(source.value.path, 0, 0, width, height)
    await new Promise<void>((resolve) => context.draw(false, () => resolve()))
    drawnWidth = width
    drawnHeight = height
  }
  if (disposed) throw new Error('页面已关闭')
  const path = await new Promise<string>((resolve, reject) => {
    uni.canvasToTempFilePath({
      canvasId: 'compressCanvas', width, height, destWidth: width, destHeight: height,
      fileType: format, quality: outputQuality,
      success: (response) => resolve(response.tempFilePath),
      fail: () => reject(new Error('图片导出失败，请尝试更小的尺寸')),
    }, instance?.proxy)
  })
  return { path, width, height, format, quality: outputQuality, size: await fileSize(path) }
}

const startCompress = async () => {
  if (!source.value || busy.value || saving.value) return
  busy.value = true
  failed.value = false
  result.value = null
  const converting = mode.value === 'format'
  message.value = converting ? '正在转换图片格式，请稍候' : '正在本地压缩，请稍候'
  drawnWidth = 0
  drawnHeight = 0
  try {
    const original = source.value
    const scale = Math.min(1, 2400 / Math.max(original.width, original.height))
    const width = Math.max(1, Math.round(original.width * scale))
    const height = Math.max(1, Math.round(original.height * scale))
    if (converting) {
      const output = await encodeImage(width, height, 0.95, outputFormat.value)
      if (disposed) return
      result.value = output
      message.value = '转换完成，可以预览并保存。'
      return
    }
    const targetBytes = mode.value === 'ratio'
      ? Math.floor(original.size * ratio.value / 100)
      : Math.floor(Number(targetSize.value) * (targetUnit.value === 'MB' ? 1024 * 1024 : 1024))
    if (!Number.isFinite(targetBytes) || targetBytes < 1024) throw new Error('目标体积至少为1KB，请填写有效数值')
    if (original.size <= targetBytes) {
      message.value = '原图已在目标大小以内，可直接使用原图。'
      return
    }
    const output = await compressToTarget(width, height, targetBytes, encodeImage)
    if (disposed) return
    result.value = output
    message.value = '目标 ' + formatSize(targetBytes) + '，实际 ' + formatSize(output.size)
      + (output.size < targetBytes * 0.97 ? '。受图片编码限制，结果低于目标。' : '。')
  } catch (error) {
    if (!disposed) { failed.value = true; message.value = error instanceof Error ? error.message : '压缩失败，请重试' }
  } finally {
    busy.value = false
  }
}

const previewResult = () => {
  if (result.value) uni.previewImage({ urls: [result.value.path] })
}
const saveResult = () => {
  if (!result.value || saving.value || busy.value) return
  saving.value = true
  uni.saveImageToPhotosAlbum({
    filePath: result.value.path,
    success: () => uni.showToast({ title: '已保存到相册' }),
    fail: () => uni.showModal({ title: '保存失败', content: '请检查相册权限后重试。', showCancel: false }),
    complete: () => { saving.value = false },
  })
}
onUnload(() => { disposed = true })
</script>

<style lang="scss" scoped>
.compress-page {
  min-height: 100vh;
  padding: 32rpx 24rpx 64rpx;
  box-sizing: border-box;
  background: var(--dragon-page);
  color: var(--dragon-text);
  .heading {
    padding: 8rpx 8rpx 28rpx;
    .title {
      display: block;
      font-size: 40rpx;
      font-weight: 600;
    }
    .subtitle {
      display: block;
      margin-top: 12rpx;
      font-size: 25rpx;
      color: var(--dragon-muted);
    }
  }
  .image-card,
  .settings-card,
  .result-card {
    padding: 28rpx;
    border-radius: 24rpx;
    background: var(--dragon-surface);
  }
  .preview {
    display: block;
    width: 100%;
    height: 360rpx;
  }
  .empty {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    height: 280rpx;
    color: var(--dragon-muted);
    font-size: 27rpx;
  }
  .meta {
    display: block;
    margin-top: 16rpx;
    font-size: 23rpx;
    color: var(--dragon-muted);
    line-height: 1.6;
  }
  .mode-tabs {
    display: flex;
    padding: 8rpx;
    margin: 28rpx 0;
    border-radius: 20rpx;
    background: var(--dragon-base);
    .mode-tab {
      flex: 1;
      padding: 20rpx 0;
      text-align: center;
      color: var(--dragon-muted);
      font-size: 27rpx;
      border-radius: 16rpx;
      &.active {
        background: var(--dragon-surface);
        color: var(--dragon-accent);
        font-weight: 600;
      }
    }
  }
  .label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 28rpx;
  }
  .hint,
  .format-note {
    display: block;
    color: var(--dragon-muted);
    font-size: 24rpx;
    line-height: 1.7;
  }
  .format-options {
    .format-option {
      margin: 0 0 12rpx;
      padding: 16rpx 20rpx;
      text-align: left;
      background: var(--dragon-raised);
      border-radius: 16rpx;

      &.selected {
        background: var(--dragon-highlight);
        box-shadow: inset 0 0 0 2rpx var(--dragon-accent);
      }

      .format-name {
        display: block;
        color: var(--dragon-text);
        font-size: 28rpx;
        font-weight: 600;
        line-height: 1.5;
      }
    }
  }
  .format-note {
    margin-top: 24rpx;
    padding-top: 20rpx;
    border-top: 2rpx solid var(--dragon-border);
  }
  .field-label {
    font-size: 28rpx;
  }
  .target-row {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin: 24rpx 0;
    .target-input {
      flex: 1;
      min-width: 0;
      height: 84rpx;
      padding: 0 20rpx;
      border-radius: 14rpx;
      background: var(--dragon-raised);
      font-size: 30rpx;
    }
    .unit {
      padding: 20rpx 18rpx;
      border-radius: 14rpx;
      font-size: 26rpx;
      background: var(--dragon-raised);
      &.selected {
        background: var(--dragon-highlight);
        color: var(--dragon-accent);
      }
    }
  }
  .primary {
    margin-top: 28rpx;
    border-radius: 20rpx;
    background: var(--dragon-primary);
    color: #fff;
    font-size: 30rpx;
    &::after {
      border: none;
    }
    &[disabled] {
      background: var(--dragon-border);
      color: #fff;
    }
  }
  .message {
    display: block;
    margin: 24rpx 8rpx;
    font-size: 25rpx;
    color: var(--dragon-muted);
    line-height: 1.7;
    &.error {
      color: var(--dragon-danger);
    }
  }
  .result-card {
    margin-top: 28rpx;
    .result-title {
      font-weight: 600;
    }
  }
  .work-canvas {
    position: fixed;
    left: -10000px;
    top: 0;
    pointer-events: none;
  }
}
</style>
