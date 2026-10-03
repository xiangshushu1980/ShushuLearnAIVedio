// Owner: Sean — isolated V3 PC fixture, colored mock pictures, never a model/ComfyUI call.
import {catalog} from '../server/catalog.mjs';
export async function installMultiviewFixture(store,projects,authoring,projectId){
  const images=catalog.multiview.map(m=>({key:m.layout,label:m.name,role:'three_view',prompt:m.promptsByStyle.original,purpose:'PC 模拟验证',modelId:m.id,styleId:'original',referenceAssetIds:[],useMainAppearance:true,useBaseAppearance:false,parameters:{},invariants:['仅引用本人物主形象'],unknowns:[]}));
  const saved=authoring.save(projectId,{title:'V3 多视图 PC 模拟方案',summary:'色块仅验证交互，不证明图像质量',candidates:[{key:'character',kind:'character',profile:{name:'V3 测试人物',description:'模拟人物',appearance:'模拟形象',voiceDescription:'',flags:['人物']},baseEntityId:null,variationOf:null,changes:'',projectRole:{role:'测试',plotNotes:''},unknowns:[],images}],relations:[],questions:[]});
  const applied=authoring.apply(projectId,saved.id,{expectedContentHash:saved.contentHash,acknowledgeNewDesign:true});
  const source=store.db.prepare("SELECT id FROM assets WHERE kind='concept' AND deleted_at IS NULL LIMIT 1").get();
  const stage=await store.stageImage(store.assetBytes(source.id),'模拟人物概念图',applied.entities.character,'concept',null,{source:'browser-fixture'}),asset=store.transaction(()=>store.registerStages([stage]))[0];
  return {entityId:applied.entities.character,assetId:asset.id,planId:saved.id};
}
