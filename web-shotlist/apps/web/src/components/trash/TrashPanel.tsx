/**
 * 回收站面板（次要入口：顶栏右侧 🕘 按钮）
 * 列表 + 恢复 + 永久删除（确认）
 */
import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { TrashItem } from '@shotlist/shared'
import { api } from '@/lib/api'
import { ConfirmDialog, Dialog } from '@/components/ui/dialog'

export function TrashPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const [purgeTarget, setPurgeTarget] = useState<TrashItem | null>(null)

  const { data: items = [] } = useQuery({ queryKey: ['trash'], queryFn: api.listTrash, enabled: open })

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ['trash'] })
    qc.invalidateQueries({ queryKey: ['projects'] })
  }

  const restoreMut = useMutation({
    mutationFn: (id: string) => api.restoreProject(id),
    onSuccess: refresh,
  })

  const purgeMut = useMutation({
    mutationFn: (id: string) => api.purgeProject(id),
    onSuccess: () => {
      setPurgeTarget(null)
      refresh()
    },
  })

  return (
    <>
      <Dialog open={open} onClose={onClose} title={`回收站（${items.length}）`} className="max-w-md">
        <p className="mb-3 text-[11px] text-slate-500">已删除的项目（剧本+拍摄本+提示词）。可恢复或永久删除。</p>
        {items.length === 0 ? (
          <p className="py-6 text-center text-xs text-slate-600">回收站为空</p>
        ) : (
          <ul className="max-h-72 space-y-1.5 overflow-y-auto">
            {items.map((it) => (
              <li key={it.id} className="flex items-center justify-between rounded border border-slate-800 bg-slate-950 px-2.5 py-2">
                <div className="min-w-0">
                  <p className="truncate text-xs text-slate-200">{it.name}</p>
                  <p className="text-[10px] text-slate-500">{it.trashedAt.slice(0, 19).replace('T', ' ')}</p>
                </div>
                <div className="flex shrink-0 gap-1.5">
                  <button
                    onClick={() => restoreMut.mutate(it.id)}
                    disabled={restoreMut.isPending}
                    className="rounded border border-slate-700 px-2 py-0.5 text-[11px] text-slate-300 hover:bg-slate-800"
                  >
                    恢复
                  </button>
                  <button
                    onClick={() => setPurgeTarget(it)}
                    className="rounded border border-red-900 px-2 py-0.5 text-[11px] text-red-400 hover:bg-red-950"
                  >
                    永久删除
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Dialog>
      <ConfirmDialog
        open={!!purgeTarget}
        onClose={() => setPurgeTarget(null)}
        onConfirm={() => purgeTarget && purgeMut.mutate(purgeTarget.id)}
        title="永久删除项目"
        message={`「${purgeTarget?.name}」将被彻底删除（剧本/拍摄本/提示词），此操作不可恢复。`}
        confirmLabel="永久删除"
        danger
      />
    </>
  )
}
