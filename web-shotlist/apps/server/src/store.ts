/**
 * 项目文件存储（docs/22 五节：项目 = 一个目录）
 * 项目目录格式：
 *   <项目名>/script.yaml | shotlist.yaml | prompt_<mode>.txt | inputs.json | meta.json
 * 默认数据根：web-shotlist/data/projects/（data/ gitignored；V2 对接 experiments/shotlist 导入）
 */
import fs from 'node:fs'
import path from 'node:path'
import { parseScript, parseShotlistYaml, type InputRef, type Project, type ProjectMeta, type PromptMode, type TrashItem } from '@shotlist/shared'
import { DATA_ROOT, ENTITIES_DIR, ROLE_CARD_DIR } from './config.ts'

export function projectsRoot(): string {
  const dir = path.join(DATA_ROOT, 'projects')
  fs.mkdirSync(dir, { recursive: true })
  return dir
}

function projectDir(id: string): string {
  // id 白名单防路径穿越（支持中文项目名）
  if (!/^[a-zA-Z0-9_\u4e00-\u9fff-]+$/.test(id)) throw new Error(`非法项目 id: ${id}`)
  return path.join(projectsRoot(), id)
}

export function listProjects(): ProjectMeta[] {
  const root = projectsRoot()
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      try {
        const meta = readJson<ProjectMeta>(path.join(root, d.name, 'meta.json'))
        return meta ?? { id: d.name, name: d.name, createdAt: '' }
      } catch {
        return { id: d.name, name: d.name, createdAt: '' }
      }
    })
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
}

export function createProject(name: string, imported?: { script?: string; shotlist?: string; prompt?: string; promptMode?: PromptMode }): Project {
  const id = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fff_-]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 60)
  if (!id) throw new Error('项目名不能为空')
  const dir = projectDir(id)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })

  const meta: ProjectMeta = {
    id,
    name: name.trim(),
    createdAt: new Date().toISOString(),
    entities: [],
  }
  writeJson(path.join(dir, 'meta.json'), meta)
  if (imported?.script) fs.writeFileSync(path.join(dir, 'script.yaml'), imported.script, 'utf-8')
  if (imported?.shotlist) fs.writeFileSync(path.join(dir, 'shotlist.yaml'), imported.shotlist, 'utf-8')
  if (imported?.prompt && imported.promptMode) {
    fs.writeFileSync(path.join(dir, `prompt_${imported.promptMode}.txt`), imported.prompt, 'utf-8')
  }
  return readProject(id)
}

export function readProject(id: string): Project {
  const dir = projectDir(id)
  const meta = readJson<ProjectMeta>(path.join(dir, 'meta.json'))
  if (!meta) throw new Error(`项目不存在: ${id}`)
  const project: Project = { meta, inputs: [] }
  const scriptPath = path.join(dir, 'script.yaml')
  if (fs.existsSync(scriptPath)) {
    project.script = parseScript(fs.readFileSync(scriptPath, 'utf-8')).script
  }
  const slPath = path.join(dir, 'shotlist.yaml')
  if (fs.existsSync(slPath)) {
    const raw = fs.readFileSync(slPath, 'utf-8')
    const { data } = parseShotlistYaml(raw)
    project.shotlist = data
    project.shotlistRaw = raw
  }
  const mode = promptModeOf(dir)
  if (mode) {
    const p = path.join(dir, `prompt_${mode}.txt`)
    if (fs.existsSync(p)) {
      project.prompt = fs.readFileSync(p, 'utf-8')
      project.promptMode = mode
    }
  }
  project.inputs = parseInputs(project)
  return project
}

export function saveProject(id: string, patch: { script?: string; shotlist?: string; prompt?: string; promptMode?: PromptMode }): Project {
  const dir = projectDir(id)
  if (!fs.existsSync(dir)) throw new Error(`项目不存在: ${id}`)
  if (patch.script !== undefined) fs.writeFileSync(path.join(dir, 'script.yaml'), patch.script, 'utf-8')
  if (patch.shotlist !== undefined) fs.writeFileSync(path.join(dir, 'shotlist.yaml'), patch.shotlist, 'utf-8')
  if (patch.prompt !== undefined && patch.promptMode) {
    fs.writeFileSync(path.join(dir, `prompt_${patch.promptMode}.txt`), patch.prompt, 'utf-8')
  }
  return readProject(id)
}

function promptModeOf(dir: string): PromptMode | null {
  for (const m of ['i2va', 'ref2va'] as const) {
    if (fs.existsSync(path.join(dir, `prompt_${m}.txt`))) return m
  }
  return null
}


/** 渲染输入源清单（V1：解析拍摄本 audio_refs + 提示词 <Picture N> 引用） */
export function parseInputs(project: Project): InputRef[] {
  const inputs: InputRef[] = []
  const audioRefs = project.shotlist?.audio_refs ?? {}
  let audioN = 1
  for (const [rid, src] of Object.entries(audioRefs)) {
    inputs.push({
      kind: 'audio',
      n: audioN++,
      src,
      label: `音色种子 ${rid}`,
      entityId: rid,
    })
  }
  const prompt = project.prompt ?? ''
  const picRefs = [...prompt.matchAll(/<Picture (\d+)>/g)].map((m) => Number(m[1]))
  const picN = [...new Set(picRefs)]
  const srcBase = `ComfyUI/input/${project.shotlist?.scene ?? ''}/` // 首帧图库约定（docs/21）
  for (const n of picN) {
    inputs.push({
      kind: 'image',
      n,
      src: `${srcBase}frame_${n}.png`,
      label: `参考图 <Picture ${n}>`,
    })
  }
  return inputs
}

// ===== 实体注册表（V1 基础版；V2 对接 experiments/entities）=====
export function listEntities(): Array<{ id: string; name: string; type: string; importance: string }> {
  const idx = readJson<Array<{ id: string; name: string; type: string; importance: string }>>(path.join(ENTITIES_DIR, 'index.json'))
  return idx ?? []
}

export function readEntity(id: string): { entity?: unknown; errs?: string[] } {
  const f = path.join(ENTITIES_DIR, `${id}.md`)
  if (!fs.existsSync(f)) return { errs: [`实体不存在: ${id}`] }
  return { entity: { id, description: fs.readFileSync(f, 'utf-8') } }
}

// ===== 回收站（软删除：项目目录移入 data/trash/）=====
function trashRoot(): string {
  const dir = path.join(DATA_ROOT, 'trash')
  fs.mkdirSync(dir, { recursive: true })
  return dir
}

function inTrash(id: string): boolean {
  return fs.existsSync(path.join(trashRoot(), id))
}

/** 删除项目 → 回收站（确认由前端完成）；返回回收站条目 */
export function trashProject(id: string): TrashItem {
  const dir = projectDir(id)
  if (!fs.existsSync(dir)) throw new Error(`项目不存在: ${id}`)
  if (inTrash(id)) throw new Error(`项目已在回收站: ${id}`)
  const trashedAt = new Date().toISOString()
  // 更新 meta 记入回收时间
  const metaPath = path.join(dir, 'meta.json')
  const meta = readJson<ProjectMeta>(metaPath) ?? { id, name: id, createdAt: trashedAt }
  meta.trashedAt = trashedAt
  writeJson(metaPath, meta)
  fs.renameSync(dir, path.join(trashRoot(), id))
  return { id, name: meta.name, trashedAt }
}

export function listTrash(): TrashItem[] {
  const root = trashRoot()
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const meta = readJson<ProjectMeta>(path.join(root, d.name, 'meta.json'))
      return { id: d.name, name: meta?.name ?? d.name, trashedAt: meta?.trashedAt ?? '' }
    })
    .sort((a, b) => b.trashedAt.localeCompare(a.trashedAt))
}

/** 恢复回收站项目 */
export function restoreProject(id: string): ProjectMeta {
  const from = path.join(trashRoot(), id)
  if (!fs.existsSync(from)) throw new Error(`回收站无此项目: ${id}`)
  const meta = readJson<ProjectMeta>(path.join(from, 'meta.json'))
  if (!meta) throw new Error(`回收站项目元信息损坏: ${id}`)
  const to = path.join(projectsRoot(), id)
  if (fs.existsSync(to)) throw new Error(`目标位置已存在同名项目，无法恢复: ${id}`)
  delete meta.trashedAt
  writeJson(path.join(from, 'meta.json'), meta)
  fs.renameSync(from, to)
  return meta
}

/** 永久删除（仅回收站内允许） */
export function purgeProject(id: string): void {
  const dir = path.join(trashRoot(), id)
  if (!fs.existsSync(dir)) throw new Error(`回收站无此项目: ${id}`)
  fs.rmSync(dir, { recursive: true, force: true })
}

/** 角色卡 id 列表（工具 A 参数头 role_cards 多选用） */
export function listRoleCards(): string[] {
  if (!fs.existsSync(ROLE_CARD_DIR)) return []
  return fs
    .readdirSync(ROLE_CARD_DIR)
    .filter((f) => f.endsWith('.md'))
    .map((f) => f.slice(0, -3))
    .sort()
}

// ===== helpers =====
function readJson<T>(p: string): T | null {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8')) as T
  } catch {
    return null
  }
}

function writeJson(p: string, v: unknown): void {
  fs.mkdirSync(path.dirname(p), { recursive: true })
  fs.writeFileSync(p, JSON.stringify(v, null, 2), 'utf-8')
}

