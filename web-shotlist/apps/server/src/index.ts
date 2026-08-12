/** Fastify 入口（docs/22：后端 = Fastify，API 前缀 /api） */
import cors from '@fastify/cors'
import multipart from '@fastify/multipart'
import Fastify from 'fastify'
import { generateArt, waitArtDone } from './art.ts'
import { saveEntity } from './entities.ts'
import { registerRunner } from './tasks.ts'
import { extractEntities } from './tools/entityExtract.ts'
import { draftRoutes } from './routes/draft.ts'
import { entityRoutes } from './routes/entities.ts'
import { projectRoutes } from './routes/projects.ts'

// 任务 runner 注册（单实例队列：抽取 / 设定图）
registerRunner('extract', async (task) => {
  const { worldview, script, model } = task.input as { worldview: string; script: string; model?: string }
  const entities = await extractEntities({ worldview, script, model })
  const saved = entities.map((e) => saveEntity(e))
  return { entities: saved }
})

registerRunner('art', async (task) => {
  const { entityId, prompt, seed, type } = task.input as { entityId: string; prompt?: string; seed?: number; type?: import('@shotlist/shared').EntityType }
  const { promptId } = await generateArt(entityId, prompt, seed, type)
  if (!promptId) throw new Error('未拿到 prompt_id')
  const images = await waitArtDone(entityId, promptId)
  return { images }
})

const PORT = Number(process.env.SHOTLIST_PORT ?? 8787)

const app = Fastify({ logger: true })

await app.register(cors, { origin: true })
await app.register(multipart, { limits: { fileSize: 20 * 1024 * 1024 } })

await app.register(
  async (api) => {
    await api.register(projectRoutes)
    await api.register(entityRoutes)
    await api.register(draftRoutes)
  },
  { prefix: '/api' },
)

app.get('/health', async () => ({ ok: true, ts: Date.now() }))

try {
  await app.listen({ port: PORT, host: '0.0.0.0' })
} catch (err) {
  app.log.error(err)
  process.exit(1)
}
