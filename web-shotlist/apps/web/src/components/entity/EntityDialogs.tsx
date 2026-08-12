/**
 * 实体全局弹层（三页共用）：详情/编辑 + 资源面板（画面/声音/文字 可重刷可观测）+ 新建 + 选择器
 */
import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Entity } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { useTaskPoll } from '@/lib/useTaskPoll'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ConfirmDialog, Dialog } from '@/components/ui/dialog'

/** 全局宿主：渲染实体详情弹层（由 store.entityDialogId 驱动） */
export function EntityDialogHost() {
  const entityDialogId = useAppStore((s) => s.entityDialogId)
  const closeEntity = useAppStore((s) => s.closeEntity)
  return <>{entityDialogId && <EntityDetailDialog id={entityDialogId} onClose={closeEntity} />}</>
}

/** 实体详情/编辑弹层（含设定图；id='__new__' 为新建） */
export function EntityDetailDialog({ id, onClose }: { id: string; onClose: () => void }) {
  const qc = useQueryClient()
  const isNew = id === '__new__'
  const { data: entity } = useQuery({ queryKey: ['entity', id], queryFn: () => api.getEntity(id), enabled: !isNew })
  const [form, setForm] = useState<Entity | null>(null)
  const [confirmDel, setConfirmDel] = useState(false)
  const e = form ?? (isNew ? null : entity)

  const set = (patch: Partial<Entity>) => setForm({ ...(e ?? empty()), ...patch })

  const save = async () => {
    if (!e) return
    if (isNew) await api.saveEntity(e)
    else await api.updateEntity(id, e)
    qc.invalidateQueries({ queryKey: ['entities'] })
    onClose()
  }

  const del = async () => {
    await api.deleteEntity(id)
    qc.invalidateQueries({ queryKey: ['entities'] })
    onClose()
  }

  return (
    <>
      <Dialog open onClose={onClose} title={isNew ? '新建实体卡' : `实体卡 · ${entity?.name ?? ''}`} className="max-w-xl">
        {!isNew && !entity ? (
          <p className="py-4 text-center text-xs text-slate-500">加载中…</p>
        ) : (
          <div className="max-h-[70vh] space-y-2.5 overflow-y-auto">
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
            <TextArea label="外观（canon：可作画级描述）" value={e?.appearance ?? ''} onChange={(v) => set({ appearance: v })} rows={3} />
            <TextArea label="声音（音色/语气）" value={e?.sound ?? ''} onChange={(v) => set({ sound: v })} rows={2} />
            <TextArea label="介绍（身份/背景/作用）" value={e?.description ?? ''} onChange={(v) => set({ description: v })} rows={3} />
            <input value={e?.source ?? ''} onChange={(ev) => set({ source: ev.target.value })} placeholder="来源（如：剧本《XX》/世界观手册）" className="w-full text-xs" />
            {!isNew && e && <AssetsSection entityId={e.id} entityName={e.name} />}
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
      <ConfirmDialog open={confirmDel} onClose={() => setConfirmDel(false)} onConfirm={del} title="删除实体卡" message={`「${e?.name}」将被删除。`} confirmLabel="删除" danger />
    </>
  )
}

/** 资源面板：三态（文字/画面/声音）+ 设定图生成（任务式）+ 上传/试听/删除 */
function AssetsSection({ entityId, entityName }: { entityId: string; entityName: string }) {
  const qc = useQueryClient()
  const { data: art } = useQuery({ queryKey: ['entity-art', entityId], queryFn: () => api.getEntityArt(entityId) })
  const { data: assets } = useQuery({ queryKey: ['entity-assets', entityId], queryFn: () => api.getEntityAssets(entityId) })
  const [prompt, setPrompt] = useState('')
  const [artTaskId, setArtTaskId] = useState<string | null>(null)
  const [artConflict, setArtConflict] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const voiceRef = useRef<HTMLInputElement>(null)

  const artTask = useTaskPoll(artTaskId, () => {
    qc.invalidateQueries({ queryKey: ['entity-art', entityId] })
    qc.invalidateQueries({ queryKey: ['entity-assets', entityId] })
  })

  const upload = async (kind: 'art' | 'voice', file: File) => {
    try {
      await api.uploadEntityAsset(entityId, kind, file)
      qc.invalidateQueries({ queryKey: ['entity-assets', entityId] })
      qc.invalidateQueries({ queryKey: ['entity-art', entityId] })
    } catch (e) {
      useAppStore.getState().setError(`上传失败: ${(e as Error).message}`)
    }
  }

  const del = async (file: string) => {
    try {
      await api.deleteEntityAsset(entityId, file)
      qc.invalidateQueries({ queryKey: ['entity-assets', entityId] })
      qc.invalidateQueries({ queryKey: ['entity-art', entityId] })
    } catch (e) {
      useAppStore.getState().setError((e as Error).message)
    }
  }

  const genArt = async () => {
    setArtConflict(null)
    try {
      const r = await api.generateEntityArt(entityId, { prompt: prompt.trim() || undefined })
      setArtTaskId(r.taskId)
    } catch (e) {
      const msg = (e as Error).message
      if (msg.includes('已有任务')) setArtConflict(msg)
      else useAppStore.getState().setError(msg)
    }
  }

  const artFiles = art?.images ?? []
  const artAssets = assets?.assets.filter((a) => a.kind === 'art') ?? []
  const voiceAssets = assets?.assets.filter((a) => a.kind === 'voice') ?? []

  return (
    <div className="space-y-2 rounded border border-slate-800 bg-slate-950/50 p-2">
      {/* 三态徽章 */}
      <div className="flex flex-wrap gap-1.5">
        <StateBadge ok={artFiles.length > 0} label="画面（设定图）" missing="无设定图" count={artFiles.length} />
        <StateBadge ok={voiceAssets.length > 0} label="声音（音色种子）" missing="无音色" count={voiceAssets.length} />
        <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400">文字（外观/介绍）</span>
      </div>

      {/* 设定图：生成 + 展示 */}
      <div>
        <div className="mb-1 flex gap-1.5">
          <input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="自定义 prompt（留空=用外观描述）" className="min-w-0 flex-1 text-[11px]" />
          <Button size="sm" variant="secondary" onClick={genArt} loading={artTask?.status === 'running'} disabled={art?.comfyOnline === false}>
            {art?.comfyOnline === false ? 'ComfyUI 离线' : artFiles.length ? '重刷' : '生成'}
          </Button>
          <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()}>上传</Button>
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files?.[0] && upload('art', e.target.files[0])} />
        </div>
        {artConflict && <p className="mb-1 text-[10px] text-amber-300">⏳ {artConflict}</p>}
        {artTask?.status === 'running' && <p className="mb-1 text-[10px] text-cyan-300">⏳ 生成中… 已等待 {artTask.elapsed}s（ANIMA 约 1-2 分钟）</p>}
        {artTask?.status === 'error' && <p className="mb-1 text-[10px] text-red-300">✗ {artTask.error}</p>}
        <div className="grid grid-cols-3 gap-1.5">
          {artFiles.slice(0, 6).map((f) => (
            <div key={f} className="group relative">
              <a href={api.assetUrl(entityId, f)} target="_blank" rel="noreferrer">
                <img src={api.assetUrl(entityId, f)} alt={f} className="aspect-video w-full rounded border border-slate-700 object-cover" />
              </a>
              <button
                onClick={() => del(f)}
                className="absolute right-0.5 top-0.5 hidden rounded bg-red-950/80 px-1 text-[9px] text-red-300 group-hover:block"
                title="删除"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
        {artFiles.length === 0 && artTask?.status !== 'running' && <p className="text-[10px] text-slate-600">暂无设定图（生成或上传）</p>}
      </div>

      {/* 音色种子：上传 + 试听 */}
      <div>
        <div className="mb-1 flex items-center justify-between">
          <span className="text-[10px] font-medium uppercase tracking-wide text-slate-500">音色种子（{voiceAssets.length}）</span>
          <Button size="sm" variant="outline" onClick={() => voiceRef.current?.click()}>上传 wav</Button>
          <input ref={voiceRef} type="file" accept="audio/*" className="hidden" onChange={(e) => e.target.files?.[0] && upload('voice', e.target.files[0])} />
        </div>
        {voiceAssets.length === 0 && <p className="text-[10px] text-slate-600">暂无音色种子（上传角色声音 wav）</p>}
        <div className="space-y-1">
          {voiceAssets.map((a) => (
            <div key={a.file} className="flex items-center gap-2 rounded border border-slate-800 bg-slate-950 px-1.5 py-1">
              <audio controls src={api.assetUrl(entityId, a.file)} className="h-6 min-w-0 flex-1" />
              <button onClick={() => del(a.file)} className="text-[10px] text-red-400 hover:text-red-300" title="删除">✕</button>
            </div>
          ))}
        </div>
      </div>
      <p className="text-[10px] leading-relaxed text-slate-600">
        渲染门禁：生成提示词前会检查引用实体——文字不合格阻塞；画面/声音缺失警告。「{entityName}」的设定图可作 ref2va 参考图。
      </p>
    </div>
  )
}

function StateBadge({ ok, label, missing, count }: { ok: boolean; label: string; missing: string; count: number }) {
  return ok ? (
    <span className="rounded bg-emerald-900/60 px-1.5 py-0.5 text-[10px] text-emerald-300">✓ {label} ×{count}</span>
  ) : (
    <span className="rounded bg-amber-950/60 px-1.5 py-0.5 text-[10px] text-amber-400">△ {label}：{missing}</span>
  )
}

/** 实体选择器（ref chip / 镜头主体关联用） */
export function EntityPickerDialog({
  open,
  onClose,
  onPick,
  title,
}: {
  open: boolean
  onClose: () => void
  onPick: (id: string) => void
  title: string
}) {
  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities, enabled: open })
  return (
    <Dialog open={open} onClose={onClose} title={title}>
      <p className="mb-2 text-[11px] text-slate-500">选择实体（点击查看/编辑）</p>
      <div className="max-h-64 space-y-1 overflow-y-auto">
        {entities.length === 0 && <p className="py-4 text-center text-[11px] text-slate-600">实体库为空 —— 先在①剧本页从剧本+世界观抽取实体</p>}
        {entities.map((e) => (
          <button
            key={e.id}
            onClick={() => onPick(e.id)}
            className="flex w-full items-center justify-between rounded border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-left hover:bg-slate-800"
          >
            <span className="text-xs text-slate-200">{e.name}</span>
            <span className="text-[10px] text-slate-500">{e.type}</span>
          </button>
        ))}
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
