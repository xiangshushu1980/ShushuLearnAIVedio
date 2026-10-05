// Owner: Sean — real passing regression/adoption/restore against a disposable source copy.
import {mkdtempSync,cpSync,symlinkSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import assert from 'node:assert/strict';
import {Store,id,now} from '../../../film-editor/server/store.mjs';
import {ProgramWorkbench} from '../../../film-editor/server/program-workbench.mjs';
const temp=mkdtempSync(join(tmpdir(),'sean-workbench-acceptance-')),root=join(temp,'film-editor'),store=new Store(join(temp,'data'));
try{
 cpSync(resolve('film-editor/server'),join(root,'server'),{recursive:true});symlinkSync(resolve('film-editor/node_modules'),join(root,'node_modules'),'dir');for(const dir of ['.pi','docs'])symlinkSync(resolve(dir),join(temp,dir),'dir');
 const p={id:id(),owner:'Sean',revision:0,title:'program regression acceptance',createdAt:now(),plot:'',script:'',dialogue:'',shots:[],entities:{},settings:{targetDurationSec:10}};store.save(p);
 const w=new ProgramWorkbench(store,root),file=w.read('server/spatial.mjs'),v=w.propose(p.id,{path:file.path,baseHash:file.contentHash,text:file.text+'\n// Owner: Sean — bounded acceptance fixture.\n',summary:'测试程序修订采用',evidence:'临时源码副本，不修改实际应用'});
 const applied=await w.apply(p.id,v.id);assert.equal(applied.validation.regression,'passed');assert.notEqual(w.read(file.path).contentHash,file.contentHash);
 const restore=w.restore(p.id,v.id);assert.equal(restore.baseHash,w.read(file.path).contentHash);const reverted=await w.apply(p.id,restore.id);assert.equal(reverted.validation.regression,'passed');assert.equal(w.read(file.path).contentHash,file.contentHash);
 console.log(JSON.stringify({owner:'Sean',regression:'passed',adoption:'passed',restore:'passed',actualApplicationSourceChanged:false,details:applied.validation.output.slice(-250)}));
}finally{store.db.close();rmSync(temp,{recursive:true,force:true});}
