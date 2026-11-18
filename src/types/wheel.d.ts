export interface Wheel {
  id: string
  name: string
  spinTime: number
  prizes: string[]
}

export type WheelDraft = Omit<Wheel, 'id'>

export interface DeletedWheel extends Wheel {
  deletedAt: number
}

export interface WheelPopupInstance {
  open: () => void
  close: () => void
}

export interface WheelFormInstance {
  validate: () => Promise<unknown>
  clearValidate: () => void
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
export type Settings = {
  dong: boolean
  noRepeat: boolean
  showModal: boolean
}
