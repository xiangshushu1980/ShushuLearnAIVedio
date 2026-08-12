/**
 * H3 提示词确定性校验（移植 scripts/prompt_validator.py，2026-08-12）
 * 规则：三核心段齐全 / [Shot N] 预算 / 切点式时间戳递增 / 无前言 / 无 fence / 无第三方 IP
 * ref2va 额外：六段式字段齐全 + <Subject N>/<Picture N> label
 */
import { shotBudget } from './shotlistSchema.ts'

export const PROMPT_FIELDS = ['integrated_multimodal_description', 'overall_soundscape', 'non_diegetic_music'] as const
export const SIX_FIELDS = [
  'subject_definitions',
  'summary',
  'retention_analysis',
  'detailed_description',
  'overall_soundscape',
  'non_diegetic_music',
] as const

const IP_PATTERN = /\b(Warcraft|Marvel|Star Wars|Pok[eé]mon|Disney|Nintendo|Batman|Superman)\b/gi

export interface PromptCheckResult {
  issues: string[]
  warns: string[]
  level: 'pass' | 'warn' | 'fail'
  shots: number
}

export function checkPrompt(text: string, duration?: number, mode: 'i2va' | 'ref2va' | 't2va' = 't2va'): PromptCheckResult {
  const issues: string[] = []
  const warns: string[] = []
  const t = text.trim()

  if (mode === 'ref2va') {
    return checkSixField(t, duration)
  }

  // 1. 字段齐全 + 冒号
  for (const f of PROMPT_FIELDS) {
    if (!t.includes(f)) issues.push(`缺字段: ${f}`)
    else if (!new RegExp(`${f}\\s*:`).test(t)) issues.push(`字段缺冒号: ${f}`)
  }

  // 2. 镜头数与 Shot1 时间戳
  const shots = [...t.matchAll(/\[Shot (\d+)\]/g)].map((m) => Number(m[1]))
  const uniq = [...new Set(shots)]
  if (uniq.length === 0) {
    issues.push('无 [Shot N] 镜头标记')
  } else {
    if (duration) {
      const { max } = shotBudget(duration)
      if (uniq.length > max) warns.push(`镜头预算超: ${duration}s 出 ${uniq.length} 镜（应 ≤${max}）`)
      else if (duration >= 7 && uniq.length < 2) warns.push(`镜头预算偏离: ${duration}s 出 ${uniq.length} 镜（应 2-3）`)
    }
    // Shot 1 段内时间戳（[Shot 1] 到 [Shot 2] 或结尾之间）
    const m1 = /\[Shot 1\]([^\[]*?)(?:\[Shot 2\]|\Z)/s.exec(t)
    if (m1 && /At\s*0*:\d/.test(m1[1])) {
      if (mode === 'i2va') warns.push('Shot 1 段内嵌切点（i2v 与 IR 实测同构，软要求）')
      else issues.push('Shot 1 段落内出现时间戳（t2v 应带 [Shot N] 标签切点）')
    }
    // 切点式时间戳
    const cutTs = [...t.matchAll(/\[Shot (\d+)\](?:[^\[]*?)At (00:\d{2}\.\d{3})/g)].map((m) => m[2])
    const times = cutTs.map((x) => Number(x.split(':')[1]))
    // 裸切点 = 切点总数 - 带标签数
    const allCuts = [...t.matchAll(/At 00:\d{2}\.\d{3}, the camera (?:cuts|transitions|changes)/g)].length
    const taggedCuts = [...t.matchAll(/\[Shot \d+\](?:[^\[]*?)At 00:\d{2}\.\d{3}, the camera (?:cuts|transitions|changes)/g)].length
    const bare = allCuts - taggedCuts
    if (bare > 0) warns.push(`裸切点缺 [Shot N] 标签: ${bare} 处（i2v 软要求，t2v 建议修）`)
    if (uniq.length > 1 && cutTs.length === 0 && bare === 0) warns.push('多镜但无切点式时间戳（At MM:SS.mmm）')
    const sorted = [...times].sort((a, b) => a - b)
    if (times.length && JSON.stringify(times) !== JSON.stringify(sorted)) issues.push(`时间戳非递增: ${times.join(',')}`)
    if (duration && times.length && Math.max(...times) >= duration) issues.push(`时间戳超时长: ${times.join(',')} >= ${duration}s`)
    if (/^(?:[Ff]rom|[Tt]o) 00:/.test(t)) warns.push('使用时段式时间（From..to），应为切点式')
  }

  // 3. 无前言
  const firstLine = t.split('\n')[0] ?? ''
  if (!/^integrated_multimodal_description\s*:/.test(firstLine)) {
    if (!(mode === 'i2va' && firstLine.startsWith('For the target video'))) {
      warns.push(`首行非字段开头（有前言?）: ${JSON.stringify(firstLine.slice(0, 60))}`)
    }
  }

  // 4. 无 fence / IP
  if (t.includes('```')) issues.push('包含 markdown fence')
  const ipHits = t.match(IP_PATTERN) ?? []
  for (const hit of ipHits) issues.push(`含第三方 IP 名: ${hit}`)

  // 5. 声音层非空
  for (const f of ['overall_soundscape', 'non_diegetic_music'] as const) {
    const m = new RegExp(`${f}\\s*:\\s*(.+)`, 's').exec(t)
    if (!m || !m[1].trim()) issues.push(`${f} 为空`)
    else if (m[1].trim() === 'N/A' && f === 'overall_soundscape') issues.push('overall_soundscape 不允许 N/A')
  }

  return { issues, warns, level: issues.length ? 'fail' : warns.length ? 'warn' : 'pass', shots: uniq.length }
}

/** ref2va 六段式检查（移植 h3_prompt_stage2.py six_field_check） */
function checkSixField(t: string, duration?: number): PromptCheckResult {
  const issues: string[] = []
  const warns: string[] = []
  for (const f of SIX_FIELDS) {
    if (!t.includes(f)) issues.push(`缺六段式字段: ${f}`)
    else if (!new RegExp(`${f}\\s*:`).test(t)) issues.push(`字段缺冒号: ${f}`)
  }
  if (!/<Subject/.test(t) && !/<Picture/.test(t)) issues.push('六段式缺 <Subject N>/<Picture N> label')
  const shots = [...t.matchAll(/\[Shot (\d+)\]/g)].map((m) => Number(m[1]))
  const uniq = [...new Set(shots)]
  if (uniq.length && duration) {
    const { max } = shotBudget(duration)
    if (uniq.length > max) warns.push(`镜头预算超: ${duration}s 出 ${uniq.length} 镜（应 ≤${max}）`)
  }
  if (t.includes('```')) issues.push('包含 markdown fence')
  const ipHits = t.match(IP_PATTERN) ?? []
  for (const hit of ipHits) issues.push(`含第三方 IP 名: ${hit}`)
  return { issues, warns, level: issues.length ? 'fail' : warns.length ? 'warn' : 'pass', shots: uniq.length }
}
