/** 新建项目对话框（+ 入口；空名默认"未命名剧本"，重复名自动加数字） */
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { scriptTemplate } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Dialog } from '@/components/ui/dialog'

export function NewProjectDialog({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: (id: string) => void }) {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const setScriptDraft = useAppStore((s) => s.setScriptDraft)

  const createMut = useMutation({
    mutationFn: () => api.createProject({ name: name.trim() }),
    onSuccess: (p) => {
      setScriptDraft(scriptTemplate(p.meta.name))
      setName('')
      onClose()
      onCreated(p.meta.id)
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
    onError: (e) => useAppStore.getState().setError((e as Error).message),
  })

  return (
    <Dialog open={open} onClose={onClose} title="新建项目">
      <p className="mb-3 text-[11px] text-slate-500">输入项目名（可留空，默认"未命名剧本"；重名自动加数字）</p>
      <input
        autoFocus
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && createMut.mutate()}
        placeholder="未命名剧本"
        className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
      />
      <div className="mt-4 flex justify-end gap-2">
        <button onClick={onClose} className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          取消
        </button>
        <button
          onClick={() => createMut.mutate()}
          disabled={createMut.isPending}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500"
        >
          创建
        </button>
      </div>
    </Dialog>
  )
}
