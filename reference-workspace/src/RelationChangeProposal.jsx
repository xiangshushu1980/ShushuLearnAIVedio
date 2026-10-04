// Owner: Sean — human acceptance of relation text changes.
import React from 'react';
export function RelationChangeProposal({proposal:p,disabled,onApply}){
 return <article className="spatial-summary"><h4>关系修改 · {p.before.sourceName} → {p.before.targetName}</h4><p>{p.summary}</p><p className="muted">{p.scope==='entity-setting'?'修改共用实体设定关系，会影响使用这些实体的其他项目。':'只修改本项目剧情关系。'}关系两端与 ID 保持不变。</p>{Object.entries(p.changes).map(([k,v])=><details open key={k}><summary>{k==='type'?'关系类型':'关系说明'}</summary><p><b>提案时：</b>{p.before[k]||'空'}</p><p><b>建议改为：</b>{v||'清空此字段'}</p></details>)}{p.stale&&<p className="agent-notice">来源资料已更新，请重新讨论。</p>}<button disabled={disabled||p.stale||!!p.appliedReceipt} onClick={()=>onApply(p)}>{p.appliedReceipt?'已应用关系修改':'接受并应用关系修改'}</button><p className="muted">不会自动生成或确认素材，相关报告与图片步骤需重新核对。</p></article>;
}
