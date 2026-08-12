/**
 * ④ 输出区（docs/22 布局底部横贯）：H3 提示词（语法高亮/标色，只读）+ 复制/保存
 */
import { useState } from 'react'
import { checkPrompt, type PromptMode } from '@shotlist/shared'
import { useAppStore } from '@/lib/store'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { PromptHighlight } from './PromptHighlight'

interface Props {
  onGenerate: (mode: PromptMode) => void
}

export function OutputPanel({ onGenerate }: Props) {
  const project = useAppStore((s) => s.project)
  const busy = useAppStore((s) => s.busy)
  const [copied, setCopied] = useState(false)

  const prompt = project?.prompt
  const mode = project?.promptMode
  const check = prompt && mode ? checkPrompt(prompt, project.shotlist?.duration_total, mode === 'ref2va' ? 'ref2va' : 'i2va') : null

  const copy = async () => {
    if (!prompt) return
    await navigator.clipboard.writeText(prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <Card className="flex h-full min-h-0 flex-col">
      {/* 头部：模式切换 + 操作 */}
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-300">④ H3 提示词</span>
          <div className="flex gap-1">
            <ModeButton active={mode === 'i2va'} onClick={() => onGenerate('i2va')} loading={busy === 'prompt'} label="i2va 快车道" />
            <ModeButton active={mode === 'ref2va'} onClick={() => onGenerate('ref2va')} loading={busy === 'prompt'} label="ref2va 慢车道" />
          </div>
          {check && <CheckBadge check={check} />}
        </div>
        <div className="flex gap-1.5">
          <Button variant="outline" size="sm" onClick={copy} disabled={!prompt}>
            {copied ? '已复制' : '复制'}
          </Button>
        </div>
      </div>
      {/* 提示词只读标色视图 */}
      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {prompt ? (
          <PromptHighlight text={prompt} />
        ) : (
          <p className="text-xs text-slate-500">尚未生成提示词 —— 先在②区确认拍摄本，再点上方模式生成（或直接导入已有提示词）</p>
        )}
      </div>
    </Card>
  )
}

function ModeButton({ active, onClick, loading, label }: { active: boolean; onClick: () => void; loading: boolean; label: string }) {
  return (
    <Button size="sm" variant={active ? 'default' : 'outline'} onClick={onClick} loading={loading} disabled={loading}>
      {label}
    </Button>
  )
}

function CheckBadge({ check }: { check: ReturnType<typeof checkPrompt> }) {
  if (check.level === 'pass') return <Badge variant="success">校验通过 {check.shots} 镜</Badge>
  if (check.level === 'warn') return <Badge variant="warning" title={check.warns.join('\n')}>警告 {check.warns.length}</Badge>
  return <Badge variant="destructive" title={check.issues.join('\n')}>硬伤 {check.issues.length}</Badge>
}
