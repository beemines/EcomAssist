"use strict";
// Exercise the real live runner with controlled browser/network boundaries.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const os = require('node:os');
const script = path.join(__dirname, 'verify-context-browser.cjs');
async function check(finalFailure) {
  const output = fs.mkdtempSync(path.join(os.tmpdir(), 'context-live-failure-'));
  const config = {profile:'demo', 'run-id':'failure-test', 'max-glm-calls':1,
    'max-embedding-calls':0, 'max-rerank-calls':0, output};
  const health = {context_profile:'demo', acceptance:{run_id:'failure-test', limits:{glm:1, embedding:0, rerank:0}}};
  const locator = {click:async()=>{}, fill:async()=>{}, evaluate:async()=>{}};
  const page = {setDefaultTimeout(){}, on(event, callback){callback(Error('captured-page-error'));},
    route:async()=>{}, goto:async()=>{}, locator:()=>locator, waitForFunction:async()=>{},
    waitForResponse:async()=>({status:()=>503, text:async()=> 'original round failure'})};
  const browser = {newContext:async()=>({newPage:async()=>page}), close:async()=>{}};
  const playwright = {chromium:{launch:async()=>browser, executablePath:()=>''}};
  let healthCalls=0;
  const sandbox = {require:(name)=>name==='playwright'?playwright:require(name),
    __dirname, module:{exports:{}}, process, console,
    fetch:async()=>{if(healthCalls++ && finalFailure) throw Error('final health unavailable');
      return {status:200,json:async()=>vm.runInContext('('+JSON.stringify(health)+')', sandbox)};}};
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(script,'utf8')+'\nmodule.exports.live=live;', sandbox, {filename:script});
  await assert.rejects(sandbox.module.exports.live(config), /503.*200/s,
    'original round failure must remain the reported failure');
  const saved = JSON.parse(fs.readFileSync(path.join(output,'results.json'),'utf8'));
  assert.equal(saved.results[0].body,'original round failure');
  assert.deepEqual(saved.pageErrors,['captured-page-error']);
  assert.match(saved.failure,/503.*200/s);
  if(finalFailure) assert.match(saved.finalHealthError,/final health unavailable/);
  else assert.equal(saved.finalHealthError,null);
  fs.rmSync(output,{recursive:true});
}
(async()=>{await check(true); await check(false); console.log('live failure evidence preservation 2/2 PASS');})()
  .catch(error=>{console.error(error);process.exitCode=1;});
