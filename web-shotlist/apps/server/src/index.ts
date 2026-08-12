/** Fastify 入口（docs/22：后端 = Fastify，API 前缀 /api） */
import cors from '@fastify/cors'
import Fastify from 'fastify'
import { draftRoutes } from './routes/draft.ts'
import { entityRoutes } from './routes/entities.ts'
import { projectRoutes } from './routes/projects.ts'

const PORT = Number(process.env.SHOTLIST_PORT ?? 8787)

const app = Fastify({ logger: true })

await app.register(cors, { origin: true })

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
