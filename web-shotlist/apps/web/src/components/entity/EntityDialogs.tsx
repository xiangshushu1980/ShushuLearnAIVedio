/**
 * 实体全局弹层（三页共用）：详情/编辑 + 资源面板（画面/声音/文字 可重刷可观测）+ 新建 + 选择器
 * 用户决策 2026-08-14：
 *  - 侧滑面板（右侧滑出，主视图保持可见，避免模态切换）
 *  - 星级 1-5（游戏式重要度，≥4 = core 必检）
 *  - 实体内变体（换装/状态变种，引用 `实体id:变体id`）
 *  - 关系编辑界面化
 *  - 全局风格（⚙ 顶栏设置，只影响设定图）
 */
import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Entity, EntityRelation, EntityVariant } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { useTaskPoll } from '@/lib/useTaskPoll'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ConfirmDialog, Dialog } from '@/components/ui/dialog'

/** 全局宿主：渲染实体详情侧滑面板（由 store.entityDialogId 驱动） */
export function EntityDialogHost() {
  const entityDialogId = useAppStore((s) => s.entityDialogId)
  const closeEntity = useAppStore((s) => s.closeEntity)
  return <>{entityDialogId && <EntityDetailPanel id={entityDialogId} onClose={closeEntity} />}</>
}

/** 星级渲染（游戏式：金色实星 + 灰虚星） */
export function Stars({ stars, size = 'md' }: { stars: number; size?: 'sm' | 'md' | 'lg' }) {
  const s = stars ?? 3
  const cls = size === 'sm' ? 'text-[10px]' : size === 'lg' ? 'text-sm' : 'text-xs'
  return (
    <span className={cn(cls, 'tracking-tight')} title={`重要度 ${s}/5`}>
      <span className="text-amber-400">{'★'.repeat(Math.max(0, Math.min(5, s)))}</span>
      <span className="text-slate-700">{'★'.repeat(Math.max(0, 5 - Math.min(5, Math.max(1, s))))}</span>
    </span>
  )
}

/** 星级选择器（1-5 点击） */
function StarsPicker({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  const [hover, setHover] = useState(0)
  const cur = hover || value || 3
  return (
    <div className="flex items-center gap-1" onMouseLeave={() => setHover(0)}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          onMouseEnter={() => setHover(n)}
          className={cn('text-lg leading-none transition-colors', n <= cur ? 'text-amber-400' : 'text-slate-700 hover:text-slate-500')}
          title={`${n} 星`}
        >
          ★
        </button>
      ))}
      <span className="ml-1 text-[10px] text-slate-500">{cur >= 4 ? '核心（渲染门禁必检）' : '次要'}</span>
    </div>
  )
}

/** 实体详情/编辑侧滑面板（右滑出，主视图保持可见；id='__new__' 为新建） */
export function EntityDetailPanel({ id, onClose }: { id: string; onClose: () => void }) {
  const qc = useQueryClient()
  const isNew = id === '__new__'
  const { data: entity } = useQuery({ queryKey: ['entity', id], queryFn: () => api.getEntity(id), enabled: !isNew })
  const [form, setForm] = useState<Entity | null>(null)
  const [confirmDel, setConfirmDel] = useState(false)
  const e = form ?? (isNew ? null : entity)

  const set = (patch: Partial<Entity>) => setForm({ ...(e ?? empty()), ...patch })

  const save = async () => {
    if (!e) return
    try {
      if (isNew) await api.saveEntity(e)
      else await api.updateEntity(id, e)
      qc.invalidateQueries({ queryKey: ['entities'] })
      onClose()
    } catch (err) {
      useAppStore.getState().setError(`保存失败: ${(err as Error).message}`)
    }
  }

  const del = async () => {
    try {
      await api.deleteEntity(id)
      qc.invalidateQueries({ queryKey: ['entities'] })
      onClose()
    } catch (err) {
      useAppStore.getState().setError(`删除失败: ${(err as Error).message}`)
    }
  }

  return (
    <>
      {/* 侧滑面板：pointer-events-none 透传 → 主界面保持可见可交互（用户决策 2026-08-14：不关闭前景） */}
      <div className="pointer-events-none fixed inset-0 z-40" role="dialog" aria-label="实体详情">
        {/* 极淡遮罩仅视觉区分，不拦截点击 */}
        <div className="pointer-events-none absolute inset-0 bg-black/10" />
        <div className="pointer-events-auto absolute inset-y-0 right-0 flex w-full max-w-xl flex-col border-l border-slate-700 bg-slate-900 shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2.5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-100">
              {isNew ? '新建实体卡' : `实体卡 · ${entity?.name ?? ''}`}
              {!isNew && e && <Stars stars={e.stars ?? 3} size="sm" />}
            </h2>
            <button onClick={onClose} className="rounded px-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200" title="关闭（Esc）">
              ✕
            </button>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto p-4">
            {!isNew && !entity ? (
              <p className="py-8 text-center text-xs text-slate-500">加载中…</p>
            ) : (
              <div className="space-y-3">
                <div className="grid grid-cols-[1fr_110px] gap-2">
                  <input value={e?.name ?? ''} onChange={(ev) => set({ name: ev.target.value })} placeholder="名称（如 Alya）" className="w-full" />
                  <select value={e?.type ?? '角色'} onChange={(ev) => set({ type: ev.target.value as Entity['type'] })}>
                    {['角色', '场景', '物件', '技能', '组织', '地点'].map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </div>
                {/* 星级：游戏式重要度（≥4 = 核心必检） */}
                <div>
                  <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">重要度</label>
                  <StarsPicker value={e?.stars ?? 3} onChange={(v) => set({ stars: v })} />
                </div>
                <TextArea label="外观（canon：可作画级描述）" value={e?.appearance ?? ''} onChange={(v) => set({ appearance: v })} rows={3} />
                <TextArea label="声音（音色/语气）" value={e?.sound ?? ''} onChange={(v) => set({ sound: v })} rows={2} />
                <TextArea label="介绍（身份/背景/作用）" value={e?.description ?? ''} onChange={(v) => set({ description: v })} rows={3} />
                <input value={e?.source ?? ''} onChange={(ev) => set({ source: ev.target.value })} placeholder="来源（如：剧本《XX》/世界观手册）" className="w-full text-xs" />
                {/* 变体（换装/状态变种） */}
                {!isNew && e && <VariantsSection entity={e} onPatch={set} />}
                {/* 关系（界面化编辑） */}
                {!isNew && e && <RelationsSection entity={e} onPatch={set} />}
                {!isNew && e && <AssetsSection entityId={e.id} entity={e} />}
                <div className="flex items-center justify-between pt-1">
                  <button onClick={() => setConfirmDel(true)} className="rounded px-2 py-1 text-[11px] text-red-400 hover:bg-red-950/50">
                    {isNew ? '' : '删除'}
                  </button>
                  <div className="flex gap-2">
                    <button onClick={onClose} className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800">
                      取消
                    </button>
                    <button onClick={save} disabled={!e?.name?.trim()} className="rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-500">
                      保存
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <ConfirmDialog open={confirmDel} onClose={() => setConfirmDel(false)} onConfirm={del} title="删除实体卡" message={`「${e?.name}」将被删除。`} confirmLabel="删除" danger />
    </>
  )
}

/** 变体区块：换装/状态变种列表 + 新增/编辑 + 各变体生成设定图（用户决策 2026-08-14：实体内变体） */
function VariantsSection({ entity, onPatch }: { entity: Entity; onPatch: (p: Partial<Entity>) => void }) {
  const [adding, setAdding] = useState(false)
  const [vid, setVid] = useState('')
  const [vname, setVname] = useState('')
  const [vdesc, setVdesc] = useState('')
  const variants = entity.variants ?? []

  const addVariant = () => {
    if (!vid.trim()) return
    const v: EntityVariant = { id: vid.trim(), name: vname.trim() || vid.trim(), description: vdesc.trim() }
    onPatch({ variants: [...variants, v] })
    setVid('')
    setVname('')
    setVdesc('')
    setAdding(false)
  }

  const removeVariant = (rid: string) => onPatch({ variants: variants.filter((v) => v.id !== rid) })

  return (
    <div className="rounded border border-slate-800 bg-slate-950/50 p-2">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-[10px] font-medium uppercase tracking-wide text-slate-500">变体（换装/状态 · 引用写 `实体id:变体id`）</span>
        <Button size="sm" variant="outline" onClick={() => setAdding((v) => !v)}>
          {adding ? '收起' : '+ 变体'}
        </Button>
      </div>
      {adding && (
        <div className="mb-2 space-y-1.5 rounded border border-slate-700 bg-slate-900 p-2">
          <div className="grid grid-cols-2 gap-1.5">
            <input value={vid} onChange={(e) => setVid(e.target.value)} placeholder="变体 id（如 战斗服）" className="text-[11px]" />
            <input value={vname} onChange={(e) => setVname(e.target.value)} placeholder="显示名（如 战斗服 Alya）" className="text-[11px]" />
          </div>
          <textarea value={vdesc} onChange={(e) => setVdesc(e.target.value)} rows={2} placeholder="外观差异描述（叠加在基础外观上，可作画级）" className="w-full text-[11px]" />
          <Button size="sm" onClick={addVariant} disabled={!vid.trim()}>
            添加
          </Button>
        </div>
      )}
      {variants.length === 0 && !adding && <p className="text-[10px] text-slate-600">暂无变体（换装/状态变种在此管理；基础外观即默认形态）</p>}
      <div className="space-y-1.5">
        {variants.map((v) => (
          <div key={v.id} className="rounded border border-slate-800 bg-slate-900 p-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-200">
                {v.name} <span className="text-[10px] text-slate-500">({v.id})</span>
              </span>
              <button onClick={() => removeVariant(v.id)} className="text-[10px] text-red-400 hover:text-red-300" title="删除变体">
                ✕
              </button>
            </div>
            <p className="mt-0.5 text-[11px] text-slate-400">{v.description || '无描述'}</p>
            <VariantArtRow entityId={entity.id} variant={v} allVariants={variants} onPatch={onPatch} />
          </div>
        ))}
      </div>
    </div>
  )
}

/** 变体专属设定图：生成（带变体描述）+ 展示 + 删除 */
function VariantArtRow({ entityId, variant, allVariants, onPatch }: { entityId: string; variant: EntityVariant; allVariants: EntityVariant[]; onPatch: (p: Partial<Entity>) => void }) {
  const qc = useQueryClient()
  const { data: art } = useQuery({ queryKey: ['entity-art', entityId], queryFn: () => api.getEntityArt(entityId) })
  const [taskId, setTaskId] = useState<string | null>(null)
  const [conflict, setConflict] = useState<string | null>(null)
  const baselineRef = useRef<string[] | null>(null)
  const files = variant.art ?? []
  const artFiles = art?.images ?? []

  const task = useTaskPoll(taskId, () => {
    qc.invalidateQueries({ queryKey: ['entity-art', entityId] })
    qc.invalidateQueries({ queryKey: ['entity-assets', entityId] })
    qc.invalidateQueries({ queryKey: ['entity', entityId] })
  })

  const gen = async () => {
    setConflict(null)
    baselineRef.current = artFiles // 记录发起时的画面区全量，done 后 diff 出新图
    try {
      const r = await api.generateEntityArt(entityId, { variant: variant.id })
      setTaskId(r.taskId)
    } catch (e) {
      baselineRef.current = null
      const msg = (e as Error).message
      if (msg.includes('已有任务')) setConflict(msg)
      else useAppStore.getState().setError(msg)
    }
  }

  // 任务完成后：把新生成的图自动归属到该变体（diff 发起前后，排除其他变体已占用的）
  const owned = new Set(allVariants.flatMap((v) => v.art ?? []))
  const pending = baselineRef.current ? artFiles.filter((f) => !baselineRef.current!.includes(f) && !owned.has(f)) : []
  if (pending.length && task?.status === 'done') {
    onPatch({
      variants: allVariants.map((v) => (v.id === variant.id ? { ...v, art: [...(v.art ?? []), ...pending] } : v)),
    })
    baselineRef.current = null
  }

  return (
    <div className="mt-1.5">
      <div className="flex items-center gap-1.5">
        <Button size="sm" variant="secondary" onClick={gen} loading={task?.status === 'running'} disabled={art?.comfyOnline === false} className="px-2 py-0.5 text-[10px]">
          {art?.comfyOnline === false ? 'ComfyUI 离线' : '生成变体图'}
        </Button>
        {conflict && <span className="text-[10px] text-amber-300">⏳ {conflict}</span>}
        {task?.status === 'running' && <span className="text-[10px] text-cyan-300">⏳ {task.elapsed}s…</span>}
        {task?.status === 'error' && <span className="text-[10px] text-red-300">✗ {task.error}</span>}
      </div>
      {files.length > 0 && (
        <div className="mt-1 grid grid-cols-4 gap-1">
          {files.map((f) => (
            <a key={f} href={api.assetUrl(entityId, f)} target="_blank" rel="noreferrer">
              <img src={api.assetUrl(entityId, f)} alt={f} className="aspect-video w-full rounded border border-slate-700 object-cover" />
            </a>
          ))}
        </div>
      )}
      {files.length === 0 && <p className="text-[10px] text-slate-600">暂无变体图（生成后自动归属；引用它的镜头输入源显示「变体名」）</p>}
    </div>
  )
}

/** 关系区块：选择实体 + 关系词（界面化编辑 related，V1 单向存储） */
function RelationsSection({ entity, onPatch }: { entity: Entity; onPatch: (p: Partial<Entity>) => void }) {
  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })
  const [pick, setPick] = useState('')
  const [rel, setRel] = useState('')
  const [adding, setAdding] = useState(false)
  const relations = entity.related ?? []

  const add = () => {
    if (!pick || !rel.trim()) return
    const r: EntityRelation = { id: pick, relation: rel.trim() }
    onPatch({ related: [...relations, r] })
    setPick('')
    setRel('')
    setAdding(false)
  }

  const remove = (rid: string) => onPatch({ related: relations.filter((r) => r.id !== rid) })

  const nameOf = (rid: string) => entities.find((e) => e.id === rid)?.name ?? rid

  return (
    <div className="rounded border border-slate-800 bg-slate-950/50 p-2">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-[10px] font-medium uppercase tracking-wide text-slate-500">关系（{relations.length}）</span>
        <Button size="sm" variant="outline" onClick={() => setAdding((v) => !v)}>
          {adding ? '收起' : '+ 关系'}
        </Button>
      </div>
      {adding && (
        <div className="mb-2 space-y-1.5 rounded border border-slate-700 bg-slate-900 p-2">
          <select value={pick} onChange={(e) => setPick(e.target.value)} className="w-full text-[11px]">
            <option value="">选择关联实体…</option>
            {entities
              .filter((x) => x.id !== entity.id)
              .map((x) => (
                <option key={x.id} value={x.id}>
                  {x.name}（{x.type}）
                </option>
              ))}
          </select>
          <input value={rel} onChange={(e) => setRel(e.target.value)} placeholder="关系词（如：持有 / 的武器 / 师徒）" className="w-full text-[11px]" />
          <Button size="sm" onClick={add} disabled={!pick || !rel.trim()}>
            添加
          </Button>
        </div>
      )}
      {relations.length === 0 && !adding && <p className="text-[10px] text-slate-600">暂无关系（如：Alya 的武器 / 场景归属）</p>}
      <div className="flex flex-wrap gap-1.5">
        {relations.map((r) => (
          <span key={r.id} className="inline-flex items-center gap-1 rounded border border-slate-700 bg-slate-900 px-2 py-0.5 text-[11px] text-slate-300">
            {nameOf(r.id)}
            <span className="text-slate-500">{r.relation}</span>
            <button onClick={() => remove(r.id)} className="text-[10px] text-red-400 hover:text-red-300" title="删除关系">
              ✕
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}

/** 资源面板：三态（文字/画面/声音）+ 设定图生成（任务式，自动带外观描述）+ 上传/试听/删除 */
function AssetsSection({ entityId, entity }: { entityId: string; entity: Entity }) {
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

  // ===== 音色种子生成（Qwen3-TTS 三模式）=====
  const [voiceMode, setVoiceMode] = useState<'custom' | 'design'>('design')
  const [voiceSpeaker, setVoiceSpeaker] = useState('serena')
  const [voiceInstruct, setVoiceInstruct] = useState('')
  const [voiceText, setVoiceText] = useState('我是一片随风飘落的树叶，轻轻落在你的肩头。')
  const [voiceTaskId, setVoiceTaskId] = useState<string | null>(null)
  const [voiceConflict, setVoiceConflict] = useState<string | null>(null)
  const [ttsReady, setTtsReady] = useState<boolean | null>(null)
  useEffect(() => {
    api
      .ttsReady()
      .then((r) => setTtsReady(r.ready))
      .catch(() => setTtsReady(false))
  }, [])
  const voiceTask = useTaskPoll(voiceTaskId, () => {
    qc.invalidateQueries({ queryKey: ['entity-assets', entityId] })
  })
  const genVoice = async () => {
    setVoiceConflict(null)
    try {
      const r = await api.generateEntityVoice(entityId, {
        kind: voiceMode,
        text: voiceText || '你好。',
        speaker: voiceMode === 'custom' ? voiceSpeaker : undefined,
        instruct: voiceMode === 'design' ? voiceInstruct || entity.sound : undefined,
      })
      setVoiceTaskId(r.taskId)
    } catch (e) {
      const msg = (e as Error).message
      if (msg.includes('已有任务')) setVoiceConflict(msg)
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

      {/* 设定图：生成（自动带外观描述+全局风格）+ 展示 */}
      <div>
        <div className="mb-1 flex gap-1.5">
          <input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="自定义 prompt（留空=外观描述+类型构图+全局风格）" className="min-w-0 flex-1 text-[11px]" />
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
          {artFiles.slice(0, 9).map((f) => (
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

      {/* 音色种子：Qwen3-TTS 生成 + 上传 + 试听 */}
      <div>
        <div className="mb-1 flex items-center justify-between">
          <span className="text-[10px] font-medium uppercase tracking-wide text-slate-500">音色种子（{voiceAssets.length}）</span>
          <Button size="sm" variant="outline" onClick={() => voiceRef.current?.click()}>上传 wav</Button>
          <input ref={voiceRef} type="file" accept="audio/*" className="hidden" onChange={(e) => e.target.files?.[0] && upload('voice', e.target.files[0])} />
        </div>
        {/* AI 生成（Qwen3-TTS） */}
        <div className="mb-2 space-y-1.5 rounded border border-slate-800 bg-slate-950 p-2">
          <div className="flex items-center gap-1.5">
            <select value={voiceMode} onChange={(e) => setVoiceMode(e.target.value as 'custom' | 'design')} className="w-28 text-[11px]">
              <option value="design">描述设计（推荐）</option>
              <option value="custom">预设音色</option>
            </select>
            {voiceMode === 'custom' ? (
              <select value={voiceSpeaker} onChange={(e) => setVoiceSpeaker(e.target.value)} className="w-28 text-[11px]">
                {['serena', 'vivian', 'ono_anna', 'ryan', 'dylan', 'eric', 'sohee', 'aiden', 'uncle_fu'].map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            ) : (
              <input value={voiceInstruct} onChange={(e) => setVoiceInstruct(e.target.value)} placeholder="风格指令（留空=用实体声音描述）" className="min-w-0 flex-1 text-[11px]" />
            )}
            <Button size="sm" variant="secondary" onClick={genVoice} loading={voiceTask?.status === 'running'} disabled={ttsReady === false} className="shrink-0">
              {ttsReady === false ? 'TTS 未就绪' : 'AI 生成'}
            </Button>
          </div>
          <input value={voiceText} onChange={(e) => setVoiceText(e.target.value)} placeholder="试听文本（生成音色种子用，不是台词）" className="w-full text-[11px]" />
          {voiceConflict && <p className="text-[10px] text-amber-300">⏳ {voiceConflict}</p>}
          {voiceTask?.status === 'running' && <p className="text-[10px] text-cyan-300">⏳ 生成中… {voiceTask.elapsed}s（1.7B 模型，首次加载约 1-2 分钟）</p>}
          {voiceTask?.status === 'done' && <p className="text-[10px] text-emerald-400">✓ 音色种子已生成（{((voiceTask.result as { durSec?: number } | undefined)?.durSec ?? '').toString()}s）</p>}
          {voiceTask?.status === 'error' && <p className="text-[10px] text-red-300">✗ {voiceTask.error}</p>}
        </div>
        {voiceAssets.length === 0 && voiceTask?.status !== 'running' && <p className="text-[10px] text-slate-600">暂无音色种子（AI 生成或上传 wav）</p>}
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
        渲染门禁：生成提示词前检查引用实体——文字不合格阻塞；画面/声音缺失警告。「{entity.name}」设定图可作 ref2va 参考图；换装变体在「变体」区生成专属图。
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

/** 实体选择器（ref chip / 镜头主体关联用；显示星级） */
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
            <span className="flex items-center gap-2 text-xs text-slate-200">
              {e.name}
              <Stars stars={(e as Entity & { stars?: number }).stars ?? 3} size="sm" />
            </span>
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
  return { id: '', name: '', type: '角色', importance: 'secondary', stars: 3, appearance: '', sound: '', description: '' }
}
