// Owner: Sean — select an existing concept as appearance; multiview stays bound to its version.
import React, { useEffect, useRef, useState } from 'react';

export function AppearancePanel({ workspace, Picture, onPreview, onConfirm, busy, onViews }) {
  const current = workspace.visualState?.appearance;
  const candidates = workspace.assets.filter(asset => asset.kind === 'concept');
  const [selectedId, setSelectedId] = useState(current?.assetId || candidates[0]?.id || '');
  useEffect(() => { setSelectedId(current?.assetId || candidates[0]?.id || ''); }, [workspace.entity.id, current?.id]);
  const selected = candidates.find(asset => asset.id === selectedId);
  return <>
    <div className="section-head"><div><h2>选定主形象</h2><p>从概念图结果选择一张，作为三视图／四视图的输入。</p></div>{current && <span className="pill">当前版本 {current.version}</span>}</div>
    {current && <div className="appearance-current"><img src={current.asset.url} alt={current.asset.name} /><div><b>当前主形象 · 版本 {current.version}</b><p>{current.asset.name}</p><p className="muted">来源已保护，后续概念图试验不会替换它。</p><button className="primary" onClick={onViews}>前往多视图 →</button></div></div>}
    {selected ? <><div className="large-preview appearance-preview"><img src={selected.url} alt={selected.name} /></div><div className="preview-caption"><span>{selected.name}{selected.everConfirmed ? ' · 曾定稿' : ''}</span><div className="card-actions"><button onClick={() => onPreview(selected)}>放大</button><button className="primary" disabled={!!busy || current?.assetId === selected.id} onClick={() => onConfirm(selected)}>{current?.assetId === selected.id ? '当前主形象' : '设为当前主形象'}</button></div></div></> : <div className="empty"><h3>先生成概念图候选</h3><p>主形象直接选用概念图结果。</p></div>}
    <div className="section-head"><h3>概念图候选 · {candidates.length}</h3><span className="muted">点击选择，再确认主形象</span></div>
    <div className="reference-grid">{candidates.map(asset => <Picture key={asset.id} asset={asset} selected={asset.id === selectedId} onClick={() => setSelectedId(asset.id)} />)}</div>
    {!!workspace.visualState?.appearanceHistory.length && <section className="run-history"><h3>主形象版本</h3>{workspace.visualState.appearanceHistory.map(version => <div className="appearance-version" key={version.id}><span>版本 {version.version}{version.id === current?.id ? ' · 当前' : ''}</span><span>{version.asset.name}{version.asset.deletedAt ? ' · 来源图已删除' : ''}</span><small className="muted">{new Date(version.createdAt).toLocaleString('zh-CN')}</small></div>)}</section>}
  </>;
}

export function MultiViewPanel({ workspace, catalog, Picture, api, refresh, notify, onPreview, onAppearance, activeRun, onGenerate, onDirtyChange, onDelete }) {
  const current = workspace.visualState?.appearance;
  const models = catalog.multiview || [];
  const defaults = model => Object.fromEntries(Object.entries(model?.fields || {}).map(([key, field]) => [key, field.default]));
  const initial = () => workspace.multiviewDraft?.value || { layout: 'three', appearanceId: current?.id || null,
    parameters: defaults(models.find(model => model.layout === 'three')), purpose: '', notes: '' };
  const [draft, setDraft] = useState(initial), [saved, setSaved] = useState(() => JSON.stringify(initial()));
  const [draftAt, setDraftAt] = useState(workspace.multiviewDraft?.updatedAt || null), [busy, setBusy] = useState('');
  const [loaded, setLoaded] = useState(null), [previewId, setPreviewId] = useState(null);
  const request = useRef(null);
  const dirty = JSON.stringify(draft) !== saved;
  const model = models.find(model => model.layout === draft.layout);
  const runs = workspace.runs.filter(run => run.snapshot.stage === 'multiview');
  const sourceRun = runs.find(run => run.id === draft.sourceRunId);
  const displayedRun = previewId ? runs.find(run => run.outputs.some(asset => asset.id === previewId)) : sourceRun || runs.find(run => run.snapshot.appearance?.id === current?.id && run.snapshot.layout === draft.layout && run.outputs.some(asset => !asset.deletedAt));
  const result = displayedRun?.outputs.find(asset => !asset.deletedAt && (!previewId || asset.id === previewId));
  const inputCurrent = !!current && draft.appearanceId === current.id;
  const resultCurrent = !!current && displayedRun?.snapshot.appearance?.id === current.id;
  const inputAppearance = workspace.visualState?.appearanceHistory.find(version => version.id === draft.appearanceId);
  const inputAsset = inputAppearance?.asset || (!draft.appearanceId ? current?.asset : null);
  const patch = values => setDraft(value => ({ ...value, ...values }));
  useEffect(() => {
    const value = initial(); setDraft(value); setSaved(JSON.stringify(value)); setDraftAt(workspace.multiviewDraft?.updatedAt || null);
    setLoaded(null); setPreviewId(null); request.current = null;
  }, [workspace.entity.id]);
  useEffect(() => { onDirtyChange(dirty); }, [dirty, onDirtyChange]);
  useEffect(() => {
    if (current && !draft.appearanceId && !draft.sourceRunId) patch({ appearanceId: current.id });
  }, [current?.id, draft.appearanceId, draft.sourceRunId]);
  useEffect(() => {
    const warn = event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } };
    addEventListener('beforeunload', warn); return () => removeEventListener('beforeunload', warn);
  }, [dirty]);
  useEffect(() => {
    if (!draft.sourceRunId) { setLoaded(null); return; }
    let cancelled = false;
    api(`/runs/${draft.sourceRunId}/input`).then(value => { if (!cancelled) setLoaded(value); })
      .catch(error => { if (!cancelled) setLoaded({ compatible: false, reason: error.message }); });
    return () => { cancelled = true; };
  }, [draft.sourceRunId]);
  async function save() {
    setBusy('save');
    try {
      const value = await api(`/entities/${workspace.entity.id}/multiview/draft`, { method: 'PUT', body: JSON.stringify({ value: draft, expectedUpdatedAt: draftAt }) });
      setDraftAt(value.updatedAt); setSaved(JSON.stringify(draft)); notify('多视图输入已保存');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function generate() {
    onGenerate(); setBusy('generate');
    try {
      const body = JSON.stringify(draft);
      if (request.current?.body !== body) request.current = { body, key: crypto.randomUUID() };
      await api(`/entities/${workspace.entity.id}/multiview/runs`, { method: 'POST', body, headers: { 'Idempotency-Key': request.current.key } });
      request.current = null; patch({ sourceRunId: undefined }); setPreviewId(null); await refresh(); notify('多视图已提交，输入主形象版本已保存');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function load(run) {
    if (dirty && !confirm('用这次多视图运行替换当前未保存的输入？')) return;
    setBusy('load');
    try {
      const value = await api(`/runs/${run.id}/input`);
      setDraft({ layout: run.snapshot.layout, appearanceId: value.input.appearanceId, parameters: value.input.parameters,
        purpose: value.input.purpose, notes: value.input.notes || '', sourceRunId: run.id });
      setLoaded(value); setPreviewId(null); notify('已载入多视图历史输入及其主形象版本');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function confirmResult() {
    setBusy('confirm');
    try {
      await api(`/entities/${workspace.entity.id}/multiview/confirm`, { method: 'POST', body: JSON.stringify({ assetId: result.id, expectedAppearanceId: current.id }) });
      await refresh(); notify('已选定当前视图合成图');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function lock(asset) {
    setBusy('lock');
    try { await api(`/assets/${asset.id}/lock`, { method: 'PATCH', body: JSON.stringify({ locked: !asset.locked }) }); await refresh(); }
    catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function runAction(run, type) {
    if (type === 'retry' && run.error?.includes('结果未知') && !confirm('确认已核对 ComfyUI 队列与历史，并开始新的运行？')) return;
    setBusy(type);
    try {
      await api(`/runs/${run.id}/${type}`, { method: 'POST', ...(type === 'retry' ? { headers: { 'Idempotency-Key': crypto.randomUUID() } } : {}) });
      await refresh();
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  return <>
    <div className="section-head"><div><h2>三视图／四视图</h2><p>以已选定的主形象生成统一视图合成图。</p></div></div>
    {current ? <div className="appearance-current">{inputAsset?.url ? <img src={inputAsset.url} alt={inputAsset.name} /> : <span className="input-missing">来源图已删除</span>}<div><b>输入主形象 · 版本 {inputAppearance?.version || current.version}</b><p>{inputAsset?.name || '来源图不可用'}</p><button onClick={onAppearance}>更换主形象</button>{!inputCurrent && <><p className="error-text">当前主形象是版本 {current.version}，请更新本轮输入。</p><button className="primary" onClick={() => { patch({ appearanceId: current.id, sourceRunId: undefined }); setPreviewId(null); }}>引用当前主形象</button></>}</div></div> : <div className="empty"><h3>先选定主形象</h3><p>从概念图结果选一张即可。</p><button className="primary" onClick={onAppearance}>选择主形象</button></div>}
    {workspace.visualState?.view && <div className="notice"><span>当前已确认：{workspace.visualState.view.name}</span><button className="quiet" onClick={() => setPreviewId(workspace.visualState.view.id)}>查看</button></div>}
    <section className="input-panel"><label>视图布局<select value={draft.layout} onChange={event => { patch({ layout: event.target.value, sourceRunId: undefined }); setPreviewId(null); }}>
      <option value="three">三视图 · 正面／侧面／背面</option><option value="four">四视图 · 表情特写＋正面／侧面／背面</option></select></label>
      <p className="muted">{draft.layout === 'three' ? '三个等比例全身视角。' : '沿用 V3 Simple：左侧四种表情特写，右侧正／侧／背。'}保持主形象的服装、装备和画风。</p>
      <details className="fixed-prompt"><summary>查看固定提示词</summary><p className="saved-prompt">{model?.prompt || '工作流配置尚未就绪'}</p></details>
      <label>补充要求 <span className="muted">（选填）</span><textarea rows={3} value={draft.notes} maxLength={2000} placeholder="例如：保留腰间的刀鞘，不添加其他武器。" onChange={event => patch({ notes: event.target.value })} /></label>
      <label>本轮目的 <span className="muted">（选填）</span><input value={draft.purpose} maxLength={2000} onChange={event => patch({ purpose: event.target.value })} /></label>
      {sourceRun && <div className="loaded-workflow"><b>已载入历史 · {sourceRun.id.slice(0, 8)}</b><a href={`/api/runs/${sourceRun.id}/workflow`} target="_blank" rel="noreferrer">查看历史原始工作流 ↗</a>{loaded && !loaded.compatible && <><p className="error-text">{loaded.reason}</p><button onClick={() => { if (confirm('改用当前固定工作流？请检查输入后再生成。')) patch({ sourceRunId: undefined }); }}>改用当前工作流</button></>}</div>}
    </section>
    <section className="generation-settings"><h3>生成设置</h3><div className="fields-row">{Object.entries(model?.fields || {}).map(([key, field]) => <label key={key}>{field.label}{field.type === 'select' ? <select value={draft.parameters[key] ?? field.default} onChange={event => patch({ parameters: { ...draft.parameters, [key]: event.target.value } })}>{field.options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : <input type="number" min={field.min} max={field.max} step={1} value={draft.parameters[key] ?? field.default} onChange={event => patch({ parameters: { ...draft.parameters, [key]: event.target.value === '' ? '' : Number(event.target.value) } })} />}</label>)}</div>
      <div className="generate-actions"><span className="muted">{dirty ? '多视图输入有未保存修改' : draftAt ? '输入已保存' : ''}</span><button disabled={!dirty || !!busy} onClick={save}>保存本轮输入</button><button className="primary" disabled={!inputCurrent || !model?.enabled || !!activeRun || !!busy || (!!draft.sourceRunId && !loaded?.compatible)} onClick={generate}>{activeRun?.snapshot.stage === 'multiview' ? activeRun.phase : busy === 'generate' ? '正在提交…' : '开始生成多视图'}</button></div>
      {activeRun?.snapshot.stage === 'multiview' && <p className="muted">{activeRun.phase}{activeRun.progress != null ? ` · ${Math.round(activeRun.progress)}%` : ''}</p>}
    </section>
    <section className="result-section"><div className="section-head"><div><h3>生成结果</h3>{displayedRun && <p>主形象版本 {displayedRun.snapshot.appearance.version} · {displayedRun.snapshot.layout === 'three' ? '三视图' : '四视图'}{!resultCurrent ? ' · 来自旧版主形象' : ''}</p>}</div></div>
      <div className="large-preview">{result?.url ? <img src={result.url} alt={result.name} /> : <div className="empty"><h3>生成后在这里确认视图</h3><p>合成图作为一个完整结果保留。</p></div>}</div>
      {result && <div className="preview-caption"><span>{result.name}</span><div className="card-actions"><button onClick={() => onPreview(result)}>放大</button><button className="primary" onClick={confirmResult} disabled={!!busy || !resultCurrent || result.protected}>{result.protected ? '当前视图' : '设为当前视图'}</button></div></div>}
    </section>
    <section className="run-history"><div className="section-head"><h3>多视图历史</h3><span className="muted">点击载入该次输入，旧主形象来源保留</span></div>
      {runs.map(run => <article className={`run-card ${draft.sourceRunId === run.id ? 'loaded' : ''}`} key={run.id} onClick={event => { if (!busy && !event.target.closest('button,a,details')) void load(run); }}>
        <button className="history-load" aria-label={`载入多视图历史 ${run.id.slice(0, 8)}`} onClick={() => load(run)} disabled={!!busy}><span className="run-heading"><b>{{queued:'等待生成',running:'生成中',succeeded:'已生成',failed:'失败',cancelled:'已取消'}[run.status]}</b><span>{run.snapshot.layout === 'three' ? '三视图' : '四视图'} · 主形象版本 {run.snapshot.appearance.version}</span><span className="muted">{new Date(run.createdAt).toLocaleString('zh-CN')} · {run.id.slice(0, 8)}</span><span className="accent">载入 →</span></span></button>
        <p>{run.snapshot.purpose || run.phase}</p>{run.error && <p className="error-text">{run.error}</p>}
        <div className="reference-grid multiview-output-grid">{run.outputs.map(asset => <Picture key={asset.id} asset={asset} actionLabel="载入历史" onClick={() => load(run)}><div className="card-actions"><button className="quiet" disabled={!!busy || asset.protected || !!asset.deletedAt} onClick={() => lock(asset)}>{asset.locked ? '解锁' : '锁定'}</button><button className="quiet danger" disabled={!!busy || asset.locked || asset.protected || !!asset.deletedAt} onClick={() => onDelete(asset)}>删除</button></div></Picture>)}</div>
        <details><summary>查看本轮输入</summary><p className="saved-prompt">{run.snapshot.prompt}</p><p className="muted">{JSON.stringify(run.snapshot.parameters)}</p><p>来源：主形象版本 {run.snapshot.appearance.version} · {run.references[0]?.name}{run.references[0]?.deletedAt ? ' · 来源图已删除' : ''}</p>{run.promptId && <a href={`/api/runs/${run.id}/workflow`} target="_blank" rel="noreferrer">原始工作流 ↗</a>}</details>
        <div className="run-actions">{['failed', 'cancelled'].includes(run.status) && <button disabled={!!busy || !!activeRun || run.snapshot.appearance?.id !== current?.id} onClick={() => runAction(run, 'retry')}>重新运行</button>}{run.status === 'queued' && run.promptId && <button className="quiet" disabled={!!busy} onClick={() => runAction(run, 'cancel')}>取消排队</button>}</div>
      </article>)}{!runs.length && <p className="muted">暂无多视图生成记录。</p>}
    </section>
  </>;
}
