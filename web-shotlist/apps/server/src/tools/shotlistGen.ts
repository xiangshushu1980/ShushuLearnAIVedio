/**
 * 工具 A：剧本 + 参数头 → 导演拍摄本（stage1，断点审阅）
 * 移植 scripts/h3_shotlist_gen.py（2026-08-12），校验转 zod
 */
import fs from 'node:fs'
import path from 'node:path'
import { parse } from 'yaml'
import {
  CAMERA_TYPES,
  type Script,
  type Shotlist,
  parseScript,
  validateShotlist,
} from '@shotlist/shared'
import { IR_REVERSE_DIR, RULES_FILE } from '../config.ts'
import { loadEntityCards } from '../entities.ts'
import { chatCompletion, stripFence, type Effort } from '../llm.ts'
import { reviewTemplate, shotlistSystemTemplate } from './templates.ts'

export interface GenShotlistOptions {
  model: string
  effort?: Effort
  maxTokens?: number
  retry?: number
  shotStyle?: string
  fewshot?: string[]
  /** 生成后调用 DeepSeek 导演视角自审（只报问题不改写） */
  review?: boolean
}

export interface GenShotlistResult {
  shotlist: Shotlist
  raw: string
  attempts: number
  review?: string
}

/** 剧本文件（script.yaml 文本）→ 生成拍摄本 */
export async function genShotlist(scriptText: string, opts: GenShotlistOptions): Promise<GenShotlistResult> {
  const { script, errs } = parseScript(scriptText)
  if (!script || errs.length) throw new Error(errs.join('；'))

  const keyOk = process.env.DEEPSEEK_API_KEY || fs.existsSync(path.join(process.env.HOME ?? '', '.config', 'mem0_deepseek_key'))
  if (!keyOk) throw new Error('缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY')

  const duration = Number(script.head.duration ?? 8)
  const roleBlock = loadEntityCards(script.head.role_cards ?? [])
  const fewshotBlock = loadFewshot(opts.fewshot ?? [])
  const systemPrompt = shotlistSystemTemplate(CAMERA_TYPES.join(', '), roleBlock, fewshotBlock)

  const noBgm = Boolean(script.head.no_bgm) || script.head.bgm === 'N/A'
  const chain = script.head.chain
  const chainLine = chain
    ? `chain: ${chain}  # 跨段策略（执行层；本段镜头规划不受影响）`
    : 'chain: auto  # 自动推断（第一段→first_static；多段中间→firstlast_bridge；散段→independent）'
  const shotStyle = opts.shotStyle ?? script.head.shot_style
  const styleLine = shotStyle
    ? `shot_style: ${shotStyle}`
    : 'shot_style: auto  # 按剧本内容自主选择 分镜剪辑 / 长镜头流'
  const userLines = [
    `===== 剧本 =====\n${script.body}`,
    `===== 参数 =====\n` +
      `style: ${script.head.style ?? ''}\nratio: ${script.head.ratio ?? '16:9'}\n` +
      `scene: ${script.head.scene ?? ''}\n` +
      `duration_total: ${duration}s\nsound: ${script.head.sound ?? ''}\n` +
      `role_cards: ${JSON.stringify(script.head.role_cards ?? [])}` +
      `\n${chainLine}\n${styleLine}\n` +
      `audio_refs: ${JSON.stringify(script.head.audio_refs ?? {})}` +
      `  # 音色种子（角色 id → wav 路径，可选）`,
    `no_bgm: ${noBgm}  # true=本段不要 BGM：bgm 一律 N/A + 镜头情绪中性化`,
    '请输出拍摄本 YAML（严格按 Schema）。',
  ]

  const { retry = 3, review = false } = opts
  let lastErr = '未执行'
  for (let attempt = 1; attempt <= retry + 1; attempt++) {
    const raw = stripFence(
      await chatCompletion(systemPrompt, userLines.join('\n'), {
        model: opts.model,
        effort: opts.effort,
        maxTokens: opts.maxTokens ?? 12000,
      }),
    )
    let data: unknown
    try {
      data = parse(raw)
    } catch (e) {
      lastErr = `YAML 解析失败: ${(e as Error).message}`
      continue
    }
    const errs = validateShotlist(data, duration)
    if (!errs.length) {
      const result: GenShotlistResult = { shotlist: data as Shotlist, raw, attempts: attempt }
      if (review) {
        result.review = await chatCompletion('你是审阅助手，只输出结构化审阅结果。', reviewTemplate(raw), {
          model: opts.model,
          effort: opts.effort,
          temperature: 0.3,
          maxTokens: 16000, // reasoning 会吃大量 token（实测 4000 不够）
        })
      }
      return result
    }
    lastErr = errs.join('；')
  }
  throw new Error(`${retry + 1} 次尝试后仍失败，最后错误: ${lastErr}`)
}

/** 从 IR 逆向样本库加载代表样本作为 few-shot（风格锚点，不复制内容） */
export function loadFewshot(names: string[]): string {
  if (!names.length) return ''
  const blocks: string[] = []
  for (const n of names) {
    const cand = path.join(IR_REVERSE_DIR, n.endsWith('_ir_shotlist.yaml') ? n : `${n}_ir_shotlist.yaml`)
    if (fs.existsSync(cand)) {
      blocks.push(
        `===== IR 参考样本（模仿其镜头内信息密度/景别选择/声音写法，不要复制具体内容）=====\n${fs.readFileSync(cand, 'utf-8')}`,
      )
    }
  }
  return blocks.join('\n\n')
}

/** 注入 docs/17 镜头规划节（二、三节，避免无关内容干扰）—— 当前模板已内联规则，保留此函数供后续按需扩展 */
export function loadRulesSection(): string {
  if (!fs.existsSync(RULES_FILE)) return ''
  const text = fs.readFileSync(RULES_FILE, 'utf-8')
  const m = /## 二、镜头规划.*?(?=## )/s.exec(text)
  return m ? m[0] : ''
}
