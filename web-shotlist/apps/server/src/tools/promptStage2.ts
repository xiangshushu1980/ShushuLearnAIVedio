/**
 * 工具 B：导演拍摄本 → H3 提示词（i2va 三核心段快车道 / ref2va 六段式慢车道）
 * 移植 scripts/h3_prompt_stage2.py（2026-08-12），校验转 zod/TS 规则
 */
import fs from 'node:fs'
import path from 'node:path'
import { parse } from 'yaml'
import {
  type PromptMode,
  type Shotlist,
  checkPrompt,
  validateShotlist,
} from '@shotlist/shared'
import { IR_SAMPLE, REF2VA_GUIDE } from '../config.ts'
import { loadEntityCards } from '../entities.ts'
import { chatCompletion, stripFence, type Effort } from '../llm.ts'
import { i2vaSystemTemplate, ref2vaSystemTemplate } from './templates.ts'

export interface GenPromptOptions {
  mode: PromptMode
  model: string
  effort?: Effort
  maxTokens?: number
  retry?: number
}

export interface GenPromptResult {
  prompt: string
  attempts: number
  issues?: string[]
}

export async function genPrompt(shotlistYaml: string, opts: GenPromptOptions): Promise<GenPromptResult> {
  let sl: Shotlist
  try {
    sl = parse(shotlistYaml) as Shotlist
  } catch (e) {
    throw new Error(`拍摄本 YAML 解析失败: ${(e as Error).message}`)
  }
  const errs = validateShotlist(sl, Number(sl.duration_total ?? 8))
  if (errs.length) throw new Error(`拍摄本校验失败: ${errs.slice(0, 5).join('；')}`)

  const roleCards = loadEntityCards(sl.role_cards ?? [])
  const systemPrompt =
    opts.mode === 'i2va'
      ? i2vaSystemTemplate(fs.existsSync(IR_SAMPLE) ? fs.readFileSync(IR_SAMPLE, 'utf-8') : '')
      : ref2vaSystemTemplate(loadRefGuide())

  const userLines: string[] = [
    `===== 拍摄本（导演已确认）=====\n${shotlistYaml}`,
    roleCards ? `===== 角色卡（subject_definitions 外观锚定用）=====\n${roleCards}` : '===== 角色卡 =====（无）',
  ]
  const audioRefs = sl.audio_refs ?? {}
  if (Object.keys(audioRefs).length) {
    const lines = Object.entries(audioRefs).map(([rid, p]) => `${rid} -> ${p}`)
    userLines.splice(1, 0, `===== 音频参考（音色种子，按顺序编 <Audio N>）=====\n${lines.join('\n')}`)
  }
  userLines.push('请输出 H3 提示词（纯文本，严格按模式）。')

  const duration = Number(sl.duration_total ?? 8)
  const { retry = 3 } = opts
  let lastIssues: string[] = ['未执行']
  for (let attempt = 1; attempt <= retry + 1; attempt++) {
    const raw = stripFence(
      await chatCompletion(systemPrompt, userLines.join('\n'), {
        model: opts.model,
        effort: opts.effort,
        maxTokens: opts.maxTokens ?? 24000, // reasoning 会吃大量 token，默认给足
      }),
    )
    const result = checkPrompt(raw, duration, opts.mode)
    if (result.level !== 'fail') {
      return { prompt: raw, attempts: attempt, issues: result.issues }
    }
    lastIssues = result.issues
  }
  throw new Error(`${retry + 1} 次尝试后仍失败: ${lastIssues.slice(0, 5).join('；')}`)
}

/** ref2va 官方参考指南（.pi/skills/h3-prompt-writing/references/ref-en.txt） */
function loadRefGuide(): string {
  if (fs.existsSync(REF2VA_GUIDE)) return fs.readFileSync(REF2VA_GUIDE, 'utf-8')
  const fallback = path.join(process.cwd(), '.pi', 'skills', 'h3-prompt-writing', 'references', 'ref-en.txt')
  return fs.existsSync(fallback) ? fs.readFileSync(fallback, 'utf-8') : ''
}
