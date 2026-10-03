// Owner: Sean — minimum export contract checks using isolated business data; never ComfyUI.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { once } from 'node:events';
import { get as httpGet } from 'node:http';
import { createHash } from 'node:crypto';
import express from 'express';
import sharp from 'sharp';
import { createStore, id, now } from './store.mjs';
import { createReferenceExport, referenceExportRouter, contentHash } from './reference-export.mjs';
import { localAccess } from './local-access.mjs';
import { manifestResponseSchema, entityListResponseSchema } from './reference-export-schema.mjs';

async function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'sean-reference-export-')), store = createStore(dir), entityId = id(), otherId = id();
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId, 'Export entity', JSON.stringify({ owner: 'Sean', description: 'An explicit introduction', apiKey: 'sk-private-secret', relations: [{ target: otherId }], appearance: '/home/sean/private/avatar.png' }), now());
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(otherId, 'Other entity', '{}', now());
  const bytes = await sharp({ create: { width: 12, height: 12, channels: 3, background: '#678abc' } }).png().toBuffer();
  async function image(kind, owner = entityId, snapshot = {}) {
    const r = store.createRun(owner, { prompt: 'An appearance prompt', purpose: 'design', references: [], template: { id: 'sean-fixture', version: 1, hash: 'fixture' }, ...snapshot }, id()).run;
    const stage = await store.stageImage(bytes, 'image.png', owner, kind, r.id, { layout: kind === 'multiview' ? 'three' : undefined });
    const a = store.transaction(() => store.registerStages([stage]))[0]; store.updateRun(r.id, { status: 'succeeded' }); return a;
  }
  const primary = await image('concept'), candidate = await image('concept'), view = await image('multiview', entityId, { stage: 'multiview' }), other = await image('concept', otherId);
  const appearance = store.confirmAppearance(entityId, primary.id, null).appearance;
  store.db.prepare('UPDATE runs SET snapshot=? WHERE id=?').run(JSON.stringify({ references: [], prompt: 'Three views', purpose: 'turnaround', stage: 'multiview', appearance: { id: appearance.id } }), view.runId);
  store.confirmView(entityId, view.id, appearance.id);
  // Small valid PCM WAV fixture: direct registration keeps the test independent of audio tools/models.
  const wav = Buffer.alloc(48); wav.write('RIFF'); wav.writeUInt32LE(40, 4); wav.write('WAVEfmt ', 8); wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22); wav.writeUInt32LE(24000, 24); wav.writeUInt32LE(48000, 28); wav.writeUInt16LE(2, 32); wav.writeUInt16LE(16, 34); wav.write('data', 36); wav.writeUInt32LE(4, 40);
  const voiceId = id(), voiceRun = store.createRun(entityId, { stage: 'voice', prompt: 'Warm low voice', purpose: 'base voice', references: [], model: { apiKey: 'secret' } }, id()).run;
  writeFileSync(join(store.media, `${voiceId}.wav`), wav);
  store.transaction(() => store.registerStages([{ assetId: voiceId, file: `${voiceId}.wav`, entityId, kind: 'voice', name: 'voice.wav', mime: 'audio/wav', hash: createHash('sha256').update(wav).digest('hex'), width: 0, height: 0, runId: voiceRun.id, metadata: { owner: 'Sean', voiceRole: 'base', durationSec: .01 }, createdAt: now() }]));
  store.updateRun(voiceRun.id, { status: 'succeeded' }); store.confirmVoice(entityId, voiceId, null);
  const app = express(); app.use(localAccess); app.use(express.json()); app.use('/api/reference/v1', referenceExportRouter(store));
  app.use((e, _req, res, _next) => res.status(e.status || 500).json({ error: e.message, details: e.details }));
  const server = app.listen(0, '127.0.0.1'); await once(server, 'listening');
  t.after(async () => { await new Promise(resolve => server.close(resolve)); store.db.close(); rmSync(dir, { recursive: true, force: true }); });
  const base = `http://127.0.0.1:${server.address().port}/api/reference/v1`;
  const request = (path, body, headers = {}) => fetch(base + path, body === undefined ? { headers } : { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body) });
  return { store, entityId, otherId, primary, candidate, view, other, voiceId, bytes, wav, base, request, service: createReferenceExport(store) };
}

test('default selection exports real confirmations, text and prompts; no graph expansion or invented fields', async t => {
  const f = await fixture(t), response = await f.request('/manifests', { entityIds: [f.entityId], includeRelations: 'direct' });
  assert.equal(response.status, 201); const m = manifestResponseSchema.parse(await response.json()), e = m.entities[0];
  assert.deepEqual(e.assets.map(a => a.role).sort(), ['main_appearance', 'three_view', 'voice']);
  assert.ok(e.assets.every(a => a.confirmation.status === 'confirmed')); assert.equal(e.assets.find(a => a.assetId === f.voiceId).fileSize, f.wav.length);
  assert.equal(e.type, null); assert.equal(e.voiceDescription, 'Warm low voice'); assert.equal(e.description, 'An explicit introduction');
  assert.deepEqual(m.relations, []); assert.equal(m.capabilities.relations.supported, false); assert.equal(m.capabilities.reviewStatus.supported, false);
  assert.ok(e.prompts.every(p => p.version === null)); assert.equal(e.assets.some(a => a.assetId === f.other.id), false);
  const serialized = JSON.stringify(m); assert.ok(!serialized.includes('/home/sean')); assert.ok(!serialized.includes('sk-private-secret')); assert.ok(!serialized.includes('apiKey'));
  const { manifestId, createdAt, contentHash: hash, ...payload } = m; assert.equal(contentHash(payload), hash);
  const repeated = f.service.create({ entityIds: [f.entityId], includeRelations: 'direct' }); assert.notEqual(repeated.manifestId, manifestId); assert.equal(repeated.contentHash, hash);
  const list = entityListResponseSchema.parse(await (await f.request('/entities')).json()); assert.equal(list.entities.find(x => x.entityId === f.entityId).sourceRevision, e.sourceRevision);
});
test('includeUnconfirmed and explicit asset selection respect roles, ownership and missing confirmation', async t => {
  const f = await fixture(t);
  let m = await (await f.request('/manifests', { entityIds: [f.entityId], assetRoles: ['concept'], includeUnconfirmed: false })).json(); assert.equal(m.entities[0].assets.length, 0);
  m = await (await f.request('/manifests', { entityIds: [f.entityId], assetRoles: ['concept'], includeUnconfirmed: true, assetIds: [f.candidate.id] })).json();
  assert.equal(m.entities[0].assets[0].assetId, f.candidate.id); assert.equal(m.entities[0].assets[0].confirmation, null); assert.equal(m.entities[0].assets[0].reviewStatus, null);
  const bad = await f.request('/manifests', { entityIds: [f.entityId], assetIds: [f.other.id] }); assert.equal(bad.status, 400); assert.ok((await bad.json()).details.fieldErrors.assetIds);
});
test('stored snapshots remain byte-identical after edits, deletion and service recreation', async t => {
  const f = await fixture(t), m = f.service.create({ entityIds: [f.entityId], assetRoles: ['concept'], includeUnconfirmed: true });
  const before = await (await f.request(`/manifests/${m.manifestId}`)).text();
  f.store.db.prepare('UPDATE entities SET name=? WHERE id=?').run('Changed', f.entityId); f.store.db.prepare('UPDATE assets SET locked=0 WHERE id=?').run(f.candidate.id); f.store.deleteAsset(f.candidate.id);
  assert.equal(await (await f.request(`/manifests/${m.manifestId}`)).text(), before); assert.deepEqual(createReferenceExport(f.store).get(m.manifestId), m);
  const reopened = createStore(f.store.root);
  try { assert.deepEqual(createReferenceExport(reopened).get(m.manifestId), m); } finally { reopened.db.close(); }
  assert.throws(() => f.store.db.prepare('UPDATE reference_manifests SET payload=? WHERE id=?').run('{}', m.manifestId), /immutable/);
  assert.equal((await f.request(`/assets/${f.candidate.id}/content`)).status, 404);
});
test('field errors, unknown IDs and duplicate selections have correct status codes', async t => {
  const f = await fixture(t);
  for (const body of [{ entityIds: [] }, { entityIds: ['bad'] }, { entityIds: [f.entityId, f.entityId] }, { entityIds: [f.entityId], assetRoles: ['invalid'] }, { entityIds: [f.entityId], path: '/etc/passwd' }]) {
    const r = await f.request('/manifests', body); assert.equal(r.status, 400); assert.ok(Object.keys((await r.json()).details.fieldErrors).length);
  }
  assert.equal((await f.request('/manifests', { entityIds: [id()] })).status, 404);
  assert.equal((await f.request(`/manifests/${id()}`)).status, 404); assert.equal((await f.request(`/assets/${id()}/content`)).status, 404);
  assert.equal((await f.request('/assets/not-a-uuid/content')).status, 400);
  assert.equal((await f.request(`/assets/${f.primary.id}/content?path=/etc/passwd`)).status, 400);
});
test('image and audio content use registered MIME, exact bytes and Range; boundary stays local', async t => {
  const f = await fixture(t);
  const img = await f.request(`/assets/${f.primary.id}/content`); assert.equal(img.headers.get('content-type'), 'image/png'); assert.deepEqual(Buffer.from(await img.arrayBuffer()), f.bytes);
  const audio = await f.request(`/assets/${f.voiceId}/content`, undefined, { Range: 'bytes=0-11' }); assert.equal(audio.status, 206); assert.equal(audio.headers.get('content-type'), 'audio/wav'); assert.deepEqual(Buffer.from(await audio.arrayBuffer()), f.wav.subarray(0, 12));
  const hostStatus = await new Promise((resolve, reject) => { const r = httpGet(f.base + '/entities', { headers: { Host: 'remote.example' } }, res => { res.resume(); resolve(res.statusCode); }); r.on('error', reject); });
  assert.equal(hostStatus, 403);
  assert.equal((await f.request('/manifests', { entityIds: [f.entityId] }, { Origin: 'https://evil.example' })).status, 403);
  f.store.db.prepare('UPDATE assets SET file=? WHERE id=?').run('../../../../etc/passwd', f.primary.id);
  assert.equal((await f.request(`/assets/${f.primary.id}/content`)).status, 404);
});
