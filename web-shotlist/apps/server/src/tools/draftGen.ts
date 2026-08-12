/**
 * 工具 A0：点子 → 世界观手册 + 剧本 YAML（docs/22 扩展路线第 6 项）
 * 输入几句话，扩展为可选长度的世界观和剧本
 */
import { chatCompletion, type Effort } from '../llm.ts'

export type DraftLength = 'short' | 'medium' | 'long'

export const LENGTH_SPECS: Record<DraftLength, string> = {
  short: '短（约 8s，1 个场景，1-2 个角色，1-2 镜）',
  medium: '中（约 12s，2 个场景，2-3 个角色，2-3 镜）',
  long: '长（约 20s，3-4 个场景，3 个以上角色含配角，3-5 镜）',
}

const DRAFT_TPL = `你是动画短片编剧（工具 A0）。基于用户点子，创作世界观手册和剧本 YAML。

===== 世界观手册要求 =====
1-2 段：世界基调 / 核心设定 / 角色关系一句话。简洁，为剧本服务。

===== 剧本要求 =====
YAML 参数头 + 正文：
--- 
title: 场景标题（短名）
style: 视觉风格（如 日系清新/冷峻纪实/舞台戏剧）
ratio: 16:9
scene: 首帧场景 id（简短英文，如 beach/stage/night/classroom）
duration: 秒数数字（不带单位，如 8）
sound: 环境音 + BGM 描述
role_cards: [角色 id 列表（英文短 id，如 alya_v1）]
chain: independent
shot_style: 分镜剪辑（或 长镜头流，二选一，不要写其他值）
--- 
正文：2-5 段，场景/动作/台词（台词用引号）。一镜一动作，画面具体可拍摄。

长度档位（按档位控制 duration 与内容量）：
{length_spec}

===== 输出格式（严格）=====
===== 世界观 =====
（世界观文本）

===== 剧本 =====
（剧本 YAML 全文）

无其他前言解释。`

export interface DraftInput {
  idea: string
  length: DraftLength
  /** 是否需要世界观（false 只出剧本） */
  withWorldview: boolean
}

export interface DraftResult {
  worldview: string
  script: string
}

export async function genDraft(input: DraftInput, opts: { model?: string; effort?: Effort } = {}): Promise<DraftResult> {
  const user = DRAFT_TPL.replace('{length_spec}', LENGTH_SPECS[input.length])
  const raw = await chatCompletion(
    '你是动画短片编剧，输出严格按格式。',
    `${user}\n\n===== 用户点子 =====\n${input.idea}`,
    {
      model: opts.model ?? 'deepseek-v4-flash',
      effort: opts.effort ?? 'high',
      temperature: 0.8,
      maxTokens: 16000,
    },
  )
  return splitDraft(raw, input.withWorldview)
}

export function splitDraft(raw: string, withWorldview: boolean): DraftResult {
  const wm = /===== 世界观 =====\n([\s\S]*?)\n===== 剧本 =====/.exec(raw)
  const sm = /===== 剧本 =====\n([\s\S]*)$/.exec(raw)
  if (!sm) throw new Error(`LLM 输出缺少「===== 剧本 =====」段: ${raw.slice(0, 300)}`)
  return {
    worldview: withWorldview ? (wm?.[1]?.trim() ?? '') : '',
    script: sm[1].trim(),
  }
}
