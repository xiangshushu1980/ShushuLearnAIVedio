/** 项目级小弹层：重命名 / 导入（JSON 包） */
import { useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ProjectExport } from '@shotlist/shared'
import { api } from '@/lib/api'
import { Dialog } from '@/components/ui/dialog'

/** 重命名项目（仅改显示名，id/目录不变） */
export function RenameDialog({
  open,
  onClose,
  projectId,
  currentName,
  onRenamed,
}: {
  open: boolean
  onClose: () => void
  projectId: string
  currentName: string
  onRenamed: () => void
}) {
  const [name, setName] = useState(currentName)
  const [error, setError] = useState<string | null>(null)
  const mut = useMutation({
    mutationFn: () => api.renameProject(projectId, name),
    onSuccess: () => {
      onRenamed()
      onClose()
    },
    onError: (e) => setError((e as Error).message),
  })
  return (
    <Dialog open={open} onClose={onClose} title="重命名项目">
      <input
        autoFocus
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && name.trim()) mut.mutate()
        }}
        className="w-full rounded border border-slate-700 bg-slate-950 px-2.5 py-1.5 text-sm text-slate-200 outline-none focus:border-blue-500"
        placeholder="项目名称"
      />
      {error && <p className="mt-2 text-xs text-red-400">{error}</p>}
      <p className="mt-2 text-[11px] text-slate-500">仅修改显示名称；项目 id 与目录名不变，引用关系安全。</p>
      <div className="mt-4 flex justify-end gap-2">
        <button onClick={onClose} className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          取消
        </button>
        <button
          disabled={!name.trim() || mut.isPending}
          onClick={() => mut.mutate()}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {mut.isPending ? '保存中…' : '重命名'}
        </button>
      </div>
    </Dialog>
  )
}

/** 导入项目（上传 JSON 包 → 新建项目并打开） */
export function ImportDialog({
  open,
  onClose,
  onImported,
}: {
  open: boolean
  onClose: () => void
  onImported: (id: string) => void
}) {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const handleFile = async (f: File | undefined) => {
    if (!f) return
    setBusy(true)
    setError(null)
    try {
      const text = await f.text()
      const pack = JSON.parse(text) as ProjectExport
      if (pack.format !== 'shotlist-project') throw new Error('不是拍摄本项目包（缺少 format: shotlist-project）')
      const p = await api.importProject(pack)
      qc.invalidateQueries({ queryKey: ['projects'] })
      onImported(p.meta.id)
      onClose()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title="导入项目">
      <p className="text-sm text-slate-300">选择导出的项目 JSON 包（.shotlist.json），将新建同名项目并打开。</p>
      <input
        ref={fileRef}
        type="file"
        accept=".json,.shotlist.json"
        className="mt-3 block w-full text-xs text-slate-400 file:mr-3 file:rounded file:border-0 file:bg-slate-800 file:px-3 file:py-1.5 file:text-xs file:text-slate-200"
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />
      {busy && <p className="mt-2 text-xs text-slate-400">导入中…</p>}
      {error && <p className="mt-2 text-xs text-red-400">{error}</p>}
      <p className="mt-2 text-[11px] text-slate-500">提示：实体是全局注册表（data/entities），包内仅记录引用 id；换环境需同步实体库。</p>
      <div className="mt-4 flex justify-end">
        <button onClick={onClose} className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          关闭
        </button>
      </div>
    </Dialog>
  )
}
