"use strict";

const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const assert = require("node:assert/strict");
const { createRequire } = require("node:module");
const { randomUUID } = require("node:crypto");
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
  const state = { pending: null, records: [], refundAttempts: 0, selectionAttempts: 0, refreshAllowed: true, ...settings };
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
    if (url.pathname === "/api/conversations") return json({ conversation_id: conversation });
    if (url.pathname.endsWith("/pending-order")) return json({ pending: state.pending });
    if (url.pathname.endsWith("/refund-offer")) return json(state.refreshAllowed ? offer : { code: "invalid_offer" }, state.refreshAllowed ? 200 : 422);
    if (url.pathname === "/api/chat") {
      state.pending = null;
      if (body.message.startsWith("paused")) {
        state.pending = pending;
        state.selectionConflict = body.message === "paused409";
        return stream(frame("order_selection", pending) + frame("paused", { turn_id: turnId, selection_id: selectionId, checkpoint_id: checkpoint, reason: "order_selection" }));
      }
      if (body.message === "text-only") return stream(frame("delta", { delta: "可以退款，申请退款。" }) + frame("done", { conversation_id: conversation, message_id: messageId }));
      if (body.message === "incomplete") return stream(frame("delta", { delta: "尚未完成的回复" }) + frame("refund_offer", offer));
      if (body.message === "hold-offer") {
        response.writeHead(200, { "Content-Type": "text/event-stream; charset=utf-8" });
        response.write(frame("delta", { delta: "等待完成" }) + frame("refund_offer", offer));
        const timer = setTimeout(() => response.end(frame("done", { conversation_id: conversation, message_id: messageId })), 900);
        response.on("close", () => clearTimeout(timer));
        return;
      }
      return stream(completed(true, body.message === "actions"));
    }
    if (url.pathname.endsWith("/actions/select-order")) {
      state.selectionAttempts += 1;
      if (state.selectionConflict && state.selectionAttempts === 1) return json({ code: "selection_conflict", message: "受控409：请重新读取待选。" }, 409);
      state.pending = null;
      return stream(completed());
    }
    if (url.pathname.endsWith("/actions/refund")) {
      state.refundAttempts += 1;
      const timer = setTimeout(() => json(state.refundAttempts <= (state.refundFailures || 0) ? { code: "service_unavailable" } : { request_no: "R-CONTROLLED-ONLY-001", status: "待审核", order_id: card.order_id, amount_cents: card.amount_cents, currency: "CNY" }, state.refundAttempts <= (state.refundFailures || 0) ? 503 : 200), 250);
      response.on("close", () => clearTimeout(timer));
      return;
    }
    if (url.pathname.endsWith("/actions/ticket")) return json({ ticket_no: "TK-CONTROLLED-001", status: "待处理" });
    const files = { "/": ["index.html", "text/html"], "/static/chat.js": ["chat.js", "text/javascript"], "/static/chat.css": ["chat.css", "text/css"] };
    const file = files[url.pathname];
    if (!file) { response.writeHead(404).end(); return; }
    response.writeHead(200, { "Content-Type": file[1] + "; charset=utf-8" });
    response.end(fs.readFileSync(path.join(root, "app/static", file[0])));
  });
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

// 真实模式不安装路由拦截，不伪造SQL结果；只记录实际服务请求和响应，落库由Task9另核。
async function runLive(browser, url, output, args) {
  const context = await browser.newContext({ viewport: { width: 1200, height: 900 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  page.setDefaultTimeout(260000);
  const result = { name: "live-order-refund", status: "FAIL", requests: [], responses: [], sql_verified: false, screenshot: path.join(output, "live-order-refund.png") };
  const responses = [];
  page.on("request", (request) => { if (new URL(request.url()).pathname.startsWith("/api/")) result.requests.push({ url: request.url(), method: request.method(), body: request.postData() }); });
  page.on("response", (response) => { if (new URL(response.url()).pathname.startsWith("/api/")) responses.push(response.body().then((body) => result.responses.push({ url: response.url(), status: response.status(), body: body.toString() })).catch((error) => result.responses.push({ url: response.url(), error: error.message }))); });
  try {
    await page.goto(url);
    const queryIndex = args.indexOf("--message");
    await send(page, queryIndex >= 0 ? args[queryIndex + 1] : "我想退货退款，请先帮我选择订单。");
    if (await page.locator(".order-select:enabled").count()) {
      await page.screenshot({ path: path.join(output, "live-paused.png"), fullPage: true });
      await page.reload();
      await ready(page);
      await page.locator(".order-select:enabled").first().click();
      await ready(page);
    }
    await openRefund(page);
    await page.screenshot({ path: path.join(output, "live-form.png"), fullPage: true });
    await page.locator("#refund-cancel").click();
    assert.equal(result.requests.filter((item) => item.method === "POST" && item.url.endsWith("/actions/refund")).length, 0);
    if (args.includes("--submit-refund")) {
      await openRefund(page);
      await page.locator("#refund-reason").selectOption("unwanted");
      await page.locator("#refund-submit").click();
      await page.locator("#refund-dialog").waitFor({ state: "hidden" });
      assert.equal(result.requests.filter((item) => item.method === "POST" && item.url.endsWith("/actions/refund")).length, 1);
      assert.match(await page.locator(".message.assistant").last().innerText(), /待审核/);
    }
    result.status = "PASS";
  } catch (error) { result.error = error.stack; }
  await page.screenshot({ path: result.screenshot, fullPage: true });
  await Promise.allSettled(responses);
  await context.close();
  return [result];
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
    fs.writeFileSync(path.join(output, "results.json"), JSON.stringify({ mode, requested_url: requestedUrl, executablePath, browser_version: browser.version(), sql_verified: false, results }, null, 2) + "\n");
    console.log(`${results.filter((item) => item.status === "PASS").length}/${results.length} PASS; evidence=${output}`);
    process.exitCode = results.some((item) => item.status === "FAIL") ? 1 : 0;
  } finally { await browser.close(); }
}

if (require.main === module) main().catch((error) => { console.error(error.stack); process.exitCode = 1; });
