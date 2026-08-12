/**
 * 拍摄本看板主布局（docs/22 二节）
 * ┌─────────────┬──────────────────────────┬──────────┐
 * │ ① 剧本区     │ ② 拍摄本区（卡片流+时间轴） │ ③ 侧栏    │
 * ├─────────────┴──────────────────────────┴──────────┤
 * │ ④ 输出区：H3 提示词（标色，只读）                    │
 * └───────────────────────────────────────────────────┘
 * 顶栏：主入口区（项目选择/新建）留白给后续功能；删除/回收站 = 右侧次要入口
 */
import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { scriptTemplate, type PromptMode } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { ConfirmDialog } from '@/components/ui/dialog'
import { ScriptPanel } from '@/components/script/ScriptPanel'
import { ShotList } from '@/components/shotlist/ShotList'
import { SidebarPanel } from '@/components/sidebar/SidebarPanel'
import { OutputPanel } from '@/components/prompt/OutputPanel'
import { TrashPanel } from '@/components/trash/TrashPanel'

export default function App() {
  const qc = useQueryClient()
  const [projectId, setProjectId] = useState<string | null>(null)
  const [newName, setNewName] = useState('')
  const [trashOpen, setTrashOpen] = useState(false)
  const [opsOpen, setOpsOpen] = useState(false)
  const [confirmTrash, setConfirmTrash] = useState(false)
  const { project, setProject, setScriptDraft, setBusy, setError, error, saveState, setSaveState } = useAppStore()
  const lastSavedRef = useRef('')

  // 项目列表
  const { data: projects } = useQuery({ queryKey: ['projects'], queryFn: api.listProjects })

  // 回收站数量（顶栏角标）
  const { data: trashItems = [] } = useQuery({ queryKey: ['trash'], queryFn: api.listTrash })

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
      lastSavedRef.current = fetched.script?.raw ?? ''
    }
  }, [fetched, setProject, setScriptDraft])

  // 自动保存：剧本改动 → 防抖 2s PUT
  const scriptDraft = useAppStore((s) => s.scriptDraft)
  useEffect(() => {
    if (!projectId || !scriptDraft) return
    if (scriptDraft === lastSavedRef.current) return
    setSaveState('dirty')
    const t = setTimeout(async () => {
      setSaveState('saving')
      try {
        await api.saveProject(projectId, { script: scriptDraft })
        lastSavedRef.current = scriptDraft
        setSaveState('saved')
      } catch (e) {
        setError(`保存失败: ${(e as Error).message}`)
        setSaveState('dirty')
      }
    }, 2000)
    return () => clearTimeout(t)
  }, [scriptDraft, projectId, setSaveState, setError])

  // 生成前强制落盘（避免用旧剧本生成）
  const flushSave = async (): Promise<boolean> => {
    if (!projectId) return false
    const draft = useAppStore.getState().scriptDraft
    if (draft && draft !== lastSavedRef.current) {
      try {
        await api.saveProject(projectId, { script: draft })
        lastSavedRef.current = draft
      } catch (e) {
        setError(`保存失败: ${(e as Error).message}`)
        return false
      }
    }
    return true
  }

  const refresh = () => qc.invalidateQueries({ queryKey: ['project', projectId] })

  const createMut = useMutation({
    mutationFn: () => api.createProject({ name: newName }),
    onSuccess: (p) => {
      setProjectId(p.meta.id)
      setScriptDraft(scriptTemplate(p.meta.name)) // 模板预填
      setNewName('')
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
    onError: (e) => setError((e as Error).message),
  })

  const trashMut = useMutation({
    mutationFn: () => api.trashProject(projectId!),
    onSuccess: async () => {
      setProjectId(null)
      setProject(null)
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['trash'] })
    },
    onError: (e) => setError((e as Error).message),
  })

  const genShotlistMut = useMutation({
    mutationFn: async () => {
      const ok = await flushSave()
      if (!ok) throw new Error('剧本保存失败，未生成')
      return api.generateShotlist(projectId!, { model: 'deepseek-v4-flash', effort: 'high' })
    },
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
      {/* 顶栏：主入口区在左，删除/回收站等次要操作在右 */}
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
          <button onClick={() => setError(null)} className="ml-auto max-w-[40%] truncate rounded bg-red-950/60 px-2 py-1 text-[11px] text-red-300" title={error}>
            ⚠ {error.slice(0, 80)}
          </button>
        )}

        {/* 次要入口区（右侧）：项目操作（删除）+ 回收站 */}
        <div className="ml-auto flex items-center gap-1.5">
          {projectId && (
            <div className="relative">
              <button
                onClick={() => setOpsOpen((v) => !v)}
                onBlur={() => setTimeout(() => setOpsOpen(false), 150)}
                className="rounded border border-slate-700 px-2 py-1 text-[11px] text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              >
                项目操作 ▾
              </button>
              {opsOpen && (
                <div className="absolute right-0 top-full z-20 mt-1 w-32 rounded border border-slate-700 bg-slate-900 py-1 shadow-xl">
                  <button
                    onMouseDown={() => setConfirmTrash(true)}
                    className="w-full px-3 py-1.5 text-left text-[11px] text-red-400 hover:bg-slate-800"
                  >
                    删除项目（回收站）
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            onClick={() => setTrashOpen(true)}
            className="relative rounded border border-slate-700 px-2 py-1 text-[11px] text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            title="回收站"
          >
            🕘 回收站
            {trashItems.length > 0 && (
              <span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-600 px-1 text-[9px] font-bold text-white">
                {trashItems.length}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* 三段式 + 输出区 */}
      {project ? (
        <div className="grid min-h-0 flex-1 grid-cols-[340px_minmax(0,1fr)_260px] grid-rows-[minmax(0,1fr)_260px] gap-0">
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

      {/* 弹层：确认删除 / 回收站 */}
      <ConfirmDialog
        open={confirmTrash}
        onClose={() => setConfirmTrash(false)}
        onConfirm={() => trashMut.mutate()}
        title="删除项目"
        message={`「${project?.meta.name}」将移入回收站（剧本/拍摄本/提示词完整保留，可恢复）。`}
        confirmLabel="移入回收站"
      />
      <TrashPanel open={trashOpen} onClose={() => setTrashOpen(false)} />
    </div>
  )
}
