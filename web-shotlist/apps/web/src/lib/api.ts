/** API client（Fastify 后端，/api 前缀经 Vite proxy） */
import type { DraftLength, Entity, Project, ProjectMeta, TrashItem } from '@shotlist/shared'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {}
  if (init?.body !== undefined) headers['Content-Type'] = 'application/json'
  const r = await fetch(path, {
    headers,
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
  listTrash: () => req<TrashItem[]>('/api/trash'),
  trashProject: (id: string) => req<TrashItem>(`/api/projects/${id}/trash`, { method: 'POST' }),
  restoreProject: (id: string) => req<ProjectMeta>(`/api/projects/${id}/restore`, { method: 'POST' }),
  purgeProject: (id: string) => req<{ ok: true }>(`/api/projects/${id}`, { method: 'DELETE' }),
  listRoleCards: () => req<string[]>('/api/role-cards'),
  // 实体
  listEntities: () => req<Array<Pick<Entity, 'id' | 'name' | 'type' | 'importance'>>>(`/api/entities`),
  getEntity: (id: string) => req<Entity>(`/api/entities/${encodeURIComponent(id)}`),
  saveEntity: (e: Partial<Entity> & { name: string }) => req<Entity>('/api/entities', { method: 'POST', body: JSON.stringify(e) }),
  updateEntity: (id: string, e: Partial<Entity> & { name: string }) => req<Entity>(`/api/entities/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(e) }),
  deleteEntity: (id: string) => req<{ ok: true }>(`/api/entities/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  extractEntities: (body: { worldview: string; script: string }) => req<{ entities: Entity[] }>('/api/entities/extract', { method: 'POST', body: JSON.stringify(body) }),
  // 设定图（ANIMA t2i）
  getEntityArt: (id: string) => req<{ images: string[]; comfyOnline: boolean }>(`/api/entities/${encodeURIComponent(id)}/art`),
  generateEntityArt: (id: string, body: { prompt?: string; seed?: number }) => req<{ ok: true; images: string[] }>(`/api/entities/${encodeURIComponent(id)}/art`, { method: 'POST', body: JSON.stringify(body) }),
  artUrl: (file: string) => `/api/art/${encodeURIComponent(file)}`,
  // 工具 A0
  genDraft: (body: { idea: string; length: DraftLength; withWorldview: boolean }) => req<{ worldview: string; script: string }>('/api/draft', { method: 'POST', body: JSON.stringify(body) }),
}
