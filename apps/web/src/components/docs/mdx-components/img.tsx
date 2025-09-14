import { cn } from '@/lib/utils'

export const img = ({
  alt,
  className,
  ...props
}: React.ImgHTMLAttributes<HTMLImageElement>) => (
  <img className={cn('rounded-md', className)} alt={alt} {...props} />
)
