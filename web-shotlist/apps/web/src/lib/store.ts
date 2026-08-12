import { create } from 'zustand'
import type { Project } from '@shotlist/shared'

interface AppState {
  project: Project | null
  scriptDraft: string
  busy: 'shotlist' | 'prompt' | null
  error: string | null
  setProject: (p: Project | null) => void
  setScriptDraft: (t: string) => void
  setBusy: (b: 'shotlist' | 'prompt' | null) => void
  setError: (e: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  project: null,
  scriptDraft: '',
  busy: null,
  error: null,
  setProject: (project) => set({ project }),
  setScriptDraft: (scriptDraft) => set({ scriptDraft }),
  setBusy: (busy) => set({ busy }),
  setError: (error) => set({ error }),
}))
