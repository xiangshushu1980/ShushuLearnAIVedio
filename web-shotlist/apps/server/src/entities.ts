/**
 * 实体卡存储（docs/22 实体系统，V1 结构化轻度描述）
 * 存储：data/entities/<id>.md（frontmatter 元信息 + 外观/声音/介绍三段）+ 扫描生成索引
 */
import fs from 'node:fs'
import path from 'node:path'
import { parse, stringify } from 'yaml'
import type { Entity, EntityImportance, EntityType } from '@shotlist/shared'
import { ENTITIES_DIR } from './config.ts'

export function entitiesDir(): string {
  fs.mkdirSync(ENTITIES_DIR, { recursive: true })
  return ENTITIES_DIR
}

function safeId(name: string): string {
  const id = name
    .trim()
    .replace(/[^\p{L}\p{N}_-]+/gu, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 60)
  return id || '未命名'
}

/** 实体索引（轻量：扫描 .md frontmatter，不读正文） */
export function listEntities(): Array<Pick<Entity, 'id' | 'name' | 'type' | 'importance'>> {
  const dir = entitiesDir()
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => {
      const meta = parseFrontmatter(path.join(dir, f))
      return {
        id: (meta.id as string) ?? f.slice(0, -3),
        name: (meta.name as string) ?? f.slice(0, -3),
        type: (meta.type as EntityType) ?? '角色',
        importance: (meta.importance as EntityImportance) ?? 'secondary',
      }
    })
    .sort((a, b) => a.id.localeCompare(b.id))
}

export function readEntity(id: string): Entity | null {
  const f = path.join(entitiesDir(), `${id}.md`)
  if (!fs.existsSync(f)) return null
  const text = fs.readFileSync(f, 'utf-8')
  const m = /^---\n(.*?)\n---\n(.*)$/s.exec(text)
  if (!m) return { id, name: id, type: '角色', importance: 'secondary', appearance: '', sound: '', description: text }
  const meta = (parse(m[1]) ?? {}) as Record<string, unknown>
  const body = m[2]
  const sections: Record<string, string> = {}
  let lastTitle = ''
  let buf: string[] = []
  const flush = () => {
    if (lastTitle) sections[lastTitle] = buf.join('\n').trim()
    buf = []
  }
  for (const line of body.split('\n')) {
    if (/^## .+$/.test(line)) {
      flush()
      lastTitle = line.slice(3).trim()
    } else {
      buf.push(line)
    }
  }
  flush()
  return {
    id,
    name: (meta.name as string) ?? id,
    type: (meta.type as EntityType) ?? '角色',
    importance: (meta.importance as EntityImportance) ?? 'secondary',
    appearance: sections['外观'] ?? '',
    sound: sections['声音'] ?? '',
    description: sections['介绍'] ?? '',
    source: meta.source as string | undefined,
    related: meta.related as Entity['related'],
    createdAt: meta.createdAt as string | undefined,
  }
}

export function saveEntity(e: Entity): Entity {
  const dir = entitiesDir()
  const id = safeId(e.id || e.name)
  const meta: Record<string, unknown> = {
    name: e.name,
    type: e.type,
    importance: e.importance,
    createdAt: e.createdAt ?? new Date().toISOString(),
  }
  if (e.source) meta.source = e.source
  if (e.related?.length) meta.related = e.related
  const body = [
    `# ${e.name}`,
    '',
    '## 外观',
    e.appearance.trim(),
    '',
    '## 声音',
    e.sound.trim(),
    '',
    '## 介绍',
    e.description.trim(),
    '',
  ].join('\n')
  const text = `---\n${stringify(meta)}\n---\n${body}`
  fs.writeFileSync(path.join(dir, `${id}.md`), text, 'utf-8')
  return { ...e, id, createdAt: meta.createdAt as string }
}

export function deleteEntity(id: string): void {
  const f = path.join(entitiesDir(), `${id}.md`)
  if (!fs.existsSync(f)) throw new Error(`实体不存在: ${id}`)
  fs.rmSync(f)
}

function parseFrontmatter(f: string): Record<string, unknown> {
  try {
    const text = fs.readFileSync(f, 'utf-8')
    const m = /^---\n(.*?)\n---/s.exec(text)
    return m ? ((parse(m[1]) ?? {}) as Record<string, unknown>) : {}
  } catch {
    return {}
  }
}
