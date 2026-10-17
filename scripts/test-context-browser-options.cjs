"use strict";
const { spawnSync } = require('node:child_process');
const assert = require('node:assert/strict');
const path = require('node:path');
const script = path.join(__dirname, 'verify-context-browser.cjs');
const result = spawnSync(process.execPath, [script, '--live', '--profile', 'demo'], { encoding: 'utf8' });
assert.equal(result.status, 1, 'incomplete live options must fail before browser/network startup');
assert.match(result.stderr, /run-id.*all three.*limits/i, 'must explain missing run cap group');
console.log('live incomplete-cap guard PASS');
const { options, validateHealth } = require('./verify-context-browser.cjs');
const config = options(['--live','--profile','demo','--run-id','test-run','--max-glm-calls','1','--max-embedding-calls','2','--max-rerank-calls','3','--output','unused']);
const valid = { context_profile:'demo', acceptance:{run_id:'test-run', limits:{glm:1,embedding:2,rerank:3}} };
validateHealth(valid, config);
for (const changed of [{...valid,context_profile:'default'}, {...valid,acceptance:{...valid.acceptance,run_id:'another'}}, {...valid,acceptance:{...valid.acceptance,limits:{glm:2,embedding:2,rerank:3}}}, {context_profile:'demo'}]) {
  assert.throws(() => validateHealth(changed, config));
}
assert.throws(() => options(['--live','--profile','bad']));
console.log('exact server profile/run/limits guard PASS');
