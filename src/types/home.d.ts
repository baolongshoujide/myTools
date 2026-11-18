import type { ListMode } from './navigation'

export interface Tool {
  title: string
  description: string
  tone: string
  color: 'accent' | 'green' | 'purple'
  icon: string
  destination: { list: ListMode } | { url: string }
}

export interface ToolCardProps {
  tone?: string
}

export interface ToolCardEmits {
  (event: 'tap'): void
}
