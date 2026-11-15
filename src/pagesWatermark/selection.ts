import type { SelectionFrame, SelectionPoint, SelectionSize, WatermarkRegion } from '@/types/watermark'

export const fitImageFrame = (stage: SelectionSize, image: SelectionSize): SelectionFrame => {
  if (stage.width <= 0 || stage.height <= 0 || image.width <= 0 || image.height <= 0) {
    return { left: 0, top: 0, width: 0, height: 0 }
  }
  const scale = Math.min(stage.width / image.width, stage.height / image.height)
  const width = image.width * scale
  const height = image.height * scale
  return { left: (stage.width - width) / 2, top: (stage.height - height) / 2, width, height }
}

export const clampImagePoint = (point: SelectionPoint, size: SelectionSize): SelectionPoint => {
  return {
    x: Math.max(0, Math.min(size.width, point.x)),
    y: Math.max(0, Math.min(size.height, point.y)),
  }
}

export const normalizedRegion = (start: SelectionPoint, end: SelectionPoint, size: SelectionSize): WatermarkRegion => {
  return {
    x: Math.min(start.x, end.x) / size.width,
    y: Math.min(start.y, end.y) / size.height,
    width: Math.abs(end.x - start.x) / size.width,
    height: Math.abs(end.y - start.y) / size.height,
  }
}
