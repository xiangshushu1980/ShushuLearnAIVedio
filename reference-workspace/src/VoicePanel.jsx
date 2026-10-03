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
  const fileInput = useRef(null), request = useRef(null), creationDraft = useRef(null);
  const creating = draft.mode !== 'reference';
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
  const emotionalRun = current && runs.find(run => run.snapshot.voiceRole === 'emotion' && run.status === 'succeeded'
    && run.snapshot.anchor?.assetId === current.assetId && run.outputs.some(asset => !asset.deletedAt));
  const patch = values => setDraft(value => ({ ...value, ...values }));
  const canGenerate = draft.mode === 'design' ? !!draft.instruction.trim() || Object.values(draft.features || {}).some(Boolean)
    : !!source && !!draft.referenceText.trim() && draft.transcriptConfirmed
      && (draft.mode !== 'reference' || source.id === current?.assetId);
  useEffect(() => {
    const value = initial(); setDraft(value); setSaved(JSON.stringify(value)); setDraftAt(workspace.voiceDraft?.updatedAt || null);
    setLoaded(null); request.current = null; creationDraft.current = value.mode !== 'reference' ? value : null;
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
      if (creating) creationDraft.current = draft;
      setDraft(normalize(response.input)); setLoaded(response);
      document.getElementById(response.input.mode === 'reference' ? 'voice-emotion-create' : 'voice-create')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); notify(response.input.mode === 'design' && response.input.sampleCount === 3
        ? '已载入历史输入；当前流程先生成一段基础样音，再固定音色做情绪试听。原工作流保留可查看。' : '已载入声音历史的特征、提示词、基础音源、转写、模板和参数');
    } catch (error) { notify(error.message, true); }
    finally { setBusy(''); }
  }
  function useBase(asset) {
    if (creating) creationDraft.current = draft;
    patch({ mode: 'reference', referenceAssetId: asset.id, referenceText: asset.metadata.sampleText || '',
      transcriptConfirmed: false, instruction: '', sampleCount: 3, sourceRunId: undefined, parameters: { ...draft.parameters, cfgScale: 1 } });
    document.getElementById('voice-emotion-create')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    notify('已使用当前声音，请校对转写后生成情绪试听');
  }
  function chooseCreation(mode) {
    const value = creating ? draft : creationDraft.current || normalize(structuredClone(config.defaults));
    setDraft({ ...value, mode, sampleCount: 1, sourceRunId: undefined, transcriptConfirmed: false,
      parameters: { ...value.parameters, cfgScale: mode === 'clone' ? 1 : config.fields.cfgScale.default } });
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
  const candidates = run => [...run.outputs].sort((a, b) => (a.metadata.sampleIndex ?? 0) - (b.metadata.sampleIndex ?? 0)).map(asset => {
    const selected = current?.assetId === asset.id;
    return <article className={`voice-candidate ${selected ? 'voice-selected' : ''}`} key={asset.id}>
      <div className="section-head"><b>{asset.metadata.sampleLabel || asset.name}</b>{selected && <span className="voice-yellow-mark">★ 当前声音</span>}{asset.everConfirmed && !selected && <small className="muted">曾选用</small>}</div>
      <p>{asset.metadata.sampleText}</p><AudioClip asset={asset} />
      <div className="card-actions">{asset.metadata.voiceRole !== 'emotion' && <button className={selected ? 'voice-selected-button' : 'primary'} disabled={!!busy || !!asset.deletedAt || selected || run.status !== 'succeeded'} onClick={() => confirmVoice(asset)}>{selected ? '已选为当前声音' : '选择为当前声音'}</button>}
        <button disabled={!!busy || !!asset.deletedAt || asset.protected} onClick={() => lock(asset)}>{asset.locked ? '解锁' : '锁定'}</button>
        <button className="danger" disabled={!!busy || !!asset.deletedAt || asset.locked || asset.protected} onClick={() => remove(asset)}>删除</button></div>
    </article>;
  });

  const generationSettings = () => <>
      <label>本轮目的 <span className="muted">（选填）</span><input value={draft.purpose} maxLength={2000} onChange={event => patch({ purpose: event.target.value })} /></label>
      {sourceRun && <div className="loaded-workflow">{sourceRun.snapshot.template.version === 1 && <p className="muted">旧版工作流保留供查看；再次生成采用当前的基础音色／固定音源流程。</p>}<b>已载入声音历史 · {sourceRun.id.slice(0, 8)}</b><a href={`/api/runs/${sourceRun.id}/workflow`} target="_blank" rel="noreferrer">查看原始工作流 ↗</a>
        {loaded && !loaded.compatible && <><p className="error-text">{loaded.reason}</p><button onClick={() => { if (confirm('改用当前声音工作流？请核对输入后再生成。')) patch({ sourceRunId: undefined }); }}>改用当前工作流</button></>}</div>}
    <div className="generation-settings"><h4>试听台词与生成设置</h4><div className="fields-row">
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
    </div>

  </>;
  return <div className="voice-workspace">
    <div className="section-head"><div><h2>人物声音</h2><p>创建基础声音 → 从历史确认 → 展现不同情绪</p></div><span className="pill">{config.model.name}</span></div>
    <section className="voice-stage voice-overview" id="voice-current">
      <div className="voice-stage-heading"><span className="voice-step">0</span><div><h3>当前声音和情绪试听</h3><p>人物当前使用的声音，以及由它生成的情绪表现。</p></div></div>
      <div className="voice-overview-grid"><div className="voice-current-card">
        <div className="section-head"><h4>当前声音</h4>{current && <span className="voice-yellow-mark">★ 已选定 · 版本 {current.version}</span>}</div>
        {current ? <><b>{current.asset.name}</b><p>{current.asset.metadata.sampleText}</p><AudioClip asset={current.asset} />
          <button className="primary" disabled={!!busy} onClick={() => useBase(current.asset)}>为当前声音生成情绪试听</button></>
          : <div className="empty"><p>尚未选择当前声音。</p><a href="#voice-history">从历史记录选择 ↓</a></div>}
      </div><div className="voice-emotion-list"><h4>情绪试听</h4>
        {emotionalRun ? <div className="voice-emotion-clips">{emotionalRun.outputs.filter(asset => !asset.deletedAt).map(asset => <div key={asset.id}><b>{asset.metadata.sampleLabel}</b><AudioClip asset={asset} /></div>)}</div>
          : <p className="muted">{current ? '当前声音尚未生成情绪试听。确认下方设置后即可生成。' : '选定当前声音后，这里会显示它的情绪试听。'}</p>}
      </div></div>
    </section>
    <section className="voice-stage" id="voice-create">
      <div className="voice-stage-heading"><span className="voice-step">1</span><div><h3>原始创建</h3><p>通过预制模板设计声音，或上传录音建立基础声音。</p></div></div>
      <div className="voice-create-tabs" role="tablist" aria-label="基础声音创建方式">
        <button role="tab" aria-selected={draft.mode === 'design'} onClick={() => chooseCreation('design')} disabled={!!busy}>从模板创建</button>
        <button role="tab" aria-selected={draft.mode === 'clone'} onClick={() => chooseCreation('clone')} disabled={!!busy}>上传音源创建</button>
      </div>
      {creating ? <div className="input-panel">
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
      {draft.mode === 'clone' && <div className="voice-reference"><div className="section-head"><h3>上传原始音源</h3><button onClick={() => fileInput.current.click()} disabled={!!busy}>导入音源</button></div>
        <input ref={fileInput} type="file" accept=".wav,.flac,.mp3,audio/wav,audio/flac,audio/mpeg" hidden onChange={event => { void upload(event.target.files[0]); event.target.value = ''; }} />
        <p className="muted">上传 30 秒以内的清晰单人录音，建立一段中性的基础声音。支持 WAV / FLAC / MP3，最多 25 MB。</p>
        <label>音源<select value={draft.referenceAssetId || ''} onChange={event => {
          const selected = sources.find(asset => asset.id === event.target.value);
          patch({ referenceAssetId: selected?.id || null, referenceText: selected?.metadata.sampleText || '', transcriptConfirmed: false });
        }}><option value="">请选择或导入音源</option>{draft.referenceAssetId && !source && <option value={draft.referenceAssetId}>历史音源已删除</option>}
          {sources.filter(asset => asset.kind === 'voice-source').map(asset => <option key={asset.id} value={asset.id}>{asset.kind === 'voice' ? '生成样音 · ' : ''}{asset.name}</option>)}</select></label>
        {source ? <AudioClip asset={source} /> : draft.referenceAssetId && <p className="error-text">历史音源已删除，请替换音源后再生成。</p>}
        <label>音源准确转写<textarea rows={3} value={draft.referenceText} maxLength={2000} placeholder="逐字填写这段音频实际说出的内容，先试听并校对。" onChange={event => patch({ referenceText: event.target.value, transcriptConfirmed: false })} /></label>
        <label className="transcript-confirm"><input type="checkbox" checked={draft.transcriptConfirmed} disabled={!source || !draft.referenceText.trim()} onChange={event => patch({ transcriptConfirmed: event.target.checked })} />已听音校对，确认转写与这段音源一致</label>
      </div>}

        {generationSettings()}
        <p className="muted">生成结果会加入第 3 步历史记录；试听后在那里选择为当前声音。</p>
      </div> : <p className="muted">当前正在设置情绪试听。点击上方创建方式可编辑新的基础声音。</p>}
    </section>
    <section className={`voice-stage ${!current ? 'voice-stage-locked' : ''}`} id="voice-emotion-create">
      <div className="voice-stage-heading"><span className="voice-step">2</span><div><h3>确认后情绪试听</h3><p>只使用已确认的当前声音，改变情绪表达。</p></div>{current && <span className="voice-yellow-mark">使用当前声音</span>}</div>
      {!current ? <div className="empty"><p>请先在历史记录中选择并确认一段基础声音。</p><a href="#voice-history">前往历史记录 ↓</a></div>
        : creating ? <div className="voice-emotion-start"><p>已选定：{current.asset.name}</p><button className="primary" disabled={!!busy} onClick={() => useBase(current.asset)}>开始设置情绪试听</button></div>
        : source?.id !== current.assetId ? <div className="voice-emotion-start"><p>载入的历史引用与当前声音不同。请使用已确认的当前声音继续。</p><button className="primary" disabled={!!busy} onClick={() => useBase(current.asset)}>使用当前声音</button></div>
        : <div className="input-panel"><p className="voice-anchor-summary">基础声音已固定：<b>{current.asset.name}</b></p>
          <label>基础声音准确转写<textarea rows={2} value={draft.referenceText} maxLength={2000} onChange={event => patch({ referenceText: event.target.value, transcriptConfirmed: false })} /></label>
          <label className="transcript-confirm"><input type="checkbox" checked={draft.transcriptConfirmed} disabled={!draft.referenceText.trim()} onChange={event => patch({ transcriptConfirmed: event.target.checked })} />已听音校对，确认转写与当前声音一致</label>
          {generationSettings()}
        </div>}
    </section>
    <section className="voice-stage run-history" id="voice-history">
      <div className="voice-stage-heading"><span className="voice-step">3</span><div><h3>历史记录</h3><p>在基础声音记录上选择当前声音。黄色标记代表正在使用。</p></div></div>
      {runs.map(run => {
        const selected = run.outputs.some(asset => asset.id === current?.assetId);
        return <article className={`run-card ${selected ? 'voice-selected' : ''} ${draft.sourceRunId === run.id ? 'loaded' : ''}`} key={run.id}>
          <div className="section-head"><b>{run.snapshot.voiceRole === 'emotion' ? '情绪试听' : '基础声音'} · {statusNames[run.status]}</b>{selected && <span className="voice-yellow-mark">★ 当前声音来自此记录</span>}<small className="muted">{new Date(run.createdAt).toLocaleString('zh-CN')}</small></div>
          {run.error && <p className="error-text">{run.error}</p>}
          {run.snapshot.voiceRole === 'emotion' ? <details><summary>播放 {run.outputs.length} 段情绪试听</summary><div className="voice-candidates">{candidates(run)}</div></details> : <div className="voice-candidates">{candidates(run)}</div>}
          <div className="run-actions"><button aria-label={`载入声音历史 ${run.id.slice(0, 8)}`} disabled={!!busy} onClick={() => load(run)}>载入创建设置</button>
            {['failed', 'cancelled'].includes(run.status) && <button disabled={!!busy || !!activeRun} onClick={() => runAction(run, 'retry')}>重新运行</button>}
            {run.status === 'queued' && run.promptId && <button disabled={!!busy} onClick={() => runAction(run, 'cancel')}>取消排队</button>}
          </div>
          <details className="voice-history-details"><summary>查看本轮输入与工作流</summary><p>{run.snapshot.purpose}</p><p className="saved-prompt">{run.snapshot.prompt || '使用基础音源'}</p>
            {run.references.map(reference => <p key={reference.id}>音源：{reference.name}{reference.deletedAt ? ' · 已删除' : ''}</p>)}
            {run.snapshot.mode !== 'design' && <p>转写：{run.snapshot.voiceInput.referenceText}</p>}<p className="muted">{JSON.stringify(run.snapshot.parameters)}</p>
            {run.promptId && <a href={`/api/runs/${run.id}/workflow`} target="_blank" rel="noreferrer">本次提交工作流 ↗</a>}
          </details>
        </article>;
      })}{!runs.length && <p className="muted">暂无声音记录。请先在第 1 步创建基础声音。</p>}
      {!!workspace.voiceState?.history.length && <details className="voice-history-details"><summary>查看已选声音的版本记录</summary>{workspace.voiceState.history.map(version => <div className={`appearance-version ${version.id === current?.id ? 'voice-selected' : ''}`} key={version.id}>
        <span>版本 {version.version}{version.id === current?.id ? ' · ★ 当前声音' : ''}</span><span>{version.asset.name}{version.asset.deletedAt ? ' · 已删除' : ''}</span><small className="muted">{new Date(version.createdAt).toLocaleString('zh-CN')}</small></div>)}</details>}
      {!!sources.filter(asset => asset.kind === 'voice-source').length && <details className="voice-history-details"><summary>查看已上传原始音源</summary>{sources.filter(asset => asset.kind === 'voice-source').map(asset => <article className="voice-candidate" key={asset.id}>
        <b>{asset.name}</b><AudioClip asset={asset} /><div className="card-actions"><button disabled={!!busy} onClick={() => lock(asset)}>{asset.locked ? '解锁' : '锁定'}</button><button className="danger" disabled={!!busy || asset.locked} onClick={() => remove(asset)}>删除</button></div>
      </article>)}</details>}
    </section>
  </div>;
}
