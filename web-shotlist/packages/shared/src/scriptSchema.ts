/** 剧本解析（YAML 参数头 + 正文，移植 h3_shotlist_gen.py load_script）*/
import { parse } from 'yaml'
import { z } from 'zod'
import type { Script, ScriptHead } from './types.ts'

export const scriptHeadSchema = z.object({
  title: z.string().optional(),
  style: z.string().optional(),
  ratio: z.union([z.string(), z.number()]).optional(),
  scene: z.string().optional(),
  duration: z.number().optional(),
  sound: z.string().optional(),
  role_cards: z.array(z.string()).optional(),
  chain: z.enum(['first_static', 'firstlast_bridge', 'independent']).optional(),
  audio_refs: z.record(z.string(), z.string()).optional(),
  no_bgm: z.boolean().optional(),
  bgm: z.string().optional(),
  shot_style: z.string().optional(),
  branch: z.unknown().optional(),
})

/** 解析剧本：YAML 参数头（--- ... ---）+ 正文 */
export function parseScript(text: string): { script?: Script; errs: string[] } {
  const m = /^---\n(.*?)\n---\n(.*)$/s.exec(text)
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
