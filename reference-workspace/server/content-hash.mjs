// Owner: Sean — canonical source fingerprints shared by Reference exports and spatial versions.
import { createHash } from 'node:crypto';
export const canonicalJSON = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
export const contentHash = value => createHash('sha256').update(canonicalJSON(value)).digest('hex');
