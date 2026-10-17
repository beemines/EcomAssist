"use strict";

const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const assert = require("node:assert/strict");
const { createRequire } = require("node:module");
const { randomUUID, createHash } = require("node:crypto");
const root = path.resolve(__dirname, "..");

// 复用已有运行时与Chromium缓存，不安装包、不接管现有浏览器或端口。
function loadBrowser() {
  let playwright;
  try { playwright = require("playwright"); } catch {
    const bundled = path.join(process.env.USERPROFILE || process.env.HOME || "", ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json");
    playwright = createRequire(bundled)("playwright");
  }
  const choices = [process.env.WORKFLOW_CHROMIUM_PATH, playwright.chromium.executablePath()];
  const caches = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(process.env.LOCALAPPDATA || "", "ms-playwright"), path.join(process.env.USERPROFILE || process.env.HOME || "", "AppData/Local/ms-playwright")];
  for (const cache of caches.filter(Boolean)) {
    if (!fs.existsSync(cache)) continue;
    for (const name of fs.readdirSync(cache).filter((entry) => /^chromium-\d+$/.test(entry)).sort().reverse()) choices.push(path.join(cache, name, "chrome-win64/chrome.exe"));
  }
  const executablePath = choices.find((entry) => entry && fs.existsSync(entry));
  return { chromium: playwright.chromium, executablePath };
}

const conversation = "9007199254740993";
const turnId = "9007199254740995";
const messageId = "9007199254740997";
const checkpoint = "1f0a6cab-7153-6045-8001-d47d0224b364";
const selectionId = "2f0a6cab-7153-6045-8001-d47d0224b364";
const offerId = "3f0a6cab-7153-6045-8001-d47d0224b364";
const reasons = [{ code: "unwanted", label: "不想要了" }, { code: "quality", label: "质量问题" }, { code: "not_as_described", label: "与描述不符" }, { code: "wrong_or_missing", label: "发错/漏发" }, { code: "damaged", label: "运输破损" }, { code: "other", label: "其他" }];
const card = { order_id: "9007199254740999", product_id: "101", product_name: "清风智能饮水机 <img src=x onerror=alert(1)>", model: "标准款 · 奶白", category: "家电", status: "已签收", amount_cents: 29900, currency: "CNY", signed_at: "2026-10-12", as_of: "2026-10-15", mock: true, fixture_version: "controlled-task8" };
const pending = { turn_id: turnId, selection_id: selectionId, checkpoint_id: checkpoint, prompt: "请选择本次需要办理的演示订单。", cards: [card, { ...card, order_id: "9007199254741001", product_name: "轻巧随行杯", amount_cents: 9900 }] };
const offer = { assistant_message_id: messageId, checkpoint_id: checkpoint, offer_id: offerId, order: card, refund_decision: "needs_review", decision_reason: "完好条件待审核", reasons };

// 生成真实SSE帧，分段写入HTTP以覆盖UTF-8与帧边界读取。
function frame(event, data) { return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`; }

// 成功流保持后端顺序，退款许可可紧接旧actions，终帧前入口必须隐藏。
function completed(withOffer = true, actions = false) {
  return frame("citations", { citations: [{ n: 1, chunk_id: "9007199254741003", section_path: "受控政策", question: "退货条件", answer: "受控政策原文 <script>不可执行</script>" }] }) +
    frame("delta", { delta: "根据政策可提交申请，实际条件待审核 [1]。" }) +
    (actions ? frame("actions", { assistant_message_id: messageId, checkpoint_id: checkpoint, options: [{ action: "handoff", label: "转人工" }, { action: "create_ticket", label: "建工单" }] }) : "") +
    (withOffer ? frame("refund_offer", offer) : "") + frame("done", { conversation_id: conversation, message_id: messageId });
}

// 夹具服务器仅监听临时回环端口，拥有内存计数，不接触应用DB、模型或8002/8003。
async function fixtureServer(settings = {}) {
  const state = { pending: null, records: [], refundAttempts: 0, selectionAttempts: 0, refreshAllowed: true, historyMessages: [], turnMetadata: {}, ...settings };
  const server = http.createServer(async (request, response) => {
    const url = new URL(request.url, "http://127.0.0.1");
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    let body;
    try { body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString()) : null; } catch { response.writeHead(400).end(); return; }
    state.records.push({ method: request.method, path: url.pathname, query: url.search, body });
    // 只返回明确受控JSON，不把回执描述为SQL证据。
    const json = (data, status = 200) => { response.writeHead(status, { "Content-Type": "application/json" }); response.end(JSON.stringify(data)); };
    // 分片包含任意中文字节与帧边界，定时器只维持本请求，关闭时清理。
    const stream = (text, delay = 0) => {
      response.writeHead(200, { "Content-Type": "text/event-stream; charset=utf-8" });
      const bytes = Buffer.from(text);
      let offset = 0;
      const timer = setInterval(() => {
        const start = offset;
        offset = Math.min(bytes.length, offset + 137);
        response.write(bytes.subarray(start, offset));
        if (offset === bytes.length) { clearInterval(timer); setTimeout(() => response.end(), delay); }
      }, 3);
      response.on("close", () => clearInterval(timer));
    };
    if (url.pathname === "/health") return json({ status: "controlled" });
    // Mirror Task8's separate read/create contracts; a GET is never a creation receipt.
    if (url.pathname === "/api/conversations" && request.method === "POST") return json({ conversation_id: conversation });
    if (url.pathname === "/api/conversations" && request.method === "GET") return json({ items: state.historyMessages.length ? [{ id: conversation, status: "active", created_at: "2026-10-17T12:00:00", updated_at: "2026-10-17T12:00:00", first_question_preview: state.historyMessages[0].content, has_summary: false }] : [], next_before_id: null });
    if (url.pathname === `/api/conversations/${conversation}/messages` && request.method === "GET") return json({ messages: state.historyMessages, upto_id: state.historyMessages.at(-1)?.id || null, next_after_id: null, turn_metadata: state.turnMetadata });
    if (url.pathname.endsWith("/pending-order")) return json({ pending: state.pending });
    if (url.pathname.endsWith("/refund-offer")) return json(state.refreshAllowed ? offer : { code: "invalid_offer" }, state.refreshAllowed ? 200 : 422);
    if (url.pathname === "/api/chat") {
      state.historyMessages = [{ id: turnId, role: "user", content: body.message, tool_calls: null, tool_call_id: null, created_at: "2026-10-17T12:00:00" }];
      state.turnMetadata = {};
      state.pending = null;
      if (body.message.startsWith("paused")) {
        state.pending = pending;
        state.selectionConflict = body.message === "paused409";
        return stream(frame("order_selection", pending) + frame("paused", { turn_id: turnId, selection_id: selectionId, checkpoint_id: checkpoint, reason: "order_selection" }));
      }
      if (body.message === "text-only") { rememberCompletion(false, { text: "可以退款，申请退款。", citations: [], withOffer: false }); return stream(frame("delta", { delta: "可以退款，申请退款。" }) + frame("done", { conversation_id: conversation, message_id: messageId })); }
      if (body.message === "incomplete") return stream(frame("delta", { delta: "尚未完成的回复" }) + frame("refund_offer", offer));
      if (body.message === "hold-offer") {
        response.writeHead(200, { "Content-Type": "text/event-stream; charset=utf-8" });
        response.write(frame("delta", { delta: "等待完成" }) + frame("refund_offer", offer));
        const timer = setTimeout(() => { rememberCompletion(false, { text: "等待完成", citations: [] }); response.end(frame("done", { conversation_id: conversation, message_id: messageId })); }, 900);
        response.on("close", () => clearTimeout(timer));
        return;
      }
      rememberCompletion(body.message === "actions");
      return stream(completed(true, body.message === "actions"));
    }
    if (url.pathname.endsWith("/actions/select-order")) {
      state.selectionAttempts += 1;
      if (state.selectionConflict && state.selectionAttempts === 1) return json({ code: "selection_conflict", message: "受控409：请重新读取待选。" }, 409);
      state.pending = null;
      rememberCompletion();
      return stream(completed());
    }
    if (url.pathname.endsWith("/actions/refund")) {
      state.refundAttempts += 1;
      const timer = setTimeout(() => json(state.refundAttempts <= (state.refundFailures || 0) ? { code: "service_unavailable" } : { request_no: "R-CONTROLLED-ONLY-001", status: "待审核", order_id: card.order_id, amount_cents: card.amount_cents, currency: "CNY" }, state.refundAttempts <= (state.refundFailures || 0) ? 503 : 200), 250);
      response.on("close", () => clearTimeout(timer));
      return;
    }
    if (url.pathname.endsWith("/actions/ticket")) return json({ ticket_no: "TK-CONTROLLED-001", status: "待处理" });
    const files = { "/": ["index.html", "text/html"], "/static/chat.js": ["chat.js", "text/javascript"], "/static/conversations.js": ["conversations.js", "text/javascript"], "/static/chat.css": ["chat.css", "text/css"] };
    const file = files[url.pathname];
    if (!file) { response.writeHead(404).end(); return; }
    response.writeHead(200, { "Content-Type": file[1] + "; charset=utf-8" });
    response.end(fs.readFileSync(path.join(root, "app/static", file[0])));
  });
  // Only completed controlled turns expose their original saved metadata on refresh.
  function rememberCompletion(actions = false, { text = "根据政策可提交申请，实际条件待审核 [1]。", citations = [{ n: 1, chunk_id: "9007199254741003", section_path: "受控政策", question: "退货条件", answer: "受控政策原文 <script>不可执行</script>" }], withOffer = true } = {}) {
    state.historyMessages.push({ id: messageId, role: "assistant", content: text, tool_calls: null, tool_call_id: null, created_at: "2026-10-17T12:00:01" });
    state.turnMetadata[messageId] = { turn_status: "completed", citations, tool_badges: [], ...(withOffer ? { refund_offer: { assistant_message_id: messageId, checkpoint_id: checkpoint, offer_id: offerId } } : {}), ...(actions ? { actions: { assistant_message_id: messageId, checkpoint_id: checkpoint, options: [{ action: "handoff", label: "转人工" }, { action: "create_ticket", label: "建工单" }] } } : {}) };
  }
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  return { state, server, url: `http://127.0.0.1:${server.address().port}/` };
}

// 清理本进程拥有的夹具连接，不停止任何应用服务。
async function closeServer(server) {
  server.closeAllConnections();
  await new Promise((resolve) => server.close(resolve));
}

// 通过真实输入和Enter发送，等待页面实际结束加载。
async function send(page, text, wait = true) {
  await page.locator("#message-input").fill(text);
  await page.locator("#message-input").press("Enter");
  if (wait) await ready(page);
}

// 页面恢复输入是终态依据，不从页面私有变量伪造结果。
async function ready(page) {
  await page.waitForFunction(() => !document.querySelector("#message-input").disabled);
}

// 用可见按钮打开退款表单并校验空白必选与键盘焦点。
async function openRefund(page) {
  await page.getByRole("button", { name: "申请退款", exact: true }).last().click();
  await page.locator("#refund-dialog").waitFor({ state: "visible" });
  assert.equal(await page.locator("#refund-reason").inputValue(), "");
  assert.equal(await page.locator("#refund-reason").evaluate((node) => node === document.activeElement), true);
}

// 每场景独立上下文和服务器，失败也保存截图、请求体、控制台及错误。
async function runControlled(browser, output) {
  const results = [];
  async function scenario(name, check, settings = {}, viewport = { width: 1200, height: 900 }) {
    const fixture = await fixtureServer(settings);
    const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
    const page = await context.newPage();
    page.setDefaultTimeout(5000);
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const result = { name, status: "FAIL", actual_url: fixture.url, screenshot: path.join(output, name + ".png") };
    try {
      await page.goto(fixture.url);
      await check({ page, state: fixture.state, context });
      assert.deepEqual(errors, []);
      result.status = "PASS";
    } catch (error) { result.error = error.stack; }
    result.requests = fixture.state.records;
    result.counts = { selectOrderPOST: fixture.state.selectionAttempts, refundPOST: fixture.state.refundAttempts, ticketPOST: fixture.state.records.filter((item) => item.path.endsWith("/actions/ticket")).length };
    result.pageErrors = errors;
    await page.screenshot({ path: result.screenshot, fullPage: true });
    results.push(result);
    fs.writeFileSync(path.join(output, "partial-results.json"), JSON.stringify(results, null, 2));
    console.log(`${result.status} ${name}${result.error ? ": " + result.error.split("\n")[0] : ""}`);
    await context.close();
    await closeServer(fixture.server);
  }
  await scenario("paused-cards", async ({ page, state }) => {
    await send(page, "paused");
    assert.equal(await page.locator(".order-card").count(), 2);
    assert.match(await page.locator(".order-card").first().innerText(), /9007199254740999/);
    assert.equal(await page.locator(".order-card img").count(), 0);
    assert.equal(await page.locator(".feedback-button").count(), 0);
    assert.equal(state.selectionAttempts, 0);
  });
  await scenario("refresh-pending-and-resume", async ({ page, state }) => {
    await send(page, "paused");
    await page.reload();
    await page.locator(".order-select").first().waitFor();
    await ready(page);
    assert.equal(state.records.filter((item) => item.path.endsWith("/pending-order")).length, 1);
    const count = await page.locator(".message.user").count();
    await page.locator(".order-select").first().dblclick();
    await ready(page);
    assert.equal(state.selectionAttempts, 1);
    assert.equal(await page.locator(".message.user").count(), count);
    assert.equal(await page.locator(".order-select:enabled").count(), 0);
    assert.deepEqual(state.records.find((item) => item.path.endsWith("/actions/select-order")).body, { turn_id: turnId, selection_id: selectionId, checkpoint_id: checkpoint, order_id: card.order_id });
    await page.getByRole("button", { name: "申请退款", exact: true }).waitFor();
  });
  await scenario("selection-409-recovery", async ({ page, state }) => {
    await send(page, "paused409");
    await page.locator(".order-select").first().click();
    await ready(page);
    assert.equal(await page.locator(".order-select:enabled").count(), 0);
    await page.getByRole("button", { name: "重新读取待选订单" }).click();
    await page.locator(".order-select:enabled").first().waitFor();
    await page.locator(".order-select:enabled").first().click();
    await ready(page);
    await page.getByRole("button", { name: "申请退款", exact: true }).waitFor();
    assert.equal(state.selectionAttempts, 2);
  });
  await scenario("new-message-invalidates-cards", async ({ page, state }) => {
    await send(page, "paused");
    await send(page, "text-only");
    assert.equal(await page.locator(".order-select:enabled").count(), 0);
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
    assert.equal(state.selectionAttempts, 0);
  });
  await scenario("offer-terminal-and-disconnect", async ({ page, state }) => {
    await send(page, "hold-offer", false);
    await page.waitForFunction(() => document.querySelector(".message.assistant .answer-text")?.textContent.includes("等待完成"));
    await page.screenshot({ path: path.join(output, "offer-before-done.png"), fullPage: true });
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
    await ready(page);
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 1);
    await page.locator("#new-chat").click();
    await send(page, "incomplete");
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
    assert.match(await page.locator(".message-note.error").innerText(), /连接中断/);
    assert.equal(state.refundAttempts, 0);
  });
  await scenario("refund-cancel-escape-keyboard", async ({ page, state }) => {
    await send(page, "offer");
    await openRefund(page);
    await page.locator("#refund-submit").click();
    assert.equal(state.refundAttempts, 0);
    assert.equal(await page.locator("#refund-dialog").isVisible(), true);
    await page.locator("#refund-reason").selectOption("quality");
    await page.locator("#refund-cancel").click();
    assert.equal(state.refundAttempts, 0);
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).evaluate((node) => node === document.activeElement), true);
    await openRefund(page);
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("#refund-dialog").isVisible(), false);
    assert.equal(state.refundAttempts, 0);
    await openRefund(page);
    await page.keyboard.press("Shift+Tab");
    assert.equal(await page.locator("#refund-dialog").evaluate((node) => node.contains(document.activeElement)), true);
  });
  await scenario("refund-submit-once-receipt", async ({ page, state }) => {
    await send(page, "offer");
    const original = await page.locator(".message.assistant .answer-text").first().innerText();
    await openRefund(page);
    assert.match(await page.locator("#refund-amount").innerText(), /299\.00/);
    assert.equal(await page.locator("#refund-amount input").count(), 0);
    await page.locator("#refund-reason").selectOption("quality");
    await page.locator("#refund-submit").dblclick();
    await page.locator("#refund-dialog").waitFor({ state: "hidden" });
    assert.equal(state.refundAttempts, 1);
    assert.equal(await page.locator(".message.assistant .answer-text").first().innerText(), original);
    assert.match(await page.locator(".message.assistant").last().innerText(), /服务通知[\s\S]*R-CONTROLLED-ONLY-001[\s\S]*待审核/);
    assert.deepEqual(state.records.find((item) => item.path.endsWith("/actions/refund")).body, { assistant_message_id: messageId, checkpoint_id: checkpoint, offer_id: offerId, reason: "quality" });
  });
  await scenario("refund-failure-retains-reason", async ({ page, state }) => {
    await send(page, "offer");
    await openRefund(page);
    await page.locator("#refund-reason").selectOption("damaged");
    await page.locator("#refund-submit").click();
    await page.locator("#refund-error").waitFor({ state: "visible" });
    assert.equal(await page.locator("#refund-reason").inputValue(), "damaged");
    assert.equal(state.refundAttempts, 1);
    await page.screenshot({ path: path.join(output, "refund-failure-before-retry.png"), fullPage: true });
    await page.locator("#refund-submit").click();
    await page.locator("#refund-dialog").waitFor({ state: "hidden" });
    assert.equal(state.refundAttempts, 2);
  }, { refundFailures: 1 });
  await scenario("refresh-refund-revalidated", async ({ page, state }) => {
    await send(page, "offer");
    const stored = await page.evaluate(() => JSON.parse(sessionStorage.getItem("mewhelp-intent-session-v1")));
    assert.deepEqual(stored, { conversationId: conversation, refundLocators: [{ assistant_message_id: messageId, checkpoint_id: checkpoint }] });
    await page.reload();
    await ready(page);
    await page.getByRole("button", { name: "申请退款", exact: true }).waitFor();
    const get = state.records.find((item) => item.path.endsWith("/refund-offer"));
    assert.equal(get.method, "GET");
    assert.equal(new URLSearchParams(get.query).get("assistant_message_id"), messageId);
    assert.equal(new URLSearchParams(get.query).get("checkpoint_id"), checkpoint);
    state.refreshAllowed = false;
    await page.reload();
    await ready(page);
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
    assert.equal(state.refundAttempts, 0);
  });
  await scenario("narrow-refund-dialog", async ({ page }) => {
    await send(page, "offer");
    await openRefund(page);
    await page.locator("#refund-reason").selectOption("not_as_described");
    const dimensions = await page.locator("#refund-dialog").evaluate((node) => ({ left: node.getBoundingClientRect().left, right: node.getBoundingClientRect().right, width: window.innerWidth, overflow: node.scrollWidth > node.clientWidth }));
    assert.ok(dimensions.left >= 0 && dimensions.right <= dimensions.width && !dimensions.overflow);
  }, {}, { width: 390, height: 720 });
  await scenario("existing-actions-citation-feedback", async ({ page, state }) => {
    await send(page, "actions");
    await page.locator(".citation-button").click();
    assert.match(await page.locator("#source-answer").innerText(), /受控政策原文/);
    await page.keyboard.press("Escape");
    await page.getByRole("button", { name: "有帮助", exact: true }).click();
    assert.equal(await page.locator(".feedback-button:enabled").count(), 0);
    await page.getByRole("button", { name: "转人工", exact: true }).click();
    await page.locator("#handoff-cancel").click();
    assert.equal(state.records.filter((item) => item.method === "POST").length, 2);
    await page.getByRole("button", { name: "转人工", exact: true }).click();
    await page.locator("#handoff-confirm").click();
    assert.match(await page.locator(".message.assistant").last().innerText(), /客服小猫/);
    assert.equal(state.records.filter((item) => item.method === "POST").length, 2);
    await page.getByRole("button", { name: "建工单", exact: true }).click();
    await page.locator("#ticket-cancel").click();
    assert.equal(state.records.filter((item) => item.path.endsWith("/actions/ticket")).length, 0);
    await page.getByRole("button", { name: "建工单", exact: true }).click();
    await page.locator("#ticket-type").selectOption("售后");
    await page.locator("#ticket-description").fill("需要人工核对退货条件");
    await page.locator("#ticket-submit").dblclick();
    await page.locator("#ticket-dialog").waitFor({ state: "hidden" });
    assert.equal(state.records.filter((item) => item.path.endsWith("/actions/ticket")).length, 1);
    assert.match(await page.locator(".message.assistant").last().innerText(), /TK-CONTROLLED-001/);
  });
  return results;
}

// 真实八组场景不拦截请求；每轮从实际SQL和原始SQLite完成根独立取证。
async function runLive(browser, url, output, args) {
  const { execFileSync } = require("node:child_process");
  const names = ["policy-no-picker", "logistics-refund-logistics", "missing-order-select-resume", "pause-refresh-restart-new-message", "refund-form-cancel-submit", "duplicate-and-cross-conversation", "repair-no-refund", "complaint-social-other"];
  const casesIndex = args.indexOf("--cases");
  const selected = casesIndex >= 0 ? args[casesIndex + 1].split(",") : names;
  assert.ok(selected.length && new Set(selected).size === selected.length && selected.every((name) => names.includes(name)), "cases必须为固定场景的非空无重复白名单");
  const resumeIndex = args.indexOf("--resume-evidence");
  const resumePath = resumeIndex >= 0 ? path.resolve(args[resumeIndex + 1]) : null;
  const previous = resumePath ? JSON.parse(fs.readFileSync(resumePath, "utf8")) : null;
  assert.ok(!previous || previous.mode === "live", "不能导入受控证据");
  const results = previous ? previous.results.filter((item) => !selected.includes(item.name)).map((item) => ({ ...item, source_evidence: resumePath })) : [];
  let submitted = null;
  const previousForm = previous?.results.find((item) => item.name === "refund-form-cancel-submit" && item.status === "PASS");
  if (previousForm) {
    const oldRequest = previousForm.requests.find((item) => item.method === "POST" && item.url.endsWith("/actions/refund"));
    submitted = { payload: JSON.parse(oldRequest.body), cid: previousForm.conversation_id,
      count: previousForm.storage_after.refunds.length, existing: previousForm.fresh_submission !== "passed",
      root: previousForm.root_evidence };
  }
  // 子进程复用锁定Python和仅本服务的检查点路径，输出文件不覆盖。
  function storage(name, cid, aid, checkpointId) {
    const file = path.join(output, name + ".json");
    const command = [path.join(root, "scripts/intent-routing-storage-evidence.py"), "--output", file];
    if (cid) command.push("--conversation-id", cid);
    if (aid) command.push("--assistant-id", aid);
    if (checkpointId) command.push("--checkpoint-id", checkpointId);
    execFileSync(path.join(root, ".venv/Scripts/python.exe"), command, { cwd: root, windowsHide: true, env: { ...process.env, PYTHONUTF8: "1", PYTHONPATH: root }, stdio: "pipe" });
    return JSON.parse(fs.readFileSync(file, "utf8"));
  }
  const baseline = previous?.baseline || storage("baseline");
  async function scenario(name, check) {
    if (!selected.includes(name)) return;
    const context = await browser.newContext({ viewport: { width: 1200, height: 900 }, reducedMotion: "reduce" });
    const page = await context.newPage();
    page.setDefaultTimeout(260000);
    const result = { name, status: "FAIL", requests: [], responses: [], turns: [], pageerrors: [], screenshot: path.join(output, name + ".png") };
    const responses = [];
    page.on("pageerror", (error) => result.pageerrors.push(error.message));
    page.on("request", (request) => { if (new URL(request.url()).pathname.startsWith("/api/")) result.requests.push({ url: request.url(), method: request.method(), body: request.postData() }); });
    page.on("response", (response) => { if (new URL(response.url()).pathname.startsWith("/api/")) responses.push(response.body().then((body) => result.responses.push({ url: response.url(), status: response.status(), body: body.toString() })).catch((error) => result.responses.push({ url: response.url(), error: error.message }))); });
    // 每个收费轮完整终态之后才继续；服务error/paused有明确独立边界。
    async function turn(question, { paused = false, intent, route } = {}) {
      const before = result.responses.length;
      await send(page, question);
      await Promise.allSettled(responses);
      const stream = result.responses.slice(before).find((r) => r.url.endsWith("/api/chat"));
      assert.ok(stream && stream.status === 200 && !stream.body.includes("event: error"), "当前轮出错，停止该依赖链");
      assert.ok(stream.body.includes(paused ? "event: paused" : "event: done"), "缺少完整终态");
      const session = await page.evaluate(() => JSON.parse(sessionStorage.getItem("mewhelp-intent-session-v1")));
      const state = storage(name + "-turn-" + (result.turns.length + 1), session.conversationId);
      result.conversation_id = session.conversationId;
      const observed = { question, ...state };
      result.turns.push(observed);
      if (!paused) {
        assert.equal(state.sql_evidence?.verified, true, "SQL助手与持久完成根不一致");
        if (intent) assert.equal(state.root_evidence.intent, intent);
        if (route) assert.equal(state.root_evidence.route, route);
        result.sql_evidence = state.sql_evidence;
        result.root_evidence = state.root_evidence;
      } else assert.equal(state.root_evidence?.turn_status, "awaiting_order");
      return state;
    }
    try {
      await page.goto(url);
      await ready(page);
      await check({ page, context, result, turn });
      assert.deepEqual(result.pageerrors, []);
      result.status = result.gate_blocked ? "BLOCKED" : "PASS";
    } catch (error) { result.error = error.stack; }
    await page.screenshot({ path: result.screenshot, fullPage: true });
    await Promise.allSettled(responses);
    results.push(result);
    fs.writeFileSync(path.join(output, "partial-results.json"), JSON.stringify({ mode: "live", baseline, results }, null, 2) + "\n");
    await context.close();
  }
  await scenario("policy-no-picker", async ({ page, turn }) => {
    const state = await turn("退换货政策是怎样的？", { intent: "商品咨询", route: "knowledge" });
    assert.equal(await page.locator(".order-select").count(), 0);
    assert.equal(state.root_evidence.stage_usage?.expansion, undefined);
    assert.equal(state.root_evidence.tool_call_count, 1);
  });
  await scenario("logistics-refund-logistics", async ({ page, result, turn }) => {
    const prior = previous?.results.find((item) => item.name === "logistics-refund-logistics");
    if (prior && prior.turns.length >= 2) {
      await restoreObservedSession(page, prior.conversation_id);
      result.conversation_id = prior.conversation_id;
      result.turns = prior.turns.map((item) => ({ ...item, source_evidence: resumePath }));
    } else {
      await turn("订单1001的物流到哪里了？", { intent: "物流", route: "business" });
      await turn("它能退吗？", { intent: "退款退货", route: "after_sales" });
    }
    const state = await turn("不要退款，我要查订单1001物流。", { intent: "物流", route: "business" });
    assert.equal(state.root_evidence.raw_question, state.root_evidence.resolved_question);
    assert.equal(state.root_evidence.tool_call_count > 0, true, "物流事实必须来自本轮真实读取");
  });
  await scenario("missing-order-select-resume", async ({ page, result, turn }) => {
    const paused = await turn("我想申请退货，但还没有选择订单。", { paused: true });
    const userCount = paused.messages.filter((m) => m.role === "user").length;
    await page.locator(".order-select:enabled").filter({ hasText: "选择" }).first().click();
    await ready(page);
    const resumed = storage("missing-order-resumed", result.conversation_id);
    assert.equal(resumed.sql_evidence?.verified, true);
    assert.equal(resumed.messages.filter((m) => m.role === "user").length, userCount);
    assert.equal(resumed.root_evidence.stage_usage.understanding.actual_calls, paused.root_evidence.stage_usage.understanding.actual_calls);
    result.sql_evidence = resumed.sql_evidence; result.root_evidence = resumed.root_evidence;
    await page.getByRole("button", { name: "申请退款", exact: true }).waitFor();
  });
  await scenario("pause-refresh-restart-new-message", async ({ page, result, turn }) => {
    const priorPauseFile = resumePath && path.join(path.dirname(resumePath), "pause-refresh-restart-new-message-turn-1.json");
    if (priorPauseFile && fs.existsSync(priorPauseFile)) {
      const old = JSON.parse(fs.readFileSync(priorPauseFile, "utf8"));
      result.conversation_id = old.root_evidence.conversation_id;
      result.turns.push({ ...old, source_evidence: priorPauseFile });
      await restoreObservedSession(page, result.conversation_id);
    } else await turn("我想退货退款，请让我选择订单。", { paused: true });
    await page.reload(); await ready(page);
    await page.locator(".order-select:enabled").first().waitFor();
    const restartIndex = args.indexOf("--restart-script");
    assert.ok(restartIndex >= 0, "真实重启脚本缺失，不能将刷新冒充重启");
    execFileSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", args[restartIndex + 1]], { cwd: root, windowsHide: true, env: process.env, stdio: "ignore" });
    await page.reload(); await ready(page);
    await page.locator(".order-select:enabled").first().waitFor();
    const pendingResponse = await contextRequest(page, `/api/conversations/${result.conversation_id}/pending-order`, "GET");
    const old = pendingResponse.json.pending;
    await turn("你好", { intent: "闲聊", route: "social" });
    assert.equal(await page.locator(".order-select:enabled").count(), 0);
    const rejected = await contextRequest(page, `/api/conversations/${result.conversation_id}/actions/select-order`, "POST", { turn_id: old.turn_id, selection_id: old.selection_id, checkpoint_id: old.checkpoint_id, order_id: old.cards[0].order_id });
    assert.equal(rejected.status, 409);
  });
  await scenario("refund-form-cancel-submit", async ({ page, result, turn }) => {
    const source = results.find((item) => item.name === "missing-order-select-resume" && item.status === "PASS");
    let state;
    if (source) {
      result.conversation_id = source.conversation_id;
      await restoreObservedSession(page, source.conversation_id, source.root_evidence);
      state = storage("form-source-original", source.conversation_id, source.root_evidence.assistant_message_id, source.root_evidence.checkpoint_id);
      result.sql_evidence = state.sql_evidence; result.root_evidence = state.root_evidence;
      result.reused_offer_source = source.source_evidence || "same-run-missing-order-select-resume";
    } else state = await turn("订单1001能申请退货退款吗？", { intent: "退款退货", route: "after_sales" });
    assert.ok(await page.getByRole("button", { name: "申请退款", exact: true }).count(), "当前完成根没有退款许可，停止依赖动作");
    await openRefund(page);
    await page.locator("#refund-submit").click();
    assert.equal(result.requests.filter((r) => r.url.endsWith("/actions/refund")).length, 0);
    await page.locator("#refund-cancel").click();
    const afterCancel = storage("form-after-cancel", result.conversation_id);
    assert.equal(afterCancel.refunds.length, baseline.refunds.length);
    await openRefund(page); await page.locator("#refund-reason").selectOption("unwanted");
    await page.locator("#refund-submit").dblclick();
    const existing = baseline.refunds.find((r) => r.user_id === "demo-user" && r.order_id === "1001");
    if (existing) await page.locator("#refund-error").waitFor({ state: "visible" });
    else await page.locator("#refund-dialog").waitFor({ state: "hidden" });
    const final = storage("form-after-submit", result.conversation_id);
    await Promise.allSettled([]);
    if (existing) {
      await page.locator("#refund-error").waitFor({ state: "visible" });
      assert.equal(final.refunds.length, baseline.refunds.length);
      result.fresh_submission = "not_executed_existing_pending";
    } else {
      await page.locator("#refund-dialog").waitFor({ state: "hidden" });
      assert.equal(final.refunds.length, baseline.refunds.length + 1);
      assert.match(await page.locator(".message.assistant").last().innerText(), /待审核/);
      result.fresh_submission = "passed";
    }
    const request = result.requests.find((r) => r.url.endsWith("/actions/refund"));
    submitted = { payload: JSON.parse(request.body), cid: result.conversation_id, checkpoint: state.root_evidence.checkpoint_id, count: final.refunds.length, existing: !!existing };
    result.storage_after = final;
    assert.deepEqual(final.tickets, baseline.tickets);
    for (const original of baseline.conversations) assert.deepEqual(final.conversations.find((r) => r.id === original.id), original);
    const row = final.refunds.find((r) => r.user_id === "demo-user" && r.order_id === "1001");
    assert.equal(row.status, "待审核"); assert.equal(row.amount_cents, 19900);
    assert.ok(row.policy_snapshot && row.order_snapshot && row.decision_snapshot);
  });
  await scenario("duplicate-and-cross-conversation", async ({ page, result, turn }) => {
    assert.ok(submitted, "原提交失败，禁止继续依赖申请动作");
    if (submitted.root) {
      await restoreObservedSession(page, submitted.cid, submitted.root);
      await openRefund(page);
      await page.screenshot({ path: path.join(output, "old-root-valid-form-after-fix.png"), fullPage: true });
      await page.locator("#refund-cancel").click();
    }
    const repeated = await contextRequest(page, `/api/conversations/${submitted.cid}/actions/refund`, "POST", submitted.payload);
    assert.equal(repeated.status, submitted.existing ? 409 : 200);
    const conflict = await contextRequest(page, `/api/conversations/${submitted.cid}/actions/refund`, "POST", { ...submitted.payload, reason: "damaged" });
    assert.equal(conflict.status, 409);
    await page.locator("#new-chat").click();
    await turn("我想申请退货，请让我选择订单。", { paused: true });
    await page.locator(".order-select:enabled").first().click(); await ready(page);
    const resumed = storage("cross-conversation-resumed", result.conversation_id);
    assert.equal(resumed.sql_evidence?.verified, true);
    result.sql_evidence = resumed.sql_evidence; result.root_evidence = resumed.root_evidence;
    assert.ok(await page.getByRole("button", { name: "申请退款", exact: true }).count(), "当前完成根没有退款许可，停止依赖动作");
    await openRefund(page); await page.locator("#refund-reason").selectOption("unwanted"); await page.locator("#refund-submit").click();
    await page.locator("#refund-error").waitFor({ state: "visible" });
    const final = storage("duplicates-after", result.conversation_id);
    assert.equal(final.refunds.length, submitted.count);
    result.storage_after = final;
  });
  await scenario("repair-no-refund", async ({ page, result, turn }) => {
    const state = await turn("订单1002不要退货，只想寄修。", { intent: "售后", route: "after_sales" });
    if (state.root_evidence.refund_decision === null && /资料不足/.test(state.root_evidence.final_answer)) {
      result.gate_blocked = true;
      result.functional_shortfall = "前置知识闸拒答，Agent未执行，不能计not_applicable完成";
    } else assert.equal(state.root_evidence.refund_decision, "not_applicable");
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
  });
  await scenario("complaint-social-other", async ({ page, turn }) => {
    await turn("我要投诉你们的维修服务。", { intent: "投诉", route: "complaint" });
    const social = await turn("谢谢您！", { intent: "闲聊", route: "social" });
    assert.deepEqual(social.root_evidence.stage_usage, {});
    await turn("蓝色星期八能替我给月亮签收吗？", { intent: "其他", route: "other" });
    assert.equal(await page.getByRole("button", { name: "申请退款", exact: true }).count(), 0);
  });
  const after = storage("final");
  fs.writeFileSync(path.join(output, "storage-summary.json"), JSON.stringify({ baseline, after }, null, 2) + "\n");
  return results;
}

// 仅恢复实际观测到的结构定位；页面随后必须经公开GET重验原根，不注入订单/金额/政策/许可。
async function restoreObservedSession(page, cid, rootEvidence) {
  await page.evaluate(({ cid, locator }) => sessionStorage.setItem("mewhelp-intent-session-v1", JSON.stringify({ conversationId: cid, refundLocators: locator ? [locator] : [] })),
    { cid, locator: rootEvidence ? { assistant_message_id: rootEvidence.assistant_message_id, checkpoint_id: rootEvidence.checkpoint_id } : null });
  await page.reload(); await ready(page);
  if (rootEvidence) await page.getByRole("button", { name: "申请退款", exact: true }).waitFor();
}

// 仅用于明确已授权幂等/过期请求；不调用聊天接口或页面私有函数。
async function contextRequest(page, endpoint, method, body) {
  return page.evaluate(async ({ endpoint, method, body }) => {
    const response = await fetch(endpoint, { method, headers: { "Content-Type": "application/json" }, ...(body ? { body: JSON.stringify(body) } : {}) });
    return { status: response.status, json: await response.json() };
  }, { endpoint, method, body });
}

// 入口明确区分受控与真实，保留每次独立证据目录和所有失败，不覆盖旧结果。
async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--serve-fixture")) {
    const fixture = await fixtureServer();
    console.log(`CONTROLLED_FIXTURE_URL=${fixture.url}`);
    return;
  }
  const mode = args[args.indexOf("--mode") + 1];
  const requestedUrl = args[args.indexOf("--url") + 1];
  assert.ok(args.includes("--mode") && args.includes("--url") && ["controlled", "live"].includes(mode), "用法：node scripts/verify-intent-routing-browser.cjs --url http://127.0.0.1:8003/ --mode controlled|live");
  const output = path.join(root, ".cache/intent-routing-browser", mode, randomUUID());
  fs.mkdirSync(output, { recursive: true });
  const { chromium, executablePath } = loadBrowser();
  console.log(`MODE=${mode}; requested=${requestedUrl}; browser=${executablePath || "managed"}; output=${output}`);
  if (mode === "controlled") console.log("受控模式浏览器连接自有临时本机夹具；requested URL不被启动、修改或拦截。无实际SQL或模型。");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const results = mode === "controlled" ? await runControlled(browser, output) : await runLive(browser, requestedUrl, output, args);
    fs.writeFileSync(path.join(output, "results.json"), JSON.stringify({ mode, requested_url: requestedUrl, executablePath, browser_version: browser.version(), sql_verified: false,
      backend_source_hash: createHash("sha256").update(["app/workflow/agent.py", "app/workflow/nodes.py", "app/workflow/prompts.py", "app/workflow/understanding.py", "app/refunds/repository.py", "app/orders/demo_orders.json"].map((file) => fs.readFileSync(path.join(root, file), "utf8")).join("\n")).digest("hex"),
      resumed_from: args.includes("--resume-evidence") ? path.resolve(args[args.indexOf("--resume-evidence") + 1]) : null, results }, null, 2) + "\n");
    console.log(`${results.filter((item) => item.status === "PASS").length}/${results.length} PASS; evidence=${output}`);
    process.exitCode = results.some((item) => item.status !== "PASS") ? 1 : 0;
  } finally { await browser.close(); }
}

if (require.main === module) main().catch((error) => { console.error(error.stack); process.exitCode = 1; });
