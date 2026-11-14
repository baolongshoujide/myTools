export interface Wheel {
  id: string
  name: string
  spinTime: number
  prizes: string[]
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
