import { create } from 'zustand'
import type { Project } from '@shotlist/shared'

export type SaveState = 'saved' | 'saving' | 'dirty'

/** 三个大步骤页（用户确认 2026-08-12：0=剧本 1=拍摄本 2=H3 提示词） */
export type PageId = 0 | 1 | 2

interface AppState {
  page: PageId
  project: Project | null
  scriptDraft: string
  /** 保存状态：saved=已落盘 / saving=保存中 / dirty=有未保存改动 */
  saveState: SaveState
  busy: 'shotlist' | 'prompt' | 'art' | null
  error: string | null
  /** 跨页跳转：目标镜头 id（页 3 [Shot N] → 页 2 高亮） */
  jumpShot: number | null
  /** 跨页跳转：实体详情 id（页 3 ref chip → 实体详情弹层） */
  entityDialogId: string | null
  setPage: (p: PageId) => void
  setProject: (p: Project | null) => void
  setScriptDraft: (t: string) => void
  setSaveState: (s: SaveState) => void
  setBusy: (b: 'shotlist' | 'prompt' | 'art' | null) => void
  setError: (e: string | null) => void
  gotoShot: (n: number) => void
  clearJump: () => void
  openEntity: (id: string) => void
  closeEntity: () => void
}

export const useAppStore = create<AppState>((set) => ({
  page: 0,
  project: null,
  scriptDraft: '',
  saveState: 'saved',
  busy: null,
  error: null,
  jumpShot: null,
  entityDialogId: null,
  setPage: (page) => set({ page }),
  setProject: (project) => set({ project }),
  setScriptDraft: (scriptDraft) => set({ scriptDraft }),
  setSaveState: (saveState) => set({ saveState }),
  setBusy: (busy) => set({ busy }),
  setError: (error) => set({ error }),
  gotoShot: (n) => set({ jumpShot: n, page: 1 }),
  clearJump: () => set({ jumpShot: null }),
  openEntity: (entityDialogId) => set({ entityDialogId }),
  closeEntity: () => set({ entityDialogId: null }),
}))
