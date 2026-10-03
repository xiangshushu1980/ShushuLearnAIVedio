// Owner: Sean — pending continuation for a real fixture entity; no Agent/provider/ComfyUI calls.
export function installExistingImagesFixture(store,projects,authoring,projectId,entityId){
  const proposal=authoring.saveExistingImages(projectId,{entityId,kind:'scene',title:'已有场景接续 · PC 模拟',summary:'保留候车厅资料和主图，仅增加一个细节图片步骤',images:[{key:'bench_closeup',label:'既有长凳细节',role:'scene_detail',prompt:'Use Image 1 as the same hall. Show the established bench without adding doors or changing the entrance.',purpose:'PC 接续操作验证',modelId:'qwen-image-2.1',styleId:'original',referenceAssetIds:[],useMainAppearance:true,useBaseAppearance:false,parameters:{},invariants:['保留既有入口和长凳关系'],unknowns:['绝对方向未知']} ]});
  return {planId:proposal.id,entityId};
}
