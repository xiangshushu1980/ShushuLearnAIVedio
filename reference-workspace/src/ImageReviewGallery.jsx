// Owner: Sean — simultaneous inspection of the actual reviewed images, without adding generation references.
import React,{useRef,useState} from 'react';
export function ImageReviewGallery({report}){
 const dialog=useRef(null),[failed,setFailed]=useState(new Set());
 const sources=new Map((report.workflowSources||[]).map(s=>[s.assetId,s]));
 const images=(report.reviewedAssetIds||[]).map(assetId=>sources.get(assetId)||{assetId});
 function cards(){return images.map((image,index)=><figure key={image.assetId}><a href={`/api/assets/${image.assetId}/content`} target="_blank" rel="noreferrer" aria-label={`打开已检查图片 ${index+1}`}>{failed.has(image.assetId)?<p className="agent-notice">图片不可用，请重新核对资料。</p>:<img src={`/api/assets/${image.assetId}/content`} alt={`已检查图片 ${index+1} · ${image.entityName||image.entityId||'旧报告未记录实体'}`} onError={()=>setFailed(v=>new Set([...v,image.assetId]))}/>}</a><figcaption><b>{index+1} · {image.entityName||image.entityId||'旧报告未记录实体'}</b><p>{image.assetName||image.assetId}</p><p>{image.workflow?`${image.workflow.label} · v${image.workflow.version}`:'未登记生成步骤'}</p>{report.issues?.filter(i=>i.assetIds?.includes(image.assetId)).map((issue,n)=><p key={n}><b>{{conflict:'冲突观察',missing:'待补充',suggestion:'建议'}[issue.category]}：</b>{issue.description}</p>)}</figcaption></figure>);}
 if(!images.length)return null;
 return <div className="image-review-gallery"><h5>已检查图片对照</h5>{report.stale&&<p className="agent-notice">报告依据已变化。下方显示当前可用图片，需重新检验，不能作为旧结论的有效确认。</p>}<div className="review-image-grid">{cards()}</div><button type="button" onClick={()=>dialog.current.showModal()}>并排放大比较（{images.length}）</button><dialog ref={dialog} className="review-image-dialog" aria-label="已检查图片并排比较"><header><h3>已检查图片并排比较</h3><button type="button" onClick={()=>dialog.current.close()}>关闭图片比较</button></header><p>仅显示报告已观察的图片；不改变选图、实体、步骤或生成输入。</p>{report.stale&&<p className="agent-notice">报告依据已变化，请重新检验。</p>}<div className="review-image-grid">{cards()}</div></dialog></div>;
}
