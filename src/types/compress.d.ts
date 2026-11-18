export type CompressMode = 'ratio' | 'target'
export type ImageMode = CompressMode | 'format'
export type ImageFormat = 'jpg' | 'png'

export interface CompressVideoFile {
  path: string
  size: number
}

export interface CompressImageFile {
  path: string
  size: number
  width: number
  height: number
}

export interface CompressResult extends CompressImageFile {
  quality: number
  format: ImageFormat
}

export type ImageEncoder = (width: number, height: number, quality: number) => Promise<CompressResult>

export interface CompressSliderEvent {
  detail: { value: number }
}
