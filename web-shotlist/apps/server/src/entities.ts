/**
 * 实体卡存储（docs/22 实体系统，V1 结构化轻度描述）
 * 存储：data/entities/<id>.md（frontmatter 元信息 + 外观/声音/介绍三段）+ 扫描生成索引
 */
import fs from 'node:fs'
import path from 'node:path'
import { parse, stringify } from 'yaml'
import type { Entity, EntityImportance, EntityType } from '@shotlist/shared'
import { ENTITIES_DIR, ROLE_CARD_DIR } from './config.ts'

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

/**
 * 角色卡注入（工具 A/B 共用）：实体库必须匹配（无 fallback，用户决策 2026-08-12）
 * 找不到 → 抛错阻断生成，提示先到①剧本页从剧本+世界观抽取实体
 */
export function loadEntityCards(ids: string[]): string {
  if (!ids.length) return '（无角色卡）'
  const blocks: string[] = []
  const missing: string[] = []
  for (const rid of ids) {
    const e = readEntity(rid)
    if (e) {
      blocks.push(
        `===== 角色卡 ${rid} =====\n# ${e.name}（${e.type}·${e.importance === 'core' ? '核心' : '次要'}）\n## 外观\n${e.appearance}\n## 声音\n${e.sound || '无特殊'}\n## 介绍\n${e.description}`,
      )
    } else {
      missing.push(rid)
    }
  }
  if (missing.length) {
    throw new Error(`角色卡不在实体库（无 fallback）：${missing.join('、')}——请先在①剧本页用 AI 抽取从剧本+世界观生成实体`)
  }
  return blocks.join('\n')
}

/**
 * 从 experiments/shotlist/rolecards/*.md 一键导入实体库（老项目迁移，2026-08-12）
 * 节解析：外观节 → appearance；行为锚定/场景关联 → description；声音缺省（可后补）
 */
export function importRolecardsToEntities(): Array<{ id: string; name: string; imported: boolean; error?: string }> {
  const dir = ROLE_CARD_DIR
  if (!fs.existsSync(dir)) return []
  const results: Array<{ id: string; name: string; imported: boolean; error?: string }> = []
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.md'))) {
    const id = f.slice(0, -3)
    let cardName = id
    try {
      const text = fs.readFileSync(path.join(dir, f), 'utf-8')
      const nameMatch = /^#\s*角色卡：?([^（(\s]+)/m.exec(text) ?? /^#\s*(.+)$/m.exec(text)
      cardName = (nameMatch?.[1] ?? id).trim()
      const section = (title: string): string => {
        const re = new RegExp('##\\s*' + title + '[^\\n]*\\n([\\s\\S]*?)(?=\\n##\\s|$)')
        const m = re.exec(text)
        return m ? m[1].trim() : ''
      }
      const appearance = section('外观')
      const behavior = section('行为锚定')
      const scene = section('场景关联')
      const desc = [behavior, scene].filter(Boolean).join('\n\n')
      if (!appearance && !desc) {
        results.push({ id, name: cardName, imported: false, error: '未解析到外观/行为节，跳过（可手动新建）' })
        continue
      }
      saveEntity({
        id,
        name: cardName,
        type: '角色',
        importance: 'core',
        appearance,
        sound: '',
        description: desc,
        source: `角色卡 ${id}（experiments/shotlist/rolecards 导入）`,
      })
      results.push({ id, name: cardName, imported: true })
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : String(e)
      results.push({ id, name: cardName, imported: false, error: errMsg })
    }
  }
  return results
}
