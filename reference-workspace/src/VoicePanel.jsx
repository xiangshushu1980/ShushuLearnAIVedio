// Owner: Sean — independent voice design/reference inputs, preview clips and confirmed voice history.
import React, { useEffect, useRef, useState } from 'react';

const statusNames = { queued: '等待生成', running: '生成中', succeeded: '已生成', failed: '失败', cancelled: '已取消' };
const stopOtherAudio = event => document.querySelectorAll('audio').forEach(audio => { if (audio !== event.currentTarget) audio.pause(); });

function AudioClip({ asset }) {
  return <div className="audio-clip">{asset.url ? <><audio controls preload="metadata" src={asset.url} onPlay={stopOtherAudio} />
    <a href={asset.url} download={`${asset.name}.wav`}>下载 WAV</a><small className="muted">{asset.durationSec?.toFixed(1)} 秒 · 24kHz 单声道</small></>
    : <p className="muted">音频已删除，保留来源记录。</p>}</div>;
}

export function VoicePanel({ workspace, catalog, api, refresh, notify, activeRun, onGenerate, onDirtyChange }) {
  const config = catalog.voice;
  const normalize = value => ({ ...value, features: value.features || {}, presetId: value.presetId || 'custom',
    sampleCount: value.mode !== 'reference' ? 1 : value.sampleCount });
  const initial = () => normalize(workspace.voiceDraft?.value || structuredClone(config.defaults));
  const [draft, setDraft] = useState(initial), [saved, setSaved] = useState(() => JSON.stringify(initial()));
  const [draftAt, setDraftAt] = useState(workspace.voiceDraft?.updatedAt || null), [busy, setBusy] = useState('');
  const [loaded, setLoaded] = useState(null);
  const fileInput = useRef(null), request = useRef(null);
  const dirty = JSON.stringify(draft) !== saved;
  const current = workspace.voiceState?.current;
  const runs = workspace.runs.filter(run => run.snapshot.stage === 'voice');
  const sources = workspace.assets.filter(asset => ['voice-source', 'voice'].includes(asset.kind) && asset.metadata.voiceRole !== 'emotion');
  const source = sources.find(asset => asset.id === draft.referenceAssetId);
  const previewTemplate = config.templates.find(template => template.id === draft.templateId);
  const samples = draft.mode !== 'reference' ? [config.baseSample[draft.language]] : previewTemplate?.languages[draft.language]?.slice(0, draft.sampleCount) || [];
  const designPrompt = [...config.features.map(field => field.options.find(option => option.id === draft.features?.[field.id])?.prompt[draft.language]),
    draft.language === 'en' ? 'Natural clear English. Speak normally, do not sing.' : '普通话自然清晰，正常说话，不唱歌。', draft.instruction.trim()].filter(Boolean).join('；');
  const sourceRun = runs.find(run => run.id === draft.sourceRunId);
  const displayedRun = sourceRun || runs.find(run => run.outputs.some(asset => !asset.deletedAt));
  const patch = values => setDraft(value => ({ ...value, ...values }));
  const canGenerate = draft.mode === 'design' ? !!draft.instruction.trim() || Object.values(draft.features || {}).some(Boolean)
    : !!source && !!draft.referenceText.trim() && draft.transcriptConfirmed;
  useEffect(() => {
    const value = initial(); setDraft(value); setSaved(JSON.stringify(value)); setDraftAt(workspace.voiceDraft?.updatedAt || null);
    setLoaded(null); request.current = null;
  }, [workspace.entity.id]);
  useEffect(() => { onDirtyChange(dirty); }, [dirty, onDirtyChange]);
  useEffect(() => {
    const warn = event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } };
    addEventListener('beforeunload', warn); return () => removeEventListener('beforeunload', warn);
  }, [dirty]);
  useEffect(() => {
    if (!draft.sourceRunId) { setLoaded(null); return; }
    let cancelled = false; setLoaded(null);
    api(`/runs/${draft.sourceRunId}/input`).then(value => { if (!cancelled) setLoaded(value); })
      .catch(error => { if (!cancelled) setLoaded({ compatible: false, reason: error.message }); });
    return () => { cancelled = true; };
  }, [draft.sourceRunId]);

  async function save() {
    setBusy('save');
    try {
      const response = await api(`/entities/${workspace.entity.id}/voice/draft`, { method: 'PUT', body: JSON.stringify({ value: draft, expectedUpdatedAt: draftAt }) });
      setDraftAt(response.updatedAt); setSaved(JSON.stringify(draft)); notify('声音输入已保存');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function upload(file) {
    if (!file) return;
    if (file.size > 25 * 1024 * 1024) return notify('音源不得超过 25 MB', true);
    setBusy('upload');
    try {
      const form = new FormData(); form.append('audio', file);
      const asset = await api(`/entities/${workspace.entity.id}/voice/sources`, { method: 'POST', body: form });
      patch({ mode: 'clone', sampleCount: 1, referenceAssetId: asset.id, referenceText: '', transcriptConfirmed: false, sourceRunId: undefined,
        parameters: { ...draft.parameters, cfgScale: 1 } });
      await refresh(); notify('音源已导入，请听音校对准确转写');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function generate() {
    onGenerate(); setBusy('generate');
    try {
      const body = JSON.stringify(draft);
      if (request.current?.body !== body) request.current = { body, key: crypto.randomUUID() };
      await api(`/entities/${workspace.entity.id}/voice/runs`, { method: 'POST', body, headers: { 'Idempotency-Key': request.current.key } });
      request.current = null; patch({ sourceRunId: undefined }); await refresh(); notify('声音已提交，试听台词和输入已快照保存');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function load(run) {
    if (dirty && !confirm('用这次声音运行替换当前未保存的输入？')) return;
    setBusy('load');
    try {
      const response = await api(`/runs/${run.id}/input`);
      setDraft(normalize(response.input)); setLoaded(response); notify(response.input.mode === 'design' && response.input.sampleCount === 3
        ? '已载入历史输入；当前流程先生成一段基础样音，再固定音色做情绪试听。原工作流保留可查看。' : '已载入声音历史的特征、提示词、基础音源、转写、模板和参数');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  function useBase(asset) {
    patch({ mode: 'reference', referenceAssetId: asset.id, referenceText: asset.metadata.sampleText || '',
      transcriptConfirmed: false, instruction: '', sampleCount: 3, sourceRunId: undefined, parameters: { ...draft.parameters, cfgScale: 1 } });
    notify('已固定这段基础音源；请听音校对转写，再生成情绪试听');
  }
  async function confirmVoice(asset) {
    if (current && current.assetId !== asset.id && !confirm('将这段样音设为当前声音？旧版本会保留并自动锁定。')) return;
    setBusy('confirm');
    try {
      await api(`/entities/${workspace.entity.id}/voice/confirm`, { method: 'POST', body: JSON.stringify({ assetId: asset.id, expectedVoiceId: current?.id || null }) });
      await refresh(); notify('已选定人物基础音色'); useBase(asset);
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function lock(asset) {
    setBusy('lock');
    try { await api(`/assets/${asset.id}/lock`, { method: 'PATCH', body: JSON.stringify({ locked: !asset.locked }) }); await refresh(); }
    catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function remove(asset) {
    if (!confirm(`删除“${asset.name}”？历史来源标识会保留。`)) return;
    setBusy('delete');
    try {
      try { await api(`/assets/${asset.id}`, { method: 'DELETE', body: JSON.stringify({ confirmUsed: false }) }); }
      catch (error) {
        if (!error.details?.requiresConfirmation) throw error;
        if (!confirm(`这段音频被 ${error.details.runs.length} 次历史运行引用。删除后会显示音源缺失。继续删除？`)) return;
        await api(`/assets/${asset.id}`, { method: 'DELETE', body: JSON.stringify({ confirmUsed: true }) });
      }
      await refresh(); notify('音频已删除，历史来源保留');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  async function runAction(run, type) {
    if (type === 'retry' && run.error?.includes('结果未知') && !confirm('确认已核对 ComfyUI 队列与历史，再开始新的声音运行？')) return;
    setBusy(type);
    try {
      await api(`/runs/${run.id}/${type}`, { method: 'POST', ...(type === 'retry' ? { headers: { 'Idempotency-Key': crypto.randomUUID() } } : {}) });
      await refresh();
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  const candidates = run => [...run.outputs].sort((a, b) => (a.metadata.sampleIndex ?? 0) - (b.metadata.sampleIndex ?? 0)).map(asset =>
    <article className={`voice-candidate ${asset.protected ? 'confirmed' : ''}`} key={asset.id}>
      <div className="section-head"><b>{asset.metadata.sampleLabel || asset.name}</b>{asset.protected && <span className="pill">当前声音</span>}{asset.everConfirmed && !asset.protected && <small>曾定稿</small>}</div>
      <p>{asset.metadata.sampleText}</p><AudioClip asset={asset} />
      <div className="card-actions">{asset.metadata.voiceRole !== 'emotion' ? <><button className="primary" disabled={!!busy || !!asset.deletedAt || asset.protected || run.status !== 'succeeded'} onClick={() => confirmVoice(asset)}>设为人物基础音色</button><button disabled={!!busy || !!asset.deletedAt || run.status !== 'succeeded'} onClick={() => useBase(asset)}>用这段做情绪试听</button></> : <span className="muted">情绪展示 · 基础音源 {asset.metadata.anchor?.assetId.slice(0, 8)}</span>}
        <button disabled={!!busy || !!asset.deletedAt || asset.protected} onClick={() => lock(asset)}>{asset.locked ? '解锁' : '锁定'}</button>
        <button className="danger" disabled={!!busy || !!asset.deletedAt || asset.locked || asset.protected} onClick={() => remove(asset)}>删除</button></div>
    </article>);

  return <>
    <div className="section-head"><div><h2>声音生成</h2><p>先设计并选定基础音色，再用同一段样音展现不同情绪。</p></div><span className="pill">{config.model.name}</span></div>
    {current && <section className="voice-current"><div className="section-head"><h3>人物基础音色 · 版本 {current.version}</h3><span className="pill">已定稿 · 受保护</span></div>
      <p>{current.asset.metadata.sampleText}</p><AudioClip asset={current.asset} /><button disabled={!!busy} onClick={() => useBase(current.asset)}>用当前基础音色做情绪试听</button></section>}
    <section className="input-panel"><label>输入方式<select value={draft.mode} onChange={event => patch({ mode: event.target.value, sampleCount: event.target.value === 'reference' ? 3 : 1, instruction: '', transcriptConfirmed: false, sourceRunId: undefined,
      parameters: { ...draft.parameters, cfgScale: event.target.value !== 'design' ? 1 : config.fields.cfgScale.default } })}>
      {config.modes.map(mode => <option key={mode.id} value={mode.id}>{mode.name}</option>)}</select></label>
      {draft.mode === 'design' && <div className="voice-design">
        <label>声音预制模板<select value={draft.presetId || 'custom'} onChange={event => {
          const preset = config.presets.find(item => item.id === event.target.value);
          patch({ presetId: event.target.value, ...(preset ? { features: structuredClone(preset.features), instruction: '', sourceRunId: undefined } : {}) });
        }}><option value="custom">自定义组合</option>{config.presets.map(preset => <option key={preset.id} value={preset.id}>{preset.name}</option>)}</select></label>
        <div className="fields-row voice-features">{config.features.map(field => <label key={field.id}>{field.name}<select value={draft.features?.[field.id] || ''} onChange={event => {
          const features = { ...draft.features }; if (event.target.value) features[field.id] = event.target.value; else delete features[field.id];
          patch({ features, presetId: 'custom' });
        }}><option value="">未指定</option>{field.options.map(option => <option key={option.id} value={option.id}>{option.name}</option>)}</select></label>)}</div>
        <label>额外声音特征 <span className="muted">（选填）</span><textarea rows={3} maxLength={2000} value={draft.instruction} onChange={event => patch({ instruction: event.target.value })} placeholder="补充独特的音质、共鸣或口语习惯；基础样音保持中性情绪。" /></label>
        <details><summary>查看组合后的声音描述</summary><p className="saved-prompt">{designPrompt}</p></details>
        <p className="muted">模板一键填入特征，可继续微调。先生成一段中性样音，试听通过后选为人物基础音色。</p>
      </div>}
      {draft.mode !== 'design' && <div className="voice-reference"><div className="section-head"><h3>固定基础音源</h3><button onClick={() => fileInput.current.click()} disabled={!!busy}>导入音源</button></div>
        <input ref={fileInput} type="file" accept=".wav,.flac,.mp3,audio/wav,audio/flac,audio/mpeg" hidden onChange={event => { void upload(event.target.files[0]); event.target.value = ''; }} />
        <p className="muted">所有情绪共用下方同一段音源与准确转写。可选已生成的基础样音，或导入 30 秒以内的清晰单人录音（WAV / FLAC / MP3，最多 25 MB）。</p>
        <label>音源<select value={draft.referenceAssetId || ''} onChange={event => {
          const selected = sources.find(asset => asset.id === event.target.value);
          patch({ referenceAssetId: selected?.id || null, referenceText: selected?.metadata.sampleText || '', transcriptConfirmed: false });
        }}><option value="">请选择或导入音源</option>{draft.referenceAssetId && !source && <option value={draft.referenceAssetId}>历史音源已删除</option>}
          {sources.map(asset => <option key={asset.id} value={asset.id}>{asset.kind === 'voice' ? '生成样音 · ' : ''}{asset.name}</option>)}</select></label>
        {source && <p className="muted">基础音源 {source.id.slice(0, 8)} · {source.hash.slice(0, 12)}{current && source.id !== current.assetId ? ' · 与当前定稿不同，仍使用本次明确选择的音源' : ''}</p>}
        {source ? <AudioClip asset={source} /> : draft.referenceAssetId && <p className="error-text">历史音源已删除，请替换音源后再生成。</p>}
        <label>音源准确转写<textarea rows={3} value={draft.referenceText} maxLength={2000} placeholder="逐字填写这段音频实际说出的内容，先试听并校对。" onChange={event => patch({ referenceText: event.target.value, transcriptConfirmed: false })} /></label>
        <label className="transcript-confirm"><input type="checkbox" checked={draft.transcriptConfirmed} disabled={!source || !draft.referenceText.trim()} onChange={event => patch({ transcriptConfirmed: event.target.checked })} />已听音校对，确认转写与这段音源一致</label>
      </div>}
      <label>本轮目的 <span className="muted">（选填）</span><input value={draft.purpose} maxLength={2000} onChange={event => patch({ purpose: event.target.value })} /></label>
      {sourceRun && <div className="loaded-workflow">{sourceRun.snapshot.template.version === 1 && <p className="muted">旧版工作流保留供查看；再次生成采用当前的基础音色／固定音源流程。</p>}<b>已载入声音历史 · {sourceRun.id.slice(0, 8)}</b><a href={`/api/runs/${sourceRun.id}/workflow`} target="_blank" rel="noreferrer">查看原始工作流 ↗</a>
        {loaded && !loaded.compatible && <><p className="error-text">{loaded.reason}</p><button onClick={() => { if (confirm('改用当前声音工作流？请核对输入后再生成。')) patch({ sourceRunId: undefined }); }}>改用当前工作流</button></>}</div>}
    </section>
    <section className="generation-settings"><h3>试听台词与生成设置</h3><div className="fields-row">
      <label>语言<select value={draft.language} onChange={event => patch({ language: event.target.value })}>{config.languages.map(language => <option key={language.id} value={language.id}>{language.name}</option>)}</select></label>
      {draft.mode === 'reference' && <label>情绪试听模板<select value={draft.templateId} onChange={event => patch({ templateId: event.target.value })}>{config.templates.map(template => <option key={template.id} value={template.id}>{template.name}</option>)}</select></label>}
      <label>试听范围<select disabled={draft.mode !== 'reference'} value={draft.sampleCount} onChange={event => patch({ sampleCount: Number(event.target.value) })}><option value={1}>{draft.mode !== 'reference' ? '一段基础样音' : '一种情绪'}</option>{draft.mode === 'reference' && <option value={3}>三种情绪 · 同一音源</option>}</select></label>
      {Object.entries(config.fields).map(([key, field]) => <label key={key}>{field.label}<input type="number" value={draft.parameters[key]} min={field.min} max={field.max} step={field.step}
        onChange={event => patch({ parameters: { ...draft.parameters, [key]: event.target.value === '' ? '' : Number(event.target.value) } })} /></label>)}
    </div><div className="voice-scripts">{samples.map((sample, index) => <div key={index}><b>{sample.label}</b><p>{sample.text}</p></div>)}</div>
      <p className="muted">{draft.mode !== 'reference' ? '基础音色只生成一段中性样音。' : '每种情绪都引用同一基础音源；只调整语气、力度与节奏，保留说话人的音色。'}</p>
      <div className="generate-actions"><span className="muted">{dirty ? '声音输入有未保存修改' : draftAt ? '声音输入已保存' : ''}</span>
        <button disabled={!dirty || !!busy} onClick={save}>保存声音输入</button><button className="primary" disabled={!canGenerate || !!activeRun || !!busy || (!!draft.sourceRunId && !loaded?.compatible)} onClick={generate}>{activeRun?.snapshot.stage === 'voice' ? activeRun.phase : busy === 'generate' ? '正在提交…' : draft.mode !== 'reference' ? '生成基础音色' : '生成固定音色情绪试听'}</button></div>
      {activeRun?.snapshot.stage === 'voice' && <><p>{activeRun.phase}{activeRun.progress != null ? ` · ${Math.round(activeRun.progress)}%` : ''}</p><div className={`progress ${activeRun.progress == null ? 'indeterminate' : ''}`}><span style={{ width: `${activeRun.progress ?? 35}%` }} /></div></>}
    </section>
    <section className="result-section"><div className="section-head"><h3>候选试听</h3>{displayedRun && <small>{displayedRun.id.slice(0, 8)} · {statusNames[displayedRun.status]}</small>}</div>
      {displayedRun ? <div className="voice-candidates">{candidates(displayedRun)}</div> : <div className="empty"><h3>生成后在这里试听</h3><p>先选择基础样音，再试听它的不同情绪表现。</p></div>}
      {displayedRun && !displayedRun.outputs.length && <p className="muted">{displayedRun.error || displayedRun.phase}</p>}
    </section>
    <section className="run-history"><h3>声音生成历史</h3>{runs.map(run => <article className={`run-card ${draft.sourceRunId === run.id ? 'loaded' : ''}`} key={run.id}>
      <button className="history-load" aria-label={`载入声音历史 ${run.id.slice(0, 8)}`} disabled={!!busy} onClick={() => load(run)}><span className="run-heading"><b>{statusNames[run.status]}</b><span>{run.snapshot.voiceRole === 'base' ? '基础音色' : run.snapshot.voiceRole === 'emotion' ? '固定音色情绪' : '旧版声音生成'} · {run.snapshot.samples.length} 段</span><span className="muted">{new Date(run.createdAt).toLocaleString('zh-CN')} · {run.id.slice(0, 8)}</span><span className="accent">载入 →</span></span></button>
      <p>{run.snapshot.purpose || run.phase}</p>{run.error && <p className="error-text">{run.error}</p>}
      <details><summary>试听与本轮输入</summary><div className="voice-candidates">{candidates(run)}</div><p className="saved-prompt">{run.snapshot.prompt || '按参考音源生成'}</p>
        {run.references.map(reference => <p key={reference.id}>音源：{reference.name}{reference.deletedAt ? ' · 已删除' : ''}</p>)}
        {run.snapshot.mode !== 'design' && <p>转写：{run.snapshot.voiceInput.referenceText}</p>}<p className="muted">{JSON.stringify(run.snapshot.parameters)}</p>
        {run.promptId && <a href={`/api/runs/${run.id}/workflow`} target="_blank" rel="noreferrer">本次提交工作流 ↗</a>}</details>
      <div className="run-actions">{['failed', 'cancelled'].includes(run.status) && <button disabled={!!busy || !!activeRun} onClick={() => runAction(run, 'retry')}>重新运行</button>}
        {run.status === 'queued' && run.promptId && <button disabled={!!busy} onClick={() => runAction(run, 'cancel')}>取消排队</button>}</div>
    </article>)}{!runs.length && <p className="muted">暂无声音生成记录。</p>}</section>
    {!!workspace.voiceState?.history.length && <section className="run-history"><h3>声音定稿版本</h3>{workspace.voiceState.history.map(version => <div className="appearance-version" key={version.id}>
      <span>版本 {version.version}{version.id === current?.id ? ' · 当前' : ''}</span><span>{version.asset.name}{version.asset.deletedAt ? ' · 音频已删除' : ''}</span><small className="muted">{new Date(version.createdAt).toLocaleString('zh-CN')}</small></div>)}</section>}
    {!!sources.filter(asset => asset.kind === 'voice-source').length && <section className="run-history"><h3>已导入音源</h3>{sources.filter(asset => asset.kind === 'voice-source').map(asset => <article className="voice-candidate" key={asset.id}>
      <b>{asset.name}</b><AudioClip asset={asset} /><div className="card-actions"><button disabled={!!busy} onClick={() => lock(asset)}>{asset.locked ? '解锁' : '锁定'}</button><button className="danger" disabled={!!busy || asset.locked} onClick={() => remove(asset)}>删除</button></div>
    </article>)}</section>}
  </>;
}
