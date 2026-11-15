export type WatermarkJobStatus = 'queued' | 'processing' | 'completed' | 'no_watermark' | 'failed'

export interface WatermarkJob {
  mode?: WatermarkMode
  id: string
  status: WatermarkJobStatus
  regions?: number
  skippedRegions?: number
  unverifiedRegions?: number
  message?: string
  resized?: boolean
}

export type WatermarkPollTimer = ReturnType<typeof setTimeout> | undefined

export type WatermarkMode = 'auto' | 'manual'

// Coordinates are relative to the displayed image, excluding aspectFit margins.
export interface WatermarkRegion {
  x: number
  y: number
  width: number
  height: number
}

export interface WatermarkSubmitOptions {
  mode: WatermarkMode
  regions?: WatermarkRegion[]
}

export interface WatermarkHealth {
  manualSelection?: boolean
}

export interface SelectionSize {
  width: number
  height: number
}

export interface SelectionPoint {
  x: number
  y: number
}

export interface SelectionFrame extends SelectionSize {
  left: number
  top: number
}

export interface SelectionTouchPoint {
  clientX?: number
  clientY?: number
  pageX?: number
  pageY?: number
}

export interface SelectionTouchEvent {
  touches?: SelectionTouchPoint[]
  changedTouches?: SelectionTouchPoint[]
}

export interface RegionSelectorProps {
  image: string
}

export interface RegionSelectorEmits {
  (event: 'confirm', regions: WatermarkRegion[]): void
  (event: 'cancel'): void
}
