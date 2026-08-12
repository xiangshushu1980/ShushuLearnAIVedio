/**
 * 镜头卡片（docs/22 拍摄本区竖排卡片流）
 * 实体 chip：类型定色 + 重要度边框（V1 基础版，实体数据为空时用默认角色色）
 */
import { ENTITY_TYPE_COLORS, IMPORTANCE_LABEL, SOUND_LAYER_COLORS, type EntityImportance, type EntityType, type Shot } from '@shotlist/shared'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

export function EntityChip({ name, type = '角色', importance = 'core' }: { name: string; type?: EntityType; importance?: EntityImportance }) {
  const c = ENTITY_TYPE_COLORS[type] ?? ENTITY_TYPE_COLORS['角色']
  const border = importance === 'core' ? 'border-2 border-solid' : 'border border-dashed'
  return (
    <span
      className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium', c.bg, c.text, border, border === 'border-2 border-solid' ? 'border-current' : 'border-current/60')}
      title={`${type} · ${IMPORTANCE_LABEL[importance]}`}
    >
      {name}
    </span>
  )
}

export function ShotCard({ shot }: { shot: Shot }) {
  const cam = shot.camera
  const camDesc = [cam.type, cam.amplitude, cam.speed].filter(Boolean).join(' · ')
  return (
    <Card className="border-slate-800 hover:border-slate-600 transition-colors" data-shot-id={shot.id}>
      <CardContent className="p-3 space-y-2">
        {/* 头部：镜号/时长/景别/运动 */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-slate-950 px-2 py-0.5 text-sm font-bold text-cyan-300 ring-1 ring-slate-700">#{shot.id}</span>
          <span className="text-xs text-slate-400">{shot.duration_s.toFixed(1)}s</span>
          <Badge variant="secondary">{shot.framing}</Badge>
          <Badge variant="outline" className="italic text-fuchsia-300">🎥 {camDesc}</Badge>
        </div>

        {/* 主体 chip */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] uppercase tracking-wide text-slate-500">主体</span>
          <EntityChip name={shot.subject} />
        </div>

        {/* 动作 */}
        <p className="text-sm leading-relaxed text-slate-200">{shot.action}</p>

        {/* 台词 */}
        {shot.dialogue?.length ? (
          <div className="space-y-1 rounded border-l-2 border-blue-500 bg-blue-950/30 pl-2">
            {shot.dialogue.map((d, i) => (
              <p key={i} className="text-sm text-blue-100">
                <EntityChip name={d.speaker === 'off_screen' ? '画外音' : d.speaker} />
                <span className="ml-1.5">「{d.text}」</span>
              </p>
            ))}
          </div>
        ) : null}

        {/* 声音三层 */}
        <div className="flex flex-wrap gap-1.5">
          {shot.sound.ambient && <SoundTag layer="ambient" v={shot.sound.ambient} />}
          {shot.sound.fx && <SoundTag layer="fx" v={shot.sound.fx} />}
          <SoundTag layer="bgm" v={shot.sound.bgm} />
        </div>

        {/* 连续性 */}
        {shot.continuity && (
          <p className="border-t border-slate-800 pt-1.5 text-xs leading-relaxed text-slate-400">
            <span className="text-slate-500">连续性 · </span>
            {shot.continuity}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function SoundTag({ layer, v }: { layer: 'ambient' | 'fx' | 'bgm'; v: string }) {
  const c = SOUND_LAYER_COLORS[layer]
  const label = layer === 'ambient' ? '环境' : layer === 'fx' ? 'fx' : 'bgm'
  return (
    <span className={cn('inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs', c)} title={label}>
      🔊 {v}
    </span>
  )
}
