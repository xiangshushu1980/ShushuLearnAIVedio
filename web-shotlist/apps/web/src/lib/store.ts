import { create } from 'zustand'
import type { Project } from '@shotlist/shared'

export type SaveState = 'saved' | 'saving' | 'dirty'

interface AppState {
  project: Project | null
  scriptDraft: string
  /** 保存状态：saved=已落盘 / saving=保存中 / dirty=有未保存改动 */
  saveState: SaveState
  busy: 'shotlist' | 'prompt' | null
  error: string | null
  setProject: (p: Project | null) => void
  setScriptDraft: (t: string) => void
  setSaveState: (s: SaveState) => void
  setBusy: (b: 'shotlist' | 'prompt' | null) => void
  setError: (e: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  project: null,
  scriptDraft: '',
  saveState: 'saved',
  busy: null,
  error: null,
  setProject: (project) => set({ project }),
  setScriptDraft: (scriptDraft) => set({ scriptDraft }),
  setSaveState: (saveState) => set({ saveState }),
  setBusy: (busy) => set({ busy }),
  setError: (error) => set({ error }),
}))
