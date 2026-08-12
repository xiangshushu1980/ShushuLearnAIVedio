/** 项目路由（docs/22 六节 API 设计） */
import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { createProject, listProjects, readProject, saveProject } from '../store.ts'
import { genShotlist } from '../tools/shotlistGen.ts'
import { genPrompt } from '../tools/promptStage2.ts'

const idParam = z.object({ id: z.string().regex(/^[a-zA-Z0-9_\u4e00-\u9fff-]+$/) })

const createBody = z.object({
  name: z.string().min(1),
  script: z.string().optional(),
  shotlist: z.string().optional(),
  prompt: z.string().optional(),
  promptMode: z.enum(['i2va', 'ref2va']).optional(),
})

const saveBody = z.object({
  script: z.string().optional(),
  shotlist: z.string().optional(),
  prompt: z.string().optional(),
  promptMode: z.enum(['i2va', 'ref2va']).optional(),
})

const genShotlistBody = z.object({
  model: z.enum(['deepseek-v4-flash', 'deepseek-v4-pro']).default('deepseek-v4-flash'),
  effort: z.enum(['high', 'medium', 'low']).default('high'),
  maxTokens: z.number().int().positive().optional(),
  retry: z.number().int().min(0).max(10).optional(),
  shotStyle: z.enum(['分镜剪辑', '长镜头流']).optional(),
  fewshot: z.array(z.string()).optional(),
  review: z.boolean().optional(),
})

const genPromptBody = z.object({
  mode: z.enum(['i2va', 'ref2va']),
  model: z.enum(['deepseek-v4-flash', 'deepseek-v4-pro']).default('deepseek-v4-flash'),
  effort: z.enum(['high', 'medium', 'low']).default('high'),
  maxTokens: z.number().int().positive().optional(),
  retry: z.number().int().min(0).max(10).optional(),
})

export async function projectRoutes(app: FastifyInstance): Promise<void> {
  app.get('/projects', async () => listProjects())

  app.post('/projects', async (req, reply) => {
    const parsed = createBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const { name, ...imported } = parsed.data
    try {
      return createProject(name, imported)
    } catch (e) {
      return reply.code(400).send({ error: (e as Error).message })
    }
  })

  app.get('/projects/:id', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      return readProject(id)
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  app.put('/projects/:id', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    const parsed = saveBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    try {
      return saveProject(id, parsed.data)
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  app.post('/projects/:id/generate-shotlist', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    const parsed = genShotlistBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const project = readProject(id)
    if (!project.script?.raw) return reply.code(400).send({ error: '项目缺少剧本（script）' })
    try {
      const result = await genShotlist(project.script.raw, parsed.data)
      saveProject(id, { shotlist: result.raw })
      return { ...result, shotlist: undefined, raw: undefined }
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  app.post('/projects/:id/generate-prompt', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    const parsed = genPromptBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const project = readProject(id)
    if (!project.shotlist) return reply.code(400).send({ error: '项目缺少拍摄本（shotlist）' })
    try {
      const result = await genPrompt(project.shotlistRaw ?? '', parsed.data)
      saveProject(id, { prompt: result.prompt, promptMode: parsed.data.mode })
      return { mode: parsed.data.mode, attempts: result.attempts, issues: result.issues }
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  app.get('/projects/:id/inputs', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      const project = readProject(id)
      return { inputs: project.inputs }
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })
}
