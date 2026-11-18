<template>
  <view class="video-page" :style="theme.pageStyle">
    <view class="card">
      <video v-if="source && !result" class="preview" :src="source.path" />
      <text v-if="source" class="meta">原视频 · {{ formatSize(source.size) }}</text>
      <button class="secondary" :disabled="busy || saving" @tap="chooseVideo">{{ source ? '更换视频' : '从相册选择视频' }}</button>
    </view>

    <view class="tabs">
      <button class="tab" :class="{ active: mode === 'ratio' }" :disabled="busy || saving" @tap="selectMode('ratio')">按比例</button>
      <button class="tab" :class="{ active: mode === 'target' }" :disabled="busy || saving" @tap="selectMode('target')">目标体积</button>
    </view>

    <view class="card">
      <view v-if="mode === 'ratio'">
        <text>缩小到原体积的 {{ ratio }}%</text>
        <slider :value="ratio" :min="10" :max="95" :step="5" :disabled="busy || saving" :activeColor="theme.colors.accent" @change="changeRatio" />
      </view>
      <view v-else class="size-row">
        <input v-model="targetMb" class="size-input" type="digit" placeholder="输入目标大小" :disabled="busy || saving" />
        <text>MB</text>
      </view>
      <text class="meta">视频在本机处理。若无法达到目标，会显示实际大小。</text>
    </view>

    <button class="primary" :disabled="!source || busy || saving" :loading="busy" @tap="startCompress">开始压缩</button>
    <text v-if="message" class="message">{{ message }}</text>

    <view v-if="result" class="card result">
      <video class="preview" :src="result.path" />
      <text class="meta">压缩后 {{ formatSize(result.size) }} · 减少 {{ reduction }}%</text>
      <button class="primary" :disabled="saving || busy" :loading="saving" @tap="saveVideo">保存到相册</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onUnload } from '@dcloudio/uni-app'
import { formatSize } from './compressor'
import type { CompressMode, CompressSliderEvent, CompressVideoFile } from '@/types/compress'
import { usePageTheme } from '@/composables/usePageTheme'

const theme = usePageTheme()

const source = ref<CompressVideoFile | null>(null)
const result = ref<CompressVideoFile | null>(null)
const mode = ref<CompressMode>('ratio')
const ratio = ref(50)
const targetMb = ref('')
const busy = ref(false)
const saving = ref(false)
const message = ref('')
const megabyte = 1024 * 1024
const qualities = ['high', 'medium', 'low'] as const
let disposed = false

const reduction = computed(() => {
  if (!source.value || !result.value) return '0'
  return ((1 - result.value.size / source.value.size) * 100).toFixed(1)
})

const selectMode = (value: CompressMode) => { mode.value = value }
const changeRatio = (event: Event | CompressSliderEvent) => {
  ratio.value = (event as CompressSliderEvent).detail.value
}

const chooseVideo = () => {
  if (busy.value || saving.value) return
  uni.chooseVideo({
    sourceType: ['album'],
    compressed: false,
    success: (video) => {
      if (disposed) return
      if (!video.tempFilePath || !Number.isFinite(video.size) || video.size <= 0) {
        message.value = '无法读取视频，请重新选择。'
        return
      }
      source.value = { path: video.tempFilePath, size: video.size }
      result.value = null
      message.value = ''
    },
  })
}

const compressVideo = (path: string, quality: UniNamespace.CompressVideoOptions['quality']) => {
  return new Promise<CompressVideoFile>((resolve, reject) => {
    uni.compressVideo({
      src: path,
      quality,
      success: ({ tempFilePath }) => {
        // 读取输出文件的实际字节数，统一与原视频及目标大小比较。
        uni.getFileInfo({
          filePath: tempFilePath,
          success: ({ size }) => {
            if (size > 0) resolve({ path: tempFilePath, size })
            else reject(new Error('压缩结果为空'))
          },
          fail: reject,
        })
      },
      fail: reject,
    })
  })
}

const startCompress = async () => {
  const original = source.value
  if (!original || busy.value || saving.value) return
  result.value = null
  if (typeof uni.compressVideo !== 'function') {
    message.value = '当前平台不支持压缩视频，请在手机微信小程序中使用。'
    return
  }
  const targetBytes = Math.floor(mode.value === 'ratio'
    ? original.size * ratio.value / 100
    : Number(targetMb.value) * megabyte)
  if (!Number.isFinite(targetBytes) || targetBytes <= 0) {
    message.value = '请输入有效的目标体积。'
    return
  }
  if (original.size <= targetBytes) {
    message.value = '原视频已经符合目标体积，可直接使用原视频。'
    return
  }

  busy.value = true
  message.value = '正在本机压缩视频，请稍候…'
  let best: CompressVideoFile | null = null
  try {
    for (const quality of qualities) {
      let candidate: CompressVideoFile
      try {
        candidate = await compressVideo(original.path, quality)
      } catch {
        if (disposed) return
        continue
      }
      if (disposed) return
      if (!best || candidate.size < best.size) best = candidate
      if (candidate.size <= targetBytes) break
    }

    if (!best) {
      message.value = '视频压缩失败，请尝试换一段视频，或使用手机微信重试。'
    } else if (best.size >= original.size) {
      message.value = '未能缩小这个视频，建议使用原视频。'
    } else {
      result.value = best
      message.value = best.size <= targetBytes
        ? '已达到目标体积，可以预览并保存。'
        : '未达到目标体积，已保留本次最小的结果。'
    }
  } finally {
    busy.value = false
  }
}

const saveVideo = () => {
  if (!result.value || saving.value || busy.value) return
  saving.value = true
  uni.saveVideoToPhotosAlbum({
    filePath: result.value.path,
    success: () => uni.showToast({ title: '已保存到相册' }),
    fail: () => { message.value = '保存失败，请检查相册权限后重试。' },
    complete: () => { saving.value = false },
  })
}

onUnload(() => { disposed = true })
</script>

<style lang="scss" scoped>
.video-page {
  min-height: 100vh;
  padding: 32rpx 24rpx 64rpx;
  box-sizing: border-box;
  background: var(--dragon-page);
  color: var(--dragon-text);

  .card {
    padding: 28rpx;
    border-radius: 24rpx;
    background: var(--dragon-surface);

    .preview {
      display: block;
      width: 100%;
      height: 360rpx;
      border-radius: 16rpx;
    }
  }

  .tabs {
    display: flex;
    gap: 16rpx;
    margin: 24rpx 0;

    .tab {
      flex: 1;
      margin: 0;
      background: var(--dragon-base);
      color: var(--dragon-muted);
      font-size: 27rpx;

      &.active {
        background: var(--dragon-surface);
        color: var(--dragon-accent);
        font-weight: 600;
      }
    }
  }

  .size-row {
    display: flex;
    align-items: center;
    gap: 16rpx;

    .size-input {
      flex: 1;
      padding: 16rpx;
      border-radius: 14rpx;
      background: var(--dragon-raised);
    }
  }

  .meta,
  .message {
    display: block;
    margin-top: 16rpx;
    color: var(--dragon-muted);
    font-size: 25rpx;
    line-height: 1.6;
  }

  .primary,
  .secondary {
    margin-top: 24rpx;
    border-radius: 20rpx;
    font-size: 28rpx;
  }

  .primary {
    background: var(--dragon-primary);
    color: #fff;
  }

  .secondary {
    background: var(--dragon-raised);
    color: var(--dragon-accent);
  }

  .result {
    margin-top: 24rpx;
  }
}
</style>
