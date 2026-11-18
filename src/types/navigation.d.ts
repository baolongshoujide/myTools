export interface MainSwiperEvent {
  detail: {
    current: number
    source?: string
  }
}

export type ListMode = 'wheel' | 'clicker'
