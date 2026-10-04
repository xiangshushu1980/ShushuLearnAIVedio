// Owner: Sean — PC scene assistant: common project context, reference images, conversation and review.
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import './scene-agent.css';
import {RelationChangeProposal} from './RelationChangeProposal.jsx';
import {EntityChangeProposal} from './EntityChangeProposal.jsx';
import {ImageReviewFeedback} from './ImageReviewFeedback.jsx';

const statusName={running:'正在回复',succeeded:'已结束',failed:'未完成',cancelled:'已取消',interrupted:'服务中断'};
const sourceName={image:'参考图观察',user:'用户补充',existing:'已有设定'};
export function SceneAgentPanel({entityId=null,projectId:inheritedProjectId,purpose='scene-spatial',initialText='',initialReferenceIds=[],api,notify,onClose,onSaved=()=>{},onDirtyChange}) {
  const [projects,setProjects]=useState([]),projectId=inheritedProjectId,spatialMode=purpose==='scene-spatial';
  const [projectImages,setProjectImages]=useState([]),[workspace,setWorkspace]=useState(null),[record,setRecord]=useState(null),[cap,setCap]=useState(null);
  const [refs,setRefs]=useState([]),[model,setModel]=useState(''),[sessions,setSessions]=useState([]),[sessionId,setSessionId]=useState(''),[chat,setChat]=useState(null);
  const [text,setText]=useState(initialText),[busy,setBusy]=useState(false),[runId,setRunId]=useState(''),[phase,setPhase]=useState(''),[ack,setAck]=useState(false),[proposalId,setProposalId]=useState('');
  const generation=useRef(0),bottom=useRef(null),stream=useRef(null),pendingRequest=useRef(null);
  const project=projects.find(p=>p.id===projectId),memberReady=!!project&&(!entityId||project.entityIds.includes(entityId));
  const working=!!runId||busy,dirty=!!text.trim()||working;
  const images=entityId?(workspace?.assets.filter(a=>a.mediaType==='image')||[]):projectImages;
  const proposals=spatialMode?(chat?.proposals||[]):(chat?.projectProposals||[]),proposal=proposals.find(p=>p.id===proposalId)||proposals.at(-1);
  useEffect(()=>{onDirtyChange?.(dirty);},[dirty,onDirtyChange]);
  useEffect(()=>{const warn=e=>{if(dirty){e.preventDefault();e.returnValue='';}};addEventListener('beforeunload',warn);return()=>removeEventListener('beforeunload',warn);},[dirty]);
  useEffect(()=>()=>onDirtyChange?.(false),[onDirtyChange]);
  useEffect(()=>{let gone=false;generation.current++;
    Promise.all([api('/projects'),api('/agents/capabilities'),entityId?api(`/entities/${entityId}/workspace`):Promise.resolve(null),spatialMode&&entityId?api(`/manage/entities/${entityId}/spatial`):Promise.resolve(null),!entityId&&projectId?api(`/projects/${projectId}/context`):Promise.resolve(null)]).then(([p,c,w,r,ctx])=>{
      if(gone)return;setProjects(p.projects);setCap(c);setWorkspace(w);setRecord(r);const shared=ctx?.entities.flatMap(e=>e.images.map(a=>({id:a.assetId,name:e.name+' · '+a.name,url:`/api/assets/${a.assetId}/content`,mediaType:'image'})))||[];setProjectImages(shared);
      setModel(c.models[0]?JSON.stringify([c.models[0].provider,c.models[0].id]):'');
      const available=new Set(entityId?(w?.assets.filter(a=>a.mediaType==='image').map(a=>a.id)||[]):shared.map(a=>a.id));
      const defaults=[...initialReferenceIds,w?.visualState?.appearance?.assetId,...(r?.document.referenceAssetIds||[])].filter(v=>v&&available.has(v));
      setRefs([...new Set(defaults.length?defaults:w?.assets.filter(a=>a.mediaType==='image').slice(0,1).map(a=>a.id)||[])].slice(0,8));
    }).catch(e=>notify(e.message,true));
    return()=>{gone=true;generation.current++;stream.current?.close();};
  },[entityId,projectId,purpose]);
  useEffect(()=>{
    if(!projectId){setSessions([]);setSessionId('');setChat(null);return;}
    localStorage.setItem('sean.reference.agentProject',projectId);
    let gone=false;setSessionId('');setChat(null);setSessions([]);setProposalId('');
    api(`/agents/projects/${projectId}/sessions?purpose=${purpose}${entityId?'&entityId='+entityId:''}`).then(r=>{if(!gone){setSessions(r.sessions);setSessionId(r.sessions[0]?.id||'');}}).catch(e=>notify(e.message,true));
    return()=>{gone=true;};
  },[projectId,entityId,purpose]);
  useEffect(()=>{
    let gone=false;generation.current++;stream.current?.close();setChat(null);setRunId('');setPhase('');setProposalId('');setAck(false);
    if(sessionId)api(`/agents/sessions/${sessionId}`).then(c=>{
      if(gone)return;setChat(c);const running=c.runs.find(r=>r.status==='running');if(running){setRunId(running.id);connect(running.id,sessionId);}
    }).catch(e=>notify(e.message,true));
    return()=>{gone=true;generation.current++;stream.current?.close();};
  },[sessionId]);
  useEffect(()=>{bottom.current?.scrollIntoView({block:'nearest'});},[chat?.messages.at(-1)?.text,phase]);
  function close(){if(dirty&&!confirm(working?'助手仍在回复，关闭后可重新打开继续查看。关闭窗口？':'有未发送的文字或工程修改，放弃并关闭？'))return;onClose();}
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
    if(!memberReady||!model)return;
    setBusy(true);try{const [provider,modelId]=JSON.parse(model);const c=await api('/agents/sessions',{method:'POST',body:JSON.stringify({projectId,entityId,purpose,provider,modelId})});
      setSessions(v=>[{id:c.id,provider:c.provider,modelId:c.modelId,createdAt:c.createdAt},...v]);setSessionId(c.id);
    }catch(e){notify(e.message,true);}finally{setBusy(false);}
  }
  async function send(){
    if(!text.trim()||!sessionId||(spatialMode&&!refs.length)||working)return;
    setBusy(true);try{
      const data={text:text.trim(),referenceAssetIds:refs};
      if(pendingRequest.current?.fingerprint!==JSON.stringify(data))pendingRequest.current={fingerprint:JSON.stringify(data),requestId:crypto.randomUUID()};
      const r=await api(`/agents/sessions/${sessionId}/messages`,{method:'POST',body:JSON.stringify({...data,requestId:pendingRequest.current.requestId})});
      pendingRequest.current=null;setText('');await loadChat();if(r.status==='running'){setRunId(r.runId);connect(r.runId,sessionId);}
    }catch(e){notify(e.message,true);}finally{setBusy(false);}
  }
  function feedbackFollowup(message,assetIds){if(text.trim()&&!confirm('替换未发送文字为报告修订要求？'))return;setText(message);setRefs(assetIds.filter(a=>images.some(im=>im.id===a)).slice(0,8));notify('修订要求已填写，请检查选图后发送');}
  async function applyRelationChange(proposal){setBusy(true);try{await api(`/agents/relation-proposals/${proposal.id}/apply`,{method:'POST',body:JSON.stringify({expectedContentHash:proposal.contentHash,acknowledgeUpdate:true})});await loadChat();onSaved();notify('关系内容已更新；请重新检查相关设定和图片步骤');}catch(e){notify(e.message,true);await loadChat();}finally{setBusy(false);}}
  async function applyEntityChange(proposal){setBusy(true);try{await api(`/agents/entity-proposals/${proposal.id}/apply`,{method:'POST',body:JSON.stringify({expectedContentHash:proposal.contentHash,acknowledgeUpdate:true})});await loadChat();if(entityId)setWorkspace(await api(`/entities/${entityId}/workspace`));onSaved();notify('实体文字已更新；请核对相关图片步骤和空间设定');}catch(e){notify(e.message,true);await loadChat();}finally{setBusy(false);}}
  async function apply(){setBusy(true);try{
    await api(`/agents/${spatialMode?'proposals':'project-proposals'}/${proposal.id}/apply`,{method:'POST',body:JSON.stringify({expectedContentHash:proposal.contentHash})});
    if(spatialMode)setRecord(await api(`/manage/entities/${entityId}/spatial`));else setProjects((await api('/projects')).projects);setAck(false);await loadChat();onSaved();notify(spatialMode?'提案已应用为空间草稿，请对照图片确认':'项目设定修改已应用');
  }catch(e){notify(e.message,true);await loadChat();}finally{setBusy(false);}}
  async function confirmFacts(){setBusy(true);try{
    const r=await api(`/manage/entities/${entityId}/spatial/confirm`,{method:'POST',body:JSON.stringify({expectedVersionId:record.expectedVersionId,expectedContentHash:record.summary.contentHash,expectedEvidenceStateHash:record.evidenceStateHash,acknowledgeConsistency:true})});
    setRecord(r);setAck(false);onSaved();notify('场景固定空间已确认，可通过实体接口导出');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  const projectReports=chat?.projectProposals||[];
  const appliedCurrent=!!proposal?.appliedVersionId&&record?.expectedVersionId===proposal.appliedVersionId;
  return createPortal(<div className="scene-agent-backdrop"><section className="scene-agent-window" role="dialog" aria-modal="true" aria-label={spatialMode?'场景空间助手':'项目创作助手'}>
    <header className="section-head"><div><h2>{spatialMode?'场景空间助手':'项目创作助手'} · {workspace?.entity.name||project?.name||'载入中'}</h2><p className="muted">继承当前项目设定；每轮读取最新实体资料，讨论与事实分别保存。</p></div><button onClick={close}>关闭</button></header>
    <div className="scene-agent-grid">
      <aside className="scene-agent-context">
        <h3>当前项目 · {project?.name||'未选择'}</h3>
        {project?<>{[['brief','项目介绍'],['synopsis','故事梗概'],['worldRules','世界规则'],['visualStyle','风格规则'],['decisions','已确定决定']].map(([k,label])=><details key={k} open={k==='brief'}><summary>{label}</summary><p className="entity-text">{project[k]||'待补充，不会由助手静默推测。'}</p></details>)}<p className="muted">共用 {project.entityIds.length} 个实体及其剧情作用、设定和剧情关系。项目资料请在“项目工作区”编辑。</p>{!memberReady&&<p className="agent-notice">当前实体尚未加入此项目，请先在项目工作区加入。</p>}</>:<p className="agent-notice">请先在项目工作区选择项目，再打开助手。</p>}
        <h3>核对参考图</h3><p className="muted">{spatialMode?'空间布局需要图片依据。':'文字讨论无需选图。'}本轮选 {refs.length}/8 张；优先包含当前主形象。</p>
        <div className="agent-image-grid">{images.map(a=><label key={a.id} className={refs.includes(a.id)?'selected':''}><img src={a.url} alt={a.name} loading="lazy"/><span><input type="checkbox" disabled={working||(!refs.includes(a.id)&&refs.length>=8)} checked={refs.includes(a.id)} onChange={e=>setRefs(e.target.checked?[...refs,a.id]:refs.filter(v=>v!==a.id))}/>{a.id===workspace?.visualState?.appearance?.assetId?'当前主形象':a.name}</span></label>)}</div>
        {!images.length&&<p className="muted">{spatialMode?'请先导入或生成场景参考图。':'项目讨论不要求选图；打开实体助手后可选择该实体参考图。'}</p>}
      </aside>
      <section className="scene-agent-conversation">
        <div className="agent-session-controls"><h3>{spatialMode?'空间讨论':'创作讨论'}</h3><label>已保存对话<select value={sessionId} disabled={working} onChange={e=>{if(text.trim()&&!confirm('放弃未发送文字并切换对话？'))return;setText('');setSessionId(e.target.value);}}><option value="">新建对话后开始</option>{sessions.map((s,i)=><option value={s.id} key={s.id}>{new Date(s.createdAt).toLocaleString('zh-CN')} · {s.modelId}</option>)}</select></label>
          <div className="agent-model-row"><select aria-label="新对话模型" value={model} disabled={working} onChange={e=>setModel(e.target.value)}>{cap?.models.map(m=><option key={m.provider+'/'+m.id} value={JSON.stringify([m.provider,m.id])}>{m.provider} · {m.name}</option>)}</select><button disabled={working||!memberReady||!model} onClick={startNewSession}>新建对话</button></div>
          {chat&&<small className="muted">当前：{chat.provider} · {chat.modelId}</small>}{cap?.configurationIssue&&<p className="agent-notice">{cap.configurationIssue}</p>}
        </div>
        <div className="agent-chat-log" aria-live="polite">{!chat?.messages.length&&<p className="muted">{spatialMode?'例如：这个图书馆需要拍入口到书架的移动，请帮我整理布局，先问不确定的地方。':'例如：请根据故事设定，讨论主角与这件武器的关系，并检查现有实体有无矛盾。'}</p>}
          {chat?.messages.map(m=><article key={m.id} className={'agent-message '+m.role}><b>{m.role==='user'?'你':'创作助手'}</b><p>{m.text||(runId?'正在整理…':'未产生完整回复')}</p></article>)}
          {chat?.runs.filter(r=>['failed','interrupted','cancelled'].includes(r.status)).map(r=><p key={r.id} className="agent-notice">{statusName[r.status]}：{r.error||'可继续讨论，先前资料仍保留。'}</p>)}<div ref={bottom}/>
        </div>
        <div className="agent-composer">{phase&&<p className="muted">{phase}</p>}<textarea aria-label={spatialMode?'与场景助手讨论':'与项目助手讨论'} rows={3} value={text} disabled={busy} placeholder={spatialMode?'描述用途、补充布局，或指出草稿需要修改的地方…':'讨论项目设定、人物关系与形象，或检查项目一致性…'} onChange={e=>setText(e.target.value)}/><div className="card-actions"><button className="primary" disabled={working||!sessionId||!text.trim()||(spatialMode&&!refs.length)||!memberReady} onClick={send}>发送</button>{runId&&<button onClick={()=>{void api(`/agents/runs/${runId}/cancel`,{method:'POST',body:'{}'}).catch(e=>notify(e.message,true));}}>停止回复</button>}</div></div>
      </section>
      <aside className="scene-agent-proposal">{chat?.relationProposals?.map(p=><RelationChangeProposal key={p.id} proposal={p} disabled={working||chat?.runs.find(r=>r.id===p.runId)?.status!=='succeeded'} onApply={applyRelationChange}/>)}{chat?.entityProposals?.map(p=><EntityChangeProposal key={p.id} proposal={p} disabled={working||chat?.runs.find(r=>r.id===p.runId)?.status!=='succeeded'} onApply={applyEntityChange}/>)}{chat?.stepRevisions?.map(s=><article className="spatial-summary" key={s.id}><h4>图片步骤修订 · {s.entityName} · {s.label}</h4><p>版本 {s.version} · {s.revisionStatus==='current'?'当前选用':s.revisionStatus==='proposal'?'待审阅':'历史版本'}</p><p>{s.reason}</p>{s.feedback&&<p className="muted">依据检验：{s.feedback.summary} · {s.feedback.assets.length} 张结果图片</p>}{s.stale&&<p>实体资料已变化，需基于最新资料继续修订。</p>}<button onClick={close}>返回工作区比较并采用</button></article>)}{chat?.authoringPlans?.map(p=><article className="spatial-summary" key={p.id}><h4>实体创作方案 · {p.title}</h4><p>{p.summary}</p><small>{p.candidateCount} 个候选{p.stale?' · 来源已变化':p.applied?' · 已应用':' · 待审阅'}</small><p>在项目工作区下方「实体创作工作流」查看、调整并应用。</p><button onClick={close}>返回工作区审阅</button></article>)}{spatialMode&&projectReports.map(p=><article className="spatial-summary" key={p.id}><h4>项目检查意见</h4><p>{p.summary}</p>{p.conclusion&&<p><b>{{consistent:'已检查范围内一致',conflicts:'发现冲突',inconclusive:'证据不足，暂不能判断'}[p.conclusion]}</b> · 实际检查 {p.reviewedAssetIds.length} 张图</p>}{p.coverage&&<p className="muted">完整文字已读 {p.coverage.reviewedEntityIds.length}/{p.coverage.projectEntityCount} 个实体；{(p.coverage.entityCoverage==='complete'||(!p.coverage.entityCoverage&&p.coverage.reviewedEntityIds.length===p.coverage.projectEntityCount))?'本轮全部实体文字已读，报告仍是审阅意见。':'其余只读取索引摘要，不能代表全部实体已检查。'}选图不代表已完成图文核验。</p>}{p.relationSources?.length>0&&<details><summary>关系检查依据（{p.relationSources.length}）</summary>{p.relationSources.map(r=><p key={r.relationId}>{r.sourceName} → {r.targetName} · {r.type} · {{'entity-setting':'实体设定关系','project-story':'本项目剧情关系','legacy-unassigned-story':'历史关系，未分配项目'}[r.scope]}<br/>{r.description}<br/><small>{r.relationId}</small></p>)}</details>}{p.stale&&<p className="agent-notice">依据已更新，请重新检查。</p>}{p.issues?.map((v,i)=><p key={i}>{v.description}；{v.suggestion}</p>)}{p.kind==='update'&&<p>请在项目创作模式中讨论并应用此类项目修改。</p>}</article>)}<h3>{spatialMode?'空间提案':'检查报告与设定建议'}</h3>
        {!!proposals.length&&<select aria-label="空间提案版本" value={proposal?.id||''} onChange={e=>{setProposalId(e.target.value);setAck(false);}}>{proposals.map((p,i)=><option value={p.id} key={p.id}>提案 {i+1}{p.appliedVersionId?' · 已应用':''}{p.stale?' · 资料已变化':''}</option>)}</select>}
        {!spatialMode?<>{!proposals.length&&<p className="muted">可讨论项目设定，或要求检查世界规则、实体与关系的一致性。实体文字修改由提案预览后接受；也可在实体详情中编辑。</p>}{proposals.map(p=><article key={p.id} className="spatial-summary"><h4>{p.kind==='image-review'?'图片逻辑一致性报告':p.kind==='review'?'一致性检查报告':'项目资料修改建议'}</h4><p>{p.summary}</p>{p.conclusion&&<p><b>{{consistent:'已检查范围内一致',conflicts:'发现冲突',inconclusive:'证据不足，暂不能判断'}[p.conclusion]}</b> · 实际检查 {p.reviewedAssetIds.length} 张图</p>}{p.coverage&&<p className="muted">完整文字已读 {p.coverage.reviewedEntityIds.length}/{p.coverage.projectEntityCount} 个实体；{(p.coverage.entityCoverage==='complete'||(!p.coverage.entityCoverage&&p.coverage.reviewedEntityIds.length===p.coverage.projectEntityCount))?'本轮全部实体文字已读，报告仍是审阅意见。':'其余只读取索引摘要，不能代表全部实体已检查。'}选图不代表已完成图文核验。</p>}{p.relationSources?.length>0&&<details><summary>关系检查依据（{p.relationSources.length}）</summary>{p.relationSources.map(r=><p key={r.relationId}>{r.sourceName} → {r.targetName} · {r.type} · {{'entity-setting':'实体设定关系','project-story':'本项目剧情关系','legacy-unassigned-story':'历史关系，未分配项目'}[r.scope]}<br/>{r.description}<br/><small>{r.relationId}</small></p>)}</details>}{p.stale&&<p className="agent-notice">项目资料已更新；此意见依据旧版本，请重新检查。</p>}{p.issues?.map((issue,i)=><div key={i}><b>{{conflict:'资料冲突',missing:'待补充',suggestion:'设计建议'}[issue.category]}</b><p>{issue.description}</p><small>{issue.entityIds.join('、')}</small><p>{issue.suggestion}</p></div>)}{p.kind==='image-review'&&<ImageReviewFeedback report={p} disabled={working||chat?.runs.find(r=>r.id===p.runId)?.status!=='succeeded'} onFollowup={feedbackFollowup}/>}{p.kind==='review'&&!p.issues?.length&&<p className="muted">在本次读取的文字范围内未列出问题；这不是完整审核结论。</p>}{p.changes&&<>{Object.entries(p.changes).map(([k,v])=><details open key={k}><summary>{{brief:'项目介绍',synopsis:'故事梗概',worldRules:'世界规则',visualStyle:'风格规则',decisions:'已确定决定'}[k]}</summary><p className="entity-text"><b>当前：</b>{project?.[k]||'空'}</p><p className="entity-text"><b>建议改为：</b>{v}</p></details>)}<button disabled={working||p.stale||!!p.appliedRevision||chat?.runs.find(r=>r.id===p.runId)?.status!=='succeeded'} onClick={()=>{setProposalId(p.id);void (async()=>{setBusy(true);try{await api(`/agents/project-proposals/${p.id}/apply`,{method:'POST',body:JSON.stringify({expectedContentHash:p.contentHash})});setProjects((await api('/projects')).projects);await loadChat();onSaved();notify('项目设定已更新');}catch(e){notify(e.message,true);}finally{setBusy(false);}})();}}>{p.appliedRevision?'已应用':'接受并应用项目修改'}</button></>}</article>)}</>:!proposal?<p className="muted">助手提出布局后，锚点、修改差异和待补充问题会显示在这里。</p>:<>
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
