/**
 * 拍摄本看板主布局（docs/22 二节）
 * ┌─────────────┬──────────────────────────┬──────────┐
 * │ ① 剧本区     │ ② 拍摄本区（卡片流+时间轴） │ ③ 侧栏    │
 * ├─────────────┴──────────────────────────┴──────────┤
 * │ ④ 输出区：H3 提示词（标色，只读）                    │
 * └───────────────────────────────────────────────────┘
 */
import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { PromptMode } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { ScriptPanel } from '@/components/script/ScriptPanel'
import { ShotList } from '@/components/shotlist/ShotList'
import { SidebarPanel } from '@/components/sidebar/SidebarPanel'
import { OutputPanel } from '@/components/prompt/OutputPanel'

export default function App() {
  const qc = useQueryClient()
  const [projectId, setProjectId] = useState<string | null>(null)
  const [newName, setNewName] = useState('')
  const { project, setProject, setScriptDraft, setBusy, setError, error } = useAppStore()

  // 项目列表
  const { data: projects } = useQuery({ queryKey: ['projects'], queryFn: api.listProjects })

  // 当前项目
  const { data: fetched } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.getProject(projectId!),
    enabled: !!projectId,
  })
  useEffect(() => {
    if (fetched) {
      setProject(fetched)
      setScriptDraft(fetched.script?.raw ?? '')
    }
  }, [fetched, setProject, setScriptDraft])

  const refresh = () => qc.invalidateQueries({ queryKey: ['project', projectId] })

  const createMut = useMutation({
    mutationFn: () => api.createProject({ name: newName }),
    onSuccess: (p) => {
      setProjectId(p.meta.id)
      setNewName('')
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
    onError: (e) => setError((e as Error).message),
  })

  const genShotlistMut = useMutation({
    mutationFn: () => api.generateShotlist(projectId!, { model: 'deepseek-v4-flash', effort: 'high' }),
    onMutate: () => setBusy('shotlist'),
    onSuccess: async (r) => {
      setBusy(null)
      if (r.review) setError(`导演自审：\n${r.review}`)
      await refresh()
    },
    onError: (e) => {
      setBusy(null)
      setError((e as Error).message)
    },
  })

  const genPromptMut = useMutation({
    mutationFn: (mode: PromptMode) => api.generatePrompt(projectId!, { mode, model: 'deepseek-v4-flash', effort: 'high' }),
    onMutate: () => setBusy('prompt'),
    onSuccess: async () => {
      setBusy(null)
      await refresh()
    },
    onError: (e) => {
      setBusy(null)
      setError((e as Error).message)
    },
  })

  return (
    <div className="flex h-full flex-col">
      {/* 顶栏 */}
      <header className="flex items-center gap-3 border-b border-slate-800 bg-slate-900/80 px-4 py-2">
        <h1 className="text-sm font-bold text-slate-100">拍摄本看板</h1>
        <select
          value={projectId ?? ''}
          onChange={(e) => setProjectId(e.target.value || null)}
          className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200"
        >
          <option value="">选择项目…</option>
          {(projects ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && newName.trim() && createMut.mutate()}
          placeholder="新建项目名（回车）"
          className="w-44 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200 placeholder:text-slate-600"
        />
        <Button size="sm" variant="secondary" onClick={() => createMut.mutate()} disabled={!newName.trim()} loading={createMut.isPending}>
          新建
        </Button>
        {error && (
          <button onClick={() => setError(null)} className="ml-auto max-w-[50%] truncate rounded bg-red-950/60 px-2 py-1 text-[11px] text-red-300" title={error}>
            ⚠ {error.slice(0, 80)}
          </button>
        )}
      </header>

      {/* 三段式 + 输出区 */}
      {project ? (
        <div className="grid min-h-0 flex-1 grid-cols-[280px_minmax(0,1fr)_240px] grid-rows-[minmax(0,1fr)_240px] gap-0">
          <div className="min-h-0 border-r border-slate-800 p-2">
            <ScriptPanel onGenerate={() => genShotlistMut.mutate()} />
          </div>
          <div className="min-h-0 overflow-y-auto border-r border-slate-800 p-2">
            <ShotList />
          </div>
          <div className="min-h-0 p-2">
            <SidebarPanel project={project} />
          </div>
          <div className="col-span-3 min-h-0 border-t border-slate-800 p-2">
            <OutputPanel onGenerate={(m) => genPromptMut.mutate(m)} />
          </div>
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center text-xs text-slate-500">
          新建项目或从下拉选择已有项目（导入剧本 → 生成拍摄本 → 生成提示词）
        </div>
      )}
    </div>
  )
}
