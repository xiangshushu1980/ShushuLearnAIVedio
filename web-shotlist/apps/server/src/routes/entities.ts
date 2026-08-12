/** 实体注册表路由（docs/22 六节；V1 基础版） */
import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { listEntities, readEntity } from '../store.ts'

export async function entityRoutes(app: FastifyInstance): Promise<void> {
  app.get('/entities', async () => listEntities())

  app.get('/entities/:id', async (req, reply) => {
    const { id } = z.object({ id: z.string().min(1) }).parse(req.params)
    const { entity, errs } = readEntity(id)
    if (errs) return reply.code(404).send({ error: errs.join('；') })
    return entity
  })
}
