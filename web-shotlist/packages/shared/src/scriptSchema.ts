/** 剧本解析（YAML 参数头 + 正文，移植 h3_shotlist_gen.py load_script）*/
import { parse, stringify } from 'yaml'
import { z } from 'zod'
import type { Script, ScriptHead } from './types.ts'

/** YAML 空值（`key: ` → null）宽容为 undefined */
const strOrUndef = z.preprocess((v) => (v == null ? undefined : v), z.string().optional())

export const scriptHeadSchema = z.object({
  title: strOrUndef,
  style: strOrUndef,
  ratio: z.preprocess((v) => (v == null ? undefined : v), z.union([z.string(), z.number()]).optional()),
  scene: strOrUndef,
  duration: z.number().optional(),
  sound: strOrUndef,
  role_cards: z.array(z.string()).optional(),
  chain: z.enum(['first_static', 'firstlast_bridge', 'independent']).optional(),
  audio_refs: z.record(z.string(), z.string()).optional(),
  no_bgm: z.boolean().optional(),
  bgm: strOrUndef,
  shot_style: strOrUndef,
  branch: z.unknown().optional(),
})

/** 解析剧本：YAML 参数头（--- ... ---）+ 正文 */
export function parseScript(text: string): { script?: Script; errs: string[] } {
  const m = /^---\s*\n(.*?)\n---\s*\n(.*)$/s.exec(text)
  if (!m) {
    return { errs: ['剧本格式错误（需 --- 参数头 --- 正文）'] }
  }
  let headRaw: unknown
  try {
    headRaw = parse(m[1])
  } catch (e) {
    return { errs: [`参数头 YAML 解析失败: ${(e as Error).message}`] }
  }
  const parsed = scriptHeadSchema.safeParse(headRaw)
  if (!parsed.success) {
    return { errs: parsed.error.issues.map((i) => `参数头 ${i.path.join('.')}: ${i.message}`) }
  }
  const head = parsed.data as ScriptHead
  if (head.ratio !== undefined) head.ratio = String(head.ratio)
  const body = m[2].trim()
  return {
    script: { head, body, raw: text },
    errs: [],
  }
}

/** 已知参数头字段的输出顺序（序列化时按此排序） */
const HEAD_KEY_ORDER = [
  'title', 'style', 'ratio', 'scene', 'duration', 'sound', 'role_cards', 'chain', 'audio_refs', 'no_bgm', 'shot_style',
] as const

/**
 * 参数头表单值 → 剧本 YAML 文本
 * 策略：yaml 解析原参数头 → merge 表单值 → 重序列化；保留未知字段（branch 等），丢弃注释
 */
export function serializeScript(prevRaw: string, head: ScriptHead): string {
  const m = /^---\s*\n(.*?)\n---\s*\n(.*)$/s.exec(prevRaw)
  if (!m) return prevRaw
  const body = m[2]
  let prevHead: Record<string, unknown> = {}
  try {
    const parsed = parse(m[1])
    if (parsed && typeof parsed === 'object') prevHead = parsed as Record<string, unknown>
  } catch {
    /* 原文参数头不可解析：仅用表单值重建 */
  }
  const merged: Record<string, unknown> = { ...prevHead }
  for (const k of HEAD_KEY_ORDER) {
    if (k in head && head[k as keyof ScriptHead] !== undefined) {
      merged[k] = head[k as keyof ScriptHead]
    }
  }
  // 输出顺序：已知字段按 HEAD_KEY_ORDER，未知字段按原顺序追加
  const out: Record<string, unknown> = {}
  for (const k of HEAD_KEY_ORDER) if (k in merged) out[k] = merged[k]
  for (const [k, v] of Object.entries(prevHead)) if (!(k in out)) out[k] = v
  return `---\n${stringify(out)}\n---\n${body}`
}
