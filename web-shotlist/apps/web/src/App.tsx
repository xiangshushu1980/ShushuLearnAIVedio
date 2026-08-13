/**
 * 拍摄本看板 —— 三大步骤页（用户确认 2026-08-12）
 * 页 0 剧本：剧本生成/编辑 + 实体制作（AI 抽取/设定图）
 * 页 1 拍摄本：剧本 → 拍摄内容（卡片流+时间轴+实体关联，可回剧本改）
 * 页 2 H3 提示词：调试检查（标色/校验），连接视频生成与预览（V2）
 * 顶栏：Tab 导航（主入口）；删除/回收站 = 右侧次要入口
 */
import { useEffect, useRef, useState, type ReactNode } from 'react'
import * as React from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { PromptMode } from '@shotlist/shared'
import { api } from '@/lib/api'
import { useAppStore, type PageId } from '@/lib/store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ConfirmDialog } from '@/components/ui/dialog'
import { NewProjectDialog } from '@/components/NewProjectDialog'
import { ImportDialog, RenameDialog, StyleDialog } from '@/components/ProjectDialogs'
import { ScriptPanel } from '@/components/script/ScriptPanel'
import { EntityPanel } from '@/components/sidebar/EntityPanel'
import { EntityDialogHost } from '@/components/entity/EntityDialogs'
import { ShotListView } from '@/components/shotlist/ShotListView'
import { PromptPage } from '@/components/prompt/PromptPage'
import { TrashPanel } from '@/components/trash/TrashPanel'

/** 错误边界：局部组件崩溃不冻结全屏（可刷新恢复） */
class ErrorBoundary extends React.Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) {
    return { error }
  }
  render() {
    if (this.state.error) {
      return (
        <div className="flex h-full flex-col items-center justify-center gap-2 p-8 text-center">
          <p className="text-sm font-semibold text-red-300">界面出错了</p>
          <p className="max-w-md break-all text-xs text-slate-400">{this.state.error.message}</p>
          <button
            onClick={() => {
              this.setState({ error: null })
              window.location.reload()
            }}
            className="mt-2 rounded-md bg-blue-600 px-4 py-1.5 text-xs text-white hover:bg-blue-500"
          >
            重新加载
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

const PAGES: Array<{ id: PageId; label: string; hint: string }> = [
  { id: 0, label: '① 剧本', hint: '剧本 · 实体 · 设定图' },
  { id: 1, label: '② 拍摄本', hint: '镜头 · 关联实体' },
  { id: 2, label: '③ H3 提示词', hint: '调试 · 检查 · 视频' },
]

export default function App() {
  const qc = useQueryClient()
  const { page, setPage, project, setProject, setScriptDraft, setBusy, setError, error, saveState, setSaveState } = useAppStore()
  const [projectId, setProjectId] = useState<string | null>(null)
  const [newOpen, setNewOpen] = useState(false)
  const [trashOpen, setTrashOpen] = useState(false)
  const [opsOpen, setOpsOpen] = useState(false)
  const [confirmTrash, setConfirmTrash] = useState(false)
  const [renameOpen, setRenameOpen] = useState(false)
  const [importOpen, setImportOpen] = useState(false)
  const [styleOpen, setStyleOpen] = useState(false)
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
    mutationFn: ({ name, script }: { name: string; script?: string }) => api.createProject({ name, script }),
    onSuccess: (p) => {
      setProjectId(p.meta.id)
      setPage(0)
      if (p.script?.raw) setScriptDraft(p.script.raw)
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

  // 导出项目 JSON 包（下载）
  const exportMut = useMutation({
    mutationFn: async () => {
      const pack = await api.exportProject(projectId!)
      const blob = new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${pack.name || projectId}.shotlist.json`
      a.click()
      URL.revokeObjectURL(url)
    },
    onError: (e) => setError((e as Error).message),
  })

  const genShotlistMut = useMutation({
    mutationFn: async (shotStyle?: '分镜剪辑' | '长镜头流') => {
      const ok = await flushSave()
      if (!ok) throw new Error('剧本保存失败，未生成')
      return api.generateShotlist(projectId!, { model: 'deepseek-v4-flash', effort: 'high', shotStyle })
    },
    onMutate: () => setBusy('shotlist'),
    onSuccess: async (r) => {
      setBusy(null)
      if (r.review) setError(`导演自审：\n${r.review}`)
      await refresh()
      setPage(1) // 生成成功 → 拍摄本页
    },
    onError: (e) => {
      setBusy(null)
      setError((e as Error).message)
    },
  })

  const genPromptMut = useMutation({
    mutationFn: (mode: PromptMode) => api.generatePrompt(projectId!, { mode, model: 'deepseek-v4-flash', effort: 'high' }),
    onMutate: () => setBusy('prompt'),
    onSuccess: async (r) => {
      setBusy(null)
      const warns = (r as { gate?: { warns: string[] } }).gate?.warns
      if (warns?.length) setError(`门禁警告（可后补）：${warns.slice(0, 3).join('；')}`)
      await refresh()
      setPage(2) // 生成成功 → 提示词页
    },
    onError: (e) => {
      setBusy(null)
      setError((e as Error).message)
    },
  })

  return (
    <ErrorBoundary>
      <div className="flex h-full flex-col">
      {/* 顶栏：Tab 主入口 + 项目选择；删除/回收站右侧次要入口 */}
      <header className="flex items-center gap-2 border-b border-slate-800 bg-slate-900/80 px-4 py-1.5">
        <h1 className="mr-1 text-sm font-bold text-slate-100">拍摄本看板</h1>
        {/* 三大步骤 Tab */}
        <nav className="flex gap-0.5">
          {PAGES.map((p) => (
            <button
              key={p.id}
              onClick={() => setPage(p.id)}
              title={p.hint}
              className={cn(
                'rounded-md px-3 py-1.5 text-xs transition-colors',
                page === p.id ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200',
              )}
            >
              {p.label}
            </button>
          ))}
        </nav>

        <select
          value={projectId ?? ''}
          onChange={(e) => setProjectId(e.target.value || null)}
          className="ml-2 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-200"
        >
          <option value="">选择项目…</option>
          {(projects ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        {/* 任务全局可见：当前项目 + 三步骤完成度指示 */}
        {project && (
          <span className="ml-2 flex items-center gap-1.5 rounded border border-slate-800 bg-slate-950/60 px-2 py-1 text-[11px]">
            <span className="max-w-40 truncate font-semibold text-slate-200">{project.meta.name}</span>
            <span className="text-slate-600">|</span>
            {[
              { label: '剧本', ok: !!project.script?.raw },
              { label: '拍摄本', ok: !!project.shotlist },
              { label: '提示词', ok: !!project.prompt },
            ].map((s) => (
              <span key={s.label} title={s.ok ? `${s.label} 已有` : `${s.label} 未生成`} className={s.ok ? 'text-emerald-400' : 'text-slate-600'}>
                {s.ok ? '✓' : '○'} {s.label}
              </span>
            ))}
          </span>
        )}
        <Button size="sm" variant="secondary" onClick={() => setNewOpen(true)} title="新建项目" className="px-2.5">
          +
        </Button>
        <Button size="sm" variant="secondary" onClick={() => setImportOpen(true)} title="导入项目包" className="px-2.5">
          ⇪ 导入
        </Button>
        <Button size="sm" variant="secondary" onClick={() => setStyleOpen(true)} title="全局风格（设定图）" className="px-2.5">
          ⚙ 风格
        </Button>

        {error && (
          <button onClick={() => setError(null)} className="ml-auto max-w-[35%] truncate rounded bg-red-950/60 px-2 py-1 text-[11px] text-red-300" title={error}>
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
                <div className="absolute right-0 top-full z-20 mt-1 w-40 rounded border border-slate-700 bg-slate-900 py-1 shadow-xl">
                  <button
                    onMouseDown={() => {
                      setOpsOpen(false)
                      setRenameOpen(true)
                    }}
                    className="w-full px-3 py-1.5 text-left text-[11px] text-slate-300 hover:bg-slate-800"
                  >
                    重命名项目
                  </button>
                  <button
                    onMouseDown={() => {
                      setOpsOpen(false)
                      exportMut.mutate()
                    }}
                    className="w-full px-3 py-1.5 text-left text-[11px] text-slate-300 hover:bg-slate-800"
                  >
                    导出项目（JSON 包）
                  </button>
                  <div className="my-1 border-t border-slate-800" />
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

      {/* 页面主体 */}
      {project ? (
        page === 0 ? (
          <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_300px] gap-2 p-2">
            <div className="min-h-0">
              <ScriptPanel onGenerate={() => genShotlistMut.mutate(undefined)} />
            </div>
            <div className="min-h-0 rounded-lg border border-slate-800 bg-slate-900/40 p-2">
              <div className="mb-1.5 text-xs font-semibold text-slate-300">实体库</div>
              <EntityPanel />
            </div>
          </div>
        ) : page === 1 ? (
          <ShotListView
            onRegenerate={(style) => genShotlistMut.mutate(style)}
            onGoPrompt={() => setPage(2)}
          />
        ) : (
          <PromptPage onGenerate={(m) => genPromptMut.mutate(m)} />
        )
      ) : (
        <div className="flex flex-1 items-center justify-center text-xs text-slate-500">
          新建项目或从下拉选择已有项目（①剧本 → ②拍摄本 → ③H3 提示词）
        </div>
      )}

      {/* 弹层 */}
      <NewProjectDialog open={newOpen} onClose={() => setNewOpen(false)} onCreated={(id) => setProjectId(id)} />
      <ImportDialog open={importOpen} onClose={() => setImportOpen(false)} onImported={(id) => setProjectId(id)} />
      <StyleDialog open={styleOpen} onClose={() => setStyleOpen(false)} />
      {projectId && (
        <RenameDialog
          open={renameOpen}
          onClose={() => setRenameOpen(false)}
          projectId={projectId}
          currentName={project?.meta.name ?? ''}
          onRenamed={() => {
            qc.invalidateQueries({ queryKey: ['projects'] })
            qc.invalidateQueries({ queryKey: ['project', projectId] })
          }}
        />
      )}
      <ConfirmDialog
        open={confirmTrash}
        onClose={() => setConfirmTrash(false)}
        onConfirm={() => trashMut.mutate()}
        title="删除项目"
        message={`「${project?.meta.name}」将移入回收站（剧本/拍摄本/提示词完整保留，可恢复）。`}
        confirmLabel="移入回收站"
      />
      <TrashPanel open={trashOpen} onClose={() => setTrashOpen(false)} />
      <EntityDialogHost />
      </div>
    </ErrorBoundary>
  )
}
