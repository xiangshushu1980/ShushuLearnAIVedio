// Owner: Sean — one PC workspace for flags, entity profiles, derivation and two relation categories.
import React, { useEffect, useState } from 'react';
import { SceneAgentPanel } from './SceneAgentPanel.jsx';
import { SceneImageSetEditor } from './SceneImageSetEditor.jsx';
import { EntitySpatialEditor } from './EntitySpatialEditor.jsx';
const emptyProfile = { name: '', flags: [], description: '', appearance: '', voiceDescription: '' };
const relationTypes = { setting: ['穿着','使用','拥有','掌握','使用时显现','位于'], story: ['同伴','敌对','合作','师徒','亲属','相识'] };
export function EntityManager({ projectId=null, api, notify, onOpenCreate, onDirtyChange, onSelect, initialEntityId }) {
  const [list,setList]=useState({entities:[],flags:[]}),[all,setAll]=useState([]),[selected,setSelected]=useState(initialEntityId || new URLSearchParams(location.search).get('entity') || ''),[detail,setDetail]=useState(null);
  const [query,setQuery]=useState(''),[filter,setFilter]=useState([]),[match,setMatch]=useState('all'),[busy,setBusy]=useState(false);
  const [editing,setEditing]=useState(false),[creating,setCreating]=useState(false),[form,setForm]=useState(emptyProfile),[saved,setSaved]=useState('');
  const [spatialDirty,setSpatialDirty]=useState(false),[imageSetDirty,setImageSetDirty]=useState(false),[project,setProject]=useState(null),[projectRole,setProjectRole]=useState(null),[roleForm,setRoleForm]=useState(null),[storyRelations,setStoryRelations]=useState([]),[assistant,setAssistant]=useState(false),[agentDirty,setAgentDirty]=useState(false);
  const listPath=projectId?`/projects/${projectId}/entities`:'/manage/entities';
  const [flagInput,setFlagInput]=useState(''),[category,setCategory]=useState('setting'),[relation,setRelation]=useState(null),[derive,setDerive]=useState(null),[zoom,setZoom]=useState(null);
  useEffect(()=>{if(selected&&!creating){onSelect(selected);const url=new URL(location.href);url.searchParams.set('entity',selected);url.searchParams.set('view',projectId?'manage':'library');history.replaceState(null,'',url);}},[selected,creating,onSelect]);
  const dirty=editing&&JSON.stringify(form)!==saved || !!relation || !!derive || spatialDirty || imageSetDirty || agentDirty || !!roleForm;
  useEffect(()=>{onDirtyChange(!!dirty);},[dirty,onDirtyChange]);
  useEffect(()=>{const warn=e=>{if(dirty){e.preventDefault();e.returnValue='';}};addEventListener('beforeunload',warn);return()=>removeEventListener('beforeunload',warn);},[dirty]);
  useEffect(()=>{const escape=e=>{if(e.key==='Escape')setZoom(null);};addEventListener('keydown',escape);return()=>removeEventListener('keydown',escape);},[]);
  async function loadList() {
    const [value,full]=await Promise.all([api(`${listPath}?q=${encodeURIComponent(query)}&flags=${encodeURIComponent(filter.join(','))}&match=${match}`),api(listPath)]);
    setList(value);setAll(full.entities);if(full.project)setProject(full.project);if((!selected||!full.entities.some(e=>e.id===selected))&&!creating)setSelected(value.entities[0]?.id||'');
  }
  useEffect(()=>{let disposed=false;Promise.all([api(`${listPath}?q=${encodeURIComponent(query)}&flags=${encodeURIComponent(filter.join(','))}&match=${match}`),api(listPath)]).then(([value,full])=>{
    if(disposed)return;setList(value);setAll(full.entities);if(full.project)setProject(full.project);if((!selected||!full.entities.some(e=>e.id===selected))&&!creating)setSelected(value.entities[0]?.id||'');
  }).catch(e=>notify(e.message,true));return()=>{disposed=true;};},[query,filter.join(','),match,projectId]);
  async function loadProject(){if(!projectId)return;const [p,r]=await Promise.all([api(`/projects/${projectId}`),api(`/projects/${projectId}/relations`)]);setProject(p);setStoryRelations(r.relations);if(selected&&p.entityIds.includes(selected)){const v=await api(`/projects/${projectId}/entities/${selected}/role`);setProjectRole(v.projectRole);}}
  useEffect(()=>{if(!selected||creating)return;let disposed=false;setDetail(null);setRoleForm(null);setProjectRole(null);
    Promise.all([api(`/manage/entities/${selected}`),projectId?api(`/projects/${projectId}/entities/${selected}/role`):Promise.resolve(null),projectId?api(`/projects/${projectId}/relations`):Promise.resolve(null)]).then(([value,pr,sr])=>{if(!disposed){setDetail(value);setForm(value.profile);setSaved(JSON.stringify(value.profile));if(pr){setProject(pr.project);setProjectRole(pr.projectRole);}setStoryRelations(sr?.relations||[]);}}).catch(e=>notify(e.message,true));return()=>{disposed=true;};},[selected,creating,projectId]);
  async function saveRole(){setBusy(true);try{await api(`/projects/${projectId}/entities/${selected}/role`,{method:'PUT',body:JSON.stringify({...roleForm,expectedRevision:project.revision})});setRoleForm(null);await loadProject();notify('当前项目的剧情作用已保存');}catch(e){notify(e.message,true);if(e.status===409)await loadProject().catch(()=>{});}finally{setBusy(false);}}
  function abandon(){return !dirty||confirm('当前有未保存的资料、关系或派生设置，放弃修改？');}
  function choose(id){if(!abandon())return;setSpatialDirty(false);setEditing(false);setCreating(false);setRelation(null);setDerive(null);setRoleForm(null);if(projectId&&!all.some(e=>e.id===id)){notify('关联实体在资料库中，尚未加入当前项目。请先从项目工作区加入。',true);return;}setSelected(id);}
  function patch(values){setForm(f=>({...f,...values}));}
  function newEntity(){if(!abandon())return;setSpatialDirty(false);setCreating(true);setEditing(true);setDetail(null);setForm({...emptyProfile});setSaved(JSON.stringify(emptyProfile));setRelation(null);setDerive(null);setRoleForm(null);}
  async function saveProfile(){setBusy(true);try{
    const payload={...form,...(!creating?{expectedRevision:detail.revision}:{})};
    const value=await api(creating?listPath:`/manage/entities/${selected}`,{method:creating?'POST':'PATCH',body:JSON.stringify(creating&&projectId?{profile:payload,expectedRevision:project.revision}:payload)});
    setDetail(value);setSelected(value.entity.id);setCreating(false);setEditing(false);setSaved(JSON.stringify(value.profile));setForm(value.profile);await loadList();notify('实体资料已保存');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  async function saveRelation(){setBusy(true);try{
    if(projectId&&category==='story'){
      await api(`/projects/${projectId}/relations${relation.relationId?'/'+relation.relationId:''}`,{method:relation.relationId?'PATCH':'POST',body:JSON.stringify({sourceEntityId:relation.sourceEntityId||selected,targetEntityId:relation.targetEntityId,type:relation.type,description:relation.description,expectedRevision:project.revision})});await loadProject();
    }else{const value=await api(`/manage/entities/${selected}/relations${relation.relationId?'/'+relation.relationId:''}`,{method:relation.relationId?'PATCH':'POST',body:JSON.stringify({targetEntityId:relation.targetEntityId,category:relation.category,type:relation.type,description:relation.description,...(relation.relationId?{expectedUpdatedAt:relation.updatedAt}:{})})});setDetail(value);}
    setRelation(null);notify('关系已保存');
  }catch(e){notify(e.message,true);if(projectId)await loadProject().catch(()=>{});}finally{setBusy(false);}}
  async function removeRelation(row){if(!confirm('解除这条关系？实体和素材仍会保留。'))return;setBusy(true);try{
    if(projectId&&category==='story'){await api(`/projects/${projectId}/relations/${row.relationId}`,{method:'DELETE',body:JSON.stringify({expectedRevision:project.revision})});await loadProject();}
    else setDetail(await api(`/manage/entities/${selected}/relations/${row.relationId}`,{method:'DELETE',body:JSON.stringify({expectedUpdatedAt:row.updatedAt})}));notify('关系已解除');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  async function createDerived(){setBusy(true);try{
    const payload={name:derive.name,flags:detail.profile.flags,description:'',appearance:'',voiceDescription:'',changes:derive.changes,copyProfile:derive.copyProfile,copyReference:derive.copyReference,reuseVoice:derive.reuseVoice,copySettingRelations:derive.copySettingRelations,expectedBaseRevision:detail.revision};
    const value=await api(projectId?`/projects/${projectId}/entities/${selected}/derive`:`/manage/entities/${selected}/derive`,{method:'POST',body:JSON.stringify(projectId?{profile:payload,expectedRevision:project.revision}:payload)});
    setDerive(null);setSelected(value.entity.id);setDetail(value);setEditing(false);setCreating(false);await loadList();notify('派生实体已创建，资料和素材独立保存');
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  function openCreate(tab='settings'){if(!abandon())return;onOpenCreate(selected,tab);}
  const v=detail?.visualState,voice=detail?.voiceState.current;
  const visibleRelations=projectId&&category==='story'?storyRelations.filter(r=>r.sourceEntityId===selected||r.targetEntityId===selected):detail?.relations.filter(r=>r.category===category)||[];
  return <main className="entity-management">
    <div className="page-title"><div><h1>{projectId?(project?.name||'载入项目')+' · 项目实体':'实体资料库'}</h1><p>用 flag 组织资料，管理独立形象、声音、设定和剧情关系。</p></div></div>
    <div className="entity-management-grid">
      <aside className="entity-browser panel"><div className="section-head"><h2>实体</h2><button className="primary" onClick={newEntity} disabled={busy}>＋ 新建</button></div>
        <label>搜索<input placeholder="名称、介绍或 flag" value={query} onChange={e=>setQuery(e.target.value)} /></label>
        <div className="entity-flag-filters">{list.flags.map(({flag,count})=><button key={flag} className={filter.includes(flag)?'selected':''} aria-pressed={filter.includes(flag)} onClick={()=>setFilter(value=>value.includes(flag)?value.filter(f=>f!==flag):[...value,flag])}>{flag} <small>{count}</small></button>)}</div>
        {!!filter.length&&<label>flag 匹配<select value={match} onChange={e=>setMatch(e.target.value)}><option value="all">全部匹配</option><option value="any">匹配任一</option></select></label>}
        <p className="muted">{list.entities.length} 个实体{filter.length>0&&<button className="quiet" onClick={()=>setFilter([])}>清除筛选</button>}</p>
        <div className="entity-browser-list">{list.entities.map(e=><button key={e.id} className={`entity-browser-item ${selected===e.id&&!creating?'selected':''}`} onClick={()=>choose(e.id)}>
          {e.thumbnail?<img src={e.thumbnail} alt="" />:<span className="entity-avatar">◇</span>}<span><b>{e.name}</b><small>{e.flags.join(' · ')||'未设置 flag'}{e.baseEntityId?' · 派生':''}</small><small>{e.hasView?'多视图 ✓':'多视图待创作'} · {e.hasVoice?'声音 ✓':'声音待创作'}</small></span>
        </button>)}{!list.entities.length&&<p className="muted">没有符合条件的实体。</p>}</div>
      </aside>
      <section className="entity-detail panel">
        {creating||detail?<><div className="section-head"><h2>{creating?'新建实体':detail.entity.name}</h2>{!editing&&!creating&&<button onClick={()=>{setForm(detail.profile);setSaved(JSON.stringify(detail.profile));setEditing(true);}}>编辑资料</button>}</div>
          {editing?<div className="entity-profile-form"><label>名称<input value={form.name} maxLength={100} onChange={e=>patch({name:e.target.value})} /></label>
            <label>flag</label><div className="entity-flags">{form.flags.map(flag=><button key={flag} onClick={()=>patch({flags:form.flags.filter(f=>f!==flag)})}>{flag} ×</button>)}</div>
            <div className="entity-inline-input"><input aria-label="添加flag" value={flagInput} placeholder="输入 flag，按 Enter 添加" onChange={e=>setFlagInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'){e.preventDefault();const value=flagInput.trim();if(value&&!form.flags.includes(value))patch({flags:[...form.flags,value]});setFlagInput('');}}} /><button onClick={()=>{const value=flagInput.trim();if(value&&!form.flags.includes(value))patch({flags:[...form.flags,value]});setFlagInput('');}}>添加</button></div>
            <div className="entity-flags">{['人物','物品','技能','场景'].filter(f=>!form.flags.includes(f)).map(flag=><button key={flag} onClick={()=>patch({flags:[...form.flags,flag]})}>＋ {flag}</button>)}</div>
            <label>实体介绍<textarea rows={3} value={form.description} onChange={e=>patch({description:e.target.value})} /></label>
            <label>外观描述<textarea rows={3} value={form.appearance} onChange={e=>patch({appearance:e.target.value})} /></label>
            <label>声音描述<textarea rows={2} value={form.voiceDescription} onChange={e=>patch({voiceDescription:e.target.value})} /></label>
            <div className="card-actions"><button className="primary" disabled={busy||!form.name.trim()} onClick={saveProfile}>{creating?'创建实体':'保存资料'}</button><button disabled={busy} onClick={()=>{if(!abandon())return;setEditing(false);setCreating(false);setForm(detail?.profile||emptyProfile);}}>取消</button></div>
          </div>:<><div className="entity-flags">{detail.profile.flags.map(flag=><span key={flag} className="pill">{flag}</span>)}</div>
            {detail.derivedFrom&&<p className="entity-lineage">派生自 <button className="quiet accent" onClick={()=>choose(detail.derivedFrom.entityId)}>{detail.derivedFrom.name}</button>{detail.derivedFrom.description&&<span> · {detail.derivedFrom.description}</span>}</p>}
            <p className="entity-text">{detail.profile.description||'尚未填写实体介绍。'}</p>{detail.profile.appearance&&<p className="entity-text"><b>外观：</b>{detail.profile.appearance}</p>}
            <div className="card-actions">{projectId&&<button disabled={!!roleForm} onClick={()=>setAssistant(true)}>与创作助手讨论</button>}<button className="primary" onClick={()=>openCreate()}>进入素材创作</button><button onClick={()=>{if(!abandon())return;setDerive({name:detail.entity.name+' · 派生',changes:'',copyProfile:true,copyReference:!!v?.appearance,reuseVoice:!!voice,copySettingRelations:true});}}>创建派生实体</button></div>
            {projectId&&<section className="project-role"><div className="section-head"><h3>本项目的剧情作用</h3><button disabled={busy} onClick={()=>setRoleForm({role:projectRole?.role||'',plotNotes:projectRole?.plotNotes||''})}>编辑剧情作用</button></div>{roleForm?<><label>剧情作用<textarea rows={2} value={roleForm.role} onChange={e=>setRoleForm({...roleForm,role:e.target.value})}/></label><label>剧情背景／约束<textarea rows={3} value={roleForm.plotNotes} onChange={e=>setRoleForm({...roleForm,plotNotes:e.target.value})}/></label><div className="card-actions"><button disabled={busy} onClick={saveRole}>保存剧情作用</button><button onClick={()=>setRoleForm(null)}>取消</button></div></>:<><p className="entity-text">{projectRole?.role||'待补充：这个实体如何参与当前故事？'}</p><p className="entity-text">{projectRole?.plotNotes}</p></>}</section>}
            <section className="entity-preview"><div className="section-head"><h3>{detail.profile.flags.includes('场景')||detail.entity.context.type==='scene'?'场景主图':'三视图／形象'}</h3><button onClick={()=>openCreate(detail.profile.flags.includes('场景')||detail.entity.context.type==='scene'?'concept':'views')}>{detail.profile.flags.includes('场景')||detail.entity.context.type==='scene'?'创作场景图片':'创作多视图'}</button></div>
              {v?.view?.url||v?.appearance?.asset.url?<button className="entity-preview-image" onClick={()=>setZoom(v.view||v.appearance.asset)}><img src={v.view?.url||v.appearance.asset.url} alt={v.view?'当前多视图':'当前主形象'} /></button>:<div className="empty"><p>暂无确认形象或多视图。</p></div>}
              {!v?.view&&v?.appearance&&!detail.profile.flags.includes('场景')&&detail.entity.context.type!=='scene'&&<p className="muted">当前展示主形象，多视图尚未确认。</p>}
            </section>
            <section className="entity-preview"><div className="section-head"><h3>声音</h3><button onClick={()=>openCreate('voice')}>创作声音</button></div><p className="entity-text">{detail.profile.voiceDescription||'尚未填写声音描述。'}</p>
              {voice?.asset.url?<><audio controls preload="metadata" src={voice.asset.url} onPlay={e=>document.querySelectorAll('audio').forEach(a=>{if(a!==e.currentTarget)a.pause();})} />{voice.asset.metadata.inheritance&&<p className="muted">沿用基础声音 · 独立素材快照</p>}</>:<p className="muted">暂无选定声音。</p>}
            </section>
            {!!detail.descendants.length&&<section className="entity-preview"><h3>派生实体</h3><div className="entity-flags">{detail.descendants.map(e=><button key={e.entityId} onClick={()=>choose(e.entityId)}>{e.name} ↗</button>)}</div></section>}
          </>}
          {!creating&&detail&&(detail.profile.flags.includes('场景')||['scene','location','场景'].includes(detail.entity.context.type))&&<SceneImageSetEditor key={'images-'+selected} entityId={selected} api={api} notify={notify} onDirtyChange={setImageSetDirty} disabled={editing||busy}/> }
          {!creating&&detail&&(detail.profile.flags.includes('场景')||['scene','location','场景'].includes(detail.entity.context.type)||detail.sceneSpatial?.version>0)&&<EntitySpatialEditor key={selected} projectId={projectId} entityId={selected} api={api} notify={notify} onDirtyChange={setSpatialDirty} disabled={editing||busy}/> }
        </>:<div className="empty"><h2>选择或新建实体</h2><p>资料、三视图和声音会集中显示在这里。</p></div>}
      </section>
      <aside className="entity-relations panel"><h2>实体关系</h2><div className="entity-relation-tabs">{[['setting','设定关系'],['story','剧情关系']].map(([value,label])=><button key={value} className={category===value?'selected':''} onClick={()=>{if(relation&&!confirm('放弃未保存的关系编辑？'))return;setCategory(value);setRelation(null);if(projectId)void loadProject().catch(e=>notify(e.message,true));}}>{label}</button>)}</div>
        {!detail||creating||editing?<p className="muted">保存实体资料后即可编辑关系。</p>:<><p className="muted">{category==='setting'?'服装、武器、技能、形态等设定联系。':projectId?'仅属于当前项目的角色互动与剧情联系。':'旧的全局剧情关系未归属项目；请在项目内建立新的剧情关系。'}</p>
          {!relation&&!(category==='story'&&!projectId)&&<button onClick={()=>setRelation({targetEntityId:'',category,type:relationTypes[category][0],description:''})}>＋ 添加关系</button>}
          {relation&&<div className="entity-relation-form"><label>关联实体<select value={relation.targetEntityId} onChange={e=>setRelation({...relation,targetEntityId:e.target.value})}><option value="">请选择实体</option>{all.filter(e=>e.id!==selected).map(e=><option key={e.id} value={e.id}>{e.name}</option>)}</select></label>
            <label>关系类型<input list="entity-relation-types" value={relation.type} onChange={e=>setRelation({...relation,type:e.target.value})} /><datalist id="entity-relation-types">{relationTypes[category].map(type=><option key={type} value={type}/>)}</datalist></label>
            <label>说明<textarea rows={3} value={relation.description} onChange={e=>setRelation({...relation,description:e.target.value})}/></label><div className="card-actions"><button className="primary" disabled={busy||!relation.targetEntityId||!relation.type.trim()} onClick={saveRelation}>保存关系</button><button disabled={busy} onClick={()=>setRelation(null)}>取消</button></div>
          </div>}
          <div className="entity-relation-list">{visibleRelations.map(r=><article key={r.relationId}><small className="muted">{r.sourceEntityId===selected?'本实体 →':'关联实体 → 本实体'}</small>
            <p><button className="quiet accent" onClick={()=>choose(r.sourceEntityId===selected?r.targetEntityId:r.sourceEntityId)}>{r.sourceEntityId===selected?r.targetName:r.sourceName}</button><span className="pill">{r.type}</span></p>{r.description&&<p className="entity-text">{r.description}</p>}
            {r.type!=='派生自'&&!(category==='story'&&!projectId)&&(r.sourceEntityId===selected?<div className="card-actions"><button disabled={busy} onClick={()=>setRelation(r)}>编辑</button><button disabled={busy} onClick={()=>removeRelation(r)}>解除</button></div>:<button className="quiet" onClick={()=>choose(r.sourceEntityId)}>到来源实体编辑</button>)}
          </article>)}{!visibleRelations.length&&<p className="muted">暂无关系。</p>}</div>
        </>}
      </aside>
    </div>
    {derive&&<div className="entity-modal-backdrop"><section className="entity-modal" role="dialog" aria-modal="true" aria-label="创建派生实体"><h2>创建派生实体</h2><p className="muted">新实体独立保存，不覆盖基础实体，也不随基础实体自动更新。</p>
      <label>新实体名称<input value={derive.name} onChange={e=>setDerive({...derive,name:e.target.value})}/></label><label>变化说明<textarea rows={3} placeholder="例如：学会某技能，出现一缕白发；使用时显现翅膀。" value={derive.changes} onChange={e=>setDerive({...derive,changes:e.target.value})}/></label>
      {[['copyProfile','复制实体介绍和外观描述',false],['copyReference','将当前主形象复制为引用图',!v?.appearance],['reuseVoice','沿用当前声音（独立素材快照）',!voice],['copySettingRelations','复制设定关系（不复制剧情关系）',false]].map(([key,label,disabled])=><label key={key} className="transcript-confirm"><input type="checkbox" checked={derive[key]} disabled={disabled} onChange={e=>setDerive({...derive,[key]:e.target.checked})}/>{label}</label>)}
      <p className="muted">新主形象和多视图需在现有创作流程中确认；引用图不会自动定稿。</p><div className="card-actions"><button className="primary" disabled={busy||!derive.name.trim()} onClick={createDerived}>创建派生实体</button><button disabled={busy} onClick={()=>setDerive(null)}>取消</button></div>
    </section></div>}
    {assistant&&<SceneAgentPanel projectId={projectId} entityId={selected} purpose="project-authoring" api={api} notify={notify} onDirtyChange={setAgentDirty} onClose={()=>{setAssistant(false);setAgentDirty(false);void loadProject().catch(e=>notify(e.message,true));}} onSaved={()=>void loadProject().catch(e=>notify(e.message,true))}/>}
    {zoom&&<div className="entity-modal-backdrop" onClick={()=>setZoom(null)}><section className="entity-image-modal" role="dialog" aria-modal="true" aria-label="形象预览"><button onClick={()=>setZoom(null)}>关闭</button><img src={zoom.url} alt={zoom.name}/></section></div>}
  </main>;
}
