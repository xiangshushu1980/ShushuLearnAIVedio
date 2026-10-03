// Owner: Sean — fixed Breeze voice inputs, preview scripts and workflow snapshots.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { z } from 'zod';
import { HttpError } from './store.mjs';

export function voiceTemplate() {
  const bytes = readFileSync(new URL('../catalog/breeze-voice.v1.json', import.meta.url));
  return { ...JSON.parse(bytes), hash: createHash('sha256').update(bytes).digest('hex') };
}
const template = voiceTemplate();
export const voiceCatalog = { model: template.model, modes: template.modes, languages: template.languages,
  defaults: template.defaults, fields: template.fields, templates: template.templates };
export const voiceDraftSchema = z.object({
  mode: z.enum(['design', 'reference']), language: z.enum(['zh', 'en']), templateId: z.string().max(100),
  sampleCount: z.union([z.literal(1), z.literal(3)]), instruction: z.string().max(2000),
  referenceAssetId: z.string().uuid().nullable(), referenceText: z.string().max(2000),
  transcriptConfirmed: z.boolean(), purpose: z.string().max(2000),
  parameters: z.object({ seed: z.number().int().min(1).max(2147483647), cfgScale: z.number().min(0.1).max(6) }).strict(),
  sourceRunId: z.string().uuid().optional()
}).strict();

export function validateVoiceDraft(store, entityId, body, generating = false) {
  const result = voiceDraftSchema.safeParse(body);
  if (!result.success) throw new HttpError(400, '声音输入格式不正确', result.error.flatten());
  const input = result.data;
  if (!template.templates.some(t => t.id === input.templateId)) throw new HttpError(400, '试听台词模板不可用');
  if (input.referenceAssetId && (!generating || input.mode === 'reference')) {
    const source = store.asset(input.referenceAssetId, !generating);
    if (source.entityId !== entityId || !['voice-source', 'voice'].includes(source.kind)) throw new HttpError(400, '请选择当前实体的声音素材');
    if (generating && source.durationSec > 30) throw new HttpError(400, '参考音源须在 30 秒以内');
  }
  if (input.sourceRunId) {
    const source = store.run(input.sourceRunId);
    if (source.entityId !== entityId || source.snapshot.stage !== 'voice') throw new HttpError(400, '历史声音不属于当前实体');
    if (generating && !voiceCompatible(source.snapshot)) throw new HttpError(409, '历史声音工作流已变化，请检查后改用当前配置');
  }
  if (generating) {
    if (input.mode === 'design' && !input.instruction.trim()) throw new HttpError(400, '请描述希望生成的声音');
    if (input.mode === 'reference' && (!input.referenceAssetId || !input.referenceText.trim() || !input.transcriptConfirmed))
      throw new HttpError(400, '请提供音源，并听音校对、确认准确转写');
  }
  return input;
}
export function voiceCompatible(snapshot) {
  return snapshot.stage === 'voice' && snapshot.template.hash === template.hash && isDeepStrictEqual(snapshot.model, template.model);
}
export function createVoiceSnapshot(store, entityId, body) {
  const input = validateVoiceDraft(store, entityId, body, true), entity = store.entity(entityId);
  const refs = input.mode === 'reference' ? [store.asset(input.referenceAssetId)] : [];
  const lines = template.templates.find(t => t.id === input.templateId).languages[input.language].slice(0, input.sampleCount);
  return { owner: 'Sean', stage: 'voice', entity: { id: entity.id, name: entity.name, context: entity.context },
    model: structuredClone(template.model), voiceInput: input, parameters: input.parameters,
    prompt: input.instruction, purpose: input.purpose, mode: input.mode, language: input.language,
    samples: lines.map((line, index) => ({ ...line, index, instruction: [input.instruction.trim(), line.direction].filter(Boolean).join('\n') })),
    references: refs.map(asset => ({ id: asset.id, hash: asset.hash, kind: asset.kind, name: asset.name, runId: asset.runId, createdAt: asset.createdAt })),
    template: { id: template.id, version: template.version, hash: template.hash } };
}
export function buildVoiceWorkflow(snapshot, uploadedNames, runId) {
  if (!voiceCompatible(snapshot)) throw new HttpError(409, '声音工作流已变化，请检查后新建运行');
  const graph = { '1': structuredClone(template.graph.loader) };
  if (snapshot.mode === 'reference') {
    if (uploadedNames.length !== 1) throw new HttpError(400, '声音引导需要一段已确认转写的音源');
    graph['2'] = { class_type: 'LoadAudio', inputs: { audio: uploadedNames[0] } };
  }
  for (const sample of snapshot.samples) {
    const speaker = String(10 + sample.index * 3), generate = String(11 + sample.index * 3), save = String(12 + sample.index * 3);
    graph[speaker] = { class_type: 'BreezeTTS2Speaker', inputs: { name: 'SeanReference', audio: 'none',
      reference_text: snapshot.mode === 'reference' ? snapshot.voiceInput.referenceText.trim() : '', auto_transcribe_if_empty: false,
      instruction: sample.instruction, cfg_scale: snapshot.parameters.cfgScale,
      ...(snapshot.mode === 'reference' ? { reference_audio: ['2', 0] } : {}) } };
    graph[generate] = { class_type: 'BreezeTTS2MultiSpeaker', inputs: { ...template.graph.controls,
      breeze_model: ['1', 0], speaker_1: [speaker, 0], text: JSON.stringify([{ speaker: 'SeanReference', text: sample.text }]), seed: snapshot.parameters.seed } };
    graph[save] = { class_type: 'SaveAudio', inputs: { audio: [generate, 0], filename_prefix: `sean_reference_workspace/${runId}/voice_${sample.index + 1}` } };
  }
  return graph;
}
