// Owner: Sean — model capabilities and fixed workflow mapping live on the server.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { z } from 'zod';
import { HttpError } from './store.mjs';

const profiles = JSON.parse(readFileSync(new URL('../catalog/profiles.json', import.meta.url)));
const size = { type: 'select', label: '画幅', default: '1536x1024', options: [
  { value: '1536x1024', label: '3:2 · 1536 × 1024' },
  { value: '1024x1024', label: '1:1 · 1024 × 1024' },
  { value: '1344x768', label: '16:9 · 1344 × 768' },
  { value: '768x1344', label: '9:16 · 768 × 1344' }
] };
const fields = {
  size,
  seed: { type: 'integer', label: '随机种子', default: 42, min: 0, max: 2147483647 },
  steps: { type: 'integer', label: '采样步数', default: 8, min: 1, max: 30 }
};
const models = [
  { id: 'qwen-image-2.1', name: 'Qwen Image 2.1', version: 1, adapter: 'comfy', enabled: true,
    references: { min: 0, max: 16, instruction: '按所选顺序对应 Image 1、Image 2…，在提示词中明确每张图的职责。节点支持 0–16 张；已有四图组合实验。' },
    fields: { ...fields, steps: { ...fields.steps, default: 25, max: 50 } }, localGpu: true },
  { id: 'krea2-edit', name: 'Krea 2 Edit · 本地备选', version: 1, adapter: 'comfy', enabled: true,
    references: { min: 1, max: 2, instruction: '一图为主体；两图按训练顺序：Image 1 场景，Image 2 主体。参考一致性需人工复核。' },
    fields, localGpu: true },
  { id: 'krea2-t2i', name: 'Krea 2 · 文本概念图', version: 1, adapter: 'comfy', enabled: true,
    references: { min: 0, max: 0, instruction: '此工作流只使用提示词。需要引用图片时请选择其他模型。' },
    fields, localGpu: true }
];

export const catalog = {
  models: models.map(({ endpoint, ...model }) => model), styles: profiles.styles
};
export function modelFor(modelId) {
  const model = models.find(m => m.id === modelId);
  if (!model) throw new HttpError(400, '未知模型配置');
  if (!model.enabled) throw new HttpError(409, model.unavailableReason);
  return model;
}
const requestSchema = z.object({
  modelId: z.string(), styleId: z.string(), prompt: z.string().trim().min(1).max(16000),
  purpose: z.string().max(2000).default(''), references: z.array(z.string().uuid()).max(16),
  sourceRunId: z.string().uuid().optional(),
  parameters: z.record(z.string(), z.union([z.string(), z.number()]))
}).strict();
export function validateRun(body) {
  const result = requestSchema.safeParse(body);
  if (!result.success) throw new HttpError(400, '运行输入格式不正确', result.error.flatten());
  const input = result.data;
  const model = modelFor(input.modelId);
  const style = profiles.styles.find(s => s.id === input.styleId);
  if (!style) throw new HttpError(400, '请选择已保存的风格');
  if (new Set(input.references).size !== input.references.length) throw new HttpError(400, '引用图片不可重复');
  if (input.references.length < model.references.min || input.references.length > model.references.max)
    throw new HttpError(400, `该模型需要 ${model.references.min}–${model.references.max} 张引用图片`);
  for (const key of Object.keys(input.parameters)) if (!model.fields[key]) throw new HttpError(400, `未知参数：${key}`);
  const parameters = {};
  for (const [key, field] of Object.entries(model.fields)) {
    const value = input.parameters[key] ?? field.default;
    if (field.type === 'integer' && (!Number.isInteger(value) || value < field.min || value > field.max))
      throw new HttpError(400, `${field.label} 超出允许范围`);
    if (field.type === 'select' && !field.options.some(o => o.value === value)) throw new HttpError(400, `${field.label} 不可用`);
    parameters[key] = value;
  }
  return { input: { ...input, parameters }, model, style };
}

export function workflowTemplate(modelId) {
  const path = modelId === 'qwen-image-2.1' ? '../catalog/qwen-concept.v1.json' : '../catalog/krea-concept.v1.json';
  const bytes = readFileSync(new URL(path, import.meta.url));
  return { ...JSON.parse(bytes), hash: createHash('sha256').update(bytes).digest('hex') };
}

export function buildComfyWorkflow(snapshot, uploadedNames, runId) {
  const [width, height] = snapshot.parameters.size.split('x').map(Number);
  const template = workflowTemplate(snapshot.model.id);
  if (snapshot.template.hash && snapshot.template.hash !== template.hash) throw new HttpError(409, '模板内容已变化，请检查配置后新建运行');
  if (snapshot.model.id === 'qwen-image-2.1') {
    const graph = template.graph;
    graph['5'].inputs.prompt = snapshot.effectivePrompt;
    Object.assign(graph['6'].inputs, { width, height });
    Object.assign(graph['7'].inputs, { seed: snapshot.parameters.seed, steps: snapshot.parameters.steps });
    graph['9'].inputs.filename_prefix = `sean_reference_workspace/${runId}/concept`;
    uploadedNames.forEach((name, index) => {
      const nodeId = String(10 + index);
      graph[nodeId] = { class_type: 'LoadImage', inputs: { image: name } };
      graph['5'].inputs[`images.image_${index + 1}`] = [nodeId, 0];
    });
    return graph;
  }
  const graph = template.graph;
  graph['4'].inputs.text = snapshot.effectivePrompt;
  Object.assign(graph['5'].inputs, { width, height });
  Object.assign(graph['6'].inputs, { seed: snapshot.parameters.seed, steps: snapshot.parameters.steps });
  graph['8'].inputs.filename_prefix = `sean_reference_workspace/${runId}/concept`;
  if (snapshot.model.id === 'krea2-edit') {
    graph['20'] = { class_type: 'LoraLoaderModelOnly', inputs: { model: ['1', 0], lora_name: 'krea2_identity_edit_v1_2.safetensors', strength_model: 1 } };
    uploadedNames.forEach((name, index) => {
      graph[String(30 + index)] = { class_type: 'LoadImage', inputs: { image: name } };
      graph[String(40 + index)] = { class_type: 'VAEEncode', inputs: { pixels: [String(30 + index), 0], vae: ['3', 0] } };
    });
    graph['21'] = { class_type: 'Krea2EditModelPatch', inputs: { model: ['20', 0], source_latent: ['40', 0],
      ref_boost: 1, ref_boost_a: 1, fit_mode: 'fit', vae: ['3', 0], source_image: ['30', 0], target_latent: ['5', 0] } };
    // Negative vision grounding is kept separate from the editable positive prompt.
    graph['22'] = { class_type: 'Krea2EditGroundedEncode', inputs: { clip: ['2', 0], prompt: '', image: ['30', 0], grounding_px: 768 } };
    if (uploadedNames.length === 2) {
      graph['21'].inputs.source_latent_b = ['41', 0];
      graph['21'].inputs.source_image_b = ['31', 0];
      graph['22'].inputs.image_b = ['31', 0];
    }
    graph['6'].inputs.model = ['21', 0];
    graph['6'].inputs.negative = ['22', 0];
  }
  return graph;
}
