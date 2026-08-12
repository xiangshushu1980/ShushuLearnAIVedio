/**
 * H3 提示词标色渲染器（docs/22 第三节标色方案）
 * tokenizer 在 @shotlist/shared（promptTokenizer.ts），本组件只做渲染
 */
import { Fragment } from 'react'
import { REF_BADGE_COLORS, SOUND_LAYER_COLORS, tokenizePrompt, type PromptToken } from '@shotlist/shared'
import { cn } from '@/lib/utils'

export function PromptHighlight({ text, className }: { text: string; className?: string }) {
  const tokens = tokenizePrompt(text)
  return (
    <pre className={cn('whitespace-pre-wrap font-mono text-[13px] leading-relaxed', className)}>
      {tokens.map((t, i) => (
        <Fragment key={i}>{renderToken(t)}</Fragment>
      ))}
    </pre>
  )
}

function renderToken(t: PromptToken) {
  switch (t.kind) {
    case 'text':
      return <span className="text-slate-200">{t.text}</span>
    case 'ref': {
      const color = REF_BADGE_COLORS[(t.n - 1) % REF_BADGE_COLORS.length]
      return (
        <span className="mx-0.5 inline-flex items-center gap-1 rounded-md border border-slate-600 bg-slate-800 px-1 py-px text-blue-300">
          <span className={cn('rounded px-1 text-[10px] font-bold', color)}>
            {t.label[0]}{t.n}
          </span>
          {t.text}
        </span>
      )
    }
    case 'shot':
      return (
        <span className="mx-0.5 inline-flex items-center gap-1 rounded bg-slate-950 px-1.5 py-px font-semibold text-cyan-300 ring-1 ring-slate-700">
          ⏱ {t.text}
        </span>
      )
    case 'dialogue':
      return (
        <span className="mx-0.5 inline-flex items-center gap-0.5 rounded bg-blue-950/60 px-1 py-px italic text-blue-200 ring-1 ring-blue-900">
          ❝{t.text.replace(/^<d>|<\/d>$/g, '')}❞
        </span>
      )
    case 'motion':
      return <span className="italic text-fuchsia-300 underline decoration-dotted underline-offset-2">🎥 {t.text}</span>
    case 'sound': {
      const c = SOUND_LAYER_COLORS[t.layer]
      return (
        <span className={cn('mx-0.5 inline-flex items-center gap-1 rounded border px-1 py-px', c)}>
          🔊 {t.text}
          {t.na && <span className="rounded bg-slate-700 px-1 text-[10px] text-slate-300">N/A 特意</span>}
        </span>
      )
    }
    case 'bgmdesc':
      return <span className="text-purple-300">{t.text}</span>
    case 'na':
      return (
        <span className="mx-0.5 rounded bg-slate-700/80 px-1 py-px text-xs text-slate-300" title="无配乐为导演特意行为">
          {t.text}
        </span>
      )
  }
}
