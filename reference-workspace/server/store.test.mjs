// Owner: Sean — asset lifecycle and immutable source-history acceptance checks.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import sharp from 'sharp';
import { createStore, id, now } from './store.mjs';

async function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'sean-reference-store-'));
  const store = createStore(dir);
  t.after(() => { store.db.close(); rmSync(dir, { recursive: true, force: true }); });
  const entityId = id(), otherEntity = id();
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId, 'Test entity', '{}', now());
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(otherEntity, 'Other entity', '{}', now());
  const buffer = await sharp({ create: { width: 32, height: 24, channels: 3, background: '#6da79e' } }).png().toBuffer();
  const stage = await store.stageImage(buffer, 'fixture.png', entityId, 'concept', null);
  const [asset] = store.transaction(() => store.registerStages([stage]));
  return { store, entityId, otherEntity, asset, path: store.assetPath(asset.id), buffer };
}

test('history image requires unlock; deleting a used source preserves every run input and tombstone', async t => {
  const { store, entityId, asset, path } = await fixture(t);
  assert.equal(asset.locked, true);
  assert.throws(() => store.deleteAsset(asset.id), /解锁/);
  const snapshot = { references: [{ id: asset.id, hash: asset.hash }], prompt: 'fixed original prompt' };
  const { run } = store.createRun(entityId, snapshot, id());
  store.db.prepare('UPDATE assets SET locked=0 WHERE id=?').run(asset.id);
  assert.throws(() => store.deleteAsset(asset.id, true), /未结束运行/);
  store.updateRun(run.id, { status: 'succeeded' });
  assert.throws(() => store.deleteAsset(asset.id), error => error.status === 409 && error.details.requiresConfirmation);
  store.deleteAsset(asset.id, true);
  assert.equal(existsSync(path), false);
  assert.throws(() => store.asset(asset.id), /已删除/);
  const history = store.run(run.id);
  assert.ok(history.references[0].deletedAt);
  assert.equal(history.references[0].id, asset.id);
  assert.equal(history.references[0].url, null);
  assert.deepEqual(history.snapshot, snapshot);
});

test('idempotency cannot duplicate a run or accept changed inputs; cross-entity rejection rolls back creation', async t => {
  const { store, entityId, otherEntity, asset } = await fixture(t);
  const key = id(), snapshot = { references: [{ id: asset.id }], prompt: 'same input' };
  const first = store.createRun(entityId, snapshot, key);
  const repeated = store.createRun(entityId, snapshot, key);
  assert.equal(first.created, true); assert.equal(repeated.created, false);
  assert.equal(first.run.id, repeated.run.id);
  assert.throws(() => store.createRun(entityId, { ...snapshot, prompt: 'changed' }, key), /不一致/);
  assert.throws(() => store.createRun(otherEntity, snapshot, id()), /不属于当前实体/);
  assert.equal(store.db.prepare('SELECT COUNT(*) AS count FROM runs').get().count, 1);
});

test('protected current source cannot be deleted even after unlocking', async t => {
  const { store, asset } = await fixture(t);
  store.db.prepare('UPDATE assets SET locked=0,protected=1 WHERE id=?').run(asset.id);
  assert.throws(() => store.deleteAsset(asset.id, true), /受保护/);
  assert.ok(store.asset(asset.id));
});

test('asset registration is atomic and original encoded image bytes are retained', async t => {
  const { store, entityId, asset, buffer } = await fixture(t);
  assert.deepEqual(store.assetBytes(asset.id), buffer);
  const second = await store.stageImage(buffer, 'second.png', entityId, 'setting', null);
  assert.throws(() => store.transaction(() => store.registerStages([second, { ...second, assetId: asset.id }])), /UNIQUE/);
  assert.throws(() => store.asset(second.assetId));
  store.discardStage(second);
  assert.equal(store.db.prepare('SELECT COUNT(*) AS count FROM assets').get().count, 1);
});
