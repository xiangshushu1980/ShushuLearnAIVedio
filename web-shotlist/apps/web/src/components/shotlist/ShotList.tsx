/**
 * ② 拍摄本区：顶部时间轴概览横条 + 竖排卡片流
 */
import { useAppStore } from '@/lib/store'
import { TimelineBar } from './TimelineBar'
import { ShotCard } from './ShotCard'

export function ShotList() {
  const project = useAppStore((s) => s.project)
  const shotlist = project?.shotlist

  return (
    <div className="flex h-full flex-col gap-2">
      <div className="shrink-0 rounded border border-slate-800 bg-slate-900/60 p-2">
        <div className="mb-1 flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-300">② 拍摄本</span>
          {shotlist && (
            <span className="text-[11px] text-slate-500">
              {shotlist.title} · {shotlist.shots.length} 镜 · {shotlist.duration_total}s · {shotlist.chain}
            </span>
          )}
        </div>
        {shotlist && <TimelineBar shots={shotlist.shots} total={shotlist.duration_total} />}
      </div>
      {shotlist ? (
        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pb-1">
          {shotlist.shots.map((s) => (
            <ShotCard key={s.id} shot={s} />
          ))}
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center rounded border border-dashed border-slate-800 text-xs text-slate-600">
          ①区生成拍摄本后在此展示
        </div>
      )}
    </div>
  )
}
