import { Clock } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Badge, type BadgeProps } from '../ui/badge'

interface ReadTimeProps extends BadgeProps {
  time: number
  iconSize?: number

  messages: {
    min_read: string
  }
}

export function ReadTime({ time, messages, className, iconSize = 10, ...props }: ReadTimeProps) {
  if (!time) {
    return null
  }

  return (
    <Badge variant="secondary" className={cn('gap-1 min-w-fit', className)} {...props}>
      <Clock size={iconSize} className="max-h-full" /> {time} {messages.min_read}
    </Badge>
  )
}
