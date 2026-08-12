/**
 * 实体卡面板（页 0 右栏）：列表 + 新建 + AI 抽取；详情/编辑/设定图走全局弹层
 */
import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ENTITY_TYPE_COLORS, IMPORTANCE_LABEL, type Entity } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { EntityPickerDialog } from '@/components/entity/EntityDialogs'
import { ExtractDialog } from '@/components/entity/ExtractDialog'

export function EntityPanel() {
  const openEntity = useAppStore((s) => s.openEntity)
  const qc = useQueryClient()
  const [extractOpen, setExtractOpen] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importMsg, setImportMsg] = useState<string | null>(null)

  const { data: entities = [] } = useQuery({ queryKey: ['entities'], queryFn: api.listEntities })
  // 三态门禁（文字/画面/声音）——列表可观测
  const { data: gate } = useQuery({
    queryKey: ['entity-gate'],
    queryFn: () => api.gateEntities(entities.map((e) => e.id)),
    enabled: entities.length > 0,
  })
  const gateMap = new Map((gate?.checks ?? []).map((c) => [c.id, c]))

  const importCards = async () => {
    setImporting(true)
    try {
      const r = await api.importRolecards()
      setImportMsg(`已导入 ${r.imported} 张角色卡`)
      qc.invalidateQueries({ queryKey: ['entities'] })
      qc.invalidateQueries({ queryKey: ['entity-gate'] })
    } catch (e) {
      useAppStore.getState().setError((e as Error).message)
    } finally {
      setImporting(false)
    }
  }

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
      <div className="flex items-center justify-between">
        <p className="text-[10px] leading-relaxed text-slate-600">实体从剧本+世界观获得：AI 抽取自动生成实体卡并保存为文件；也可手动新建</p>
        <button onClick={importCards} disabled={importing} className="shrink-0 rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-400 hover:bg-slate-800" title="从 experiments/shotlist/rolecards 导入旧角色卡">
          {importing ? '导入中…' : '导入角色卡'}
        </button>
      </div>
      {importMsg && <p className="text-[10px] text-emerald-400">✓ {importMsg}</p>}
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
          const g = gateMap.get(e.id)
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
              <span className="flex min-w-0 items-center gap-1.5">
                <span className={cn('truncate text-xs font-medium', c.text)}>{e.name}</span>
                {g && (
                  <span className="flex shrink-0 gap-0.5">
                    <span title="文字" className={g.text.ok ? 'text-emerald-500' : 'text-red-400'}>文</span>
                    <span title="画面" className={g.art.ok ? 'text-emerald-500' : 'text-amber-400'}>画</span>
                    <span title="声音" className={g.voice.ok ? 'text-emerald-500' : 'text-amber-400'}>声</span>
                  </span>
                )}
              </span>
              <span className={cn('shrink-0 text-[10px] opacity-70', c.text)}>
                {e.type} · {(e as Entity & { stars?: number }).stars ?? (e.importance === 'core' ? 4 : 2)}★
              </span>
            </button>
          )
        })}
      </div>
      {extractOpen && <ExtractDialog onClose={() => setExtractOpen(false)} />}
    </div>
  )
}
