"use strict";

// Real Chromium, fresh browser contexts, owned ephemeral HTTP port; no app DB/model/services.
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const assert = require("node:assert/strict");
const { createRequire } = require("node:module");
const { randomUUID } = require("node:crypto");
const root = path.resolve(__dirname, "..");
function options(argv) {
  const result = { live: false, profile: 'default' }, allowed = new Set(['profile', 'run-id', 'max-glm-calls', 'max-embedding-calls', 'max-rerank-calls', 'output']);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--live') { if (result.live) throw Error('Duplicate --live'); result.live = true; continue; }
    const key = argv[i].replace(/^--/, '');
    if (!argv[i].startsWith('--') || !allowed.has(key) || i + 1 >= argv.length || argv[i+1].startsWith('--') || Object.hasOwn(result, key) && key !== 'profile') throw Error('Invalid or duplicate option');
    result[key] = argv[++i];
  }
  if (!['default','demo'].includes(result.profile)) throw Error('Invalid profile');
  const keys = ['run-id','max-glm-calls','max-embedding-calls','max-rerank-calls'];
  if (result.live && (keys.some((key) => result[key] === undefined) || !result.output)) throw Error('Live requires run-id, all three provider limits, and output');
  if (!result.live && keys.some((key) => result[key] !== undefined)) throw Error('Run limits require explicit --live');
  if (result.live) {
    if (!/^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/.test(result['run-id'])) throw Error('Invalid run-id');
    for (const key of keys.slice(1)) { if (!/^\d+$/.test(result[key]) || !Number.isSafeInteger(Number(result[key]))) throw Error('Invalid provider limit'); result[key] = Number(result[key]); }
  }
  return result;
}
function validateHealth(health, config) {
  assert.equal(health.context_profile, config.profile, 'server profile mismatch');
  assert.equal(health.acceptance?.run_id, config['run-id'], 'server run mismatch');
  assert.deepEqual(health.acceptance?.limits, { glm: config['max-glm-calls'], embedding: config['max-embedding-calls'], rerank: config['max-rerank-calls'] }, 'server limits mismatch');
}
async function live(config) {
  // Fixed owned demo port; no arbitrary URL or silently uncapped fallback.
  const url = 'http://127.0.0.1:8004';
  const healthResponse = await fetch(url + '/health');
  assert.equal(healthResponse.status, 200);
  const before = await healthResponse.json(); validateHealth(before, config);
  const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tests/fixtures/context/long_conversation.json'), 'utf8'));
  const { createHash } = require('node:crypto');
  assert.equal(createHash('sha256').update(fixture.turns.map((row) => row.question).join('\n')).digest('hex'), fixture.sha256);
  const output = path.resolve(config.output); fs.mkdirSync(output, { recursive: true });
  const { chromium, executablePath } = loadBrowser();
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const results = [], errors = [];
  let failure = null, after = null, finalHealthError = null, closeError = null;
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage(); page.setDefaultTimeout(250000);
    page.on('pageerror', (error) => errors.push(error.message));
    await page.route('**/actions/**', (route) => route.request().method() === 'POST' ? route.abort() : route.continue());
    await page.goto(url);
    await page.locator('#new-chat').click();
    await page.waitForFunction(() => !document.querySelector('#message-input').disabled);
    for (const row of fixture.turns) {
      const responsePromise = page.waitForResponse((response) => response.url() === url+'/api/chat' && response.request().method() === 'POST');
      await page.locator('#message-input').fill(row.question);
      await page.locator('#chat-form').evaluate((form) => form.requestSubmit());
      const response = await responsePromise;
      const body = await response.text();
      results.push({ turn: row.turn, question: row.question, status: response.status(), body });
      assert.equal(response.status(), 200); assert.match(body, /event: done/); assert.doesNotMatch(body, /event: (?:error|paused)/);
      await page.waitForFunction(() => !document.querySelector('#message-input').disabled);
      if ([1,4,10,16,21].includes(row.turn)) await page.screenshot({ path: path.join(output, `turn-${row.turn}.png`), fullPage: true });
    }
    assert.deepEqual(errors, []);
  } catch (error) {
    failure = error;
  } finally {
    try { await browser.close(); } catch (error) { closeError = error; }
    try {
      const response = await fetch(url+'/health'); assert.equal(response.status, 200);
      after = await response.json(); validateHealth(after, config);
    } catch (error) { finalHealthError = error; }
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify({ mode: 'live', profile: config.profile, fixture_sha256: fixture.sha256, before, after, results, pageErrors: errors, failure: failure?.stack || null, finalHealthError: finalHealthError?.stack || null, closeError: closeError?.stack || null, sql_verified: false }, null, 2));
  }
  if (failure || closeError || finalHealthError) throw failure || closeError || finalHealthError;
  console.log(`21 live rounds completed; inspect answers and collect SQL evidence: ${output}`);
}
function loadBrowser() {
  let playwright;
  try { playwright = require("playwright"); } catch {
    playwright = createRequire(path.join(process.env.USERPROFILE || process.env.HOME, ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json"))("playwright");
  }
  const choices = [process.env.WORKFLOW_CHROMIUM_PATH, playwright.chromium.executablePath()];
  for (const cache of [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(process.env.LOCALAPPDATA || "", "ms-playwright"), path.join(process.env.USERPROFILE || process.env.HOME, "AppData/Local/ms-playwright")].filter(Boolean)) {
    if (fs.existsSync(cache)) for (const name of fs.readdirSync(cache).filter((v) => /^chromium-\d+$/.test(v)).sort().reverse()) choices.push(path.join(cache, name, "chrome-win64/chrome.exe"));
  }
  return { chromium: playwright.chromium, executablePath: choices.find((v) => v && fs.existsSync(v)) };
}
const oldId = "9007199254740993", nextId = "9007199254740995", slowId = "9007199254740991", freshId = "9007199254741011";
const checkpoint = "1f0a6cab-7153-6045-8001-d47d0224b364", offerId = "3f0a6cab-7153-6045-8001-d47d0224b364";
const originalChunkText = "第一轮原始政策 <script>不可执行</script>。";
const secondChunkText = "第二轮完全不同的原始政策。";
const citation = (answer, id) => ({ n: 1, chunk_id: id, section_path: "原始政策", question: "政策问题", answer });
const actions = { assistant_message_id: "103", checkpoint_id: checkpoint, options: [{ action: "handoff", label: "转人工" }, { action: "create_ticket", label: "建工单" }] };
const order = { order_id: "9007199254741021", product_name: "受控商品", model: "标准款", status: "已签收", as_of: "2026-10-15", mock: true, currency: "CNY", amount_cents: 29900 };
const offer = { assistant_message_id: "106", checkpoint_id: checkpoint, offer_id: offerId, order, refund_decision: "needs_review", decision_reason: "待审核", reasons: [{ code: "unwanted", label: "不想要了" }, { code: "quality", label: "质量问题" }, { code: "not_as_described", label: "与描述不符" }, { code: "wrong_or_missing", label: "发错/漏发" }, { code: "damaged", label: "运输破损" }, { code: "other", label: "其他" }] };
const pending = { turn_id: "105", selection_id: "2f0a6cab-7153-6045-8001-d47d0224b364", checkpoint_id: checkpoint, prompt: "请选择本次订单", cards: [order] };
const row = (id, role, content, extra = {}) => ({ id, role, content, tool_calls: null, tool_call_id: null, created_at: "2026-10-17T12:00:00", ...extra });
const raw = [row("101", "user", "最早的问题 <img src=x onerror=alert(1)>"), row("102", "assistant", null, { tool_calls: [{ id: "call-original", name: "query_faq", args: {} }] }), row("103", "assistant", "第一轮答复 [1]"), row("104", "tool", "SQL原始工具正文", { tool_call_id: "call-original" }), row("105", "user", "第二个问题"), row("106", "assistant", "第二轮答复 [1]"), row("107", "assistant", "缺失来源仍是原文 [1]")];
async function fixtureServer(settings = {}) {
  const state = { records: [], refundSubmissions: 0, ticketSubmissions: 0, creates: 0, ...settings };
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://127.0.0.1");
    const chunks = []; for await (const chunk of req) chunks.push(chunk);
    const body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString()) : null;
    state.records.push({ method: req.method, path: url.pathname, query: url.search, body });
    const json = (value, status = 200) => { res.writeHead(status, { "Content-Type": "application/json" }); res.end(JSON.stringify(value)); };
    if (url.pathname === "/health") return json({ status: "controlled" });
    if (url.pathname === "/api/conversations" && req.method === "POST") { state.creates++; return json({ conversation_id: freshId }); }
    if (url.pathname === "/api/conversations" && req.method === "GET") {
      if (state.listFailure) return json({}, 500);
      const ids = url.searchParams.has("before_id") ? [slowId] : (state.creates ? [freshId, nextId, oldId] : [nextId, oldId]);
      return json({ items: ids.map((id) => ({ id, status: "active", created_at: "2026-10-17T12:00:00", updated_at: "2026-10-17T12:00:00", first_question_preview: id === oldId ? "最早的问题" : id === nextId ? "另一个会话" : id === slowId ? "慢速旧会话" : "新对话", has_summary: id === oldId })), next_before_id: url.searchParams.has("before_id") ? null : oldId });
    }
    const match = /^\/api\/conversations\/(\d+)\/messages$/.exec(url.pathname);
    if (match && req.method === "GET") {
      const id = match[1], after = url.searchParams.get("after_id");
      const value = id === oldId ? { messages: after ? raw.slice(4) : raw.slice(0, 4), upto_id: "107", next_after_id: after ? null : "104", turn_metadata: after ? { "106": { turn_status: "completed", citations: [citation(secondChunkText, "9007199254741041")], tool_badges: [], refund_offer: { assistant_message_id: "106", checkpoint_id: checkpoint, offer_id: offerId } } } : { "103": { turn_status: "completed", citations: [citation(originalChunkText, "9007199254741031")], tool_badges: [{ name: "query_faq", tool_call_id: "call-original", status: "success" }], actions } } } : { messages: id === freshId ? [] : [row("201", "user", id === nextId ? "新选择问题" : "迟到的问题"), row("202", "assistant", id === nextId ? "新选择答复" : "迟到旧答复")], upto_id: id === freshId ? null : "202", next_after_id: null, turn_metadata: {} };
      if (id === oldId && after && state.pageFailure) return json({}, 503);
      if (id === slowId) { setTimeout(() => json(value), 700); return; }
      return json(value);
    }
    if (url.pathname.endsWith("/pending-order") && req.method === "GET") return json({ pending: state.withPending && url.pathname.includes(oldId) ? pending : null });
    if (url.pathname.endsWith("/refund-offer") && req.method === "GET") return json(offer);
    if (url.pathname.endsWith("/actions/refund") && req.method === "POST") { state.refundSubmissions++; return json({}, 500); }
    if (url.pathname.endsWith("/actions/ticket") && req.method === "POST") { state.ticketSubmissions++; return json({}, 500); }
    if (url.pathname === "/api/chat" && req.method === "POST") {
      res.writeHead(200, { "Content-Type": "text/event-stream" });
      res.write('event: delta\ndata: {"delta":"继续聊的受控答复"}\n\n');
      const timer = setTimeout(() => res.end(`event: done\ndata: ${JSON.stringify({ conversation_id: body.conversation_id, message_id: "301" })}\n\n`), body.message === "hold" ? 800 : 30);
      res.on("close", () => clearTimeout(timer)); return;
    }
    const files = { "/": ["index.html", "text/html"], "/static/chat.css": ["chat.css", "text/css"], "/static/chat.js": ["chat.js", "text/javascript"], "/static/conversations.js": ["conversations.js", "text/javascript"] };
    const file = files[url.pathname];
    if (!file || !fs.existsSync(path.join(root, "app/static", file[0]))) return res.writeHead(404).end();
    res.writeHead(200, { "Content-Type": file[1] + "; charset=utf-8" }); res.end(fs.readFileSync(path.join(root, "app/static", file[0])));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  return { server, state, url: `http://127.0.0.1:${server.address().port}/` };
}
async function main(config = options(process.argv.slice(2))) {
  if (config.live) return live(config);
  const output = config.output ? path.resolve(config.output) : path.join(root, ".cache/context-browser", randomUUID()); fs.mkdirSync(output, { recursive: true });
  const { chromium, executablePath } = loadBrowser();
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const results = [];
  async function scenario(name, check, settings = {}, viewport = { width: 1280, height: 900 }) {
    const fixture = await fixtureServer(settings), context = await browser.newContext({ viewport, reducedMotion: "reduce" });
    const page = await context.newPage(); page.setDefaultTimeout(2500);
    const errors = []; page.on("pageerror", (e) => errors.push(e.message));
    const result = { name, status: "FAIL", screenshot: path.join(output, name + ".png"), controlled_url: fixture.url };
    try { await page.goto(fixture.url); await check(page, fixture.state); assert.deepEqual(errors, []); result.status = "PASS"; }
    catch (error) { result.error = error.stack; }
    await page.screenshot({ path: result.screenshot, fullPage: true }); result.requests = fixture.state.records; result.pageErrors = errors;
    result.submissions = { refunds: fixture.state.refundSubmissions, tickets: fixture.state.ticketSubmissions };
    results.push(result); console.log(`${result.status} ${name}${result.error ? ": " + result.error.split("\n")[0] : ""}`);
    await context.close(); fixture.server.closeAllConnections(); await new Promise((resolve) => fixture.server.close(resolve));
  }
  const select = (page, id) => page.locator(`[data-conversation-id="${id}"]`).click();
  const loaded = (page, text) => page.getByText(text, { exact: true }).waitFor();
  const send = async (page, text) => { await page.locator("#message-input").fill(text); await page.locator("#message-input").press("Enter"); await loaded(page, "继续聊的受控答复"); await page.waitForFunction(() => !document.querySelector("#message-input").disabled); };
  try {
    await scenario("desktop-pagination-original-citations", async (page, state) => {
      await page.locator(`[data-conversation-id="${slowId}"]`).waitFor();
      assert.deepEqual(await page.locator("[data-conversation-id]").evaluateAll((nodes) => nodes.map((n) => n.dataset.conversationId)), [nextId, oldId, slowId]);
      assert.match(await page.locator(`[data-conversation-id="${oldId}"]`).innerText(), /已摘要/);
      await select(page, oldId); await loaded(page, "第二轮答复 [1]");
      assert.equal(await page.locator(".citation-button").count(), 2);
      await page.locator(".citation-button").first().click(); assert.equal(await page.locator("#source-answer").innerText(), originalChunkText);
      await page.screenshot({ path: path.join(output, "old-citation.png") }); await page.locator("#source-close").click();
      await page.locator(".citation-button").last().click(); assert.equal(await page.locator("#source-answer").innerText(), secondChunkText); await page.locator("#source-close").click();
      assert.equal(await page.locator("#messages img, #messages script").count(), 0);
      assert.doesNotMatch(await page.locator("#messages .answer-text").allTextContents().then((texts) => texts.join('\n')), /SQL原始工具正文/);
      assert.doesNotMatch(await page.locator('#messages').innerText(), /SQL原始工具正文|call-original|tool_calls|原始工具/);
      const rawResponse = await page.request.get(new URL(`/api/conversations/${oldId}/messages`, page.url()).href);
      assert.equal((await rawResponse.json()).messages.find((row) => row.id === '104').content, 'SQL原始工具正文', 'API retains raw tool content');
      assert.equal(await page.locator('.history-tool').count(), 0);
      assert.match(await page.locator(".tool-badge").innerText(), /已完成/);
      assert.ok(state.records.some((r) => r.path.endsWith("/messages") && r.query.includes("after_id=104") && r.query.includes("upto_id=107")));
      assert.equal(state.refundSubmissions, 0); assert.equal(state.ticketSubmissions, 0);
    });
    await scenario("switch-back-continue-and-refresh", async (page, state) => {
      await select(page, oldId); await loaded(page, "第二轮答复 [1]");
      await select(page, nextId); await loaded(page, "新选择答复"); await select(page, oldId); await loaded(page, "第二轮答复 [1]");
      await send(page, "继续旧会话"); assert.equal(state.records.find((r) => r.path === "/api/chat").body.conversation_id, oldId);
      await page.screenshot({ path: path.join(output, "switch-back-continue.png") });
      await page.reload(); await loaded(page, "第二轮答复 [1]"); assert.equal(await page.locator(".citation-button").count(), 2);
      assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 1);
      assert.equal(state.refundSubmissions, 0); assert.equal(state.ticketSubmissions, 0);
    });
    await scenario("late-old-history-cannot-overwrite", async (page) => {
      await select(page, slowId); await select(page, nextId); await loaded(page, "新选择答复");
      await page.waitForTimeout(900); assert.doesNotMatch(await page.locator("#messages").innerText(), /迟到/);
      assert.equal(await page.locator(`[data-conversation-id="${nextId}"]`).getAttribute("aria-current"), "true");
    });
    await scenario("all-pages-or-preserve-current", async (page) => {
      await select(page, nextId); await loaded(page, "新选择答复"); await select(page, oldId);
      await page.getByRole("status").filter({ hasText: "历史暂时无法读取" }).waitFor();
      assert.match(await page.locator("#messages").innerText(), /新选择答复/); assert.doesNotMatch(await page.locator("#messages").innerText(), /最早的问题/);
      await send(page, "失败后仍能继续");
    }, { pageFailure: true });
    await scenario("list-500-still-send", async (page, state) => {
      await send(page, "列表不可用仍可发送"); assert.equal(state.creates, 1); assert.equal(state.records.find((r) => r.path === "/api/chat").body.conversation_id, freshId);
    }, { listFailure: true });
    await scenario("stream-blocks-switch-and-new", async (page, state) => {
      await select(page, nextId); await loaded(page, "新选择答复");
      await page.locator("#message-input").fill("hold"); await page.locator("#message-input").press("Enter");
      assert.equal(await page.locator(`[data-conversation-id="${oldId}"]`).isDisabled(), true); assert.equal(await page.locator("#new-chat").isDisabled(), true);
      await page.waitForFunction(() => !document.querySelector("#message-input").disabled);
      assert.equal(state.records.filter((r) => r.path === `/api/conversations/${oldId}/messages`).length, 0);
    });
    await scenario("new-immediate-post-and-forms-local", async (page, state) => {
      await select(page, oldId); await loaded(page, "第二轮答复 [1]");
      await page.getByRole("button", { name: "建工单", exact: true }).click(); await page.locator("#ticket-description").fill("未提交草稿");
      await page.evaluate((id) => { void switchConversation(id); }, nextId); await loaded(page, "新选择答复"); assert.equal(await page.locator("#ticket-dialog").isVisible(), false);
      await page.locator("#new-chat").click(); await page.waitForFunction(() => !document.querySelector("#message-input").disabled);
      assert.equal(state.creates, 1); assert.equal(await page.locator("#messages .message").count(), 0);
      await select(page, oldId); await loaded(page, "第二轮答复 [1]");
      await page.getByRole("button", { name: "申请退款", exact: true }).click(); assert.equal(await page.locator("#refund-reason").inputValue(), "");
      await page.evaluate((id) => { void switchConversation(id); }, nextId); await loaded(page, "新选择答复"); assert.equal(await page.locator("#refund-dialog").isVisible(), false);
      assert.equal(state.refundSubmissions, 0); assert.equal(state.ticketSubmissions, 0);
    });
    await scenario("pending-and-handoff-separate-bubbles", async (page, state) => {
      await select(page, oldId); await page.locator(".order-card").waitFor(); assert.equal(state.records.filter((r) => r.path.endsWith("/actions/select-order")).length, 0);
      await page.getByRole("button", { name: "转人工", exact: true }).click(); await page.locator("#handoff-confirm").click();
      assert.equal(await page.locator(".message").filter({ hasText: "已接入人工客服" }).count(), 1);
      assert.equal(await page.locator(".message").filter({ hasText: "您好，我是客服小猫，请问有什么可以帮您的" }).count(), 1);
      assert.equal(state.refundSubmissions, 0); assert.equal(state.ticketSubmissions, 0);
    }, { withPending: true });
    await scenario("loading-history-blocks-old-actions", async (page, state) => {
      await select(page, oldId); await page.locator(".order-card").waitFor();
      await select(page, slowId);
      await page.locator(".citation-button").first().click();
      assert.equal(await page.locator("#source-dialog").isVisible(), false);
      await page.getByRole("button", { name: "选择此订单", exact: true }).click();
      await page.getByRole("button", { name: "建工单", exact: true }).click();
      assert.equal(await page.locator("#ticket-dialog").isVisible(), false);
      await loaded(page, "迟到旧答复");
      assert.equal(state.records.filter((r) => r.path.endsWith("/actions/select-order")).length, 0);
    }, { withPending: true });
    await scenario("mobile-drawer-history", async (page) => {
      assert.equal(await page.locator(".sidebar").isVisible(), false);
      await page.locator("#conversation-toggle").click(); assert.equal(await page.locator(".sidebar").isVisible(), true);
      await page.screenshot({ path: path.join(output, "mobile-drawer-open.png") });
      await select(page, oldId); await loaded(page, "第二轮答复 [1]"); assert.equal(await page.locator(".sidebar").isVisible(), false);
      assert.equal(await page.locator('.history-tool').count(), 0);
      assert.doesNotMatch(await page.locator('#messages').innerText(), /SQL原始工具正文|call-original|tool_calls|原始工具/);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    }, {}, { width: 390, height: 844 });
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(output, "results.json"), JSON.stringify({ mode: "controlled", sql_verified: false, executablePath, results }, null, 2));
  console.log(`${results.filter((r) => r.status === "PASS").length}/${results.length} PASS; controlled evidence=${output}`);
  process.exitCode = results.some((r) => r.status !== "PASS") ? 1 : 0;
}
if (require.main === module) main().catch((e) => { console.error(e.message); process.exitCode = 1; });
module.exports = { options, validateHealth };
