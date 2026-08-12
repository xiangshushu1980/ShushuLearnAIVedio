/**
 * 页 1 拍摄本：时间轴概览 + 卡片流（两列）+ 跳转高亮 + 镜头主体关联实体
 * 流程：可返回剧本修改并重新生成拍摄本；生成提示词 → 页 2
 */
import { useEffect, useRef, useState } from 'react'
import { yamlStringify } from '@shotlist/shared'
import { useQuery } from '@tanstack/react-query'
import type { Shot, Shotlist } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { EntityPickerDialog } from '@/components/entity/EntityDialogs'
import { TimelineBar } from './TimelineBar'
import { ShotCard } from './ShotCard'

interface Props {
  onRegenerate: () => void
  onGoPrompt: () => void
}

export function ShotListView({ onRegenerate, onGoPrompt }: Props) {
  const { project, setProject, setError, jumpShot, clearJump, busy, setPage } = useAppStore()
  const shotlist = project?.shotlist
  const [pickFor, setPickFor] = useState<Shot | null>(null)
  const [highlight, setHighlight] = useState<number | null>(null)
  const cardRefs = useRef<Record<number, HTMLDivElement | null>>({})
  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })

  // 跨页跳转：页 2 提示词 [Shot N] → 本页高亮镜头
  useEffect(() => {
    if (jumpShot != null) {
      setHighlight(jumpShot)
      cardRefs.current[jumpShot]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      const t = setTimeout(() => {
        setHighlight(null)
        clearJump()
      }, 2000)
      return () => clearTimeout(t)
    }
  }, [jumpShot, clearJump])

  // 镜头主体 → 关联实体（保存回拍摄本文件）
  const applySubject = async (shot: Shot, entityId: string) => {
    if (!shotlist || !project) return
    const entity = entities.find((e) => e.id === entityId)
    const next: Shotlist = {
      ...shotlist,
      shots: shotlist.shots.map((s) => (s.id === shot.id ? { ...s, subject: entity?.name ?? entityId } : s)),
    }
    setProject({ ...project, shotlist: next })
    setPickFor(null)
    try {
      await api.saveProject(project.meta.id, { shotlist: yamlStringify(next) })
    } catch (e) {
      setError(`保存失败: ${(e as Error).message}`)
    }
  }

  return (
    <div className="flex h-full flex-col gap-2 p-2">
      {/* 顶部：信息 + 操作 */}
      <Card className="shrink-0">
        <CardContent className="p-2.5">
          <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-semibold text-slate-200">
              ② 拍摄本
              {shotlist && (
                <span className="ml-2 text-[11px] font-normal text-slate-500">
                  {shotlist.title} · {shotlist.shots.length} 镜 · {shotlist.duration_total}s · {shotlist.chain}
                </span>
              )}
            </span>
            <div className="flex gap-1.5">
              <Button size="sm" variant="ghost" onClick={() => setPage(0)} title="回剧本修改">
                ← 回剧本
              </Button>
              <Button size="sm" variant="secondary" onClick={onRegenerate} loading={busy === 'shotlist'} disabled={!project?.script?.raw}>
                重新生成
              </Button>
              <Button size="sm" onClick={onGoPrompt} disabled={!shotlist}>
                生成提示词 →
              </Button>
            </div>
          </div>
          {shotlist && <TimelineBar shots={shotlist.shots} total={shotlist.duration_total} />}
          {!shotlist && <p className="text-[11px] text-slate-500">暂无拍摄本 —— ①剧本页生成，或改剧本后重新生成（可反复调整）</p>}
        </CardContent>
      </Card>

      {/* 卡片流（两列） */}
      {shotlist ? (
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="grid grid-cols-2 gap-2 pb-1">
            {shotlist.shots.map((s) => (
              <div key={s.id} ref={(el) => { cardRefs.current[s.id] = el }} className={highlight === s.id ? 'rounded-lg ring-2 ring-cyan-400' : ''}>
                <ShotCard shot={s} onSubjectClick={() => setPickFor(s)} />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center rounded border border-dashed border-slate-800 text-xs text-slate-600">
          ①剧本页生成拍摄本后在此展示
        </div>
      )}

      {/* 镜头主体关联实体 */}
      <EntityPickerDialog
        open={!!pickFor}
        onClose={() => setPickFor(null)}
        title={`镜头 #${pickFor?.id} 主体关联（当前：${pickFor?.subject}）`}
        onPick={(id) => pickFor && applySubject(pickFor, id)}
      />
    </div>
  )
}
