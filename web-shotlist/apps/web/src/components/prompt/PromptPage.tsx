/**
 * 页 2 H3 提示词：一次调试和检查，连接视频生成和预览
 * 左=提示词标色（模式/校验/复制）；右=渲染输入源；底=视频生成预览（V2）
 */
import { useState } from 'react'
import { checkPrompt, type PromptMode } from '@shotlist/shared'
import { useAppStore } from '@/lib/store'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PromptHighlight } from './PromptHighlight'
import { InputsSidebar } from '@/components/sidebar/InputsSidebar'
import { EntityPickerDialog } from '@/components/entity/EntityDialogs'

interface Props {
  onGenerate: (mode: PromptMode) => void
}

export function PromptPage({ onGenerate }: Props) {
  const project = useAppStore((s) => s.project)
  const busy = useAppStore((s) => s.busy)
  const gotoShot = useAppStore((s) => s.gotoShot)
  const openEntity = useAppStore((s) => s.openEntity)
  const setPage = useAppStore((s) => s.setPage)
  const [copied, setCopied] = useState(false)
  const [pickerOpen, setPickerOpen] = useState(false)

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
    <div className="flex h-full min-h-0 flex-col gap-2 p-2">
      <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_240px] gap-2">
        {/* 左：提示词调试 */}
        <Card className="flex min-h-0 flex-col">
          <CardHeader className="border-b border-slate-800 pb-2">
            <div className="flex flex-wrap items-center gap-2">
              <CardTitle className="text-xs text-slate-300">③ H3 提示词（调试/检查）</CardTitle>
              <div className="flex gap-1">
                <ModeButton active={mode === 'i2va'} onClick={() => onGenerate('i2va')} loading={busy === 'prompt'} label="i2va 快车道" />
                <ModeButton active={mode === 'ref2va'} onClick={() => onGenerate('ref2va')} loading={busy === 'prompt'} label="ref2va 慢车道" />
              </div>
              {check && <CheckBadge check={check} />}
              <div className="ml-auto flex items-center gap-1.5">
                <Button variant="outline" size="sm" onClick={() => setPage(1)}>
                  ← 拍摄本
                </Button>
                <Button variant="outline" size="sm" onClick={copy} disabled={!prompt}>
                  {copied ? '已复制' : '复制'}
                </Button>
              </div>
            </div>
            <p className="text-[10px] text-slate-600">
              点击 <span className="text-cyan-300">[Shot N]</span> 跳转拍摄本镜头；点击{' '}
              <span className="text-blue-300">&lt;Subject N&gt;</span> 查看对应实体
            </p>
          </CardHeader>
          <CardContent className="min-h-0 flex-1 overflow-y-auto p-3">
            {prompt ? (
              <PromptHighlight
                text={prompt}
                onShotClick={(n) => gotoShot(n)}
                onRefClick={() => setPickerOpen(true)}
              />
            ) : (
              <p className="text-xs text-slate-500">尚未生成提示词 —— ②拍摄本页确认后，点上方模式生成（或导入已有提示词文件）</p>
            )}
          </CardContent>
        </Card>

        {/* 右：渲染输入源 */}
        <InputsSidebar project={project} />
      </div>

      <EntityPickerDialog
        open={pickerOpen}
        onClose={() => setPickerOpen(false)}
        title="选择实体查看"
        onPick={(id) => {
          openEntity(id)
          setPickerOpen(false)
        }}
      />

      {/* 底部：视频生成预览（V2） */}
      <Card className="shrink-0">
        <CardContent className="flex items-center justify-between p-2.5">
          <div className="text-[11px] text-slate-500">
            视频生成与预览（V2）：提交 ComfyUI + 进度回传（WebSocket）——当前阶段提示词仅为调试检查产物
          </div>
          <Button size="sm" variant="outline" disabled title="V2 开放">
            提交渲染（V2）
          </Button>
        </CardContent>
      </Card>
    </div>
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
