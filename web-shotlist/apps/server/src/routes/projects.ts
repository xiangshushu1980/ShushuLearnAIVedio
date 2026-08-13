/** 项目路由（docs/22 六节 API 设计） */
import type { FastifyInstance } from 'fastify'
import {
  createProjectBody,
  genPromptBody,
  genShotlistBody,
  idParam,
  renameProjectBody,
  saveProjectBody,
  projectImportBody,
} from '@shotlist/shared'
import { createProject, exportProject, importProject, listProjects, listRoleCards, listTrash, purgeProject, readProject, renameProject, restoreProject, saveProject, trashProject } from '../store.ts'
import { gateEntities } from '../gate.ts'
import { genShotlist } from '../tools/shotlistGen.ts'
import { genPrompt } from '../tools/promptStage2.ts'

export async function projectRoutes(app: FastifyInstance): Promise<void> {
  app.get('/projects', async () => listProjects())

  app.post('/projects', async (req, reply) => {
    const parsed = createProjectBody.safeParse(req.body)
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
    const parsed = saveProjectBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    try {
      return saveProject(id, parsed.data)
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  // 重命名（仅改显示名）
  app.post('/projects/:id/rename', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    const parsed = renameProjectBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    try {
      const meta = renameProject(id, parsed.data.name)
      return meta
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  // 导出 JSON 包
  app.get('/projects/:id/export', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      return exportProject(id)
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  // 导入 JSON 包（新建项目）
  app.post('/projects/import', async (req, reply) => {
    const pack = projectImportBody.safeParse(req.body)
    if (!pack.success) return reply.code(400).send({ error: pack.error.issues.map((i) => i.message).join('；') })
    try {
      return importProject(pack.data as import('@shotlist/shared').ProjectExport)
    } catch (e) {
      return reply.code(400).send({ error: (e as Error).message })
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
    // 渲染门禁：引用实体必须合格（无 fallback；文字不合格 = 硬阻塞）
    // 引用来源：剧本参数头 role_cards + 拍摄本 role_cards + audio_refs（防 LLM 输出丢 role_cards）
    const scriptRoleIds = project.script?.head?.role_cards ?? []
    const shotlistRoleIds = project.shotlist.role_cards ?? []
    const audioIds = Object.keys(project.shotlist.audio_refs ?? {})
    const gate = gateEntities([...scriptRoleIds, ...shotlistRoleIds, ...audioIds])
    if (!gate.allTextOk) {
      return reply.code(422).send({ error: '实体门禁未通过：' + gate.blocks.join('；'), gate: gate.blocks })
    }
    try {
      const result = await genPrompt(project.shotlistRaw ?? '', parsed.data)
      saveProject(id, { prompt: result.prompt, promptMode: parsed.data.mode })
      return { mode: parsed.data.mode, attempts: result.attempts, issues: result.issues, gate }
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

  // ===== 回收站（次要入口；删除需前端确认）=====
  app.get('/trash', async () => listTrash())

  app.post('/projects/:id/trash', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      return trashProject(id)
    } catch (e) {
      return reply.code(400).send({ error: (e as Error).message })
    }
  })

  app.post('/projects/:id/restore', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      return restoreProject(id)
    } catch (e) {
      return reply.code(400).send({ error: (e as Error).message })
    }
  })

  app.delete('/projects/:id', async (req, reply) => {
    const { id } = idParam.parse(req.params)
    try {
      purgeProject(id)
      return { ok: true }
    } catch (e) {
      return reply.code(400).send({ error: (e as Error).message })
    }
  })

  // 角色卡列表（参数头 role_cards 多选用）
  app.get('/role-cards', async () => listRoleCards())
}
