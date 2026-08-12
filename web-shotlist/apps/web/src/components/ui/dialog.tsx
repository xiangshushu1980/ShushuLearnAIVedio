import { type ReactNode } from 'react'
import { cn } from '@/lib/utils'

/** 简单弹层（无动画依赖；遮罩点击关闭） */
export function Dialog({
  open,
  onClose,
  title,
  children,
  className,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  className?: string
}) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-label={title}>
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className={cn('relative z-10 w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 shadow-2xl', className)}>
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2.5">
          <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
          <button onClick={onClose} className="rounded px-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200">
            ✕
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  )
}

/** 确认对话框 */
export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = '确认',
  danger = false,
}: {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
}) {
  return (
    <Dialog open={open} onClose={onClose} title={title}>
      <p className="text-sm leading-relaxed text-slate-300">{message}</p>
      <div className="mt-4 flex justify-end gap-2">
        <button onClick={onClose} className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          取消
        </button>
        <button
          onClick={() => {
            onConfirm()
            onClose()
          }}
          className={
            danger
              ? 'rounded-md bg-red-600 px-3 py-1.5 text-xs text-white hover:bg-red-500'
              : 'rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500'
          }
        >
          {confirmLabel}
        </button>
      </div>
    </Dialog>
  )
}
