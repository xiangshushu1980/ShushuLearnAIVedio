/**
 * 剧本参数头表单（docs/22 参数头模板化）
 * 与正文 textarea 双向绑定：表单修改 → 立即重写参数头文本；文本修改 → 防抖解析回填表单
 */
import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  CHAIN_OPTIONS,
  DURATION_PRESETS,
  RATIO_OPTIONS,
  SCENE_PRESETS,
  SHOT_STYLE_OPTIONS,
  type ScriptHead,
} from '@shotlist/shared'
import { api } from '@/lib/api'
import { cn } from '@/lib/utils'

interface Props {
  head: ScriptHead | null
  headErr: string | null
  onPatch: (patch: Partial<ScriptHead>) => void
}

export function ScriptHeadForm({ head, headErr, onPatch }: Props) {
  const { data: roleCardIds = [] } = useQuery({ queryKey: ['role-cards'], queryFn: api.listRoleCards })
  const [audioText, setAudioText] = useState('')
  const [newRole, setNewRole] = useState('')

  // audio_refs 文本 ↔ record 同步（仅展示层，提交时统一 onPatch）
  const audioTextFromHead = useMemo(() => {
    const ar = head?.audio_refs ?? {}
    return Object.entries(ar)
      .map(([k, v]) => `${k}: ${v}`)
      .join('\n')
  }, [head?.audio_refs])
  const [audioDraft, setAudioDraft] = useState<string | null>(null)
  const audioTextShown = audioDraft ?? audioTextFromHead

  const patchAudio = (text: string) => {
    setAudioDraft(text)
    const rec: Record<string, string> = {}
    for (const line of text.split('\n')) {
      const m = /^\s*([^\s:]+)\s*:\s*(.+?)\s*$/.exec(line)
      if (m) rec[m[1]] = m[2]
    }
    onPatch({ audio_refs: Object.keys(rec).length ? rec : undefined })
  }

  const roleCards = head?.role_cards ?? []
  const toggleRole = (id: string) => {
    const next = roleCards.includes(id) ? roleCards.filter((r) => r !== id) : [...roleCards, id]
    onPatch({ role_cards: next })
  }
  const addRole = () => {
    const id = newRole.trim()
    if (id && !roleCards.includes(id)) onPatch({ role_cards: [...roleCards, id] })
    setNewRole('')
  }

  return (
    <div className="space-y-2 rounded border border-slate-800 bg-slate-900/50 p-2.5">
      {headErr && (
        <p className="rounded border border-red-900 bg-red-950/50 px-2 py-1 text-[11px] text-red-300">
          ⚠ 参数头解析失败（表单暂停同步）：{headErr}
        </p>
      )}
      <div className="grid grid-cols-2 gap-x-2 gap-y-1.5">
        <Field label="title" className="col-span-2">
          <input value={head?.title ?? ''} onChange={(e) => onPatch({ title: e.target.value })} placeholder="场景标题" />
        </Field>
        <Field label="style">
          <input
            value={head?.style ?? ''}
            onChange={(e) => onPatch({ style: e.target.value })}
            list="style-presets"
            placeholder="风格"
          />
          <datalist id="style-presets">
            <option value="日系清新" />
            <option value="冷峻纪实" />
            <option value="舞台戏剧" />
            <option value="赛璐璐" />
          </datalist>
        </Field>
        <Field label="ratio">
          <input value={head?.ratio ?? '16:9'} onChange={(e) => onPatch({ ratio: e.target.value })} list="ratio-options" />
          <datalist id="ratio-options">
            {RATIO_OPTIONS.map((r) => (
              <option key={r} value={r} />
            ))}
          </datalist>
        </Field>
        <Field label="scene">
          <input
            value={head?.scene ?? ''}
            onChange={(e) => onPatch({ scene: e.target.value })}
            list="scene-presets"
            placeholder="beach/stage/…"
          />
          <datalist id="scene-presets">
            {SCENE_PRESETS.map((s) => (
              <option key={s} value={s} />
            ))}
          </datalist>
        </Field>
        <Field label="duration (s)">
          <div className="flex items-center gap-1">
            <input
              type="number"
              min={1}
              step={0.5}
              value={head?.duration ?? 8}
              onChange={(e) => onPatch({ duration: Number(e.target.value) })}
              className="w-16"
            />
            <div className="flex flex-wrap gap-0.5">
              {DURATION_PRESETS.map((d) => (
                <button
                  key={d}
                  onClick={() => onPatch({ duration: d })}
                  className={cn(
                    'rounded px-1 py-0.5 text-[10px] transition-colors',
                    head?.duration === d ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700',
                  )}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </Field>
        <Field label="chain">
          <select
            value={head?.chain ?? 'auto'}
            onChange={(e) => {
              const v = e.target.value
              onPatch(v === 'auto' ? { chain: undefined } : { chain: v as ScriptHead['chain'] })
            }}
          >
            <option value="auto">自动（推荐）</option>
            {CHAIN_OPTIONS.map((c) => (
              <option key={c.value} value={c.value} title={c.hint}>
                {c.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="shot_style">
          <select
            value={head?.shot_style ?? 'auto'}
            onChange={(e) => {
              const v = e.target.value
              onPatch(v === 'auto' ? { shot_style: undefined } : { shot_style: v })
            }}
          >
            <option value="auto">自动（推荐）</option>
            {SHOT_STYLE_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
        <Field label="sound" className="col-span-2">
          <input value={head?.sound ?? ''} onChange={(e) => onPatch({ sound: e.target.value })} placeholder="环境音 + BGM 描述" />
        </Field>
        <Field label="no_bgm" className="col-span-2">
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="checkbox"
              checked={Boolean(head?.no_bgm)}
              onChange={(e) => onPatch({ no_bgm: e.target.checked })}
              className="h-3.5 w-3.5 accent-blue-600"
            />
            <span className="text-[11px] text-slate-400">本段不要 BGM（bgm 一律 N/A + 镜头情绪中性化）</span>
          </label>
        </Field>
        <Field label="role_cards" className="col-span-2">
          <div className="flex flex-wrap gap-1">
            {[...new Set([...roleCardIds, ...roleCards])].map((id) => (
              <button
                key={id}
                onClick={() => toggleRole(id)}
                title={roleCardIds.includes(id) ? '已有角色卡' : '自定义（未找到角色卡文件）'}
                className={cn(
                  'rounded-full px-2 py-0.5 text-[11px] transition-colors',
                  roleCards.includes(id)
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700',
                )}
              >
                {id}
              </button>
            ))}
            <span className="flex items-center gap-1">
              <input
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addRole()}
                placeholder="+ 添加"
                className="w-16 px-1 py-0.5 text-[11px]"
              />
            </span>
          </div>
          <p className="text-[10px] text-slate-600">点击切换；输入后回车可添加自定义 id</p>
        </Field>
        <Field label="audio_refs" className="col-span-2">
          <textarea
            value={audioTextShown}
            onChange={(e) => setAudioDraft(e.target.value)}
            onBlur={() => {
              if (audioDraft !== null) patchAudio(audioDraft)
              setAudioDraft(null)
            }}
            placeholder={'alya_v1: voice_seeds/voice_seed_alya.wav\n（每行：角色id: wav路径，离开输入框后生效）'}
            rows={2}
            className="w-full font-mono text-[11px]"
          />
        </Field>
      </div>
    </div>
  )
}

function Field({ label, className, children }: { label: string; className?: string; children: React.ReactNode }) {
  return (
    <div className={cn('min-w-0', className)}>
      <label className="mb-0.5 block text-[10px] font-medium uppercase tracking-wide text-slate-500">{label}</label>
      {children}
    </div>
  )
}
