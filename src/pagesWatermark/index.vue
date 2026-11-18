<template>
  <view class="watermark-page" :style="theme.pageStyle">
    <view class="service-notice">
      <uni-notice-bar
        text="使用前请联系管理员开启图片处理服务，开启后即可使用。"
        :show-icon="true"
        :scrollable="true"
        :speed="50"
        :color="theme.colors.accent"
        :background-color="theme.colors.raised"
      />
    </view>
    <view class="intro">自动识别水印，也可以手动圈选后修复</view>
    <view class="image-panel" @tap="chooseImage">
      <image v-if="selectedImage" class="preview" :src="selectedImage" mode="aspectFit" />
      <view v-else class="empty">点击选择图片</view>
    </view>
    <button class="choose" :disabled="busy" @tap="chooseImage">{{ selectedImage ? '重新选择图片' : '选择图片' }}</button>
    <view class="process-actions">
      <button class="primary" :disabled="busy || !selectedImage" :loading="busy && processingMode === 'auto'" @tap="startAutomatic">
        自动去水印
      </button>
      <button class="manual-button" :disabled="busy || !selectedImage" :loading="busy && processingMode === 'manual'" @tap="openSelector">
        手动圈选
      </button>
    </view>
    <text v-if="message" class="message" :class="{ error: failed }">{{ message }}</text>
    <view v-if="resultImage" class="result-panel">
      <text class="result-title">{{ detected ? '修复结果' : '本次未执行修复，保留原图' }}</text>
      <view class="tabs">
        <button :class="{ active: showOriginal }" @tap="showOriginal = true">原图</button>
        <button :class="{ active: !showOriginal }" @tap="showOriginal = false">处理后</button>
      </view>
      <image class="preview" :src="showOriginal ? processedOriginal : resultImage" mode="aspectFit" @tap="previewResult" />
      <text class="hint">{{ processingMode === 'manual' ? '选区内容会重新生成，请检查背景和边缘后再保存。' : '自动识别可能漏掉水印或误选正常内容，请对比后保存。' }}</text>
      <button class="primary" :loading="saving" :disabled="saving" @tap="saveResult">保存到相册</button>
    </view>
    <RegionSelector v-if="selectorOpen" :image="selectedImage" @cancel="selectorOpen = false" @confirm="repairSelection" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onUnload } from '@dcloudio/uni-app'
import { getJob, imageUrl, submitImage } from './api'
import RegionSelector from './components/RegionSelector.vue'
import type { WatermarkMode, WatermarkPollTimer, WatermarkRegion, WatermarkSubmitOptions } from '@/types/watermark'
import { usePageTheme } from '@/composables/usePageTheme'

const theme = usePageTheme()

const selectedImage = ref('')
const resultImage = ref('')
const processedOriginal = ref('')
const message = ref('')
const busy = ref(false)
const failed = ref(false)
const detected = ref(false)
const saving = ref(false)
const showOriginal = ref(false)
const selectorOpen = ref(false)
const processingMode = ref<WatermarkMode>('auto')
let timer: WatermarkPollTimer
let disposed = false

const chooseImage = () => {
  if (busy.value) return
  uni.chooseImage({
    count: 1,
    sizeType: ['original'],
    success: (response) => {
      if (disposed) return
      const files = Array.isArray(response.tempFiles) ? response.tempFiles : [response.tempFiles]
      if (!response.tempFilePaths[0] || !files[0]) return
      if (files[0].size > 20 * 1024 * 1024) {
        uni.showToast({ title: '请选择小于20MB的图片', icon: 'none' })
        return
      }
      selectedImage.value = response.tempFilePaths[0]
      resultImage.value = ''
      message.value = ''
      failed.value = false
    },
  })
}

const showError = (error: unknown) => {
  if (disposed) return
  message.value = error instanceof Error ? error.message : '图片处理失败，请重试'
  busy.value = false
  failed.value = true
}

const pollJob = async (id: string, startedAt: number) => {
  try {
    const job = await getJob(id)
    if (disposed) return
    if (job.status === 'completed' || job.status === 'no_watermark') {
      detected.value = job.status === 'completed'
      message.value = detected.value ? '处理完成，请对比原图检查效果' : '没有识别到水印，本次未执行修复'
      if (!detected.value && job.skippedRegions) message.value = '疑似水印覆盖范围过大，本次未自动修复'
      if (!detected.value && job.unverifiedRegions) message.value = '疑似区域未通过二次检查，本次已保留原图'
      if (job.resized) message.value += '；大尺寸图片已按比例缩小'
      processedOriginal.value = imageUrl(id, 'original.png')
      resultImage.value = imageUrl(id, 'result.png')
      busy.value = false
      return
    }
    if (job.status === 'failed') throw new Error(job.message || '处理失败，请重试')
    if (Date.now() - startedAt > 10 * 60 * 1000) throw new Error('处理等待超时，请稍后重试')
    message.value = job.status === 'queued' ? '图片已提交，正在等待处理' : processingMode.value === 'manual' ? '正在修复圈选区域' : '正在识别水印并修复背景'
    timer = setTimeout(() => pollJob(id, startedAt), 2000)
  } catch (error) {
    showError(error)
  }
}

const startProcess = async (options: WatermarkSubmitOptions) => {
  if (busy.value || !selectedImage.value) return
  busy.value = true
  processingMode.value = options.mode
  failed.value = false
  resultImage.value = ''
  showOriginal.value = false
  message.value = '正在上传图片'
  try {
    const job = await submitImage(selectedImage.value, options)
    if (!disposed) await pollJob(job.id, Date.now())
  } catch (error) {
    showError(error)
  }
}

const startAutomatic = () => { startProcess({ mode: 'auto' }) }
const openSelector = () => {
  if (!busy.value && selectedImage.value) selectorOpen.value = true
}
const repairSelection = (regions: WatermarkRegion[]) => {
  selectorOpen.value = false
  if (regions.length) startProcess({ mode: 'manual', regions })
}

const previewResult = () => {
  uni.previewImage({ urls: [processedOriginal.value, resultImage.value], current: showOriginal.value ? 0 : 1 })
}

const saveResult = () => {
  if (!resultImage.value || saving.value) return
  saving.value = true
  uni.downloadFile({
    url: resultImage.value,
    success: (response) => {
      if (response.statusCode !== 200) {
        saving.value = false
        uni.showToast({ title: '下载失败，请重试', icon: 'none' })
        return
      }
      uni.saveImageToPhotosAlbum({
        filePath: response.tempFilePath,
        success: () => uni.showToast({ title: '已保存到相册' }),
        fail: () => uni.showModal({ title: '未能保存', content: '请检查相册权限后重试。', showCancel: false }),
        complete: () => { saving.value = false },
      })
    },
    fail: () => {
      saving.value = false
      uni.showToast({ title: '下载失败，请重试', icon: 'none' })
    },
  })
}

onUnload(() => {
  disposed = true
  if (timer) clearTimeout(timer)
})
</script>

<style lang="scss" scoped>
.watermark-page {
  .service-notice {
    overflow: hidden;
    border-radius: 16rpx;
  }
  min-height: 100vh;
  padding: 32rpx 24rpx;
  box-sizing: border-box;
  background: var(--dragon-page);
}
.intro {
  margin-bottom: 24rpx;
  color: var(--dragon-muted);
  font-size: 28rpx;
}
.image-panel, .result-panel {
  padding: 24rpx;
  border-radius: 20rpx;
  background: var(--dragon-surface);
}
.preview {
  display: block;
  width: 100%;
  height: 520rpx;
}
.empty {
  height: 360rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--dragon-muted);
}
button {
  margin-top: 24rpx;
  font-size: 30rpx;
}
.primary {
  background: var(--dragon-primary);
  color: white;
}
.primary[disabled] {
  background: var(--dragon-border);
  color: white;
}
.choose {
  background: var(--dragon-surface);
  color: var(--dragon-accent);
}
.process-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 24rpx;
}
.process-actions button {
  flex: 1;
  min-width: 0;
  padding: 0 12rpx;
  margin: 0;
  font-size: 28rpx;
}
.manual-button {
  background: var(--dragon-raised);
  color: var(--dragon-accent);
}
.manual-button[disabled] {
  background: var(--dragon-border);
  color: #a1adbf;
}
.message {
  display: block;
  margin: 24rpx 0;
  color: var(--dragon-muted);
  font-size: 26rpx;
}
.error {
  color: var(--dragon-danger);
}
.result-panel {
  margin-top: 32rpx;
}
.result-title {
  font-weight: bold;
}
.tabs {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}
.tabs button {
  flex: 1;
  font-size: 26rpx;
}
.tabs .active {
  color: var(--dragon-accent);
  background: var(--dragon-raised);
}
.hint {
  display: block;
  font-size: 24rpx;
  color: var(--dragon-muted);
  margin-top: 20rpx;
}
</style>
