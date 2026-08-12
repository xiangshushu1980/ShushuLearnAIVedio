/** DeepSeek LLM client（OpenAI 兼容；key 从环境/配置读，不进 git）*/
import { getDeepSeekKey } from './config.ts'

const API_URL = 'https://api.deepseek.com/chat/completions'

export type Effort = 'high' | 'medium' | 'low'

export interface LlmCallOptions {
  model: string
  effort?: Effort
  temperature?: number
  maxTokens?: number
  timeoutMs?: number
}

export async function chatCompletion(system: string, user: string, opts: LlmCallOptions): Promise<string> {
  const { model, effort = 'high', temperature = 0.7, maxTokens = 12000, timeoutMs = 600_000 } = opts
  const body: Record<string, unknown> = {
    model,
    messages: [
      { role: 'system', content: system },
      { role: 'user', content: user },
    ],
    reasoning: { effort },
    temperature,
    max_tokens: maxTokens,
  }
  const r = await fetch(API_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getDeepSeekKey()}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(timeoutMs),
  })
  if (!r.ok) {
    const text = await r.text().catch(() => '')
    throw new Error(`[DeepSeek] HTTP ${r.status}: ${text.slice(0, 500)}`)
  }
  const data = (await r.json()) as {
    choices: Array<{ message: { content?: string; reasoning_content?: string } }>
  }
  const content = (data.choices[0]?.message?.content ?? '').trim()
  if (!content) {
    throw new Error(`[DeepSeek] 正文为空（reasoning 吃满 ${maxTokens} tokens，请调大 maxTokens 或降 effort）`)
  }
  return content
}

/** 去除输出 markdown fence */
export function stripFence(text: string): string {
  let t = text.trim().replace(/^```(?:yaml|yml|txt|text)?\s*/, '')
  t = t.replace(/\s*```$/, '')
  return t.trim()
}
