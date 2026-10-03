// Owner: Sean — machine-readable v1 response contracts; request schema is shared with runtime.
import { z } from 'zod';
import { spatialExportSchema } from './spatial-schema.mjs';
import { manifestRequestSchema, assetRoles } from './reference-export.mjs';
const uuid = z.string().uuid(), hash = z.string(), nullableText = z.string().nullable();
const source = z.object({ source: z.string(), contentHash: hash }).strict();
const confirmation = z.object({ status: z.enum(['confirmed', 'unconfirmed', 'needs_review']), isCurrent: z.boolean(),
  records: z.array(z.object({ kind: z.enum(['appearance', 'view', 'voice', 'scene_image_set']), confirmationId: uuid, version: z.number().int(), createdAt: z.string() }).strict()) }).strict().nullable();
const asset = z.object({ assetId: uuid, entityId: uuid, name: nullableText, role: z.enum(assetRoles).nullable(), mediaType: z.enum(['image', 'audio']), mime: z.string(),
  fileSize: z.number().int().nonnegative().nullable(), contentHash: hash, sourceRevision: hash, contentUrl: z.string(), createdAt: z.string(), description: nullableText,
  layout: nullableText, width: z.number().nullable(), height: z.number().nullable(), durationSec: z.number().nullable(), confirmation,
  inheritance: z.object({sourceEntityId:uuid,sourceAssetId:uuid,sourceHash:hash,sourceRevision:hash,sourceVoiceId:uuid.optional(),sourceRunId:uuid.optional(),sourceRunEntityId:uuid.optional()}).strict().nullable().optional(),
  reviewStatus: z.null(), sourceRunId: uuid.nullable(), available: z.boolean() }).strict();
const prompt = z.object({ promptId: z.string(), sourceRunId: uuid, sourceEntityId:uuid.optional(), stage: z.string(), version: z.null(), text: z.string(), effectiveText: z.string(), purpose: nullableText,
  workflow: z.object({ id: nullableText, version: z.union([z.number(), z.string()]).nullable(), contentHash: nullableText }).strict().nullable(),
  samples: z.array(z.object({ text: nullableText, direction: nullableText }).strict()), createdAt: z.string(), assetIds: z.array(uuid), contentHash: hash, sourceRevision: hash }).strict();
const current = z.object({ confirmationId: uuid, version: z.number().int(), assetId: uuid, contentHash: hash }).strict().nullable();
const derivedFrom=z.object({entityId:uuid,sourceRevision:hash,description:nullableText,createdAt:z.string()}).strict().nullable();
const fields = { flags:z.array(z.string()).optional(),derivedFrom:derivedFrom.optional(), entityId: uuid, name: nullableText, type: nullableText, description: nullableText, contentHash: hash, sourceRevision: hash, missingFields: z.array(z.string()) };
const projectRole=z.object({projectId:uuid,role:nullableText,plotNotes:nullableText,revision:z.number().int().nonnegative(),sourceRevision:hash,updatedAt:nullableText}).strict();
const projectContext=z.object({owner:z.literal('Sean'),projectId:uuid,name:nullableText,brief:nullableText,synopsis:nullableText,worldRules:nullableText,visualStyle:nullableText,decisions:nullableText,revision:z.number().int().positive(),updatedAt:z.string(),sourceRevision:hash,missingFields:z.array(z.string())}).strict();
const sceneImages=z.object({schemaVersion:z.literal(1),status:z.enum(['missing','draft','needs_review','confirmed']),versionId:uuid.nullable(),version:z.number().int(),contentHash:hash,sourceRevision:hash,confirmedAt:nullableText,images:z.array(z.object({assetId:uuid,role:z.enum(['scene_overview','scene_angle','scene_detail']),label:z.string(),description:z.string(),anchorIds:z.array(z.string())}).strict()),notes:z.string(),issues:z.array(z.string()),usage:z.string()}).strict();
const entity = z.object({ ...fields,projectRole:projectRole.optional(), sceneSpatial:spatialExportSchema.optional(), sceneImages:sceneImages.optional(), relationRevisions:z.array(hash).optional(), appearance: nullableText, voiceDescription: nullableText, createdAt: z.string(),
  fieldSources: z.object({ type: source.nullable(), description: source.nullable(), appearance: source.nullable(), voiceDescription: source.nullable() }).strict(),
  currentAppearance: current, currentVoice: current, assets: z.array(asset), prompts: z.array(prompt) }).strict();
const capabilities = z.record(z.string(), z.json());
export const entityListResponseSchema = z.object({ format: z.literal('reference-entity-list'), schemaVersion: z.literal(1), owner: z.literal('Sean'), capabilities,
  entities: z.array(z.object(fields).strict()) }).strict();
export const manifestResponseSchema = z.object({ format: z.literal('reference-manifest'), schemaVersion: z.literal(1), owner: z.literal('Sean'), manifestId: uuid,
  createdAt: z.string(), contentHash: hash, capabilities, projectContext:projectContext.optional(), selection: manifestRequestSchema, entities: z.array(entity),
  relations: z.array(z.object({ relationId: uuid, projectId:uuid.optional(), sourceEntityId: uuid, targetEntityId: uuid, type: nullableText, description: nullableText,
    category:z.enum(['setting','story']).optional(),targetRevision:hash.optional(),createdAt:z.string().optional(),updatedAt:z.string().optional(),status: z.string().optional(), contentHash: hash, sourceRevision: hash }).strict()).describe('direct仅导出两端均已选中的有效设定/剧情关系；不递归'),
  omissions: z.array(z.object({ entityId: uuid, assetId: uuid, reason: z.string() }).strict()), missingCapabilities: z.array(z.string()) }).strict();
export function exportJSONSchemas() {
  const schema = value => ({ ...z.toJSONSchema(value), $comment: 'Owner: Sean' });
  const request = schema(manifestRequestSchema);
  for (const key of ['entityIds', 'assetIds', 'assetRoles']) request.properties[key].uniqueItems = true;
  return { 'manifest-request.v1.schema.json': request, 'manifest.v1.schema.json': schema(manifestResponseSchema), 'entity-list.v1.schema.json': schema(entityListResponseSchema) };
}
