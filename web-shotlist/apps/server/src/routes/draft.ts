/** 工具 A0 路由：点子 → 世界观 + 剧本 */
import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { genDraft } from '../tools/draftGen.ts'

const draftBody = z.object({
  idea: z.string().min(1, '输入几句点子'),
  length: z.enum(['short', 'medium', 'long']).default('medium'),
  withWorldview: z.boolean().default(true),
  model: z.enum(['deepseek-v4-flash', 'deepseek-v4-pro']).default('deepseek-v4-flash'),
})

export async function draftRoutes(app: FastifyInstance): Promise<void> {
  app.post('/draft', async (req, reply) => {
    const parsed = draftBody.safeParse(req.body)
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.issues.map((i) => i.message).join('；') })
    try {
      const { idea, length, withWorldview, model } = parsed.data
      return await genDraft({ idea, length, withWorldview }, { model })
    } catch (e) {
      return reply.code(502).send({ error: (e as Error).message })
    }
  })
}
