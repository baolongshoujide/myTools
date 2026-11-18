export interface ClickerPlan {
  id: string
  name: string
  action: 'tap' | 'swipe'
  interval: number
  count: number
  swipeDuration: number
  x?: number
  y?: number
  endX?: number
  endY?: number
  points?: ClickerLocation[]
}

export interface ClickerLocation {
  action?: ClickerPlan['action']
  duration?: number
  x: number
  y: number
  endX: number
  endY: number
}
