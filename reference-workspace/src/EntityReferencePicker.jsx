// Owner: Sean — explicit entity asset references and optional setting relationships during creation.
import React, { useEffect, useState } from 'react';
export function EntityReferencePicker({ entityId, api, onClose, onImported, notify }) {
  const [entities,setEntities]=useState([]),[sourceId,setSourceId]=useState(''),[assets,setAssets]=useState([]),[assetId,setAssetId]=useState('');
  const [relationType,setRelationType]=useState(''),[description,setDescription]=useState(''),[busy,setBusy]=useState(false);
  useEffect(()=>{api('/manage/entities').then(v=>setEntities(v.entities.filter(e=>e.id!==entityId))).catch(e=>notify(e.message,true));},[entityId]);
  useEffect(()=>{setAssets([]);setAssetId('');if(!sourceId)return;let disposed=false;api(`/entities/${sourceId}/workspace`).then(v=>{if(!disposed)setAssets(v.assets.filter(a=>a.mediaType==='image'));}).catch(e=>notify(e.message,true));return()=>{disposed=true;};},[sourceId]);
  async function importAsset(){setBusy(true);try{
    const asset=await api(`/manage/entities/${entityId}/references`,{method:'POST',body:JSON.stringify({sourceEntityId:sourceId,assetId,category:'setting',relationType:relationType||null,description})});
    await onImported(asset);notify(relationType?'图片已加入，并建立设定关系':'图片已加入，仅作素材引用');onClose();
  }catch(e){notify(e.message,true);}finally{setBusy(false);}}
  return <div className="entity-modal-backdrop"><section className="entity-modal entity-reference-picker" role="dialog" aria-modal="true" aria-label="引用其他实体">
    <div className="section-head"><h2>引用其他实体</h2><button disabled={busy} onClick={onClose}>关闭</button></div>
    <label>来源实体<select value={sourceId} onChange={e=>setSourceId(e.target.value)}><option value="">请选择服装、装备、技能或其他实体</option>{entities.map(e=><option key={e.id} value={e.id}>{e.name} · {e.flags.join(' / ')}</option>)}</select></label>
    <div className="entity-reference-images">{assets.map(a=><button className={assetId===a.id?'selected':''} key={a.id} onClick={()=>setAssetId(a.id)}><img src={a.url} alt={a.name}/><small>{a.name}{a.protected?' · 当前选定':''}</small></button>)}</div>{sourceId&&!assets.length&&<p className="muted">这个实体还没有图片素材。</p>}
    <label>关系用途<select value={relationType} onChange={e=>setRelationType(e.target.value)}><option value="">仅作图片引用，不建立关系</option>{['穿着','使用','拥有','掌握','使用时显现','外观参考'].map(type=><option key={type} value={type}>{type}</option>)}</select></label>
    {relationType&&<label>关系说明<textarea rows={2} value={description} onChange={e=>setDescription(e.target.value)} placeholder="例如：使用技能时显现翅膀；这套服装仅用于战斗形态。"/></label>}
    <p className="muted">图片复制到当前实体，记录来源版本和 hash。来源变化不会自动替换；关系仅按你明确选择的用途建立。</p>
    <button className="primary" disabled={busy||!assetId} onClick={importAsset}>加入当前实体引用资料</button>
  </section></div>;
}
