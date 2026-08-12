/**
 * AI 实体抽取（任务式，单实例队列）：提交 → 轮询 → 结果展示（可观测）
 */
import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { Entity } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { useTaskPoll } from '@/lib/useTaskPoll'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

export function ExtractDialog({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const scriptDraft = useAppStore((s) => s.scriptDraft)
  const [scriptText, setScriptText] = useState('')
  const [worldview, setWorldview] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [conflict, setConflict] = useState<string | null>(null)

  const sourceScript = scriptDraft || scriptText
  const task = useTaskPoll(taskId, () => qc.invalidateQueries({ queryKey: ['entities'] }))

  const submit = async () => {
    setConflict(null)
    try {
      const r = await api.extractEntities({ worldview, script: sourceScript })
      setTaskId(r.taskId)
    } catch (e) {
      const msg = (e as Error).message
      if (msg.includes('已有任务')) setConflict(msg)
      else useAppStore.getState().setError(msg)
    }
  }

  const doneEntities = (task?.result as { entities?: Entity[] } | undefined)?.entities ?? null

  return (
    <Dialog open onClose={onClose} title="AI 抽取实体卡（任务式）">
      {conflict && (
        <p className="mb-2 rounded border border-amber-900 bg-amber-950/40 px-2 py-1.5 text-[11px] text-amber-300">⏳ {conflict}</p>
      )}
      {!task ? (
        <>
          <p className="mb-2 text-[11px] leading-relaxed text-slate-500">
            实体必须从剧本 + 世界观中获得。基于剧本{scriptDraft ? '（已自动代入当前项目剧本）' : ''}与世界观文本分析，生成实体卡并保存为文件（data/entities/*.md）。后台异步执行，可随时关掉弹层。
          </p>
          {!scriptDraft && (
            <>
              <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">剧本文本（必填）</label>
              <textarea value={scriptText} onChange={(e) => setScriptText(e.target.value)} placeholder="粘贴剧本…（也可先新建/选择项目，自动代入）" rows={4} className="mb-2 w-full text-xs" />
            </>
          )}
          <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">世界观手册（建议填写）</label>
          <textarea value={worldview} onChange={(e) => setWorldview(e.target.value)} placeholder="粘贴世界观手册…（留空则仅按剧本推断）" rows={4} className="mb-3 w-full text-xs" />
          <div className="flex justify-end gap-2">
            <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
              取消
            </button>
            <Button onClick={submit} disabled={!sourceScript.trim()}>
              开始抽取
            </Button>
          </div>
        </>
      ) : (
        <div className="space-y-3">
          <p className="text-[11px] text-slate-400">
            任务状态：<span className={task.status === 'running' ? 'text-cyan-300' : task.status === 'done' ? 'text-emerald-300' : task.status === 'error' ? 'text-red-300' : 'text-slate-300'}>{statusLabel(task.status)}</span>
            {task.status === 'running' && <span className="ml-2 text-slate-500">已等待 {task.elapsed}s（单实例队列，后台执行）</span>}
          </p>
          {task.status === 'running' && (
            <div className="flex items-center gap-2 text-[11px] text-slate-500">
              <span className="size-3 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
              抽取中…（DeepSeek 分析剧本+世界观，约 30-60s）
            </div>
          )}
          {task.status === 'error' && <p className="rounded border border-red-900 bg-red-950/40 px-2 py-1.5 text-[11px] text-red-300">✗ {task.error}</p>}
          {doneEntities && (
            <div>
              <p className="mb-1.5 text-[11px] text-emerald-300">✓ 已生成 {doneEntities.length} 个实体并保存为文件</p>
              <ul className="max-h-48 space-y-1 overflow-y-auto">
                {doneEntities.map((e) => (
                  <li key={e.id} className="flex items-center justify-between rounded border border-slate-800 bg-slate-950 px-2 py-1">
                    <span className="text-xs text-slate-200">{e.name}</span>
                    <span className={cn('text-[10px]', e.appearance ? 'text-emerald-500' : 'text-red-400')}>
                      {e.type} · {e.appearance ? '文字✓' : '待补'}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {task.status !== 'running' && (
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
                关闭
              </button>
            </div>
          )}
        </div>
      )}
    </Dialog>
  )
}

function statusLabel(s: string): string {
  return { queued: '排队中', running: '运行中', done: '完成', error: '失败' }[s] ?? s
}
