/**
 * 实体卡 AI 抽取：世界观 + 剧本 → 实体卡 JSON（默认创建方式）
 * 模板与解析（2026-08-12）
 */
import type { Entity, EntityImportance, EntityType } from '@shotlist/shared'
import { chatCompletion, stripFence, type Effort } from '../llm.ts'

const EXTRACT_TPL = `你是世界观实体抽取器。从世界观手册和剧本中抽取实体（角色/场景/物件/技能/组织/地点），供动画短片制作使用。

规则：
1. 角色必须有（主角优先），场景从剧本场景推断；重要物件/技能若剧情关键也抽取
2. 外观（appearance）：具体到可作画——性别/年龄感/发型发色/瞳色/服装（款式+颜色）/标志特征/体态。必须是逐字可用的中文描述，这是后续角色卡与参考图对齐的依据
3. 声音（sound）：音色/语气/说话习惯（如"清亮少女声，语速偏快，尾音上扬"）；无特殊设定写"无特殊"
4. 介绍（description）：1-3 句，身份/背景/在剧本中的作用
5. 重要度：主角/核心场景/关键物件 = core，其余 = secondary
6. 关系（related）：与其他实体的关系，如 {id: "yuki_v1", relation: "好友"}；id 用实体 name 的拼音/英文短 id 或直接中文名，保持全库一致
7. 只输出 JSON 数组，无前言、无解释、无 markdown fence：
[{"name": "...", "type": "角色", "importance": "core", "appearance": "...", "sound": "...", "description": "...", "source": "剧本《XXX》", "related": [{"id": "...", "relation": "..."}]}]

===== 世界观手册 =====
{worldview}

===== 剧本 =====
{script}`

export interface ExtractEntitiesOptions {
  worldview: string
  script: string
  model?: string
  effort?: Effort
}

/** 调用 LLM 抽取实体（不落库，调用方决定） */
export async function extractEntities(opts: ExtractEntitiesOptions): Promise<Entity[]> {
  const { worldview, script } = opts
  const user = EXTRACT_TPL.replace('{worldview}', worldview || '（无，仅按剧本推断）').replace('{script}', script)
  const raw = stripFence(
    await chatCompletion('你是结构化的实体抽取器，严格输出 JSON。', user, {
      model: opts.model ?? 'deepseek-v4-flash',
      effort: opts.effort ?? 'high',
      temperature: 0.4,
      maxTokens: 12000,
    }),
  )
  const arr = JSON.parse(extractJson(raw)) as Array<Record<string, unknown>>
  return arr.map((e, i) => ({
    id: String(e.id ?? e.name ?? `entity_${i}`),
    name: String(e.name ?? `实体${i + 1}`),
    type: normalizeType(e.type),
    importance: e.importance === 'core' ? 'core' : 'secondary',
    appearance: String(e.appearance ?? ''),
    sound: String(e.sound ?? '无特殊'),
    description: String(e.description ?? ''),
    source: e.source ? String(e.source) : undefined,
    related: Array.isArray(e.related)
      ? (e.related as Array<{ id: string; relation: string }>).map((r) => ({
          id: String(r.id ?? ''),
          relation: String(r.relation ?? ''),
        }))
      : undefined,
  }))
}

/** 从 LLM 输出中提取 JSON 数组（容忍前后缀） */
function extractJson(raw: string): string {
  const m = /\[[\s\S]*\]/.exec(raw)
  if (!m) throw new Error(`LLM 输出中未找到 JSON 数组: ${raw.slice(0, 200)}`)
  return m[0]
}

function normalizeType(t: unknown): EntityType {
  const s = String(t ?? '角色')
  return (['角色', '场景', '物件', '技能', '组织', '地点'] as const).includes(s as EntityType)
    ? (s as EntityType)
    : '角色'
}
