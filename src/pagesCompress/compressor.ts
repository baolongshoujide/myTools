import type { CompressResult, ImageEncoder } from '@/types/compress'

export const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 先降低编码质量；仍不满足目标时等比缩小尺寸，再重新搜索质量。
export const compressToTarget = async (
  width: number,
  height: number,
  targetBytes: number,
  encode: ImageEncoder,
): Promise<CompressResult> => {
  if (!Number.isFinite(targetBytes) || targetBytes <= 0) throw new Error('请输入有效的目标体积')
  for (let round = 0; round < 10; round++) {
    const bestQuality = await encode(width, height, 1)
    if (bestQuality.size <= targetBytes) return bestQuality
    let low = 0.12
    let high = 1
    let best = await encode(width, height, low)
    if (best.size <= targetBytes) {
      for (let attempt = 0; attempt < 9 && best.size < targetBytes * 0.995; attempt++) {
        const quality = (low + high) / 2
        const candidate = await encode(width, height, quality)
        if (candidate.size <= targetBytes) {
          low = quality
          if (candidate.size > best.size) best = candidate
        } else {
          high = quality
        }
      }
      return best
    }
    const scale = Math.min(0.98, Math.max(0.25, Math.sqrt(targetBytes / best.size) * 0.98))
    const nextWidth = Math.max(1, Math.floor(width * scale))
    const nextHeight = Math.max(1, Math.floor(height * scale))
    if (Math.min(nextWidth, nextHeight) < 32) break
    width = nextWidth
    height = nextHeight
  }
  throw new Error('目标体积过小，请提高目标大小或保留比例')
}
