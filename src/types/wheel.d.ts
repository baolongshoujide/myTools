export interface Wheel {
  id: string
  name: string
  spinTime: number
  prizes: string[]
}

export type WheelDraft = Omit<Wheel, 'id'>

export interface WheelEmits {
  (event: 'interaction-lock', locked: boolean): void
}

export interface WheelPressEvent {
  touches?: { clientX: number; clientY: number }[]
  changedTouches?: { clientX: number; clientY: number }[]
}

export type WheelAnimationTimer = ReturnType<typeof setTimeout> | null

export type WheelInputValue = string | number

export interface WheelInputProps {
  modelValue?: WheelInputValue | null
  placeholderStyle?: string
}

export interface WheelInputEmits {
  (event: 'update:modelValue', value: WheelInputValue): void
}
