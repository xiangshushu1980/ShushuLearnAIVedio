/**
 * 实体卡面板（页 0 右栏）：列表 + 新建 + AI 抽取；详情/编辑/设定图走全局弹层
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ENTITY_TYPE_COLORS, IMPORTANCE_LABEL, type Entity } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { EntityPickerDialog } from '@/components/entity/EntityDialogs'
import { ExtractDialog } from '@/components/entity/ExtractDialog'

export function EntityPanel() {
  const openEntity = useAppStore((s) => s.openEntity)
  const [extractOpen, setExtractOpen] = useState(false)

  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })

  return (
    <div className="flex h-full flex-col gap-2">
      <div className="flex gap-1.5">
        <Button size="sm" variant="outline" className="flex-1" onClick={() => openEntity('__new__')}>
          + 新建
        </Button>
        <Button size="sm" variant="secondary" className="flex-1" onClick={() => setExtractOpen(true)}>
          AI 抽取（剧本+世界观）
        </Button>
      </div>
      <p className="text-[10px] leading-relaxed text-slate-600">实体从剧本+世界观获得：AI 抽取自动生成实体卡并保存为文件；也可手动新建</p>
      <div className="min-h-0 flex-1 space-y-1.5 overflow-y-auto">
        {entities.length === 0 && (
          <div className="rounded border border-dashed border-slate-800 p-3 text-center text-[11px] text-slate-600">
            实体库为空
            <br />
            用右上 AI 抽取，从剧本+世界观生成实体卡
          </div>
        )}
        {entities.map((e) => {
          const c = ENTITY_TYPE_COLORS[e.type] ?? ENTITY_TYPE_COLORS['角色']
          return (
            <button
              key={e.id}
              onClick={() => openEntity(e.id)}
              className={cn(
                'flex w-full items-center justify-between rounded border px-2 py-1.5 text-left transition-colors hover:bg-slate-800/60',
                c.bg,
                e.importance === 'core' ? 'border-solid border-current' : 'border-dashed border-current/60',
              )}
            >
              <span className={cn('truncate text-xs font-medium', c.text)}>{e.name}</span>
              <span className={cn('shrink-0 text-[10px] opacity-70', c.text)}>
                {e.type} · {IMPORTANCE_LABEL[e.importance]}
              </span>
            </button>
          )
        })}
      </div>
      {extractOpen && <ExtractDialog onClose={() => setExtractOpen(false)} />}
    </div>
  )
}
