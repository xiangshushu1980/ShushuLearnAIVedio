// Owner: Sean — immutable changes to existing relation text, accepted explicitly and atomically.
import {z} from 'zod';import {id,now,HttpError} from './store.mjs';import {canonicalJSON,contentHash} from './content-hash.mjs';import {projectInput} from './project-workspace.mjs';
export const relationChangeSchema=z.object({relationId:z.string().uuid(),scope:z.enum(['entity-setting','project-story']),summary:z.string().trim().min(1).max(4000),changes:z.object({type:z.string().trim().min(1).max(60).optional(),description:z.string().max(4000).optional()}).strict().refine(v=>Object.keys(v).length>0,'至少修改一个字段')}).strict();
export function createRelationChangeProposals(store,{projects,management}){
 const db=store.db;
 db.exec(`CREATE TABLE IF NOT EXISTS agent_relation_proposals(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES agent_projects(id),session_id TEXT NOT NULL REFERENCES agent_sessions(id),run_id TEXT NOT NULL REFERENCES agent_runs(id),body TEXT NOT NULL,content_hash TEXT NOT NULL,applied_receipt TEXT,created_at TEXT NOT NULL);
 CREATE TRIGGER IF NOT EXISTS relation_proposal_immutable BEFORE UPDATE OF project_id,session_id,run_id,body,content_hash ON agent_relation_proposals BEGIN SELECT RAISE(ABORT,'immutable relation proposal');END;`);
 function source(projectId,relationId,scope){const c=projects.context(projectId),relations=scope==='project-story'?c.storyRelations:c.entities.flatMap(e=>e.relations);const r=relations.find(r=>r.relationId===relationId);if(!r)throw new HttpError(404,'关系不在当前项目或来源范围');projects.member(projectId,r.sourceEntityId);projects.member(projectId,r.targetEntityId);if(r.type==='派生自')throw new HttpError(400,'派生来源不可修改');return {...r,scope};}
 function fresh(row){try{const b=JSON.parse(row.body);return b.basis.contextHash===projects.context(row.project_id).contentHash&&contentHash(source(row.project_id,b.relationId,b.scope))===b.basis.relationHash;}catch{return false;}}
 function get(row){const b=JSON.parse(row.body);return {owner:'Sean',id:row.id,projectId:row.project_id,sessionId:row.session_id,runId:row.run_id,...b,contentHash:row.content_hash,createdAt:row.created_at,appliedReceipt:row.applied_receipt?JSON.parse(row.applied_receipt):null,stale:!row.applied_receipt&&!fresh(row)};}
 function list(projectId,sessionId){projects.project(projectId);return db.prepare('SELECT * FROM agent_relation_proposals WHERE project_id=? AND session_id=? ORDER BY rowid').all(projectId,sessionId).map(get);}
 function save(projectId,raw,{sessionId,runId}){const input=projectInput(relationChangeSchema,raw);return store.transaction(()=>{
  const run=db.prepare('SELECT r.status,s.project_id,s.purpose FROM agent_runs r JOIN agent_sessions s ON s.id=r.session_id WHERE r.id=? AND s.id=?').get(runId,sessionId);if(!run||run.status!=='running'||run.project_id!==projectId||run.purpose!=='project-authoring')throw new HttpError(409,'关系提案需要当前项目创作对话');
  const before=source(projectId,input.relationId,input.scope);if(input.changes.type==='派生自')throw new HttpError(400,'派生关系由创建流程建立');if(Object.entries(input.changes).every(([k,v])=>before[k]===v))throw new HttpError(400,'提案没有修改关系内容');
  const body={owner:'Sean',...input,before,basis:{contextHash:projects.context(projectId).contentHash,relationHash:contentHash(before)}},proposalId=id();db.prepare('INSERT INTO agent_relation_proposals VALUES (?,?,?,?,?,?,?,?)').run(proposalId,projectId,sessionId,runId,canonicalJSON(body),contentHash(body),null,now());return get(db.prepare('SELECT * FROM agent_relation_proposals WHERE id=?').get(proposalId));
 });}
 function apply(proposalId,raw){const input=projectInput(z.object({expectedContentHash:z.string().length(64),acknowledgeUpdate:z.literal(true)}).strict(),raw);return store.transaction(()=>{
  const row=db.prepare('SELECT * FROM agent_relation_proposals WHERE id=?').get(proposalId);if(!row)throw new HttpError(404,'关系修改提案不存在');if(row.content_hash!==input.expectedContentHash)throw new HttpError(409,'提案内容不匹配');if(row.applied_receipt)return {...JSON.parse(row.applied_receipt),alreadyApplied:true};
  if(db.prepare('SELECT status FROM agent_runs WHERE id=?').get(row.run_id)?.status!=='succeeded')throw new HttpError(409,'对话完整结束后才能接受关系修改');if(!fresh(row))throw new HttpError(409,'项目、实体或关系已变化，请重新讨论');
  const b=JSON.parse(row.body),r=b.before,values={type:r.type,description:r.description,...b.changes};
  if(b.scope==='project-story')projects.saveRelation(row.project_id,b.relationId,{...values,sourceEntityId:r.sourceEntityId,targetEntityId:r.targetEntityId,expectedRevision:projects.project(row.project_id).revision},false,{inTransaction:true});
  else management.changeRelation(r.sourceEntityId,b.relationId,{...values,targetEntityId:r.targetEntityId,category:'setting',expectedUpdatedAt:r.updatedAt},false,{inTransaction:true});
  const receipt={relationId:b.relationId,scope:b.scope,sourceRevision:contentHash(source(row.project_id,b.relationId,b.scope)),generationSubmitted:false};db.prepare('UPDATE agent_relation_proposals SET applied_receipt=? WHERE id=?').run(canonicalJSON(receipt),proposalId);return {...receipt,alreadyApplied:false};
 });}
 return {source,save,list,apply};
}
