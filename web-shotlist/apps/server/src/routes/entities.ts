/** 实体卡路由：CRUD + AI 抽取（任务式）+ 设定图（任务式）+ 资源 + 单体重刷 + 门禁 */
import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { deleteAsset, listAssets, readAsset, saveAsset, type AssetKind } from '../assets.ts'
import { comfyAlive, generateArt, waitArtDone } from '../art.ts'
import { deleteEntity, importRolecardsToEntities, listEntities, readEntity, saveEntity } from '../entities.ts'
import { gateEntities } from '../gate.ts'
import { readStyle, writeStyle } from '../style.ts'
import { submitTask, getTask } from '../tasks.ts'
import { ttsReady } from '../voice.ts'
import { extractEntities } from '../tools/entityExtract.ts'
import { chatCompletion, stripFence, type Effort } from '../llm.ts'

const entityBody = z.object({
  id: z.string().optional(),
  name: z.string().min(1),
  type: z.enum(['角色', '场景', '物件', '技能', '组织', '地点']).default('角色'),
  importance: z.enum(['core', 'secondary']).default('secondary'),
  stars: z.number().int().min(1).max(5).optional(),
  appearance: z.string().default(''),
  sound: z.string().default(''),
  description: z.string().default(''),
  source: z.string().optional(),
  related: z.array(z.object({ id: z.string(), relation: z.string() })).optional(),
  variants: z.array(z.object({ id: z.string().min(1), name: z.string().min(1), description: z.string().default(''), art: z.array(z.string()).optional() })).optional(),
})

const styleBody = z.object({ prompt: z.string().max(500).default('') })

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
      stars: d.stars,
      appearance: d.appearance,
      sound: d.sound,
      description: d.description,
      source: d.source,
      related: d.related,
      variants: d.variants,
    })
  })

  app.put('/entities/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    const parsed = entityBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const d = parsed.data
    return saveEntity({ ...d, id })
  })

  // 全局风格（设定图生成注入；用户决策 2026-08-14：只影响设定图，不影响提示词）
  app.get('/style', async () => readStyle())

  app.put('/style', async (req, reply) => {
    const parsed = styleBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    return writeStyle(parsed.data.prompt)
  })

  // ===== 音色种子生成（Qwen3-TTS 三种模式；任务式）=====
  app.get('/tts-ready', async () => ({ ready: ttsReady() }))

  app.post('/entities/:id/voice', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const parsed = z
      .object({
        kind: z.enum(['custom', 'design', 'clone']),
        text: z.string().min(1),
        speaker: z.string().optional(),
        instruct: z.string().optional(),
        refText: z.string().optional(),
        seed: z.number().optional(),
      })
      .safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    if (!ttsReady()) return reply.code(503).send({ error: 'Qwen3-TTS 未就绪（缺脚本或 venv）' })
    const { task, conflict } = submitTask('voice', { entityId: id, input: parsed.data })
    if (conflict) return reply.code(409).send({ error: '已有任务运行中，请等待完成' })
    return { taskId: task!.id }
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

  // 角色卡迁移：experiments/shotlist/rolecards → 实体库（老项目无 fallback 后的迁移入口）
  app.post('/entities/import-rolecards', async (req, reply) => {
    try {
      const results = importRolecardsToEntities()
      return { imported: results.filter((r) => r.imported).length, results }
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  // ===== 任务式：AI 抽取（单实例队列，不阻塞）=====
  app.post('/entities/extract', async (req, reply) => {
    const parsed = extractBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const { task, conflict, current } = submitTask('extract', parsed.data)
    if (conflict) {
      return reply.code(409).send({ error: '已有任务运行中，请等待完成', current: current ? { kind: current.kind, status: current.status, startedAt: current.startedAt } : undefined })
    }
    return { taskId: task!.id }
  })

  // ===== 任务式：设定图生成（ANIMA；完成后移入实体资产目录）=====
  app.get('/entities/:id/art', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    return { images: listAssets(id).filter((a) => a.kind === 'art').map((a) => a.file), comfyOnline: await comfyAlive() }
  })

  app.post('/entities/:id/art', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const parsed = z.object({ prompt: z.string().optional(), seed: z.number().optional(), variant: z.string().optional() }).safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const entity = readEntity(id)
    if (!entity) return reply.code(404).send({ error: `实体不存在: ${id}` })
    if (!(await comfyAlive())) return reply.code(503).send({ error: 'ComfyUI 不在线（http://127.0.0.1:8188）' })
    const variant = parsed.data.variant ? entity.variants?.find((v) => v.id === parsed.data.variant || v.name === parsed.data.variant) : undefined
    const { task, conflict } = submitTask('art', {
      entityId: id,
      prompt: parsed.data.prompt,
      seed: parsed.data.seed,
      type: entity.type ?? '角色',
      appearance: entity.appearance,
      variant: variant ? `${variant.name}：${variant.description}` : undefined,
    })
    if (conflict) return reply.code(409).send({ error: '已有任务运行中，请等待完成' })
    return { taskId: task!.id }
  })

  // ===== 任务状态（前端轮询）=====
  app.get('/tasks/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const t = getTask(id)
    if (!t) return reply.code(404).send({ error: '任务不存在' })
    return {
      id: t.id,
      kind: t.kind,
      status: t.status,
      result: t.result,
      error: t.error,
      createdAt: t.createdAt,
      startedAt: t.startedAt,
      finishedAt: t.finishedAt,
    }
  })

  // ===== 实体资源（画面/声音/文件：上传/列表/删除/静态）=====
  app.get('/entities/:id/assets', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    return { assets: listAssets(id) }
  })

  app.post('/entities/:id/assets', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    if (!readEntity(id)) return reply.code(404).send({ error: `实体不存在: ${id}` })
    const kind = z.enum(['art', 'voice', 'file']).parse(req.query as { kind?: string })
    const part = await req.file()
    if (!part) return reply.code(400).send({ error: '缺少文件' })
    const buf = await part.toBuffer()
    const asset = saveAsset(id, kind as AssetKind, part.filename, buf)
    return { asset }
  })

  app.delete('/entities/:id/assets/:file', async (req, reply) => {
    const { id, file } = z.object({ id: z.string().min(1), file: z.string().min(1) }).parse(req.params)
    try {
      deleteAsset(id, file)
      return { ok: true }
    } catch (e) {
      return reply.code(404).send({ error: (e as Error).message })
    }
  })

  app.get('/assets/:entityId/:file', async (req, reply) => {
    const { entityId, file } = z.object({ entityId: z.string().min(1), file: z.string().min(1) }).parse(req.params)
    const a = readAsset(entityId, file)
    if (!a) return reply.code(404).send({ error: '资源不存在' })
    return reply.type(a.mime).send(a.buf)
  })

  // ===== 实体单体重刷（LLM 按上下文重写该实体卡；可重刷）=====
  app.post('/entities/:id/refresh', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const parsed = z.object({ worldview: z.string().default(''), script: z.string().default('') }).safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    const existing = readEntity(id)
    if (!existing) return reply.code(404).send({ error: `实体不存在: ${id}` })
    try {
      const prompt = `你是世界观实体抽取器。只重写以下单个实体卡（保留 id 与类型，改善外观/声音/介绍的准确度与可作画性）。\n\n现有实体：\n名称: ${existing.name}\n类型: ${existing.type}\n外观: ${existing.appearance}\n声音: ${existing.sound}\n介绍: ${existing.description}\n\n参考上下文（剧本+世界观）：\n${parsed.data.script || '（无）'}\n${parsed.data.worldview ? `世界观：${parsed.data.worldview}` : ''}\n\n只输出 JSON：{"appearance": "...", "sound": "...", "description": "..."}（外观必须可作画级：发型发色/瞳色/服装款式颜色/标志特征）`
      const raw = stripFence(
        await chatCompletion('你是实体卡精修器，严格输出 JSON。', prompt, {
          model: 'deepseek-v4-flash',
          effort: 'high',
          temperature: 0.4,
          maxTokens: 6000,
        }),
      )
      const m = /\{[\s\S]*\}/.exec(raw)
      if (!m) throw new Error('LLM 输出格式错误')
      const patch = JSON.parse(m[0]) as { appearance?: string; sound?: string; description?: string }
      const saved = saveEntity({ ...existing, appearance: patch.appearance ?? existing.appearance, sound: patch.sound ?? existing.sound, description: patch.description ?? existing.description })
      return saved
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })

  // ===== 渲染门禁：检查引用实体合格 =====
  app.post('/entities/gate', async (req, reply) => {
    const parsed = z.object({ ids: z.array(z.string()) }).safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: 'ids 必须为字符串数组' })
    return gateEntities(parsed.data.ids)
  })
}
