/**
 * 工具 A0 创作页：输入几句话 → 可选长度的世界观手册 + 剧本 YAML
 * 产出可应用到新项目（进入看板继续 生成拍摄本 → 提示词）
 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { type DraftLength } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const LENGTHS: Array<{ value: DraftLength; label: string; hint: string }> = [
  { value: 'short', label: '短', hint: '8s · 1 场景 · 1-2 角色' },
  { value: 'medium', label: '中', hint: '12s · 2 场景 · 2-3 角色' },
  { value: 'long', label: '长', hint: '20s · 3-4 场景 · 3+ 角色' },
]

export function A0View({ onApply }: { onApply: (script: string, name: string) => void }) {
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
    onApply(script, title || idea.trim().slice(0, 12) || '新剧本')
  }

  return (
    <div className="flex h-full min-w-0 flex-col gap-3 p-4">
      <div className="shrink-0">
        <h2 className="text-sm font-semibold text-slate-100">创作（工具 A0）</h2>
        <p className="text-[11px] text-slate-500">输入几句点子，自动扩展为可选长度的世界观手册和剧本，可应用到新项目继续制作</p>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-2 gap-3">
        {/* 输入 */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-300">点子</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder={'例如：黄昏海边的银发少女，与好友约定暑假后在天台见面。轻快的青春日常氛围。'}
              rows={5}
              className="w-full text-xs"
            />
            <div className="flex items-center gap-2">
              {LENGTHS.map((l) => (
                <button
                  key={l.value}
                  onClick={() => setLength(l.value)}
                  title={l.hint}
                  className={cn(
                    'rounded px-2.5 py-1 text-xs transition-colors',
                    length === l.value ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700',
                  )}
                >
                  {l.label}
                  <span className="ml-1 text-[10px] opacity-70">{l.hint}</span>
                </button>
              ))}
            </div>
            <label className="flex cursor-pointer items-center gap-2 text-xs text-slate-400">
              <input type="checkbox" checked={withWorldview} onChange={(e) => setWithWorldview(e.target.checked)} className="h-3.5 w-3.5 accent-blue-600" />
              同时生成世界观手册（不勾则只出剧本）
            </label>
            <Button onClick={() => genMut.mutate()} loading={genMut.isPending} disabled={!idea.trim()}>
              生成
            </Button>
          </CardContent>
        </Card>

        {/* 结果 */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-300">结果</CardTitle>
          </CardHeader>
          <CardContent className="flex min-h-0 flex-1 flex-col gap-2">
            {worldview && (
              <div className="rounded border border-emerald-900/60 bg-emerald-950/30 p-2">
                <p className="mb-1 text-[10px] font-medium uppercase tracking-wide text-emerald-500">世界观手册</p>
                <textarea value={worldview} onChange={(e) => setWorldview(e.target.value)} rows={4} className="w-full text-xs" />
              </div>
            )}
            {script && (
              <div className="flex min-h-0 flex-1 flex-col">
                <p className="mb-1 text-[10px] font-medium uppercase tracking-wide text-blue-500">剧本 YAML（可编辑）</p>
                <textarea value={script} onChange={(e) => setScript(e.target.value)} rows={12} className="w-full min-h-0 flex-1 font-mono text-[11px]" />
              </div>
            )}
            {script && (
              <Button onClick={apply} variant="secondary">
                应用到新项目 →
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
