/**
 * H3 提示词 tokenizer（纯逻辑，前后端共享）
 * 标色 token 类型见 docs/22 第三节；输入源解析（<Picture N> 引用）也复用此规则
 */
import { REF_BADGE_COLORS, SOUND_LAYER_COLORS } from './colors.ts'

export type PromptToken =
  | { kind: 'text'; text: string }
  | { kind: 'ref'; label: 'Subject' | 'Picture' | 'Video' | 'Audio'; n: number; text: string }
  | { kind: 'shot'; n: number; hasTs: boolean; text: string }
  | { kind: 'dialogue'; text: string }
  | { kind: 'motion'; text: string }
  | { kind: 'sound'; layer: 'ambient' | 'fx' | 'bgm'; na: boolean; text: string }
  | { kind: 'bgmdesc'; text: string }
  | { kind: 'na'; text: string }

// camera 上下文运动短语（动词式 + 名词式），限定语境避免误伤普通词
const MOTION_RE =
  /\bthe camera (?:pushes in|pulls out|zooms in|zooms out|pans left|pans right|trucks left|trucks right|tilts up|tilts down|tracks forward|tracks backward|arcs around|stays static|moves (?:in|out|left|right|up|down))\b|\b(push-in|push in|tracking shot|arc shot|static shot|pan left|pan right|tilt up|tilt down)\b/gi

const DIALOGUE_RE = /<d>[^<]*<\/d>/g
const REF_RE = /<(Subject|Picture|Video|Audio)\s+(\d+)>/g
const SHOT_RE = /\[Shot\s+(\d+)\](?:\s+At\s+(\d{2}:\d{2}\.\d{3}))?/g
const SOUND_RE = /(ambient|fx|bgm):\s*(N\/A)?/gi
const BGM_DESC_RE = /non_diegetic_music:\s*(?!\s*N\/A\b)[^\n]*/gi
const NA_RE = /\bN\/A\b/g

/** 把提示词文本切分为标色 token 序列（区间合并，先到先得，长 token 优先） */
export function tokenizePrompt(text: string): PromptToken[] {
  const ranges: Array<{ start: number; end: number; make: () => PromptToken }> = []
  const addAll = (re: RegExp, make: (m: RegExpExecArray) => PromptToken) => {
    const r = new RegExp(re.source, re.flags.includes('g') ? re.flags : `${re.flags}g`)
    let m: RegExpExecArray | null
    while ((m = r.exec(text)) !== null) {
      const mm = m // 快照：闭包在循环结束后执行，共享 m 会变成 null
      ranges.push({ start: m.index, end: m.index + m[0].length, make: () => make(mm) })
    }
  }

  addAll(DIALOGUE_RE, (m) => ({ kind: 'dialogue', text: m[0] }))
  addAll(REF_RE, (m) => ({ kind: 'ref', label: m[1] as PromptToken extends { kind: 'ref'; label: infer L } ? L : never, n: Number(m[2]), text: m[0] }))
  addAll(SHOT_RE, (m) => ({ kind: 'shot', n: Number(m[1]), hasTs: Boolean(m[2]), text: m[0] }))
  addAll(MOTION_RE, (m) => ({ kind: 'motion', text: m[0] }))
  addAll(SOUND_RE, (m) => ({ kind: 'sound', layer: m[1].toLowerCase() as 'ambient' | 'fx' | 'bgm', na: Boolean(m[2]), text: m[0] }))
  addAll(BGM_DESC_RE, (m) => ({ kind: 'bgmdesc', text: m[0] }))
  addAll(NA_RE, (m) => ({ kind: 'na', text: m[0] }))

  ranges.sort((a, b) => a.start - b.start || b.end - a.end)
  const tokens: PromptToken[] = []
  let pos = 0
  for (const r of ranges) {
    if (r.start < pos) continue // 已被更长 token 覆盖
    if (r.start > pos) tokens.push({ kind: 'text', text: text.slice(pos, r.start) })
    tokens.push(r.make())
    pos = r.end
  }
  if (pos < text.length) tokens.push({ kind: 'text', text: text.slice(pos) })
  return tokens
}

/** 提取提示词中 <Picture N> 引用（输入源解析用） */
export function extractPictureRefs(text: string): number[] {
  const refs = new Set<number>()
  for (const t of tokenizePrompt(text)) {
    if (t.kind === 'ref' && t.label === 'Picture') refs.add(t.n)
  }
  return [...refs].sort((a, b) => a - b)
}

/** 提取 <Subject N> 引用 */
export function extractSubjectRefs(text: string): number[] {
  const refs = new Set<number>()
  for (const t of tokenizePrompt(text)) {
    if (t.kind === 'ref' && t.label === 'Subject') refs.add(t.n)
  }
  return [...refs].sort((a, b) => a - b)
}

/**
 * 提示词引用映射解析（渲染输入源用）
 * Ref2VA 约定：`<Picture M> is the reference image for <Subject N>`；Subject N ↔ role_cards[N-1]
 */
export interface RefMapping {
  pictureN: number
  subjectN: number
  /** 映射到的实体 id（由 role_cards 顺序决定，前端传入） */
  entityId?: string
}

export function parseRefMapping(prompt: string, roleCards: string[]): RefMapping[] {
  const map: RefMapping[] = []
  // <Picture M> is the reference (still )image for <Subject N>（LLM 句式不稳定，两种都兼容；允许后缀）
  const re = /<Picture\s+(\d+)>\s+is the reference (?:still )?image for <Subject\s+(\d+)>/gi
  let m: RegExpExecArray | null
  while ((m = re.exec(prompt)) !== null) {
    const subjectN = Number(m[2])
    map.push({
      pictureN: Number(m[1]),
      subjectN,
      entityId: roleCards[subjectN - 1],
    })
  }
  return map
}

export { REF_BADGE_COLORS, SOUND_LAYER_COLORS }
