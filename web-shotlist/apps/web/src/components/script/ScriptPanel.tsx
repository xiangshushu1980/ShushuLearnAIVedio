/**
 * ① 剧本区（页 0）：参数头表单 + 正文 textarea + AI 创作 + 保存状态
 * 双向绑定：表单修改 → 重写参数头文本；文本修改（防抖）→ 解析回填表单
 */
import { useEffect, useRef, useState } from 'react'
import { parseScript, serializeScript, type ScriptHead } from '@shotlist/shared'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScriptHeadForm } from './ScriptHeadForm'
import { A0Dialog } from '@/components/a0/A0Dialog'

interface Props {
  onGenerate: () => void
}

export function ScriptPanel({ onGenerate }: Props) {
  const scriptDraft = useAppStore((s) => s.scriptDraft)
  const setScriptDraft = useAppStore((s) => s.setScriptDraft)
  const saveState = useAppStore((s) => s.saveState)
  const busy = useAppStore((s) => s.busy)
  const [head, setHead] = useState<ScriptHead | null>(null)
  const [headErr, setHeadErr] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(true)
  const [a0Open, setA0Open] = useState(false)
  const draftRef = useRef(scriptDraft)
  draftRef.current = scriptDraft

  // 文本 → 表单（防抖 500ms 解析；解析失败显示错误条但不覆盖文本）
  useEffect(() => {
    if (!scriptDraft.trim()) {
      setHead(null)
      setHeadErr(null)
      return
    }
    const t = setTimeout(() => {
      const { script, errs } = parseScript(scriptDraft)
      if (script) {
        setHead(script.head)
        setHeadErr(null)
      } else if (errs.length) {
        setHeadErr(errs[0])
      }
    }, 500)
    return () => clearTimeout(t)
  }, [scriptDraft])

  // 表单 → 文本（立即重写参数头，保留正文与未知字段）
  const patchHead = (patch: Partial<ScriptHead>) => {
    setHead((prev) => {
      const next = { ...(prev ?? {}), ...patch } as ScriptHead
      const raw = draftRef.current
      if (raw.trim()) setScriptDraft(serializeScript(raw, next))
      return next
    })
  }

  const saveLabel =
    saveState === 'saving' ? '保存中…' : saveState === 'dirty' ? '未保存' : '已保存'

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="border-b border-slate-800 pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">① 剧本</CardTitle>
          <div className="flex items-center gap-2">
            <span
              className={
                saveState === 'saved'
                  ? 'text-[10px] text-emerald-500'
                  : 'text-[10px] text-amber-500'
              }
            >
              {saveLabel}
            </span>
            <Button size="sm" variant="outline" onClick={() => setA0Open(true)}>
              AI 创作
            </Button>
            <button
              onClick={() => setFormOpen((v) => !v)}
              className="rounded px-1.5 py-0.5 text-[11px] text-slate-400 hover:bg-slate-800"
              title="参数头表单（模板字段选择）"
            >
              {formOpen ? '▾ 参数头' : '▸ 参数头'}
            </button>
          </div>
        </div>
        <p className="text-[11px] text-slate-500">参数表单点选 / 正文直接改文字（自动保存）；AI 创作生成剧本</p>
      </CardHeader>
      <CardContent className="flex min-h-0 flex-1 flex-col gap-2 p-3">
        {formOpen && <ScriptHeadForm head={head} headErr={headErr} onPatch={patchHead} />}
        <textarea
          value={scriptDraft}
          onChange={(e) => setScriptDraft(e.target.value)}
          spellCheck={false}
          className="min-h-0 flex-1 resize-none rounded border border-slate-700 bg-slate-950 p-2 font-mono text-[12px] leading-relaxed text-slate-200 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
        />
        <Button onClick={onGenerate} loading={busy === 'shotlist'} disabled={!scriptDraft.trim()}>
          生成拍摄本 →
        </Button>
        <A0Dialog open={a0Open} onClose={() => setA0Open(false)} />
      </CardContent>
    </Card>
  )
}
