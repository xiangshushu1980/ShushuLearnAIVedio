/** API client（Fastify 后端，/api 前缀经 Vite proxy） */
import type { Project, ProjectMeta } from '@shotlist/shared'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as { error?: string } | null
    throw new Error(body?.error ?? `HTTP ${r.status}`)
  }
  return r.json() as Promise<T>
}

export const api = {
  listProjects: () => req<ProjectMeta[]>('/api/projects'),
  createProject: (body: { name: string; script?: string; shotlist?: string; prompt?: string; promptMode?: 'i2va' | 'ref2va' }) =>
    req<Project>('/api/projects', { method: 'POST', body: JSON.stringify(body) }),
  getProject: (id: string) => req<Project>(`/api/projects/${id}`),
  saveProject: (id: string, body: { script?: string; shotlist?: string; prompt?: string; promptMode?: 'i2va' | 'ref2va' }) =>
    req<Project>(`/api/projects/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  generateShotlist: (id: string, body: { model?: string; effort?: string; shotStyle?: string; fewshot?: string[]; review?: boolean; retry?: number }) =>
    req<{ attempts: number; review?: string }>(`/api/projects/${id}/generate-shotlist`, { method: 'POST', body: JSON.stringify(body) }),
  generatePrompt: (id: string, body: { mode: 'i2va' | 'ref2va'; model?: string; effort?: string; retry?: number }) =>
    req<{ mode: string; attempts: number; issues?: string[] }>(`/api/projects/${id}/generate-prompt`, { method: 'POST', body: JSON.stringify(body) }),
  getInputs: (id: string) => req<{ inputs: Project['inputs'] }>(`/api/projects/${id}/inputs`),
}
