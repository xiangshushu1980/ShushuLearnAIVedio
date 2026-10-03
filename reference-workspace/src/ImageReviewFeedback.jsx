// Owner: Sean — image evidence and a reviewable, unsent correction request.
import React from 'react';
export function ImageReviewFeedback({report,disabled,onFollowup}){
  const sources=report.workflowSources||[],steps=[...new Map(sources.filter(a=>a.workflow).map(a=>[a.workflow.stepId,a.workflow])).values()];
  return <section className="image-review-feedback"><details><summary>图片与生成步骤来源</summary>{sources.length?sources.map(a=><p key={a.assetId}><a href={`/api/assets/${a.assetId}/content`} target="_blank" rel="noreferrer">查看已检查图片</a> · {a.workflow?`${a.workflow.label} · v${a.workflow.version}`:'未登记生成步骤'}{a.workflow&&!a.workflow.fullStepRead?' · 本轮未读取完整步骤':''}</p>):<p className="muted">旧报告未保存步骤来源；需要重新检验后才能关联修订。</p>}</details>
    {steps.map(step=><button key={step.stepId} disabled={disabled||report.stale} onClick={()=>onFollowup(`请根据图片检验报告 ${report.id} 修订图片步骤 ${step.stepId}。先读取完整报告与步骤、当前实体和关系，核对具体冲突及保持项。仅修正提示词与工作流需要修改的部分，保留原实体和逻辑步骤；用 feedback 关联本报告及此步骤已检查的结果图片。不要把问题输出默认改作生成参考，不自动采用、生成或确认。`,report.reviewedAssetIds)}>按报告讨论修订 · {step.label}</button>)}
    {steps.length>0&&<p className="muted">只填写下一轮讨论要求，不自动发送或生成。新版本在工作区比较并采用后，再创建实验批次。</p>}
  </section>;
}
