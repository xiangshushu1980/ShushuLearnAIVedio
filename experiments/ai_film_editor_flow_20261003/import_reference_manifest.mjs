// Owner: Sean — smoke importer for the Reference Export v1 integration.
// Usage: node import_reference_manifest.mjs <entityId> <assetId> [assetId ...]
// Downloads selected assets immediately because Reference manifests do not retain asset bytes.
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const baseUrl = new URL(process.env.REFERENCE_BASE_URL || 'http://127.0.0.1:4188');
const [entityId, ...assetIds] = process.argv.slice(2);
if (!entityId || assetIds.length === 0) {
  console.error('Usage: node import_reference_manifest.mjs <entityId> <assetId> [assetId ...]');
  process.exit(2);
}

const root = path.dirname(fileURLToPath(import.meta.url));
const outputRoot = path.join(root, 'imports');
const mimeExtensions = new Map([
  ['image/png', '.png'], ['image/jpeg', '.jpg'], ['image/webp', '.webp'],
  ['audio/wav', '.wav'], ['audio/mpeg', '.mp3'], ['audio/ogg', '.ogg'],
]);

async function request(url, init) {
  const response = await fetch(url, init);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${init?.method || 'GET'} ${url} -> ${response.status}: ${body.slice(0, 500)}`);
  }
  return response;
}

const entityList = await (await request(new URL('/api/reference/v1/entities', baseUrl))).json();
if (entityList.format !== 'reference-entity-list' || entityList.schemaVersion !== 1) {
  throw new Error('Unsupported Reference entity-list format/version');
}
const selectedEntity = entityList.entities.find(entity => entity.entityId === entityId);
if (!selectedEntity) throw new Error(`Entity not found in Reference: ${entityId}`);

const manifestResponse = await request(new URL('/api/reference/v1/manifests', baseUrl), {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({
    entityIds: [entityId],
    assetIds,
    includeRelations: 'direct',
    assetRoles: ['main_appearance', 'three_view', 'voice', 'sound_effect'],
    includeUnconfirmed: false,
  }),
});
const manifest = await manifestResponse.json();
if (manifest.format !== 'reference-manifest' || manifest.schemaVersion !== 1) {
  throw new Error('Unsupported Reference manifest format/version');
}
if (manifest.entities.length !== 1 || manifest.entities[0].entityId !== entityId) {
  throw new Error('Manifest entity selection did not match the requested entity');
}

const selected = manifest.entities[0].assets;
const selectedSet = new Set(assetIds);
if (selected.length !== selectedSet.size || selected.some(asset => !selectedSet.has(asset.assetId))) {
  throw new Error('Manifest asset selection did not exactly match requested asset IDs');
}

const importDir = path.join(outputRoot, manifest.manifestId);
const assetsDir = path.join(importDir, 'assets');
const localPathByAssetId = new Map();
await mkdir(assetsDir, { recursive: true });
for (const asset of selected) {
  if (!asset.available) throw new Error(`Asset is unavailable: ${asset.assetId}`);
  const contentUrl = new URL(asset.contentUrl, baseUrl);
  if (contentUrl.origin !== baseUrl.origin) throw new Error(`Cross-origin asset URL rejected: ${contentUrl.origin}`);
  const response = await request(contentUrl);
  const bytes = Buffer.from(await response.arrayBuffer());
  const actualHash = createHash('sha256').update(bytes).digest('hex');
  if (actualHash !== asset.contentHash) {
    throw new Error(`SHA-256 mismatch for ${asset.assetId}: expected ${asset.contentHash}, received ${actualHash}`);
  }
  const extension = mimeExtensions.get(asset.mime) || '.bin';
  await writeFile(path.join(assetsDir, `${asset.assetId}${extension}`), bytes, { flag: 'wx' });
  localPathByAssetId.set(asset.assetId, `assets/${asset.assetId}${extension}`);
}

await writeFile(path.join(importDir, 'reference-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, { flag: 'wx' });
const summary = {
  owner: 'Sean',
  manifestId: manifest.manifestId,
  contentHash: manifest.contentHash,
  entityId,
  entityName: selectedEntity.name,
  assetCount: selected.length,
  assets: selected.map(({ assetId, role, mime, contentHash }) => ({
    assetId, role, mime, contentHash, localPath: localPathByAssetId.get(assetId),
  })),
  missingCapabilities: manifest.missingCapabilities,
  verifiedAt: new Date().toISOString(),
};
await writeFile(path.join(importDir, 'import-summary.json'), `${JSON.stringify(summary, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify(summary, null, 2));
