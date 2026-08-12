/**
 * AI 实体抽取弹层（页 0 实体区）：剧本 + 世界观 → 实体卡（保存为文件）
 */
import { useState } from 'react'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'

export function ExtractDialog({ onClose }: { onClose: () => void }) {
  const scriptDraft = useAppStore((s) => s.scriptDraft)
  const [scriptText, setScriptText] = useState('')
  const [worldview, setWorldview] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const sourceScript = scriptDraft || scriptText

  const run = async () => {
    setBusy(true)
    try {
      const r = await api.extractEntities({ worldview, script: sourceScript })
      setResult(`已生成 ${r.entities.length} 个实体并保存为文件：${r.entities.map((e) => e.name).join('、')}`)
    } catch (e) {
      useAppStore.getState().setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open onClose={onClose} title="AI 抽取实体卡">
      <p className="mb-2 text-[11px] leading-relaxed text-slate-500">
        实体必须从剧本 + 世界观中获得。基于剧本{scriptDraft ? '（已自动代入当前项目剧本）' : ''}与世界观文本分析，生成实体卡并保存为文件（data/entities/*.md）。
      </p>
      {!scriptDraft && (
        <>
          <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">剧本文本（必填）</label>
          <textarea
            value={scriptText}
            onChange={(e) => setScriptText(e.target.value)}
            placeholder="粘贴剧本…（也可先新建/选择项目，自动代入）"
            rows={4}
            className="mb-2 w-full text-xs"
          />
        </>
      )}
      <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">世界观手册（建议填写）</label>
      <textarea
        value={worldview}
        onChange={(e) => setWorldview(e.target.value)}
        placeholder="粘贴世界观手册…（留空则仅按剧本推断）"
        rows={4}
        className="mb-3 w-full text-xs"
      />
      {result && <p className="mb-3 rounded border border-emerald-900 bg-emerald-950/40 px-2 py-1.5 text-[11px] text-emerald-300">✓ {result}</p>}
      <div className="flex justify-end gap-2">
        <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
          {result ? '关闭' : '取消'}
        </button>
        <Button onClick={run} loading={busy} disabled={!sourceScript.trim()}>
          生成并保存
        </Button>
      </div>
    </Dialog>
  )
}
