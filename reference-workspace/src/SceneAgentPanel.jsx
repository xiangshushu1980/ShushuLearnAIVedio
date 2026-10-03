// Owner: Sean — PC scene assistant: common project context, reference images, conversation and review.
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import './scene-agent.css';

const statusName={running:'正在回复',succeeded:'已结束',failed:'未完成',cancelled:'已取消',interrupted:'服务中断'};
const sourceName={image:'参考图观察',user:'用户补充',existing:'已有设定'};
const emptyProject={name:'',brief:'',decisions:'',entityIds:[]};
export function SceneAgentPanel({entityId,api,notify,onClose,onSaved,onDirtyChange}) {
  const [projects,setProjects]=useState([]),[projectId,setProjectId]=useState(''),[projectForm,setProjectForm]=useState(null),[projectBase,setProjectBase]=useState('');
  const [entities,setEntities]=useState([]),[workspace,setWorkspace]=useState(null),[record,setRecord]=useState(null),[cap,setCap]=useState(null);
  const [refs,setRefs]=useState([]),[model,setModel]=useState(''),[sessions,setSessions]=useState([]),[sessionId,setSessionId]=useState(''),[chat,setChat]=useState(null);
  const [text,setText]=useState(''),[busy,setBusy]=useState(false),[runId,setRunId]=useState(''),[phase,setPhase]=useState(''),[ack,setAck]=useState(false),[proposalId,setProposalId]=useState('');
  const generation=useRef(0),bottom=useRef(null),stream=useRef(null),pendingRequest=useRef(null);
  const project=projects.find(p=>p.id===projectId),projectDirty=!!projectForm&&JSON.stringify(projectForm)!==projectBase;
  const working=!!runId||busy,dirty=!!text.trim()||projectDirty||working;
  const images=workspace?.assets.filter(a=>a.mediaType==='image')||[];
  const proposals=chat?.proposals||[],proposal=proposals.find(p=>p.id===proposalId)||proposals.at(-1);
  useEffect(()=>{onDirtyChange?.(dirty);},[dirty,onDirtyChange]);
  useEffect(()=>{const warn=e=>{if(dirty){e.preventDefault();e.returnValue='';}};addEventListener('beforeunload',warn);return()=>removeEventListener('beforeunload',warn);},[dirty]);
  useEffect(()=>()=>onDirtyChange?.(false),[onDirtyChange]);
  useEffect(()=>{let gone=false;generation.current++;
    Promise.all([api('/agents/projects'),api('/agents/capabilities'),api(`/entities/${entityId}/workspace`),api(`/manage/entities/${entityId}/spatial`),api('/manage/entities')]).then(([p,c,w,r,e])=>{
      if(gone)return;setProjects(p.projects);setCap(c);setWorkspace(w);setRecord(r);setEntities(e.entities);
      const remembered=localStorage.getItem('sean.reference.agentProject');
      setProjectId(p.projects.find(x=>x.id===remembered)?.id||p.projects.find(x=>x.entityIds.includes(entityId))?.id||'');
      setModel(c.models[0]?JSON.stringify([c.models[0].provider,c.models[0].id]):'');
      const available=new Set(w.assets.filter(a=>a.mediaType==='image').map(a=>a.id));
      const defaults=[w.visualState?.appearance?.assetId,...r.document.referenceAssetIds].filter(v=>v&&available.has(v));
      setRefs([...new Set(defaults.length?defaults:w.assets.filter(a=>a.mediaType==='image').slice(0,1).map(a=>a.id))].slice(0,8));
    }).catch(e=>notify(e.message,true));
    return()=>{gone=true;generation.current++;stream.current?.close();};
  },[entityId]);
  useEffect(()=>{
    if(!projectId){setSessions([]);setSessionId('');setChat(null);return;}
    localStorage.setItem('sean.reference.agentProject',projectId);
    let gone=false;setSessionId('');setChat(null);setSessions([]);setProposalId('');setProjectForm(null);
    api(`/agents/projects/${projectId}/sessions?entityId=${entityId}`).then(r=>{if(!gone){setSessions(r.sessions);setSessionId(r.sessions[0]?.id||'');}}).catch(e=>notify(e.message,true));
    return()=>{gone=true;};
  },[projectId,entityId]);
  useEffect(()=>{
    let gone=false;generation.current++;stream.current?.close();setChat(null);setRunId('');setPhase('');setProposalId('');setAck(false);
    if(sessionId)api(`/agents/sessions/${sessionId}`).then(c=>{
      if(gone)return;setChat(c);const running=c.runs.find(r=>r.status==='running');if(running){setRunId(running.id);connect(running.id,sessionId);}
    }).catch(e=>notify(e.message,true));
    return()=>{gone=true;generation.current++;stream.current?.close();};
  },[sessionId]);
  useEffect(()=>{bottom.current?.scrollIntoView({block:'nearest'});},[chat?.messages.at(-1)?.text,phase]);
  function close(){if(dirty&&!confirm(working?'助手仍在回复，关闭后可重新打开继续查看。关闭窗口？':'有未发送的文字或工程修改，放弃并关闭？'))return;onClose();}
  function switchProject(value){if(working)return;if((text.trim()||projectDirty)&&!confirm('放弃未发送内容和未保存的工程修改？'))return;setText('');setProjectForm(null);setProjectId(value);}
  async function loadChat(id=sessionId){if(!id)return;const epoch=generation.current;const c=await api(`/agents/sessions/${id}`);if(epoch===generation.current)setChat(c);return c;}
  function connect(id,sid){
    stream.current?.close();const epoch=generation.current;
    const events=new EventSource(`/api/agents/runs/${id}/events`);stream.current=events;
    // Persisted server messages are authoritative; reload after replay/reconnect to avoid duplicate text.
    let refreshTimer;
    const refresh=()=>{if(refreshTimer)return;refreshTimer=setTimeout(()=>{refreshTimer=null;if(epoch===generation.current)void loadChat(sid).catch(()=>{});},200);};
    events.addEventListener('text',refresh);
    events.addEventListener('tool',e=>{if(epoch===generation.current)setPhase(JSON.parse(e.data).label);});
    events.addEventListener('proposal',refresh);
    events.addEventListener('done',()=>{events.close();clearTimeout(refreshTimer);if(epoch===generation.current){setRunId('');setPhase('');void loadChat(sid).catch(e=>notify(e.message,true));}});
    events.onerror=()=>{
      if(epoch!==generation.current)return;
      setPhase('连接恢复中，讨论已保存…');
      void api(`/agents/sessions/${sid}`).then(c=>{
        if(epoch!==generation.current)return;setChat(c);
        if(!c.runs.some(r=>r.id===id&&r.status==='running')){events.close();setRunId('');setPhase('');}
      }).catch(()=>{});
    };
  }
  async function startNewSession(){
    if(!project?.entityIds.includes(entityId)||!model)return;
    setBusy(true);try{const [provider,modelId]=JSON.parse(model);const c=await api('/agents/sessions',{method:'POST',body:JSON.stringify({projectId,entityId,purpose:'scene-spatial',provider,modelId})});
      setSessions(v=>[{id:c.id,provider:c.provider,modelId:c.modelId,createdAt:c.createdAt},...v]);setSessionId(c.id);
    }catch(e){notify(e.message,true);}finally{setBusy(false);}
  }
  async function send(){
    if(!text.trim()||!sessionId||!refs.length||working)return;
    setBusy(true);try{
      const data={text:text.trim(),referenceAssetIds:refs};
      if(pendingRequest.current?.fingerprint!==JSON.stringify(data))pendingRequest.current={fingerprint:JSON.stringify(data),requestId:crypto.randomUUID()};
      const r=await api(`/agents/sessions/${sessionId}/messages`,{method:'POST',body:JSON.stringify({...data,requestId:pendingRequest.current.requestId})});
      pendingRequest.current=null;setText('');await loadChat();if(r.status==='running'){setRunId(r.runId);connect(r.runId,sessionId);}
    }catch(e){notify(e.message,true);}finally{setBusy(false);}
  }
  async function saveProject(){setBusy(true);try{
    const {id,expectedRevision,...fields}=projectForm;
    const p=await api(id?`/agents/projects/${id}`:'/agents/projects',{method:id?'PATCH':'POST',body:JSON.stringify({...fields,...(id?{expectedRevision}:{})})});
    setProjects(v=>id?v.map(x=>x.id===p.id?p:x):[...v,p]);setProjectForm(null);setProjectId(p.id);notify('工程共用资料已保存');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  async function joinProject(){setBusy(true);try{
    const p=await api(`/agents/projects/${projectId}`,{method:'PATCH',body:JSON.stringify({name:project.name,brief:project.brief,decisions:project.decisions,entityIds:[...project.entityIds,entityId],expectedRevision:project.revision})});
    setProjects(v=>v.map(x=>x.id===p.id?p:x));notify('场景已加入工程');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  async function apply(){setBusy(true);try{
    await api(`/agents/proposals/${proposal.id}/apply`,{method:'POST',body:JSON.stringify({expectedContentHash:proposal.contentHash})});
    setRecord(await api(`/manage/entities/${entityId}/spatial`));setAck(false);await loadChat();onSaved();notify('提案已应用为空间草稿，请对照图片确认');
  }catch(e){notify(e.message,true);await loadChat();}finally{setBusy(false);}}
  async function confirmFacts(){setBusy(true);try{
    const r=await api(`/manage/entities/${entityId}/spatial/confirm`,{method:'POST',body:JSON.stringify({expectedVersionId:record.expectedVersionId,expectedContentHash:record.summary.contentHash,expectedEvidenceStateHash:record.evidenceStateHash,acknowledgeConsistency:true})});
    setRecord(r);setAck(false);onSaved();notify('场景固定空间已确认，可通过实体接口导出');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  const appliedCurrent=!!proposal?.appliedVersionId&&record?.expectedVersionId===proposal.appliedVersionId;
  return createPortal(<div className="scene-agent-backdrop"><section className="scene-agent-window" role="dialog" aria-modal="true" aria-label="场景空间助手">
    <header className="section-head"><div><h2>场景空间助手 · {workspace?.entity.name||'载入中'}</h2><p className="muted">与你讨论布局，形成草稿，确认后供视频使用。</p></div><button onClick={close}>关闭</button></header>
    <div className="scene-agent-grid">
      <aside className="scene-agent-context">
        <h3>工程共用资料</h3><label>当前工程<select value={projectId} disabled={working} onChange={e=>switchProject(e.target.value)}><option value="">请选择或新建工程</option>{projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
        <div className="card-actions"><button disabled={working} onClick={()=>{const f={...emptyProject,entityIds:[entityId]};setProjectForm(f);setProjectBase(JSON.stringify(f));}}>＋ 新建工程</button>{project&&<button disabled={working} onClick={()=>{const f={id:project.id,expectedRevision:project.revision,name:project.name,brief:project.brief,decisions:project.decisions,entityIds:project.entityIds};setProjectForm(f);setProjectBase(JSON.stringify(f));}}>编辑共用资料</button>}</div>
        {projectForm?<div className="agent-project-form">
          <label>工程名称<input value={projectForm.name} onChange={e=>setProjectForm({...projectForm,name:e.target.value})}/></label>
          <label>世界观、整体风格、创作约束<textarea rows={4} value={projectForm.brief} onChange={e=>setProjectForm({...projectForm,brief:e.target.value})}/></label>
          <label>已确定的创作决定<textarea rows={3} value={projectForm.decisions} onChange={e=>setProjectForm({...projectForm,decisions:e.target.value})}/></label>
          <details><summary>工程选用实体（{projectForm.entityIds.length}）</summary>{entities.map(e=><label className="transcript-confirm" key={e.id}><input type="checkbox" checked={projectForm.entityIds.includes(e.id)} onChange={event=>setProjectForm({...projectForm,entityIds:event.target.checked?[...projectForm.entityIds,e.id]:projectForm.entityIds.filter(x=>x!==e.id)})}/>{e.name}</label>)}</details>
          <div className="card-actions"><button className="primary" disabled={busy||!projectForm.name.trim()} onClick={saveProject}>保存工程</button><button disabled={busy} onClick={()=>setProjectForm(null)}>取消</button></div>
        </div>:project?<><p className="entity-text">{project.brief||'尚无工程说明。'}</p>{project.decisions&&<p className="entity-text"><b>创作决定：</b>{project.decisions}</p>}<p className="muted">共用 {project.entityIds.length} 个实体的资料。</p>{!project.entityIds.includes(entityId)&&<button disabled={busy} onClick={joinProject}>将此场景加入工程</button>}</>:<p className="muted">建立一个工程，共用设定并保存讨论。</p>}
        <h3>核对参考图</h3><p className="muted">本轮选 {refs.length}/8 张；优先包含当前主形象。</p>
        <div className="agent-image-grid">{images.map(a=><label key={a.id} className={refs.includes(a.id)?'selected':''}><img src={a.url} alt={a.name} loading="lazy"/><span><input type="checkbox" disabled={working||(!refs.includes(a.id)&&refs.length>=8)} checked={refs.includes(a.id)} onChange={e=>setRefs(e.target.checked?[...refs,a.id]:refs.filter(v=>v!==a.id))}/>{a.id===workspace.visualState?.appearance?.assetId?'当前主形象':a.name}</span></label>)}</div>
        {!images.length&&<p className="muted">请先导入或生成场景参考图。</p>}
      </aside>
      <section className="scene-agent-conversation">
        <div className="agent-session-controls"><h3>空间讨论</h3><label>已保存对话<select value={sessionId} disabled={working} onChange={e=>{if(text.trim()&&!confirm('放弃未发送文字并切换对话？'))return;setText('');setSessionId(e.target.value);}}><option value="">新建对话后开始</option>{sessions.map((s,i)=><option value={s.id} key={s.id}>{new Date(s.createdAt).toLocaleString('zh-CN')} · {s.modelId}</option>)}</select></label>
          <div className="agent-model-row"><select aria-label="新对话模型" value={model} disabled={working} onChange={e=>setModel(e.target.value)}>{cap?.models.map(m=><option key={m.provider+'/'+m.id} value={JSON.stringify([m.provider,m.id])}>{m.provider} · {m.name}</option>)}</select><button disabled={working||projectDirty||!project?.entityIds.includes(entityId)||!model} onClick={startNewSession}>新建对话</button></div>
          {chat&&<small className="muted">当前：{chat.provider} · {chat.modelId}</small>}{cap?.configurationIssue&&<p className="agent-notice">{cap.configurationIssue}</p>}
        </div>
        <div className="agent-chat-log" aria-live="polite">{!chat?.messages.length&&<p className="muted">例如：“这个图书馆需要拍入口到书架的移动，请帮我整理布局，先问不确定的地方。”</p>}
          {chat?.messages.map(m=><article key={m.id} className={'agent-message '+m.role}><b>{m.role==='user'?'你':'场景助手'}</b><p>{m.text||(runId?'正在整理…':'未产生完整回复')}</p></article>)}
          {chat?.runs.filter(r=>['failed','interrupted','cancelled'].includes(r.status)).map(r=><p key={r.id} className="agent-notice">{statusName[r.status]}：{r.error||'可继续讨论，先前资料仍保留。'}</p>)}<div ref={bottom}/>
        </div>
        <div className="agent-composer">{phase&&<p className="muted">{phase}</p>}<textarea aria-label="与场景助手讨论" rows={3} value={text} disabled={busy} placeholder="描述用途、补充布局，或指出草稿需要修改的地方…" onChange={e=>setText(e.target.value)}/><div className="card-actions"><button className="primary" disabled={working||projectDirty||!sessionId||!text.trim()||!refs.length||!project?.entityIds.includes(entityId)} onClick={send}>发送</button>{runId&&<button onClick={()=>{void api(`/agents/runs/${runId}/cancel`,{method:'POST',body:'{}'}).catch(e=>notify(e.message,true));}}>停止回复</button>}</div></div>
      </section>
      <aside className="scene-agent-proposal"><h3>空间提案</h3>
        {!!proposals.length&&<select aria-label="空间提案版本" value={proposal?.id||''} onChange={e=>{setProposalId(e.target.value);setAck(false);}}>{proposals.map((p,i)=><option value={p.id} key={p.id}>提案 {i+1}{p.appliedVersionId?' · 已应用':''}{p.stale?' · 资料已变化':''}</option>)}</select>}
        {!proposal?<p className="muted">助手提出布局后，锚点、修改差异和待补充问题会显示在这里。</p>:<>
          <p className="entity-text">{proposal.summary}</p>{proposal.stale&&<p className="agent-notice">依据资料已变化，请继续讨论生成新提案。</p>}
          <p className="entity-text"><b>方向基准：</b>{proposal.document.frame.description||'待补充'} {proposal.document.frame.status==='pending'&&'（待补充）'}</p>
          {proposal.document.elements.map(e=><article className="spatial-summary" key={e.id}><b>{e.label}</b> <span className="pill">{e.status==='known'?'有依据':'待补充'}</span><p>{e.description}</p>{[['position','位置'],['orientation','朝向'],['scale','尺度']].map(([key,name])=>e[key]&&<p key={key}>{name}：{e[key]}</p>)}<details><summary>来源与引用标识</summary><code>{entityId}#{e.id}</code>{proposal.sources.filter(s=>s.target==='elements/'+e.id).map((s,i)=><p key={i}>{sourceName[s.kind]}：{s.explanation}</p>)}</details></article>)}
          {(proposal.document.links.length>0||proposal.document.routes.length>0)&&<details open><summary>空间关系与通路</summary>{proposal.document.links.map(l=><p key={l.id}>{proposal.document.elements.find(e=>e.id===l.from)?.label} → {proposal.document.elements.find(e=>e.id===l.to)?.label}：{l.description}{l.status==='pending'?'（待补充）':''}</p>)}{proposal.document.routes.map(r=><p key={r.id}>{r.label}：{r.via.map(v=>proposal.document.elements.find(e=>e.id===v)?.label).join(' → ')}；{r.description}{r.status==='pending'?'（待补充）':''}</p>)}</details>}
          <details><summary>与当前保存资料的差异（{proposal.changes.length}）</summary>{proposal.changes.map((c,i)=><p key={i}>{c}</p>)}</details>
          {(proposal.questions.length>0||proposal.document.unknowns.length>0)&&<div className="agent-notice"><b>待讨论／待补充</b>{[...new Set([...proposal.questions,...proposal.document.unknowns])].map((q,i)=><p key={i}>{q}</p>)}</div>}
          <button className="primary" disabled={working||proposal.stale||!!proposal.appliedVersionId||chat?.runs.find(r=>r.id===proposal.runId)?.status!=='succeeded'} onClick={apply}>{proposal.appliedVersionId?'已应用为空间草稿':'应用为空间草稿'}</button>
          {appliedCurrent&&<div className="agent-confirm"><label className="transcript-confirm"><input type="checkbox" disabled={working} checked={ack} onChange={e=>setAck(e.target.checked)}/>我已核对这份文字与所选参考图一致；未确定内容保留待补充。</label><button disabled={working||!ack} onClick={confirmFacts}>确认固定空间供视频使用</button></div>}
          {record?.summary.status==='confirmed'&&<p className="muted">当前保存空间已确认，视频工具可通过实体导出接口读取。</p>}
        </>}
      </aside>
    </div>
  </section></div>,document.body);
}
