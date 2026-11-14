export type WatermarkJobStatus = 'queued' | 'processing' | 'completed' | 'no_watermark' | 'failed'

export interface WatermarkJob {
  id: string
  status: WatermarkJobStatus
  regions?: number
  skippedRegions?: number
  unverifiedRegions?: number
  message?: string
  resized?: boolean
}

export type WatermarkPollTimer = ReturnType<typeof setTimeout> | undefined
