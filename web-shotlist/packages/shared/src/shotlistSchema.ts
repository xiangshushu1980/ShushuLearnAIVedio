/** 拍摄本 zod schema + 校验（移植 scripts/h3_shotlist_gen.py validate()，2026-08-12） */
import { parse } from 'yaml'
import { z } from 'zod'
import { CAMERA_TYPES, FRAMINGS } from './types.ts'

export const cameraTypeSchema = z.enum(CAMERA_TYPES)
export const framingSchema = z.enum(FRAMINGS)

export const dialogueLineSchema = z.object({
  speaker: z.string().min(1, 'speaker 不能为空'),
  text: z.string().min(1, '台词文本不能为空'),
})

export const shotSoundSchema = z
  .object({
    ambient: z.string().optional(),
    fx: z.string().optional(),
    bgm: z.string().min(1, 'bgm 不能为空（无配乐写 N/A，导演特意决策）'),
  })
  .refine((s) => s.ambient || s.fx, {
    message: 'sound 至少要有 ambient 或 fx 之一',
    path: ['ambient'],
  })

export const shotSchema = z.object({
  id: z.number().int().positive(),
  duration_s: z.number().min(1.5, '时长 <1.5s'),
  framing: framingSchema,
  camera: z.object({
    type: cameraTypeSchema,
    amplitude: z.enum(['small', 'medium', 'large']).optional(),
    speed: z.enum(['slow', 'normal', 'fast']).optional(),
  }),
  subject: z.string().min(1, 'subject 不能为空'),
  action: z.string().min(1, 'action 不能为空'),
  dialogue: z.array(dialogueLineSchema).optional(),
  sound: shotSoundSchema,
  continuity: z.string().min(1, 'continuity 不能为空'),
})

export const shotlistSchema = z.object({
  title: z.string().min(1),
  style: z.string().optional(),
  ratio: z.string().optional(),
  scene: z.string().min(1, '缺顶层 scene 字段（首帧场景 id，如 beach/stage/night）'),
  duration_total: z.number(),
  chain: z.enum(['first_static', 'firstlast_bridge', 'independent']),
  role_cards: z.array(z.string()).optional(),
  audio_refs: z.record(z.string(), z.string()).optional(),
  shots: z.array(shotSchema).min(1, 'shots 缺失或为空'),
})

export type ValidatedShotlist = z.infer<typeof shotlistSchema>

/** 镜头预算规则（docs/17 规则 1） */
export function shotBudget(durationTotal: number): { max: number } {
  if (durationTotal <= 6) return { max: 2 }
  if (durationTotal <= 10) return { max: 3 }
  return { max: 5 }
}

/**
 * 拍摄本校验（与 Python validate() 等价，外加 zod 结构校验）
 * 返回错误列表（空 = 通过）
 */
export function validateShotlist(data: unknown, durationTotal: number): string[] {
  const errs: string[] = []
  const parsed = shotlistSchema.safeParse(data)
  if (!parsed.success) {
    for (const issue of parsed.error.issues) {
      errs.push(`${issue.path.join('.') || '(根)'}: ${issue.message}`)
    }
    // 结构都错了就不再继续业务规则（避免访问 undefined）
    if (errs.length > 0 && !isShotlistShape(data)) return errs
  }
  const sl = isShotlistShape(data) ? data : undefined
  if (!sl) return errs

  // id 从 1 连续递增
  const ids = sl.shots.map((s) => s.id)
  const expect = Array.from({ length: sl.shots.length }, (_, i) => i + 1)
  if (JSON.stringify(ids) !== JSON.stringify(expect)) {
    errs.push(`shot id 必须从 1 连续递增: ${ids.join(',')}`)
  }

  // 镜头时长和 ≈ duration_total（±1s）
  const total = sl.shots.reduce((a, s) => a + (Number(s.duration_s) || 0), 0)
  if (Math.abs(total - durationTotal) > 1.0) {
    errs.push(`镜头时长和 ${total.toFixed(2)}s 与 duration_total ${durationTotal}s 不符`)
  }

  // 镜头预算
  const { max } = shotBudget(durationTotal)
  if (sl.shots.length > max) {
    errs.push(`镜头预算超限: ${durationTotal}s 最多 ${max} 镜（实际 ${sl.shots.length}）`)
  }

  // 每镜字段（zod 已覆盖结构；这里补 Python 缺的 dialogue 空文本等）
  for (const s of sl.shots) {
    for (const d of s.dialogue ?? []) {
      if (!d.text?.trim()) errs.push(`shot ${s.id} dialogue 文本为空`)
    }
    const { ambient, bgm } = s.sound
    if (!ambient) errs.push(`shot ${s.id} sound 缺 ambient`)
    if (!bgm) errs.push(`shot ${s.id} sound 缺 bgm`)
  }

  return errs
}

/** 结构合法性：只需顶层对象 + shots 数组（scene 缺失由 validateShotlist 报错，导入历史数据宽容） */
function isShotlistShape(data: unknown): data is ValidatedShotlist {
  return (
    typeof data === 'object' &&
    data !== null &&
    Array.isArray((data as ValidatedShotlist).shots)
  )
}

/** 解析拍摄本 YAML 文本 → 结构 + 校验错误（结构合法即返回 data，errs 供展示/阻断生成） */
export function parseShotlistYaml(text: string, durationTotal?: number): { data?: ValidatedShotlist; errs: string[] } {
  let data: unknown
  try {
    data = parse(text)
  } catch (e) {
    return { errs: [`YAML 解析失败: ${(e as Error).message}`] }
  }
  if (!isShotlistShape(data)) {
    return { errs: ['拍摄本结构非法（需含 shots 数组）'] }
  }
  const errs = validateShotlist(data, durationTotal ?? data.duration_total)
  return { data, errs }
}
