/**
 * 实体卡面板（侧栏 Tab：输入源 / 实体）
 * 列表 + 新建 + AI 抽取（世界观+剧本 → 实体卡）+ 详情弹层
 */
import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ENTITY_TYPE_COLORS, IMPORTANCE_LABEL, type Entity } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ConfirmDialog, Dialog } from '@/components/ui/dialog'

export function EntityPanel() {
  const qc = useQueryClient()
  const [detailId, setDetailId] = useState<string | null>(null)
  const [extractOpen, setExtractOpen] = useState(false)

  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })

  const refresh = () => qc.invalidateQueries({ queryKey: ['entities'] })

  return (
    <div className="flex h-full flex-col gap-2">
      <div className="flex gap-1.5">
        <Button size="sm" variant="outline" className="flex-1" onClick={() => setDetailId('__new__')}>
          + 新建
        </Button>
        <Button size="sm" variant="secondary" className="flex-1" onClick={() => setExtractOpen(true)}>
          ✨ AI 抽取
        </Button>
      </div>
      <p className="text-[10px] text-slate-600">AI 抽取：用世界观+剧本分析生成实体卡（外观/声音/介绍）</p>
      <div className="min-h-0 flex-1 space-y-1.5 overflow-y-auto">
        {entities.length === 0 && <p className="pt-4 text-center text-[11px] text-slate-600">暂无实体卡</p>}
        {entities.map((e) => {
          const c = ENTITY_TYPE_COLORS[e.type] ?? ENTITY_TYPE_COLORS['角色']
          return (
            <button
              key={e.id}
              onClick={() => setDetailId(e.id)}
              className={cn(
                'flex w-full items-center justify-between rounded border px-2 py-1.5 text-left transition-colors hover:bg-slate-800/60',
                c.bg,
                e.importance === 'core' ? 'border-solid border-current' : 'border-dashed border-current/60',
              )}
            >
              <span className={cn('truncate text-xs font-medium', c.text)}>{e.name}</span>
              <span className={cn('shrink-0 text-[10px]', c.text, 'opacity-70')}>
                {e.type} · {IMPORTANCE_LABEL[e.importance]}
              </span>
            </button>
          )
        })}
      </div>

      {detailId && <EntityDetailDialog id={detailId} onClose={() => setDetailId(null)} onChanged={refresh} />}
      {extractOpen && <ExtractDialog onClose={() => setExtractOpen(false)} onDone={refresh} />}
    </div>
  )
}

/** 实体详情/编辑弹层（id='__new__' 为新建） */
function EntityDetailDialog({ id, onClose, onChanged }: { id: string; onClose: () => void; onChanged: () => void }) {
  const qc = useQueryClient()
  const isNew = id === '__new__'
  const { data: entity } = useQuery({
    queryKey: ['entity', id],
    queryFn: () => api.getEntity(id),
    enabled: !isNew,
  })
  const [form, setForm] = useState<Entity | null>(null)
  const [confirmDel, setConfirmDel] = useState(false)
  const e = form ?? (isNew ? null : entity)

  const set = (patch: Partial<Entity>) => setForm({ ...(e ?? empty()), ...patch })

  const save = async () => {
    if (!e) return
    if (isNew) await api.saveEntity(e)
    else await api.updateEntity(id, e)
    qc.invalidateQueries({ queryKey: ['entities'] })
    onChanged()
    onClose()
  }

  const del = async () => {
    await api.deleteEntity(id)
    qc.invalidateQueries({ queryKey: ['entities'] })
    onChanged()
    onClose()
  }

  return (
    <>
      <Dialog open onClose={onClose} title={isNew ? '新建实体卡' : `实体卡 · ${entity?.name ?? ''}`} className="max-w-lg">
        {!isNew && !entity ? (
          <p className="py-4 text-center text-xs text-slate-500">加载中…</p>
        ) : (
          <div className="space-y-2.5">
            <div className="grid grid-cols-[1fr_90px_90px] gap-2">
              <input value={e?.name ?? ''} onChange={(ev) => set({ name: ev.target.value })} placeholder="名称（如 Alya）" className="w-full" />
              <select value={e?.type ?? '角色'} onChange={(ev) => set({ type: ev.target.value as Entity['type'] })}>
                {['角色', '场景', '物件', '技能', '组织', '地点'].map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
              <select value={e?.importance ?? 'secondary'} onChange={(ev) => set({ importance: ev.target.value as Entity['importance'] })}>
                <option value="core">核心</option>
                <option value="secondary">次要</option>
              </select>
            </div>
            <TextArea label="外观（canon：可作画级描述，工具 B 逐字采用）" value={e?.appearance ?? ''} onChange={(v) => set({ appearance: v })} rows={3} />
            <TextArea label="声音（音色/语气）" value={e?.sound ?? ''} onChange={(v) => set({ sound: v })} rows={2} />
            <TextArea label="介绍（身份/背景/作用）" value={e?.description ?? ''} onChange={(v) => set({ description: v })} rows={3} />
            <input
              value={e?.source ?? ''}
              onChange={(ev) => set({ source: ev.target.value })}
              placeholder="来源（如：剧本《XX》/世界观手册）"
              className="w-full text-xs"
            />
            <div className="flex items-center justify-between pt-1">
              <button onClick={() => setConfirmDel(true)} className="rounded px-2 py-1 text-[11px] text-red-400 hover:bg-red-950/50">
                {isNew ? '' : '删除'}
              </button>
              <div className="flex gap-2">
                <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
                  取消
                </button>
                <button onClick={save} disabled={!e?.name.trim()} className="rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500">
                  保存
                </button>
              </div>
            </div>
          </div>
        )}
      </Dialog>
      <ConfirmDialog
        open={confirmDel}
        onClose={() => setConfirmDel(false)}
        onConfirm={del}
        title="删除实体卡"
        message={`「${e?.name}」将被删除。`}
        confirmLabel="删除"
        danger
      />
    </>
  )
}

/** AI 抽取弹层：世界观（可选）+ 当前项目剧本 → 实体卡 */
function ExtractDialog({ onClose, onDone }: { onClose: () => void; onDone: () => void }) {
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
      onDone()
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
          关闭
        </button>
        <Button onClick={run} loading={busy} disabled={!sourceScript.trim()}>
          生成并保存
        </Button>
      </div>
    </Dialog>
  )
}

function TextArea({ label, value, onChange, rows }: { label: string; value: string; onChange: (v: string) => void; rows: number }) {
  return (
    <div>
      <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">{label}</label>
      <textarea value={value} onChange={(e) => onChange(e.target.value)} rows={rows} className="w-full text-xs" />
    </div>
  )
}

function empty(): Entity {
  return { id: '', name: '', type: '角色', importance: 'secondary', appearance: '', sound: '', description: '' }
}
