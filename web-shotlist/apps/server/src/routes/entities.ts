/** 实体卡路由（docs/22 六节；V1：CRUD + AI 抽取） */
import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { comfyAlive, generateArt, listEntityArt, readArtFile, waitArtDone } from '../art.ts'
import { deleteEntity, listEntities, readEntity, saveEntity } from '../entities.ts'
import { extractEntities } from '../tools/entityExtract.ts'

const entityBody = z.object({
  id: z.string().optional(),
  name: z.string().min(1),
  type: z.enum(['角色', '场景', '物件', '技能', '组织', '地点']).default('角色'),
  importance: z.enum(['core', 'secondary']).default('secondary'),
  appearance: z.string().default(''),
  sound: z.string().default(''),
  description: z.string().default(''),
  source: z.string().optional(),
  related: z.array(z.object({ id: z.string(), relation: z.string() })).optional(),
})

const extractBody = z.object({
  worldview: z.string().default(''),
  script: z.string().min(1, '需要剧本/世界观文本'),
  model: z.enum(['deepseek-v4-flash', 'deepseek-v4-pro']).default('deepseek-v4-flash'),
})

export async function entityRoutes(app: FastifyInstance): Promise<void> {
  app.get('/entities', async () => listEntities())

  app.get('/entities/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const e = readEntity(id)
    if (!e) return reply.code(404).send({ error: `实体不存在: ${id}` })
    return e
  })

  app.post('/entities', async (req, reply) => {
    const parsed = entityBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const d = parsed.data
    return saveEntity({
      id: d.id ?? d.name,
      name: d.name,
      type: d.type,
      importance: d.importance,
      appearance: d.appearance,
      sound: d.sound,
      description: d.description,
      source: d.source,
      related: d.related,
    })
  })

  app.put('/entities/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    const parsed = entityBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    return saveEntity({ ...parsed.data, id })
  })

  app.delete('/entities/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    try {
      deleteEntity(id)
      return { ok: true }
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  // AI 抽取：世界观 + 剧本 → 实体卡（默认创建方式；落库）
  app.post('/entities/extract', async (req, reply) => {
    const parsed = extractBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    try {
      const entities = await extractEntities(parsed.data)
      const saved = entities.map((e) => saveEntity(e))
      return { entities: saved }
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  // ===== 设定图（ANIMA t2i；ComfyUI 执行层）=====
  app.get('/entities/:id/art', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    return { images: listEntityArt(id), comfyOnline: await comfyAlive() }
  })

  app.post('/entities/:id/art', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const parsed = z.object({ prompt: z.string().optional(), seed: z.number().optional() }).safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    if (!(await comfyAlive())) return reply.code(503).send({ error: 'ComfyUI 不在线（http://127.0.0.1:8188）' })
    try {
      const { promptId } = await generateArt(id, parsed.data.prompt, parsed.data.seed)
      if (!promptId) throw new Error('未拿到 prompt_id')
      const images = await waitArtDone(promptId)
      return { ok: true, images }
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  // 图片静态服务（读 ComfyUI output/shotlist-art/）
  app.get('/art/:file', async (req, reply) => {
    const { file } = z.object({ file: z.string().min(1) }).parse(req.params)
    const img = readArtFile(file)
    if (!img) return reply.code(404).send({ error: '图片不存在' })
    return reply.type(img.mime).send(img.buf)
  })
}
