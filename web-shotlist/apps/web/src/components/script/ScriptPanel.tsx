/**
 * ① 剧本区（docs/22 布局）：文本编辑框（粘贴/导入）+ [生成拍摄本]
 */
import { useRef } from 'react'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  onGenerate: () => void
}

export function ScriptPanel({ onGenerate }: Props) {
  const scriptDraft = useAppStore((s) => s.scriptDraft)
  const setScriptDraft = useAppStore((s) => s.setScriptDraft)
  const busy = useAppStore((s) => s.busy)
  const fileRef = useRef<HTMLInputElement>(null)

  const onImportFile = (f: File) => {
    const reader = new FileReader()
    reader.onload = () => setScriptDraft(String(reader.result ?? ''))
    reader.readAsText(f)
  }

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="border-b border-slate-800 pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">① 剧本</CardTitle>
          <div className="flex gap-1.5">
            <Button variant="outline" size="sm" onClick={() => fileRef.current?.click()}>
              导入
            </Button>
            <input
              ref={fileRef}
              type="file"
              accept=".yaml,.yml,.txt,.md"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && onImportFile(e.target.files[0])}
            />
          </div>
        </div>
        <p className="text-[11px] text-slate-500">YAML 参数头 + 正文（可粘贴或导入已有剧本）</p>
      </CardHeader>
      <CardContent className="flex min-h-0 flex-1 flex-col gap-2 p-3">
        <textarea
          value={scriptDraft}
          onChange={(e) => setScriptDraft(e.target.value)}
          placeholder={'---\ntitle: 场景标题\nstyle: ...\nratio: 16:9\nduration: 8\nrole_cards: [alya_v1]\nchain: independent\n---\n\n剧本正文……'}
          spellCheck={false}
          className="min-h-0 flex-1 resize-none rounded border border-slate-700 bg-slate-950 p-2 font-mono text-[12px] leading-relaxed text-slate-200 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
        />
        <Button onClick={onGenerate} loading={busy === 'shotlist'} disabled={!scriptDraft.trim()}>
          生成拍摄本
        </Button>
      </CardContent>
    </Card>
  )
}
