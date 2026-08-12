/**
 * AI 创作弹层（工具 A0，页 1 入口）：点子 → 长度档 → 世界观+剧本 → 填入剧本区
 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import type { DraftLength } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'

const LENGTHS: Array<{ value: DraftLength; label: string; hint: string }> = [
  { value: 'short', label: '短', hint: '8s' },
  { value: 'medium', label: '中', hint: '12s' },
  { value: 'long', label: '长', hint: '20s' },
]

export function A0Dialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [idea, setIdea] = useState('')
  const [length, setLength] = useState<DraftLength>('medium')
  const [withWorldview, setWithWorldview] = useState(true)
  const [worldview, setWorldview] = useState('')
  const [script, setScript] = useState('')
  const setError = useAppStore((s) => s.setError)

  const genMut = useMutation({
    mutationFn: () => api.genDraft({ idea: idea.trim(), length, withWorldview }),
    onSuccess: (r) => {
      setWorldview(r.worldview)
      setScript(r.script)
    },
    onError: (e) => setError((e as Error).message),
  })

  const apply = () => {
    const m = /^title:\s*(.+)$/m.exec(script)
    const title = (m?.[1] ?? '').trim()
    const full = `${withWorldview && worldview ? `===== 世界观 =====\n${worldview}\n\n` : ''}${script}`
    useAppStore.getState().setScriptDraft(full)
    onClose()
    void title
  }

  return (
    <Dialog open={open} onClose={onClose} title="AI 创作（点子 → 剧本）" className="max-w-xl">
      <p className="mb-2 text-[11px] text-slate-500">输入几句点子，扩展为可选长度的世界观手册和剧本 YAML，确认后填入剧本区。</p>
      <textarea
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        placeholder={'例如：黄昏海边的银发少女，与好友约定暑假后在天台见面。轻快的青春日常氛围。'}
        rows={3}
        className="mb-2 w-full text-xs"
      />
      <div className="mb-2 flex items-center gap-2">
        {LENGTHS.map((l) => (
          <button
            key={l.value}
            onClick={() => setLength(l.value)}
            className={cn(
              'rounded px-2 py-1 text-xs transition-colors',
              length === l.value ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700',
            )}
          >
            {l.label} <span className="text-[10px] opacity-70">{l.hint}</span>
          </button>
        ))}
        <label className="ml-auto flex cursor-pointer items-center gap-1.5 text-[11px] text-slate-400">
          <input type="checkbox" checked={withWorldview} onChange={(e) => setWithWorldview(e.target.checked)} className="h-3.5 w-3.5 accent-blue-600" />
          世界观
        </label>
      </div>
      <Button onClick={() => genMut.mutate()} loading={genMut.isPending} disabled={!idea.trim()} size="sm" className="mb-2">
        生成
      </Button>
      {worldview && (
        <textarea value={worldview} onChange={(e) => setWorldview(e.target.value)} rows={3} className="mb-2 w-full text-xs" placeholder="世界观手册（可编辑）" />
      )}
      {script && <textarea value={script} onChange={(e) => setScript(e.target.value)} rows={8} className="mb-2 w-full font-mono text-[11px]" placeholder="剧本 YAML（可编辑）" />}
      <div className="flex justify-end gap-2">
        <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          取消
        </button>
        <Button onClick={apply} disabled={!script} size="sm">
          填入剧本区 →
        </Button>
      </div>
    </Dialog>
  )
}
