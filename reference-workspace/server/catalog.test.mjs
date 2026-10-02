// Owner: Sean — capability validation and explicit reference mapping acceptance checks.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateRun, buildComfyWorkflow, workflowTemplate } from './catalog.mjs';
import { id } from './store.mjs';

const input = { modelId: 'qwen-image-2.1', styleId: 'original', prompt: 'Image 1 is the face, Image 2 is the clothing.', purpose: '', references: [id(), id()], parameters: {} };
test('Qwen graph contains exactly the selected references in the selected order, without silently adding a third', () => {
  const { input: normalized, model } = validateRun(input);
  const graph = buildComfyWorkflow({ model, parameters: normalized.parameters, effectivePrompt: normalized.prompt,
    template: { hash: workflowTemplate(model.id).hash } }, ['first.png', 'second.png'], 'test-run');
  assert.equal(graph['10'].inputs.image, 'first.png');
  assert.equal(graph['11'].inputs.image, 'second.png');
  assert.equal(graph['5'].inputs['images.image_3'], undefined);
  assert.deepEqual(graph['5'].inputs['images.image_1'], ['10', 0]);
  assert.deepEqual(graph['5'].inputs['images.image_2'], ['11', 0]);
  assert.equal(Object.values(graph).filter(node => node.class_type === 'LoadImage').length, 2);
  assert.equal(graph['7'].inputs.steps, 25);
  assert.match(graph['9'].inputs.filename_prefix, /^sean_reference_workspace\/test-run\//);
});
test('model limits, duplicate references, unknown fields and invalid numeric values are rejected', () => {
  assert.throws(() => validateRun({ ...input, modelId: 'krea2-edit', references: [id(), id(), id()] }), /需要/);
  assert.throws(() => validateRun({ ...input, references: [input.references[0], input.references[0]] }), /重复/);
  assert.throws(() => validateRun({ ...input, parameters: { surprise: 1 } }), /未知参数/);
  assert.throws(() => validateRun({ ...input, parameters: { steps: 1.5 } }), /范围/);
  assert.throws(() => validateRun({ ...input, parameters: { seed: -1 } }), /范围/);
  assert.throws(() => validateRun({ ...input, workflow: {} }), /格式/);
});
test('text-only run carries no reference nodes and a changed workflow hash is rejected', () => {
  const { input: normalized, model } = validateRun({ ...input, references: [] });
  const snapshot = { model, parameters: normalized.parameters, effectivePrompt: normalized.prompt, template: { hash: workflowTemplate(model.id).hash } };
  const graph = buildComfyWorkflow(snapshot, [], 'text-run');
  assert.equal(Object.values(graph).filter(node => node.class_type === 'LoadImage').length, 0);
  assert.throws(() => buildComfyWorkflow({ ...snapshot, template: { hash: 'changed' } }, [], 'text-run'), /已变化/);
});
