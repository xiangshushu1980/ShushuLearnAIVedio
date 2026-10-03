// Owner: Sean — explicit review of a shared entity text change.
import React from 'react';
const labels={name:'名称',description:'实体介绍',appearance:'固定外观',voiceDescription:'声音描述'};
export function EntityChangeProposal({proposal,disabled,onApply}){
  return <article className="spatial-summary"><h4>实体文字修改 · {proposal.before.name}</h4><p>{proposal.summary}</p><p className="muted">修改的是共用实体资料，会影响使用它的其他项目。剧情站位与动作请留在拍摄本。</p>{Object.entries(proposal.changes).map(([key,value])=><details open key={key}><summary>{labels[key]}</summary><p className="entity-text"><b>提案时：</b>{proposal.before[key]||'空'}</p><p className="entity-text"><b>建议改为：</b>{value||'清空此字段'}</p></details>)}{proposal.stale&&<p className="agent-notice">项目或实体资料已更新，请重新讨论。</p>}<button disabled={disabled||proposal.stale||!!proposal.appliedEntityRevision} onClick={()=>onApply(proposal)}>{proposal.appliedEntityRevision?'已应用实体修改':'接受并应用实体修改'}</button><p className="muted">不会自动生成图片或更新提示词；相关步骤需要重新核对。</p></article>;
}
