/**
 * 渲染输入源侧栏（页 2 右侧）：参考图墙（真实设定图，映射自提示词引用）+ 音频卡 + 高级参数
 * 联动：hover 提示词 ref chip → 卡片高亮；点击卡片 → 提示词对应引用高亮
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { parseRefMapping, type InputRef, type Project } from '@shotlist/shared'
import { api } from '@/lib/api'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  project: Project | null
  /** 提示词 hover 当前引用的 ref chip */
  hoverRef?: { label: string; n: number } | null
  /** 点击输入源卡片 → 提示词对应引用高亮 */
  onCardClick?: (label: string, n: number) => void
}

export function InputsSidebar({ project, hoverRef, onCardClick }: Props) {
  const [advOpen, setAdvOpen] = useState(false)
  const inputs = project?.inputs ?? []
  const prompt = project?.prompt ?? ''
  const roleCards = project?.shotlist?.role_cards ?? []

  // 提示词引用映射：<Picture N> ↔ <Subject N> ↔ 实体
  const mapping = prompt ? parseRefMapping(prompt, roleCards) : []

  // 音频（audio_refs / 输入源解析）
  const audios = inputs.filter((i): i is Extract<InputRef, { kind: 'audio' }> => i.kind === 'audio')

  return (
    <div className="flex h-full min-h-0 flex-col gap-2 overflow-y-auto">
      {/* 参考图墙：真实设定图 */}
      <Card>
        <CardHeader className="border-b border-slate-800 pb-2">
          <CardTitle className="text-xs text-slate-300">参考图墙（{mapping.length}）</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-2 p-3">
          {mapping.length === 0 && <p className="col-span-2 text-[11px] text-slate-500">暂无参考图映射（生成 ref2va 提示词后自动解析）</p>}
          {mapping.map((m) => (
            <RefImageCard key={m.pictureN} pictureN={m.pictureN} subjectN={m.subjectN} entityId={m.entityId} hoverRef={hoverRef} onCardClick={onCardClick} />
          ))}
        </CardContent>
      </Card>

      {/* 音频卡 */}
      <Card>
        <CardHeader className="border-b border-slate-800 pb-2">
          <CardTitle className="text-xs text-slate-300">音频（{audios.length}）</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 p-3">
          {audios.length === 0 && <p className="text-[11px] text-slate-500">暂无 audio_refs 音色种子</p>}
          {audios.map((a) => (
            <div key={a.n} className="rounded border border-slate-700 bg-slate-950 p-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-200">{a.label}</span>
                <Badge variant="secondary" className="text-[10px]">Audio {a.n}</Badge>
              </div>
              <p className="mt-1 truncate font-mono text-[10px] text-slate-500">{a.src}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* 高级参数（折叠） */}
      <Card>
        <CardHeader className="cursor-pointer border-b border-slate-800 pb-2 select-none" onClick={() => setAdvOpen((v) => !v)}>
          <CardTitle className="text-xs text-slate-300">高级参数 {advOpen ? '▾' : '▸'}</CardTitle>
        </CardHeader>
        {advOpen && (
          <CardContent className="space-y-1.5 p-3 text-[11px] text-slate-400">
            {project?.shotlist ? (
              <>
                <Row k="style" v={project.shotlist.style ?? '—'} />
                <Row k="ratio" v={project.shotlist.ratio ?? '16:9'} />
                <Row k="scene" v={project.shotlist.scene} />
                <Row k="duration_total" v={`${project.shotlist.duration_total}s`} />
                <Row k="chain" v={project.shotlist.chain} />
                <Row k="role_cards" v={roleCards.join(', ') || '—'} />
              </>
            ) : (
              <p>暂无拍摄本参数</p>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  )
}

/** 单张参考图卡片：实体设定图（无图占位） */
function RefImageCard({
  pictureN,
  subjectN,
  entityId,
  hoverRef,
  onCardClick,
}: {
  pictureN: number
  subjectN: number
  entityId?: string
  hoverRef?: { label: string; n: number } | null
  onCardClick?: (label: string, n: number) => void
}) {
  const { data: art } = useQuery({
    queryKey: ['entity-art', entityId ?? '__none__'],
    queryFn: () => api.getEntityArt(entityId!),
    enabled: !!entityId,
  })
  const { data: entities } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })
  const entityName = entities?.find((e) => e.id === entityId)?.name
  const img = art?.images[0]
  const active = hoverRef?.label === 'Subject' && hoverRef.n === subjectN

  return (
    <button
      onClick={() => onCardClick?.('Subject', subjectN)}
      className={cn(
        'group relative aspect-video overflow-hidden rounded border bg-slate-950 text-left transition-all',
        active ? 'border-cyan-400 ring-2 ring-cyan-400/60' : 'border-slate-700 hover:border-slate-500',
      )}
      title={entityName ? `点击跳回提示词 <Subject ${subjectN}>（${entityName}）` : `Subject ${subjectN} 参考图`}
    >
      {img ? (
        <img src={api.assetUrl(entityId!, img)} alt={img} className="h-full w-full object-cover" />
      ) : (
        <div className="flex h-full flex-col items-center justify-center gap-1 text-[10px] text-slate-600">
          <span className="font-mono text-blue-400">&lt;Picture {pictureN}&gt;</span>
          <span>Subject {subjectN}{entityName ? ` · ${entityName}` : ''}</span>
          {entityId && !art?.comfyOnline ? <span className="text-amber-500">ComfyUI 离线</span> : !img ? <span>无设定图（实体详情生成）</span> : null}
        </div>
      )}
      <span className="absolute bottom-0 left-0 right-0 bg-slate-950/85 px-1 py-0.5 text-[9px] leading-tight text-slate-300">
        &lt;Picture {pictureN}&gt; · Subject {subjectN}{entityName ? ` · ${entityName}` : ''}
      </span>
    </button>
  )
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-slate-500">{k}</span>
      <span className="truncate font-mono text-slate-300">{v}</span>
    </div>
  )
}
