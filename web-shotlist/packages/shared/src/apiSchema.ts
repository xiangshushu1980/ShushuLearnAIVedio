/** API schema 单源（方案 A：shared 唯一权威，server 消费、web 用 z.infer 推导类型）
 * 律令：禁止在 server 路由里新写 z.object —— 一律加到本文件
 */
import { z } from 'zod'
import { ENTITY_TYPES } from './types.js'

// ===== 通用 =====
export const modelChoice = z.enum(['deepseek-v4-flash', 'deepseek-v4-pro']).default('deepseek-v4-flash')
export const idParam = z.object({ id: z.string().regex(/^[a-zA-Z0-9_\u4e00-\u9fff-]+$/) })
export const entityIdParam = z.object({ id: z.string().min(1) })

// ===== 项目 =====
export const createProjectBody = z.object({
  name: z.string().min(1),
  script: z.string().optional(),
  shotlist: z.string().optional(),
  prompt: z.string().optional(),
  promptMode: z.enum(['i2va', 'ref2va']).optional(),
})
export type CreateProjectInput = z.input<typeof createProjectBody>

export const saveProjectBody = z.object({
  script: z.string().optional(),
  shotlist: z.string().optional(),
  prompt: z.string().optional(),
  promptMode: z.enum(['i2va', 'ref2va']).optional(),
})
export type SaveProjectInput = z.input<typeof saveProjectBody>

export const renameProjectBody = z.object({ name: z.string().min(1).max(80) })

export const projectImportBody = z.object({
  format: z.literal('shotlist-project'),
  version: z.number().optional(),
  exportedAt: z.string().optional(),
  name: z.string().min(1).max(80),
  script: z.string().nullable().optional(),
  shotlist: z.string().nullable().optional(),
  prompt: z.string().nullable().optional(),
  promptMode: z.enum(['i2va', 'ref2va']).nullable().optional(),
  entities: z.array(z.string()).optional(),
})

export const genShotlistBody = z.object({
  model: modelChoice,
  effort: z.enum(['high', 'medium', 'low']).default('high'),
  maxTokens: z.number().int().positive().optional(),
  retry: z.number().int().min(0).max(10).optional(),
  shotStyle: z.enum(['分镜剪辑', '长镜头流']).optional(),
  fewshot: z.array(z.string()).optional(),
  review: z.boolean().optional(),
})
export type GenShotlistInput = z.input<typeof genShotlistBody>

export const genPromptBody = z.object({
  mode: z.enum(['i2va', 'ref2va']),
  model: modelChoice,
  effort: z.enum(['high', 'medium', 'low']).default('high'),
  maxTokens: z.number().int().positive().optional(),
  retry: z.number().int().min(0).max(10).optional(),
})
export type GenPromptInput = z.input<typeof genPromptBody>

// ===== 实体 =====
export const entityBody = z.object({
  id: z.string().optional(),
  name: z.string().min(1),
  type: z.enum(ENTITY_TYPES).default('角色'),
  importance: z.enum(['core', 'secondary']).default('secondary'),
  stars: z.number().int().min(1).max(5).optional(),
  appearance: z.string().default(''),
  sound: z.string().default(''),
  description: z.string().default(''),
  source: z.string().optional(),
  related: z.array(z.object({ id: z.string(), relation: z.string() })).optional(),
  variants: z
    .array(z.object({ id: z.string().min(1), name: z.string().min(1), description: z.string().default(''), art: z.array(z.string()).optional() }))
    .optional(),
})
export type EntityInput = z.input<typeof entityBody>

export const styleBody = z.object({ prompt: z.string().max(500).default('') })

export const extractBody = z.object({
  worldview: z.string().default(''),
  script: z.string().min(1, '需要剧本/世界观文本'),
  model: modelChoice,
})
export type ExtractInput = z.input<typeof extractBody>

export const artGenBody = z.object({ prompt: z.string().optional(), seed: z.number().optional(), variant: z.string().optional() })

export const voiceGenBody = z.object({
  kind: z.enum(['custom', 'design', 'clone']),
  text: z.string().min(1),
  speaker: z.string().optional(),
  instruct: z.string().optional(),
  refText: z.string().optional(),
  seed: z.number().optional(),
})
export type VoiceGenInput = z.input<typeof voiceGenBody>

export const refreshEntityBody = z.object({
  worldview: z.string().default(''),
  script: z.string().min(1, '需要剧本/世界观文本'),
})

export const gateBody = z.object({ ids: z.array(z.string()) })

// ===== 工具 A0 =====
export const draftBody = z.object({
  idea: z.string().min(1, '输入几句点子'),
  length: z.enum(['short', 'medium', 'long']).default('medium'),
  withWorldview: z.boolean().default(true),
  model: modelChoice,
})
export type DraftInput = z.input<typeof draftBody>

// ===== 任务 =====
export const taskParam = z.object({ id: z.string().min(1) })
