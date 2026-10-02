// Owner: Sean — settings import and concept iteration UI.
import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, { ...options,
    headers: { ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}), ...options.headers } });
  if (response.status === 204) return null;
  const result = await response.json();
  if (!response.ok) { const error = new Error(result.error || '请求失败'); error.details = result.details; throw error; }
  return result;
}
const statuses = { queued: '等待生成', running: '生成中', succeeded: '生成完成', failed: '生成失败', cancelled: '已取消' };
const terminal = status => ['succeeded', 'failed', 'cancelled'].includes(status);
const time = value => new Date(value).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
const defaults = (model) => Object.fromEntries(Object.entries(model.fields).map(([key, field]) => [key, field.default]));
const newDraft = catalog => ({ modelId: catalog.models[0].id, styleId: catalog.styles[0].id, prompt: '', purpose: '', references: [], parameters: defaults(catalog.models[0]) });

function Picture({ asset, onClick, selected, index, children }) {
  return <div className={`picture ${selected ? 'selected' : ''}`}>
    <button className="picture-image" onClick={onClick} aria-label={`${selected ? '取消选择' : '选择'} ${asset.name}`} disabled={!onClick}>
      {asset.url ? <img src={asset.url} alt={asset.name} loading="lazy" /> : <span className="deleted-picture">来源图已删除</span>}
      {index != null && <span className="image-number">{index + 1}</span>}
      {selected && <span className="selection-check">✓</span>}
    </button>
    <div className="picture-caption"><strong title={asset.name}>{asset.name}</strong>
      <span>{asset.width ? `${asset.width} × ${asset.height}` : '本地图片'}{asset.locked ? ' · 已锁定' : ''}{asset.everConfirmed ? ' · 曾定稿' : ''}{asset.protected ? ' · 当前使用' : ''}</span>
    </div>{children}
  </div>;
}

function App() {
  const [catalog, setCatalog] = useState(null), [entities, setEntities] = useState([]), [entityId, setEntityId] = useState('');
  const [workspace, setWorkspace] = useState(null), [tab, setTab] = useState('settings'), [draft, setDraft] = useState(null);
  const [savedValue, setSavedValue] = useState(''), [draftAt, setDraftAt] = useState(null);
  const [message, setMessage] = useState(null), [busy, setBusy] = useState(''), [pending, setPending] = useState([]);
  const [importIds, setImportIds] = useState([]), [preview, setPreview] = useState(null), [status, setStatus] = useState(null);
  const [glow, setGlow] = useState(''), [muted, setMuted] = useState(localStorage.getItem('reference-muted') === '1');
  const fileInput = useRef(null), knownRuns = useRef(new Map()), audio = useRef(null), generationRequest = useRef(null);
  const currentEntity = useRef(entityId), pendingRef = useRef([]);
  const dirty = draft && JSON.stringify(draft) !== savedValue;
  const model = catalog?.models.find(m => m.id === draft?.modelId);
  const assets = workspace?.assets || [], runs = workspace?.runs || [];
  const activeRun = runs.find(r => !terminal(r.status));
  const selected = draft?.references || [];
  const visibleConcepts = assets.filter(a => a.kind === 'concept');
  const settings = assets.filter(a => a.kind === 'setting');
  const latestResult = runs.find(r => r.outputs.some(a => !a.deletedAt));
  const previewAsset = preview || latestResult?.outputs.find(a => !a.deletedAt);

  function notify(text, error = false) { setMessage({ text, error }); }
  function enableAudio() {
    try { audio.current ||= new AudioContext(); void audio.current.resume(); } catch { /* browser may disallow audio */ }
  }
  function completionFeedback(run) {
    if (!['succeeded', 'failed'].includes(run.status)) return;
    setGlow(run.status === 'succeeded' ? 'success' : 'failure');
    setTimeout(() => setGlow(''), 1300);
    if (localStorage.getItem('reference-muted') === '1' || !audio.current) return;
    try {
      const context = audio.current, osc = context.createOscillator(), gain = context.createGain();
      osc.type = 'sine'; osc.frequency.value = run.status === 'succeeded' ? 660 : 260;
      gain.gain.setValueAtTime(0.055, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.24);
      osc.connect(gain); gain.connect(context.destination); osc.start(); osc.stop(context.currentTime + 0.25);
    } catch { /* feedback glow remains available */ }
  }
  async function refresh(forEntity = entityId, initial = false) {
    const value = await api(`/entities/${forEntity}/workspace`);
    if (currentEntity.current !== forEntity) return;
    for (const run of value.runs) {
      const before = knownRuns.current.get(run.id);
      if (!initial && before && !terminal(before) && terminal(run.status)) completionFeedback(run);
      knownRuns.current.set(run.id, run.status);
    }
    setWorkspace(value);
    if (preview) {
      const current = value.assets.find(a => a.id === preview.id);
      setPreview(current || null);
    }
    return value;
  }
  useEffect(() => {
    Promise.all([api('/catalog'), api('/entities')]).then(([config, list]) => {
      setCatalog(config); setEntities(list);
      const requested = new URLSearchParams(location.search).get('entity');
      setEntityId(list.some(e => e.id === requested) ? requested : list[0]?.id || '');
    }).catch(error => notify(error.message, true));
    return () => pendingRef.current.forEach(p => URL.revokeObjectURL(p.url));
  }, []);
  useEffect(() => {
    if (!entityId || !catalog) return;
    currentEntity.current = entityId;
    setWorkspace(null); setPreview(null); setDraft(null); knownRuns.current.clear();
    refresh(entityId, true).then(value => {
      if (!value || currentEntity.current !== entityId) return;
      const valueDraft = value.draft?.value || newDraft(catalog);
      setDraft(valueDraft); setSavedValue(JSON.stringify(valueDraft)); setDraftAt(value.draft?.updatedAt || null);
    }).catch(error => notify(error.message, true));
    const url = new URL(location.href); url.searchParams.set('entity', entityId); history.replaceState(null, '', url);
    const timer = setInterval(() => refresh(entityId).catch(error => notify(error.message, true)), 2500);
    return () => clearInterval(timer);
  }, [entityId, catalog]);
  useEffect(() => {
    const check = () => api('/execution-status').then(setStatus).catch(() => setStatus({ connected: false }));
    void check(); const timer = setInterval(check, 10000); return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    const warn = event => { if (dirty || pending.length) { event.preventDefault(); event.returnValue = ''; } };
    addEventListener('beforeunload', warn); return () => removeEventListener('beforeunload', warn);
  }, [dirty, pending.length]);

  function patch(values) { setDraft(value => ({ ...value, ...values })); }
  function toggleReference(assetId) {
    if (selected.includes(assetId)) patch({ references: selected.filter(value => value !== assetId) });
    else if (selected.length < model.references.max) patch({ references: [...selected, assetId] });
    else notify(`所选模型最多支持 ${model.references.max} 张引用图片`, true);
  }
  function moveReference(index, direction) {
    const refs = [...selected]; [refs[index], refs[index + direction]] = [refs[index + direction], refs[index]];
    patch({ references: refs });
  }
  function pickFiles(files) {
    if (files.length > 16) return notify('一次最多导入 16 张图片', true);
    pendingRef.current.forEach(p => URL.revokeObjectURL(p.url));
    const values = [...files].filter(f => ['image/png', 'image/jpeg', 'image/webp'].includes(f.type)).map(file => ({
      id: crypto.randomUUID(), name: file.name, file, url: URL.createObjectURL(file)
    }));
    pendingRef.current = values; setPending(values); setImportIds(values.map(v => v.id));
    if (values.length !== files.length) notify('已过滤非 PNG、JPEG、WebP 文件');
  }
  async function importPictures() {
    const chosen = pending.filter(p => importIds.includes(p.id));
    if (!chosen.length) return;
    setBusy('import');
    try {
      const form = new FormData(); chosen.forEach(p => form.append('images', p.file));
      const result = await api(`/entities/${entityId}/settings`, { method: 'POST', body: form });
      const remaining = pending.filter(p => !importIds.includes(p.id));
      chosen.forEach(p => URL.revokeObjectURL(p.url)); pendingRef.current = remaining;
      setPending(remaining); setImportIds([]); await refresh();
      notify(`导入完成 · ${result.assets.length} 张图片已加入设定资料`);
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function saveDraft() {
    setBusy('draft');
    try {
      const result = await api(`/entities/${entityId}/draft`, { method: 'PUT', body: JSON.stringify({ value: draft, expectedUpdatedAt: draftAt }) });
      setDraftAt(result.updatedAt); setSavedValue(JSON.stringify(draft)); notify('本轮输入已保存');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function generate() {
    enableAudio(); setBusy('generate');
    try {
      const body = JSON.stringify(draft);
      if (generationRequest.current?.body !== body) generationRequest.current = { body, key: crypto.randomUUID() };
      const run = await api(`/entities/${entityId}/runs`, { method: 'POST', body, headers: { 'Idempotency-Key': generationRequest.current.key } });
      knownRuns.current.set(run.id, run.status); generationRequest.current = null;
      setPreview(null); await refresh(); notify('本轮输入已快照保存，正在准备生成');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function action(path, method, body) {
    setBusy(path);
    try {
      const result = await api(path, { method, ...(body ? { body: JSON.stringify(body) } : {}),
        ...(path.endsWith('/retry') ? { headers: { 'Idempotency-Key': crypto.randomUUID() } } : {}) });
      if (path.endsWith('/retry') && result?.id) knownRuns.current.set(result.id, result.status);
      await refresh();
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function removeAsset(asset) {
    if (!confirm(`删除“${asset.name}”？图片将从工作台移除。`)) return;
    setBusy(asset.id);
    try {
      try { await api(`/assets/${asset.id}`, { method: 'DELETE', body: JSON.stringify({ confirmUsed: false }) }); }
      catch (error) {
        if (!error.details?.requiresConfirmation) throw error;
        if (!confirm(`该图被 ${error.details.runs.length} 次历史运行引用。删除后这些记录将显示“来源图已删除”。继续删除？`)) return;
        await api(`/assets/${asset.id}`, { method: 'DELETE', body: JSON.stringify({ confirmUsed: true }) });
      }
      patch({ references: selected.filter(value => value !== asset.id) }); await refresh(); notify('图片已删除，历史来源记录已保留');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  function switchEntity(value) {
    if ((dirty || pending.length) && !confirm('有未保存输入或未导入图片，仍要切换实体？')) return;
    pendingRef.current.forEach(p => URL.revokeObjectURL(p.url)); pendingRef.current = [];
    setPending([]); setImportIds([]); setEntityId(value); generationRequest.current = null;
  }
  function reuseRun(run) {
    if (dirty && !confirm('用这次运行输入替换当前未保存的草稿？')) return;
    const source = run.snapshot;
    patch({ modelId: source.model.id, styleId: source.style.id, prompt: source.prompt, purpose: source.purpose,
      parameters: source.parameters, references: source.references.map(a => a.id) });
    notify('已载入历史输入，请检查后再运行'); window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  if (!catalog || !workspace || !draft) return <main className="loading"><span className="brand-mark">＋</span><h1>Reference 工作台</h1><p>{message?.text || '正在加载参考资料…'}</p></main>;
  const badReferences = selected.some(value => !assets.some(a => a.id === value));
  const canGenerate = model?.enabled && draft.prompt.trim() && selected.length >= model.references.min && selected.length <= model.references.max && !badReferences && !activeRun;
  return <>
    <header className="topbar"><div className="brand"><span className="brand-mark">＋</span><b>Reference 工作台</b><span className="top-tab">创建与编辑</span></div>
      <div className="header-actions"><button className="quiet" onClick={() => { setMuted(!muted); localStorage.setItem('reference-muted', muted ? '0' : '1'); }}>{muted ? '提示音已关闭' : '提示音已开启'}</button>
        <span className={`connection ${status?.connected ? 'online' : ''}`}>{status?.connected ? `ComfyUI 已连接${status.running || status.queued ? ' · 共享队列忙碌' : ''}` : 'ComfyUI 未连接'}</span></div>
    </header>
    <main className="workspace"><div className="breadcrumb">参考实体 / <select aria-label="选择实体" value={entityId} onChange={e => switchEntity(e.target.value)} disabled={!!busy}>{entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}</select> / 创建与编辑 / {tab === 'settings' ? '设定图片' : '概念图'}</div>
      <div className="page-title"><div><h1>{workspace.entity.name} <span>· 参考资料创作</span></h1><p>从设定资料出发，逐轮探索概念图。</p></div><span className="save-state">{dirty ? '本轮输入有未保存修改' : draftAt ? `输入已保存 · ${time(draftAt)}` : '请选择图片或准备本轮输入'}</span></div>
      <div className="workspace-layout"><aside className="steps-panel panel"><h2>创作步骤</h2><p className="muted">当前阶段 · 图片与概念探索</p>
        <button className={`step ${tab === 'settings' ? 'current' : ''}`} onClick={() => setTab('settings')}><span className="step-index">1</span><span><b>设定图片</b><small>{settings.length ? `已导入 ${settings.length} 张图片` : '选择已有图片'}</small></span></button>
        <button className={`step ${tab === 'concept' ? 'current' : ''}`} onClick={() => setTab('concept')}><span className="step-index">2</span><span><b>概念图</b><small>{activeRun ? activeRun.phase : visibleConcepts.length ? `${visibleConcepts.length} 张试验结果` : '引用图片，探索形象'}</small></span></button>
        {['主形象', '三视图', '声音'].map((label, index) => <div className="step unavailable" key={label}><span className="step-index">{index + 3}</span><span><b>{label}</b><small>后续阶段</small></span></div>)}
        <div className="step-note">{tab === 'settings' ? <>设定图片仅负责导入。<br/>图片生成在概念图中进行。</> : <>历史结果可直接用于下一轮。<br/>未选图片不参与生成。</>}</div>
      </aside><section className="main-panel panel">
        {message && <div role={message.error ? 'alert' : 'status'} className={`notice ${message.error ? 'error' : ''}`}><span>{message.text}</span><button className="quiet" onClick={() => setMessage(null)} aria-label="关闭提示">×</button></div>}
        {tab === 'settings' ? <>
          <div className="section-head"><div><h2>设定图片</h2><p>从当前目录选择图片，可一次多选。</p></div><button className="primary" onClick={() => fileInput.current.click()} disabled={!!busy}>＋ 选择图片</button></div>
          <input ref={fileInput} type="file" accept="image/png,image/jpeg,image/webp" multiple hidden onChange={e => { pickFiles(e.target.files); e.target.value = ''; }} />
          {pending.length > 0 && <section className="import-section"><div className="section-head"><h3>本次选择 <span className="accent">{importIds.length} 张</span></h3><span className="muted">点击图片选择 / 取消</span></div>
            <div className="picture-grid">{pending.map(asset => <Picture key={asset.id} asset={asset} selected={importIds.includes(asset.id)} onClick={() => setImportIds(ids => ids.includes(asset.id) ? ids.filter(i => i !== asset.id) : [...ids, asset.id])} />)}</div>
            <div className="import-footer"><span>已选 {importIds.length} 张 · 加入后可在概念图阶段引用</span><button className="primary" disabled={!importIds.length || !!busy} onClick={importPictures}>{busy === 'import' ? '正在导入…' : '加入设定图片'}</button></div>
          </section>}
          <div className="section-head"><h3>已导入 <span className="muted">{settings.length} 张</span></h3>{settings.length > 0 && <button className="quiet accent" onClick={() => setTab('concept')}>前往概念图 →</button>}</div>
          {settings.length ? <div className="picture-grid">{settings.map(asset => <Picture key={asset.id} asset={asset} onClick={() => { setPreview(asset); setTab('concept'); }}>
            <div className="card-actions"><button className="quiet danger" onClick={() => removeAsset(asset)} disabled={!!busy}>删除</button></div>
          </Picture>)}</div> : <div className="empty"><span className="empty-icon">▧</span><h3>从一张设定图片开始</h3><p>选择人物、服装、物品或环境图片，供概念探索时引用。</p><button onClick={() => fileInput.current.click()}>选择图片</button></div>}
        </> : <>
          <div className="section-head"><div><h2>概念图试验区</h2><p>选取引用图片，调整提示词与风格，逐轮探索形象。</p></div><span className="pill">{activeRun ? `${activeRun.phase}${activeRun.progress != null ? ` · ${Math.round(activeRun.progress)}%` : ''}` : `${visibleConcepts.length} 张历史结果`}</span></div>
          <div className="concept-layout"><section className="concept-preview">
            <div className="large-preview">{previewAsset?.url ? <img src={previewAsset.url} alt={previewAsset.name} /> : <div className="empty"><span className="empty-icon">◇</span><h3>下一轮，从这里开始</h3><p>生成结果将在这里显示。</p></div>}</div>
            <div className="preview-caption"><span>{previewAsset?.name || '候选预览'}</span>{previewAsset?.url && <a href={previewAsset.url} target="_blank" rel="noreferrer">查看原图 ↗</a>}</div>
            {previewAsset?.kind === 'concept' && <p className="muted">{previewAsset.locked ? '已自动锁定并加入试验历史' : '已解锁'} · 可选为下一轮输入</p>}
          </section><section className="input-panel">
            <label>模型<select value={draft.modelId} onChange={e => {
              const next = catalog.models.find(m => m.id === e.target.value);
              patch({ modelId: next.id, parameters: defaults(next) });
            }}>{catalog.models.map(m => <option value={m.id} key={m.id} disabled={!m.enabled}>{m.name}</option>)}</select></label>
            <label>提示词<textarea rows={6} value={draft.prompt} onChange={e => patch({ prompt: e.target.value })} placeholder="描述本轮想得到的概念图；有引用时，明确 Image 1、Image 2 各自提供什么。" maxLength={16000} /></label>
            <label>本轮目的 <span className="muted">（选填）</span><input value={draft.purpose} onChange={e => patch({ purpose: e.target.value })} placeholder="这一轮想验证什么？" maxLength={2000} /></label>
            <div className="field-title">本次引用图片 <span className="accent">{selected.length} 张</span></div>
            {selected.length ? <ol className="selected-references">{selected.map((assetId, index) => {
              const asset = assets.find(a => a.id === assetId);
              return <li key={assetId}>{asset?.url && <img src={asset.url} alt="" />}<span><b>Image {index + 1}</b><small>{asset?.name || '来源图已删除'}</small></span>
                <button className="quiet" aria-label="向前移动" disabled={index === 0} onClick={() => moveReference(index, -1)}>↑</button>
                <button className="quiet" aria-label="向后移动" disabled={index === selected.length - 1} onClick={() => moveReference(index, 1)}>↓</button>
                <button className="quiet" aria-label="移除引用" onClick={() => toggleReference(assetId)}>×</button></li>;
            })}</ol> : <div className="reference-placeholder">在下方选择设定图片或概念图历史。</div>}
            <small className="capability-note">{model?.references.instruction}</small>
          </section></div>
          <section className="generation-settings"><h3>生成设置</h3><div className="fields-row"><label>已保存风格<select value={draft.styleId} onChange={e => patch({ styleId: e.target.value })}>{catalog.styles.map(style => <option key={style.id} value={style.id}>{style.name}</option>)}</select></label>
            {Object.entries(model?.fields || {}).map(([key, field]) => <label key={key}>{field.label}{field.type === 'select' ? <select value={draft.parameters[key] ?? field.default} onChange={e => patch({ parameters: { ...draft.parameters, [key]: e.target.value } })}>{field.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select> : <input type="number" min={field.min} max={field.max} step="1" value={draft.parameters[key] ?? field.default} onChange={e => patch({ parameters: { ...draft.parameters, [key]: e.target.value === '' ? '' : Number(e.target.value) } })} />}</label>)}
          </div><div className="generate-actions"><button onClick={saveDraft} disabled={!!busy || !dirty}>保存本轮输入</button><button className="primary" onClick={generate} disabled={!canGenerate || !!busy}>{busy === 'generate' ? '正在提交…' : activeRun ? '本轮生成中' : '开始生成概念图'}</button></div>
            {badReferences && <p className="error-text">有来源图已删除，请移除后再生成。</p>}
            {selected.length > model.references.max && <p className="error-text">引用数量超过所选模型能力，请减少引用。</p>}
          </section>
          <section className="references-section"><div className="section-head"><h3>选择引用图片</h3><span className="muted">点击图片加入 / 移除本次输入</span></div><h4>设定图片 · {settings.length}</h4>
            {settings.length ? <div className="reference-grid">{settings.map(asset => <Picture key={asset.id} asset={asset} selected={selected.includes(asset.id)} onClick={() => toggleReference(asset.id)} />)}</div> : <p className="muted">暂无设定图片。可先导入，也可用文字生成第一张概念图。</p>}
            <h4>概念图历史 · {visibleConcepts.length}</h4><div className="reference-grid">{visibleConcepts.map(asset => <Picture key={asset.id} asset={asset} selected={selected.includes(asset.id)} onClick={() => toggleReference(asset.id)}>
              <div className="card-actions"><button className="quiet" onClick={() => setPreview(asset)}>预览</button><button className="quiet" disabled={!!busy || asset.protected} onClick={() => action(`/assets/${asset.id}/lock`, 'PATCH', { locked: !asset.locked })}>{asset.locked ? '解锁' : '锁定'}</button><button className="quiet danger" disabled={!!busy || asset.locked || asset.protected} onClick={() => removeAsset(asset)}>删除</button></div>
            </Picture>)}</div>
          </section>
          <section className="run-history"><div className="section-head"><h3>运行记录</h3><span className="muted">目的、输入与配置随每次运行保留</span></div>
            {runs.length ? runs.map(run => <article className={`run-card ${run.status}`} key={run.id}><div className="run-heading"><span className={`status-dot ${run.status}`} /><b>{statuses[run.status]}</b><span className="muted">{time(run.createdAt)} · {run.id.slice(0, 8)}</span><span className="run-model">{run.snapshot.model.name}</span></div>
              <p>{run.snapshot.purpose || '未填写本轮目的'}</p><div className="run-phase">{run.phase}{!terminal(run.status) && run.progress != null ? ` · ${Math.round(run.progress)}%` : ''}</div>
              {!terminal(run.status) && <div className={`progress ${run.progress == null ? 'indeterminate' : ''}`}><span style={{ width: `${run.progress ?? 35}%` }} /></div>}
              {run.error && <p className="error-text">{run.error}</p>}
              <details><summary>查看本轮输入与来源</summary><p className="saved-prompt">{run.snapshot.prompt}</p><p className="muted">风格：{run.snapshot.style.name} · {JSON.stringify(run.snapshot.parameters)}</p>
                <ol className="source-list">{run.references.map((ref, index) => <li key={ref.id}>Image {index + 1} · {ref.name}{ref.deletedAt ? ' · 来源图已删除' : ''}</li>)}</ol>
                <small className="muted">模板：{run.snapshot.template.id} v{run.snapshot.template.version}{run.promptId ? ` · ComfyUI ${run.promptId}` : ''}</small>
                {run.promptId && <p><a href={`/api/runs/${run.id}/workflow`} target="_blank" rel="noreferrer">查看本次提交工作流 ↗</a></p>}
              </details><div className="run-actions"><button className="quiet" onClick={() => reuseRun(run)} disabled={!!busy}>载入本轮输入</button>
                {['failed', 'cancelled'].includes(run.status) && <button onClick={() => {
                  if (run.error?.includes('结果未知') && !confirm('上次提交结果未知。确认已核对 ComfyUI 队列与历史，并开始新的运行？')) return;
                  enableAudio(); action(`/runs/${run.id}/retry`, 'POST');
                }} disabled={!!busy || !!activeRun}>重新运行</button>}
                {run.status === 'queued' && run.promptId && <button className="quiet" onClick={() => action(`/runs/${run.id}/cancel`, 'POST')} disabled={!!busy}>取消排队</button>}
              </div></article>) : <div className="empty compact"><p>每次探索都会保留独立运行记录。</p></div>}
          </section>
        </>}
      </section></div>
    </main>{glow && <div className={`completion-glow ${glow}`} aria-hidden="true" />}
  </>;
}

createRoot(document.getElementById('root')).render(<App />);
