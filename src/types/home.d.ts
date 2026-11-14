export interface Tool {
  title: string
  description: string
  tone: string
  color: string
  icon: string
  path?: string
}

export interface ToolCardProps {
  tone?: string
}

export interface ToolCardEmits {
  (event: 'tap'): void
}
