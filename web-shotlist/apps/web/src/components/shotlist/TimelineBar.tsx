/**
 * 时间轴概览横条（docs/22 拍摄本区顶部）
 * 只显示切点/景别/运动，不承担主阅读
 */
import type { Shot } from '@shotlist/shared'
import { cn } from '@/lib/utils'

export function TimelineBar({ shots, total }: { shots: Shot[]; total: number }) {
  if (!shots.length) return null
  let acc = 0
  const segs = shots.map((s) => {
    const start = acc
    acc += s.duration_s
    return { shot: s, start, end: acc }
  })
  return (
    <div className="w-full space-y-1">
      <div className="relative h-6 w-full overflow-hidden rounded bg-slate-900 ring-1 ring-slate-700">
        {segs.map(({ shot, start, end }) => (
          <div
            key={shot.id}
            className={cn('absolute top-0 h-full border-r border-slate-950', (shot.id - 1) % 2 ? 'bg-cyan-900/70' : 'bg-cyan-800/70')}
            style={{ left: `${(start / total) * 100}%`, width: `${((end - start) / total) * 100}%` }}
            title={`#${shot.id} ${shot.framing} · ${shot.camera.type} · ${shot.duration_s}s`}
          >
            <span className="px-1 text-[10px] leading-6 text-cyan-100">{shot.id}</span>
          </div>
        ))}
      </div>
      <div className="relative h-4 w-full">
        {segs.map(({ shot, start }) => (
          <span key={shot.id} className="absolute -translate-x-1/2 text-[10px] text-slate-500" style={{ left: `${(start / total) * 100}%` }}>
            {formatTs(start)}
          </span>
        ))}
        <span className="absolute right-0 -translate-x-0 text-[10px] text-slate-500">{formatTs(total)}</span>
      </div>
    </div>
  )
}

function formatTs(s: number): string {
  const m = Math.floor(s / 60)
  const sec = (s % 60).toFixed(1).padStart(4, '0')
  return `${m}:${sec}`
}
