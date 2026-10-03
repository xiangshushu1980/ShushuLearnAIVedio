// Owner: Sean — fixed Breeze voice inputs, preview scripts and workflow snapshots.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { z } from 'zod';
import { HttpError } from './store.mjs';

export function voiceTemplate(version = 2) {
  const bytes = readFileSync(new URL(`../catalog/breeze-voice.v${version}.json`, import.meta.url));
  return { ...JSON.parse(bytes), hash: createHash('sha256').update(bytes).digest('hex') };
}
const template = voiceTemplate(), legacyTemplate = voiceTemplate(1);
const templateFor = snapshot => [template, legacyTemplate].find(t => t.hash === snapshot.template?.hash);
export const voiceCatalog = { model: template.model, modes: template.modes, languages: template.languages,
  defaults: template.defaults, fields: template.fields, templates: template.templates, features: template.features, presets: template.presets, baseSample: template.baseSample };
export const voiceDraftSchema = z.object({
  mode: z.enum(['design', 'clone', 'reference']), language: z.enum(['zh', 'en']), templateId: z.string().max(100),
  sampleCount: z.union([z.literal(1), z.literal(3)]), instruction: z.string().max(2000),
  referenceAssetId: z.string().uuid().nullable(), referenceText: z.string().max(2000),
  transcriptConfirmed: z.boolean(), purpose: z.string().max(2000),
  parameters: z.object({ seed: z.number().int().min(1).max(2147483647), cfgScale: z.number().min(0.1).max(6) }).strict(),
  features: z.record(z.string(), z.string()).optional(), presetId: z.string().max(100).optional(),
  sourceRunId: z.string().uuid().optional()
}).strict();

export function validateVoiceDraft(store, entityId, body, generating = false) {
  const result = voiceDraftSchema.safeParse(body);
  if (!result.success) throw new HttpError(400, '声音输入格式不正确', result.error.flatten());
  const input = result.data;
  if (!template.templates.some(t => t.id === input.templateId)) throw new HttpError(400, '试听台词模板不可用');
  for (const [key, value] of Object.entries(input.features || {})) {
    if (!template.features.find(field => field.id === key)?.options.some(option => option.id === value))
      throw new HttpError(400, '声音特征不可用');
  }
  if (input.presetId && input.presetId !== 'custom' && !template.presets.some(preset => preset.id === input.presetId))
    throw new HttpError(400, '声音预制模板不可用');
  if (input.referenceAssetId && (!generating || input.mode !== 'design')) {
    const source = store.asset(input.referenceAssetId, !generating);
    if (source.entityId !== entityId || !['voice-source', 'voice'].includes(source.kind)) throw new HttpError(400, '请选择当前实体的声音素材');
    if (generating && source.metadata.voiceRole === 'emotion') throw new HttpError(400, '情绪试听不能替换基础音源，请选择原始基础样音');
    if (generating && source.durationSec > 30) throw new HttpError(400, '参考音源须在 30 秒以内');
  }
  if (input.sourceRunId) {
    const source = store.run(input.sourceRunId);
    if (source.entityId !== entityId || source.snapshot.stage !== 'voice') throw new HttpError(400, '历史声音不属于当前实体');
    if (generating && !voiceCompatible(source.snapshot)) throw new HttpError(409, '历史声音工作流已变化，请检查后改用当前配置');
  }
  if (generating) {
    if (input.mode !== 'reference' && input.sampleCount !== 1) throw new HttpError(400, '先生成一段基础音色，选定样音后再进行多段情绪试听');
    if (input.mode === 'design' && !input.instruction.trim() && !Object.keys(input.features || {}).length) throw new HttpError(400, '请描述希望生成的声音');
    if (input.mode !== 'design' && (!input.referenceAssetId || !input.referenceText.trim() || !input.transcriptConfirmed))
      throw new HttpError(400, '请提供音源，并听音校对、确认准确转写');
  }
  return input;
}
export function voiceCompatible(snapshot) {
  const selected = templateFor(snapshot);
  return snapshot.stage === 'voice' && !!selected && isDeepStrictEqual(snapshot.model, selected.model);
}
export function voiceDesignInstruction(input) {
  return [ ...template.features.map(field => field.options.find(option => option.id === input.features?.[field.id])?.prompt[input.language]),
    input.language === 'en' ? 'Natural clear English. Speak normally, do not sing.' : '普通话自然清晰，正常说话，不唱歌。', input.instruction.trim() ].filter(Boolean).join('；');
}
export function createVoiceSnapshot(store, entityId, body) {
  const input = validateVoiceDraft(store, entityId, body, true), entity = store.entity(entityId);
  const refs = input.mode !== 'design' ? [store.asset(input.referenceAssetId)] : [];
  const lines = input.mode !== 'reference' ? [template.baseSample[input.language]]
    : template.templates.find(t => t.id === input.templateId).languages[input.language].slice(0, input.sampleCount);
  const prompt = input.mode === 'design' ? voiceDesignInstruction(input) : '';
  const anchor = refs[0] ? { assetId: refs[0].id, hash: refs[0].hash, transcript: input.referenceText.trim() } : null;
  return { owner: 'Sean', stage: 'voice', entity: { id: entity.id, name: entity.name, context: entity.context },
    model: structuredClone(template.model), voiceInput: input, parameters: input.parameters,
    voiceRole: input.mode === 'reference' ? 'emotion' : 'base', anchor, prompt, purpose: input.purpose, mode: input.mode, language: input.language,
    samples: lines.map((line, index) => ({ ...line, index, instruction: [prompt, input.mode !== 'design' ? (input.language === 'en' ? 'Keep the reference speaker identity and timbre. Change only emotional delivery.' : '保持参考说话人的身份和音色，只改变情绪表达。') : '', line.direction].filter(Boolean).join('\n') })),
    references: refs.map(asset => ({ id: asset.id, hash: asset.hash, kind: asset.kind, name: asset.name, runId: asset.runId, createdAt: asset.createdAt })),
    template: { id: template.id, version: template.version, hash: template.hash } };
}
export function buildVoiceWorkflow(snapshot, uploadedNames, runId) {
  if (!voiceCompatible(snapshot)) throw new HttpError(409, '声音工作流已变化，请检查后新建运行');
  const selected = templateFor(snapshot);
  const graph = { '1': structuredClone(selected.graph.loader) };
  if (snapshot.mode !== 'design') {
    if (uploadedNames.length !== 1) throw new HttpError(400, '声音引导需要一段已确认转写的音源');
    graph['2'] = { class_type: 'LoadAudio', inputs: { audio: uploadedNames[0] } };
  }
  for (const sample of snapshot.samples) {
    const speaker = String(10 + sample.index * 3), generate = String(11 + sample.index * 3), save = String(12 + sample.index * 3);
    graph[speaker] = { class_type: 'BreezeTTS2Speaker', inputs: { name: 'SeanReference', audio: 'none',
      reference_text: snapshot.mode !== 'design' ? snapshot.voiceInput.referenceText.trim() : '', auto_transcribe_if_empty: false,
      instruction: sample.instruction, cfg_scale: snapshot.parameters.cfgScale,
      ...(snapshot.mode !== 'design' ? { reference_audio: ['2', 0] } : {}) } };
    graph[generate] = { class_type: 'BreezeTTS2MultiSpeaker', inputs: { ...selected.graph.controls,
      breeze_model: ['1', 0], speaker_1: [speaker, 0], text: JSON.stringify([{ speaker: 'SeanReference', text: sample.text }]), seed: snapshot.parameters.seed } };
    graph[save] = { class_type: 'SaveAudio', inputs: { audio: [generate, 0], filename_prefix: `sean_reference_workspace/${runId}/voice_${sample.index + 1}` } };
  }
  return graph;
}
