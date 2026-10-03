// Owner: Sean — Pi SDK adapter with app-owned settings/auth/session state and an explicit tool allowlist.
import { join } from 'node:path';
import { mkdirSync, readFileSync } from 'node:fs';
let sdkPromise;
const sdk = () => sdkPromise ||= import('@earendil-works/pi-coding-agent');
export function createPiRuntime(root) {
  const agentDir = join(root, 'agent');
  mkdirSync(agentDir, { recursive: true });
  let preferences={};
  try {preferences=JSON.parse(readFileSync(join(agentDir,'preferences.json'),'utf8'));}catch { /* optional app-owned model preference */ }
  let runtimePromise;
  async function runtime() {
    const { ModelRuntime } = await sdk();
    if (!runtimePromise) runtimePromise = ModelRuntime.create({
      authPath: process.env.REFERENCE_AGENT_AUTH_FILE || join(agentDir, 'auth.json'),
      modelsPath: process.env.REFERENCE_AGENT_MODELS_FILE || join(agentDir, 'models.json'),
      modelsStorePath: join(agentDir, 'models-store.json'), allowModelNetwork: false,
      signal: AbortSignal.timeout(15000)
    }).catch(e => { runtimePromise = null; throw e; });
    return runtimePromise;
  }
  async function models() {
    const r = await runtime();
    const available = await r.getAvailable(process.env.REFERENCE_AGENT_PROVIDER || undefined, { signal: AbortSignal.timeout(15000) });
    return available.filter(m => m.input?.includes('image') && (!process.env.REFERENCE_AGENT_MODEL || m.id === process.env.REFERENCE_AGENT_MODEL))
      .map(m => ({ provider: m.provider, id: m.id, name: m.name, imageInput: true }))
      .sort((a,b)=>Number(b.provider===preferences.defaultProvider&&b.id===preferences.defaultModel)-Number(a.provider===preferences.defaultProvider&&a.id===preferences.defaultModel)
        ||(a.provider+'/'+a.id).localeCompare(b.provider+'/'+b.id));
  }
  async function open({ sessionId, entries, provider, modelId, prompt, tools }) {
    const { createAgentSession, DefaultResourceLoader, SettingsManager, SessionManager } = await sdk();
    const r = await runtime();
    const model = r.getModel(provider, modelId);
    if (!model || !model.input?.includes('image')) throw new Error('请选择支持图片输入的已配置模型');
    const settingsManager = SettingsManager.inMemory({ retry: { enabled: false, provider: { maxRetries: 0, timeoutMs: 90000 } },
      compaction: { enabled: true }, cacheWarming: 'off', defaultProjectTrust: 'never' });
    const resourceLoader = new DefaultResourceLoader({ cwd: agentDir, agentDir, settingsManager,
      noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
      systemPromptOverride: () => prompt, appendSystemPromptOverride: () => [] });
    await resourceLoader.reload();
    const manager = SessionManager.inMemory(agentDir, { id: sessionId }, entries || []);
    const { session } = await createAgentSession({ cwd: agentDir, agentDir, modelRuntime: r, model,
      thinkingLevel: 'medium', settingsManager, resourceLoader, sessionManager: manager,
      noTools: 'builtin', tools: tools.map(t => t.name), customTools: tools });
    return { session, entries: () => [manager.getHeader(), ...manager.getEntries()].filter(Boolean) };
  }
  return { models, open };
}
