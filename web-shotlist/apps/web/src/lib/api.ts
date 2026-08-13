/** API client（Fastify 后端，/api 前缀经 Vite proxy）
 * 方案 A：请求/响应类型一律从 @shotlist/shared 的 zod schema 推导（z.infer），禁止手写重复类型
 */
import type { DraftLength, Entity, Project, ProjectMeta, TrashItem } from '@shotlist/shared'
import type {
  CreateProjectInput,
  DraftInput,
  EntityInput,
  ExtractInput,
  GenPromptInput,
  GenShotlistInput,
  SaveProjectInput,
  VoiceGenInput,
} from '@shotlist/shared'

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
  createProject: (body: CreateProjectInput) => req<Project>('/api/projects', { method: 'POST', body: JSON.stringify(body) }),
  getProject: (id: string) => req<Project>(`/api/projects/${id}`),
  saveProject: (id: string, body: SaveProjectInput) =>
    req<Project>(`/api/projects/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  generateShotlist: (id: string, body: GenShotlistInput) =>
    req<{ attempts: number; review?: string }>(`/api/projects/${id}/generate-shotlist`, { method: 'POST', body: JSON.stringify(body) }),
  generatePrompt: (id: string, body: GenPromptInput) =>
    req<{ mode: string; attempts: number; issues?: string[]; gate?: { warns: string[] } }>(`/api/projects/${id}/generate-prompt`, { method: 'POST', body: JSON.stringify(body) }),
  getInputs: (id: string) => req<{ inputs: Project['inputs'] }>(`/api/projects/${id}/inputs`),
  listTrash: () => req<TrashItem[]>('/api/trash'),
  trashProject: (id: string) => req<TrashItem>(`/api/projects/${id}/trash`, { method: 'POST' }),
  restoreProject: (id: string) => req<ProjectMeta>(`/api/projects/${id}/restore`, { method: 'POST' }),
  purgeProject: (id: string) => req<{ ok: true }>(`/api/projects/${id}`, { method: 'DELETE' }),
  renameProject: (id: string, name: string) => req<ProjectMeta>(`/api/projects/${id}/rename`, { method: 'POST', body: JSON.stringify({ name }) }),
  exportProject: (id: string) => req<import('@shotlist/shared').ProjectExport>(`/api/projects/${id}/export`),
  importProject: (pack: import('@shotlist/shared').ProjectExport) => req<Project>('/api/projects/import', { method: 'POST', body: JSON.stringify(pack) }),
  listRoleCards: () => req<string[]>('/api/role-cards'),
  // 实体
  listEntities: () => req<Array<Pick<Entity, 'id' | 'name' | 'type' | 'importance' | 'stars'>>>(`/api/entities`),
  getEntity: (id: string) => req<Entity>(`/api/entities/${encodeURIComponent(id)}`),
  saveEntity: (e: EntityInput) => req<Entity>('/api/entities', { method: 'POST', body: JSON.stringify(e) }),
  updateEntity: (id: string, e: EntityInput) => req<Entity>(`/api/entities/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(e) }),
  deleteEntity: (id: string) => req<{ ok: true }>(`/api/entities/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  extractEntities: (body: ExtractInput) => req<{ taskId: string }>('/api/entities/extract', { method: 'POST', body: JSON.stringify(body) }),
  getTask: (id: string) => req<{ id: string; kind: string; status: 'queued' | 'running' | 'done' | 'error'; result?: unknown; error?: string; createdAt: number; startedAt?: number; finishedAt?: number }>(`/api/tasks/${id}`),
  refreshEntity: (id: string, body: ExtractInput) => req<Entity>(`/api/entities/${encodeURIComponent(id)}/refresh`, { method: 'POST', body: JSON.stringify(body) }),
  gateEntities: (ids: string[]) => req<{ allTextOk: boolean; blocks: string[]; warns: string[]; checks: Array<{ id: string; name: string; text: { ok: boolean; missing: string[] }; art: { ok: boolean; count: number }; voice: { ok: boolean; count: number } }> }>('/api/entities/gate', { method: 'POST', body: JSON.stringify({ ids }) }),
  importRolecards: () => req<{ imported: number; results: Array<{ id: string; name: string; imported: boolean; error?: string }> }>('/api/entities/import-rolecards', { method: 'POST' }),
  // 实体资源
  getEntityAssets: (id: string) => req<{ assets: Array<{ kind: 'art' | 'voice' | 'file'; file: string; size: number; createdAt: number }> }>(`/api/entities/${encodeURIComponent(id)}/assets`),
  uploadEntityAsset: (id: string, kind: 'art' | 'voice' | 'file', file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch(`/api/entities/${encodeURIComponent(id)}/assets?kind=${kind}`, { method: 'POST', body: fd })
  },
  deleteEntityAsset: (id: string, file: string) => req<{ ok: true }>(`/api/entities/${encodeURIComponent(id)}/assets/${encodeURIComponent(file)}`, { method: 'DELETE' }),
  assetUrl: (entityId: string, file: string) => `/api/assets/${encodeURIComponent(entityId)}/${encodeURIComponent(file)}`,
  // 设定图（ANIMA t2i；variant 可选=变体图）
  getEntityArt: (id: string) => req<{ images: string[]; comfyOnline: boolean }>(`/api/entities/${encodeURIComponent(id)}/art`),
  generateEntityArt: (id: string, body: { prompt?: string; seed?: number; variant?: string }) => req<{ taskId: string }>(`/api/entities/${encodeURIComponent(id)}/art`, { method: 'POST', body: JSON.stringify(body) }),
  // 全局风格
  getStyle: () => req<{ prompt: string; updatedAt?: string }>('/api/style'),
  updateStyle: (prompt: string) => req<{ prompt: string; updatedAt?: string }>('/api/style', { method: 'PUT', body: JSON.stringify({ prompt }) }),
  // 音色种子（Qwen3-TTS）
  ttsReady: () => req<{ ready: boolean }>('/api/tts-ready'),
  generateEntityVoice: (id: string, body: VoiceGenInput) =>
    req<{ taskId: string }>(`/api/entities/${encodeURIComponent(id)}/voice`, { method: 'POST', body: JSON.stringify(body) }),
  // 工具 A0
  genDraft: (body: DraftInput) => req<{ worldview: string; script: string }>('/api/draft', { method: 'POST', body: JSON.stringify(body) }),
}
