// Owner: Sean — scoped, immutable entity text suggestions with explicit human application.
import {z} from 'zod';
import {id,now,HttpError} from './store.mjs';
import {canonicalJSON,contentHash} from './content-hash.mjs';
import {projectInput} from './project-workspace.mjs';

export const entityChangeSchema=z.object({entityId:z.string().uuid(),summary:z.string().trim().min(1).max(4000),changes:z.object({name:z.string().trim().min(1).max(100).optional(),description:z.string().max(8000).optional(),appearance:z.string().max(8000).optional(),voiceDescription:z.string().max(4000).optional()}).strict().refine(v=>Object.keys(v).length>0,'至少提出一项修改')}).strict();
export function createEntityChangeProposals(store,{projects,management}){
  const db=store.db;
  db.exec(`CREATE TABLE IF NOT EXISTS agent_entity_proposals(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES agent_projects(id),entity_id TEXT NOT NULL REFERENCES entities(id),session_id TEXT NOT NULL REFERENCES agent_sessions(id),run_id TEXT NOT NULL REFERENCES agent_runs(id),body TEXT NOT NULL,content_hash TEXT NOT NULL,applied_entity_revision TEXT,created_at TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS entity_proposal_immutable BEFORE UPDATE OF project_id,entity_id,session_id,run_id,body,content_hash ON agent_entity_proposals BEGIN SELECT RAISE(ABORT,'immutable entity proposal');END;`);
  function fields(entityId){const e=store.entity(entityId);return {name:e.name,description:typeof e.context.description==='string'?e.context.description:'',appearance:typeof e.context.appearance==='string'?e.context.appearance:'',voiceDescription:typeof e.context.voiceDescription==='string'?e.context.voiceDescription:''};}
  function row(projectId,proposalId){projects.project(projectId);const r=db.prepare('SELECT * FROM agent_entity_proposals WHERE id=? AND project_id=?').get(proposalId,projectId);if(!r)throw new HttpError(404,'实体修改提案不存在');return r;}
  function fresh(r){try{projects.member(r.project_id,r.entity_id);const b=JSON.parse(r.body).basis;return projects.context(r.project_id).contentHash===b.contextHash&&management.detail(r.entity_id).revision===b.entityRevision;}catch{return false;}}
  function get(projectId,proposalId){const r=row(projectId,proposalId);return {owner:'Sean',id:r.id,projectId,entityId:r.entity_id,sessionId:r.session_id,runId:r.run_id,...JSON.parse(r.body),contentHash:r.content_hash,appliedEntityRevision:r.applied_entity_revision,createdAt:r.created_at,stale:!r.applied_entity_revision&&!fresh(r)};}
  function list(projectId,sessionId){projects.project(projectId);return db.prepare('SELECT id FROM agent_entity_proposals WHERE project_id=? AND session_id=? ORDER BY rowid').all(projectId,sessionId).map(r=>get(projectId,r.id));}
  function save(projectId,raw,{sessionId,runId}){const input=projectInput(entityChangeSchema,raw);return store.transaction(()=>{
    projects.member(projectId,input.entityId);const run=db.prepare("SELECT r.status,s.project_id,s.purpose FROM agent_runs r JOIN agent_sessions s ON s.id=r.session_id WHERE r.id=? AND s.id=?").get(runId,sessionId);if(!run||run.project_id!==projectId||run.purpose!=='project-authoring'||run.status!=='running')throw new HttpError(409,'提案需要当前项目正在进行的创作对话');
    const before=fields(input.entityId);if(Object.entries(input.changes).every(([k,v])=>before[k]===v))throw new HttpError(400,'提案没有改变实体资料',{fieldErrors:{changes:['请提出具体修改']}});
    const body={owner:'Sean',summary:input.summary,before,changes:input.changes,basis:{contextHash:projects.context(projectId).contentHash,entityRevision:management.detail(input.entityId).revision}},proposalId=id();db.prepare('INSERT INTO agent_entity_proposals VALUES (?,?,?,?,?,?,?,?,?)').run(proposalId,projectId,input.entityId,sessionId,runId,canonicalJSON(body),contentHash(body),null,now());return get(projectId,proposalId);
  });}
  function apply(proposalId,raw){const input=projectInput(z.object({expectedContentHash:z.string().length(64),acknowledgeUpdate:z.literal(true)}).strict(),raw);const r=db.prepare('SELECT * FROM agent_entity_proposals WHERE id=?').get(proposalId);if(!r)throw new HttpError(404,'实体修改提案不存在');if(r.content_hash!==input.expectedContentHash)throw new HttpError(409,'提案内容不匹配');return store.transaction(()=>{
    if(r.applied_entity_revision)return {entityId:r.entity_id,revision:r.applied_entity_revision,alreadyApplied:true};if(db.prepare('SELECT status FROM agent_runs WHERE id=?').get(r.run_id)?.status!=='succeeded')throw new HttpError(409,'对话完整结束后才能应用实体修改');if(!fresh(r))throw new HttpError(409,'项目或实体资料已变化，请重新讨论');
    const body=JSON.parse(r.body),updated=management.update(r.entity_id,{...body.changes,expectedRevision:body.basis.entityRevision},{inTransaction:true,partial:true});
    db.prepare('UPDATE agent_entity_proposals SET applied_entity_revision=? WHERE id=?').run(updated.revision,r.id);return {entityId:r.entity_id,revision:updated.revision,alreadyApplied:false,generationSubmitted:false};
  });}
  return {save,get,list,apply};
}
