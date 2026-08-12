import { cva, type VariantProps } from 'class-variance-authority'
import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-blue-600 text-white',
        secondary: 'border-slate-700 bg-slate-800 text-slate-200',
        outline: 'border-slate-600 text-slate-300',
        success: 'border-transparent bg-emerald-600 text-white',
        warning: 'border-transparent bg-amber-600 text-white',
        destructive: 'border-transparent bg-red-600 text-white',
        muted: 'border-slate-600 bg-slate-800/60 text-slate-400',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />
}
