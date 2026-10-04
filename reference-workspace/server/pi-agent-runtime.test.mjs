// Owner: Sean — replay compatibility for persisted pre-fix image tool content.
import test from 'node:test';import assert from 'node:assert/strict';
import {normalizePiSessionEntries} from './pi-agent-runtime.mjs';
test('old image tool envelopes normalize for Pi without mutating saved history or current content',()=>{
 const current={type:'image',data:'new',mimeType:'image/png'},old={type:'image',source:{type:'base64',data:'old',mediaType:'image/jpeg'}};
 const entries=[{type:'session',id:'header'},{type:'message',id:'tool',message:{role:'toolResult',content:[{type:'text',text:'Evidence'},old,current]}}],before=structuredClone(entries);
 const normalized=normalizePiSessionEntries(entries);assert.deepEqual(entries,before);assert.deepEqual(normalized[1].message.content[1],{type:'image',data:'old',mimeType:'image/jpeg'});assert.equal(normalized[1].message.content[2],current);assert.equal(normalized[0],entries[0]);assert.equal(normalized[1].message.role,'toolResult');
});
