/**
 * ③ 侧栏（docs/22 四节，方案 A）：渲染输入源
 * 参考图卡片墙 + 音频卡 + 高级参数（折叠）
 * V1 只显示清单（解析自拍摄本 audio_refs / 提示词 <Picture N> 引用），不做提交
 */
import { useState } from 'react'
import type { InputRef, Project } from '@shotlist/shared'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EntityPanel } from './EntityPanel'

export function SidebarPanel({ project }: { project: Project }) {
  const [tab, setTab] = useState<'inputs' | 'entities'>('inputs')
  const [advOpen, setAdvOpen] = useState(false)
  const images = project.inputs.filter((i): i is Extract<InputRef, { kind: 'image' }> => i.kind === 'image')
  const audios = project.inputs.filter((i): i is Extract<InputRef, { kind: 'audio' }> => i.kind === 'audio')

  return (
    <div className="flex h-full flex-col gap-2">
      {/* Tab：输入源 / 实体 */}
      <div className="flex shrink-0 rounded border border-slate-800 bg-slate-900/60 p-0.5">
        {([['inputs', '输入源'], ['entities', '实体']] as const).map(([k, label]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            className={cn(
              'flex-1 rounded px-2 py-1 text-[11px] transition-colors',
              tab === k ? 'bg-slate-700 text-slate-100' : 'text-slate-500 hover:text-slate-300',
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'entities' ? (
        <div className="min-h-0 flex-1 overflow-y-auto">
          <EntityPanel />
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto">
      {/* 参考图墙 */}
      <Card>
        <CardHeader className="border-b border-slate-800 pb-2">
          <CardTitle className="text-xs text-slate-300">参考图墙（{images.length}）</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-2 p-3">
          {images.length === 0 && <p className="col-span-2 text-[11px] text-slate-500">暂无 {'<Picture N>'} 引用</p>}
          {images.map((img) => (
            <div key={img.n} className="group relative aspect-video overflow-hidden rounded border border-slate-700 bg-slate-950" title={img.label}>
              <div className="flex h-full items-center justify-center text-[10px] text-slate-600">
                <Picture n={img.n} />
              </div>
              <span className="absolute bottom-0 left-0 right-0 bg-slate-950/80 px-1 py-0.5 text-[9px] leading-tight text-slate-400">
                {img.label}
              </span>
            </div>
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
        <CardHeader
          className="cursor-pointer border-b border-slate-800 pb-2 select-none"
          onClick={() => setAdvOpen((v) => !v)}
        >
          <CardTitle className="text-xs text-slate-300">
            高级参数 {advOpen ? '▾' : '▸'}
          </CardTitle>
        </CardHeader>
        {advOpen && (
          <CardContent className="space-y-1.5 p-3 text-[11px] text-slate-400">
            {project.shotlist ? (
              <>
                <Row k="style" v={project.shotlist.style ?? '—'} />
                <Row k="ratio" v={project.shotlist.ratio ?? '16:9'} />
                <Row k="scene" v={project.shotlist.scene} />
                <Row k="duration_total" v={`${project.shotlist.duration_total}s`} />
                <Row k="chain" v={project.shotlist.chain} />
                <Row k="role_cards" v={(project.shotlist.role_cards ?? []).join(', ') || '—'} />
              </>
            ) : (
              <p>暂无拍摄本参数</p>
            )}
          </CardContent>
        )}
      </Card>
      </div>
      )}
    </div>
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

function Picture({ n }: { n: number }) {
  return <span className="font-mono text-blue-400">&lt;Picture {n}&gt;</span>
}
