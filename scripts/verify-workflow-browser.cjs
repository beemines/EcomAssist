"use strict";

const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const assert = require("node:assert/strict");
const { createRequire } = require("node:module");
const root = path.resolve(__dirname, "..");

// 优先使用项目或 NODE_PATH 包，桌面运行时目录仅作可探测的备用路径。
function loadPlaywright() {
  try { return require("playwright"); } catch {}
  const bundled = path.join(process.env.USERPROFILE || process.env.HOME || "", ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules", "playwright", "package.json");
  if (fs.existsSync(bundled)) return createRequire(bundled)("playwright");
  throw new Error("请安装 playwright 或设置 NODE_PATH 为已安装的包目录。");
}

// 浏览器支持环境覆盖、Playwright 默认缓存以及 Windows 用户缓存探测。
function browserPath(chromium) {
  const choices = [process.env.WORKFLOW_CHROMIUM_PATH, chromium.executablePath()];
  const caches = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(process.env.LOCALAPPDATA || "", "ms-playwright"), path.join(process.env.USERPROFILE || process.env.HOME || "", "AppData", "Local", "ms-playwright")];
  for (const cache of caches.filter(Boolean)) {
    if (!fs.existsSync(cache)) continue;
    for (const name of fs.readdirSync(cache).filter((entry) => /^chromium-\d+$/.test(entry)).sort().reverse()) {
      choices.push(path.join(cache, name, "chrome-win64", "chrome.exe"));
    }
  }
  return choices.find((choice) => choice && fs.existsSync(choice));
}

// 固定受控身份与协议帧只用作验收数据，不访问模型或真实业务数据。
const conversation = "9007199254740993";
const messageId = "9007199254740995";
const checkpoint = "1f0a6cab-7153-6045-8001-d47d0224b364";
const options = [{ action: "handoff", label: "转人工" }, { action: "create_ticket", label: "建工单" }];
const offer = { assistant_message_id: messageId, checkpoint_id: checkpoint, options };
const done = { conversation_id: conversation, message_id: messageId };
// 生成完整 SSE 帧，确保浏览器真实经过解码、解析和页面渲染链路。
function frame(event, data) { return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`; }
// 拼装不同故障/成功场景，避免通过页面函数调用伪装浏览器验收。
function fixture(name) {
  const delta = frame("delta", { delta: "这是受控回复 <img src=x onerror=alert(1)>。" });
  const actions = frame("actions", offer);
  const final = frame("done", done);
  const tool = (phase, id, toolName, origin = "agent") => frame("status", { phase, tool_call_id: id, tool_name: toolName, origin, ...(phase === "tool_completed" ? { status: "success" } : {}) }); // 为每个调用生成独立状态帧。
  if (name === "traces") return tool("tool_running", "order", "query_order") + tool("tool_completed", "order", "query_order") + tool("tool_running", "logistics", "query_logistics") + tool("tool_completed", "logistics", "query_logistics") + delta + final;
  if (name === "workflow") return tool("tool_running", "faq", "query_faq", "workflow") + tool("tool_completed", "faq", "query_faq", "workflow") + delta + final;
  if (name === "citation") return frame("citations", { citations: [{ n: 1, chunk_id: "42", section_path: "受控来源", question: "原文问题", answer: "原文答案 <script>不执行</script>" }] }) + frame("delta", { delta: "参考资料 [1]。" }) + final;
  if (name === "partial") return tool("tool_running", "order", "query_order") + delta;
  if (name === "stopped") return tool("tool_running", "order", "query_order");
  if (name === "error") return delta + actions + frame("error", { message: "受控故障" });
  if (name === "disconnect") return delta + actions;
  if (name === "mismatch") return delta + actions + frame("done", { ...done, message_id: "104" });
  if (name === "duplicate") return delta + actions + actions + final;
  if (name === "after-actions") return delta + actions + frame("delta", { delta: "不合法尾帧" }) + final;
  if (name === "after-done") return delta + actions + final + actions;
  if (name === "unknown-option") return delta + frame("actions", { ...offer, options: [{ action: "refund", label: "退款" }] }) + final;
  if (name === "duplicate-option") return delta + frame("actions", { ...offer, options: [options[0], options[0]] }) + final;
  if (name === "bad-label") return delta + frame("actions", { ...offer, options: [{ action: "handoff", label: "<img>" }] }) + final;
  if (name === "bad-checkpoint") return delta + frame("actions", { ...offer, checkpoint_id: "../../unsafe" }) + final;
  if (name === "extra-actions") return delta + frame("actions", { ...offer, description: "伪造" }) + final;
  if (name === "before-delta") return actions + delta + final;
  if (name === "numeric-identity") return delta + frame("actions", { ...offer, assistant_message_id: 104 }) + final;
  if (name === "extra-option") return delta + frame("actions", { ...offer, options: [{ ...options[0], url: "/unsafe" }] }) + final;
  if (name === "empty-options") return delta + frame("actions", { ...offer, options: [] }) + final;
  if (name === "no-actions") return delta + frame("done", { ...done, message_id: "9007199254740997" });
  return delta + actions + final;
}

// 自有测试服务器只服务固定静态文件、健康夹具与受控流，结束后由本进程关闭。
function createFixtureServer() {
  return http.createServer((request, response) => {
    const url = new URL(request.url, "http://127.0.0.1");
    if (url.pathname === "/__workflow_fixture") {
      response.writeHead(200, { "Content-Type": "text/event-stream; charset=utf-8", "Access-Control-Allow-Origin": "*" });
      const name = url.searchParams.get("name");
      if (name === "pending" || name === "stopped") {
        response.write(name === "pending" ? frame("delta", { delta: "等待完成。" }) + frame("actions", offer) : fixture(name));
        const timer = setTimeout(() => response.end(name === "pending" ? frame("done", done) : ""), 900); // 延迟终帧以验证未完成时不可确认与用户停止。
        response.on("close", () => clearTimeout(timer)); // 浏览器取消后立即清理本流定时器。
      } else response.end(fixture(name));
      return;
    }
    const files = { "/": ["index.html", "text/html"], "/static/chat.js": ["chat.js", "text/javascript"], "/static/chat.css": ["chat.css", "text/css"] };
    if (url.pathname === "/health") { response.writeHead(200, { "Content-Type": "application/json" }); response.end('{"status":"fixture"}'); return; }
    const file = files[url.pathname];
    if (!file) { response.writeHead(404); response.end(); return; }
    response.writeHead(200, { "Content-Type": `${file[1]}; charset=utf-8` });
    response.end(fs.readFileSync(path.join(root, "app", "static", file[0])));
  });
}

// 绑定失败不终止或替换其他服务；只有明确空闲的本机 8002 才供静态页面使用。
async function listen(server, port) {
  return new Promise((resolve, reject) => {
    server.once("error", reject); // 把占用错误交给调用者选择已有静态页面。
    server.listen(port, "127.0.0.1", () => { server.removeListener("error", reject); resolve(server.address().port); }); // 仅监听回环地址。
  });
}

// 独立页面记录显式确认请求，聊天只改写到自有夹具，不拦截静态或任意其他网络接口。
async function controlledPage(browser, url, transport, ticketFailures = 0, viewport = { width: 1200, height: 900 }) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
  const page = await context.newPage();
  page.setDefaultTimeout(3000);
  const records = [];
  const requests = [];
  page.on("request", (request) => requests.push({ url: request.url(), method: request.method() })); // 记录全部网络请求以证明人工按钮零 fetch。
  let attempts = 0;
  await page.route(new URL("/api/conversations", url).href, (route) => route.fulfill({ json: { conversation_id: conversation } })); // 固定会话创建夹具。
  await page.route(new URL("/api/chat", url).href, (route) => {
    const name = route.request().postDataJSON().message;
    return route.continue({ url: `${transport}/__workflow_fixture?name=${encodeURIComponent(name)}` }); // 真实网络分段读取，不缓存 SSE 终帧。
  });
  await page.route(new URL(`/api/conversations/${conversation}/actions/ticket`, url).href, (route) => {
    records.push({ method: route.request().method(), body: route.request().postDataJSON(), url: route.request().url() });
    attempts += 1;
    return route.fulfill(attempts <= ticketFailures ? { status: 503, json: { message: "受控失败，请重试。" } } : { json: { ticket_no: "TK-CONTROLLED-001", status: "待处理" } }); // 失败/成功明确标注为受控工单。
  });
  await page.goto(url);
  return { context, page, records, requests };
}

// 仅从真实输入框提交消息，完成等待依赖输入恢复而不是直接读取页面内部变量。
async function send(page, name, wait = true) {
  await page.locator("#message-input").fill(name);
  await page.locator("#message-input").press("Enter");
  if (wait) await page.locator("#message-input").waitFor({ state: "visible" }).then(() => page.waitForFunction(() => !document.querySelector("#message-input").disabled)); // 等待真实页面恢复输入。
}

// 原生 confirm 的接受/取消由一次性监听处理，取消不应锁定按钮或请求接口。
async function confirmClick(page, button, accept) {
  page.once("dialog", (dialog) => accept ? dialog.accept() : dialog.dismiss()); // 每次仅处理当前按钮确认。
  await button.click();
}

// 逐场景独立执行并留截图，失败继续收集，最后统一返回非零退出码。
async function runControlled(browser, url, transport, output) {
  const results = [];
  // 每个场景使用隔离页面，记录失败证据并确保关闭上下文。
  async function scenario(name, check, failures = 0, viewport) {
    const state = await controlledPage(browser, url, transport, failures, viewport);
    try {
      await check(state);
      results.push({ name, status: "PASS" });
    } catch (error) { results.push({ name, status: "FAIL", error: error.message }); }
    await state.page.screenshot({ path: path.join(output, `${name}.png`), fullPage: true });
    await state.context.close();
    console.log(`${results.at(-1).status} ${name}${results.at(-1).error ? ": " + results.at(-1).error.split("\n")[0] : ""}`);
  }
  await scenario("multi-tool-traces", async ({ page }) => {
    await send(page, "traces");
    assert.equal(await page.locator(".tool-badge").count(), 2, "两步查询应显示两个独立徽章");
    assert.equal(await page.locator('.tool-badge[data-status="success"]').count(), 2);
  }); // 验证真实页面多工具轨迹。
  await scenario("workflow-retrieval", async ({ page }) => {
    await send(page, "workflow");
    assert.match(await page.locator(".tool-badge").innerText(), /检索/);
  }); // Workflow 检索不用 Agent 选择文案。
  await scenario("independent-handoff-ticket", async ({ page, records, requests }) => {
    await send(page, "complaint");
    const handoff = page.getByRole("button", { name: "转人工", exact: true });
    const ticket = page.getByRole("button", { name: "建工单", exact: true });
    assert.equal(await page.locator(".support-action").count(), 2, "投诉完成后应有两个独立按钮");
    assert.equal(records.length, 0);
    const initialRequests = requests.length;
    await confirmClick(page, handoff, false);
    assert.equal(await handoff.isEnabled(), true);
    assert.equal(records.length, 0);
    assert.equal(requests.length, initialRequests);
    await confirmClick(page, handoff, true);
    assert.equal(records.length, 0);
    assert.equal(requests.length, initialRequests);
    assert.equal(await handoff.isDisabled(), true);
    assert.equal(await ticket.isEnabled(), true);
    assert.deepEqual(await page.locator(".handoff-line").allTextContents(), ["已转接人工客服", "您好，我是客服小猫，请问有什么可以帮您的"]);
    await confirmClick(page, ticket, false);
    assert.equal(await ticket.isEnabled(), true);
    assert.equal(records.length, 0);
    assert.equal(requests.length, initialRequests);
    await confirmClick(page, ticket, true);
    await page.getByText("工单已创建 · TK-CONTROLLED-001", { exact: true }).waitFor();
    assert.equal(records.length, 1);
    assert.deepEqual(records[0].body, { assistant_message_id: messageId, checkpoint_id: checkpoint });
    assert.equal(records[0].method, "POST");
    assert.equal(await ticket.isDisabled(), true);
    assert.equal(await page.locator(".answer-text img").count(), 0);
  }); // 两个确认独立，人工确认零 HTTP，工单请求严格两字段。
  await scenario("ticket-only-and-old-offer", async ({ page, records }) => {
    await send(page, "complaint");
    await send(page, "no-actions");
    const ticket = page.getByRole("button", { name: "建工单", exact: true });
    await confirmClick(page, ticket, true);
    await page.getByText("工单已创建 · TK-CONTROLLED-001", { exact: true }).waitFor();
    assert.equal(records.length, 1);
    assert.deepEqual(records[0].body, { assistant_message_id: messageId, checkpoint_id: checkpoint });
    assert.equal(await page.getByText("已转接人工客服", { exact: true }).count(), 0);
    assert.equal(await page.getByRole("button", { name: "转人工", exact: true }).isEnabled(), true);
  }); // 新轮完成不覆盖旧回复的动作身份。
  await scenario("ticket-retry", async ({ page, records }) => {
    await send(page, "complaint");
    const ticket = page.getByRole("button", { name: "建工单", exact: true });
    await confirmClick(page, ticket, true);
    await page.getByText("工单创建失败，请重试。", { exact: true }).waitFor();
    assert.equal(await ticket.isEnabled(), true);
    await confirmClick(page, ticket, true);
    await page.getByText("工单已创建 · TK-CONTROLLED-001", { exact: true }).waitFor();
    assert.equal(records.length, 2);
    assert.deepEqual(records[0].body, records[1].body);
    assert.equal(await page.getByText("已转接人工客服", { exact: true }).count(), 0);
  }, 1); // 失败恢复自身按钮，重复确认保留同一回复身份。
  await scenario("actions-wait-for-done", async ({ page, records }) => {
    await send(page, "pending", false);
    await page.waitForFunction(() => document.querySelector(".assistant .answer-text")?.textContent.includes("等待完成")); // 等待动作帧已进入尚未完成的流。
    assert.equal(await page.locator(".support-action").count(), 0);
    assert.equal(records.length, 0);
    await page.waitForFunction(() => !document.querySelector("#message-input").disabled); // done 后才展示确认入口。
    assert.equal(await page.locator(".support-action").count(), 2);
  }); // 验证真实延迟 SSE 中 done 之前零可点击动作。
  for (const name of ["error", "disconnect", "mismatch", "duplicate", "after-actions", "after-done", "unknown-option", "duplicate-option", "bad-label", "bad-checkpoint", "extra-actions", "before-delta", "numeric-identity", "extra-option"]) {
    await scenario(`reject-${name}`, async ({ page, records }) => {
      await send(page, name);
      assert.equal(await page.locator(".support-action").count(), 0);
      assert.equal(records.length, 0);
      assert.ok(await page.locator(".message-note.error").count());
    }); // 每种身份/顺序/格式错误均不得发布确认按钮。
  }
  await scenario("empty-actions", async ({ page }) => {
    await send(page, "empty-options");
    assert.equal(await page.locator(".support-action").count(), 0);
    assert.equal(await page.locator(".message-note.error").count(), 0);
  }); // 空选项合法且不生成入口。
  await scenario("interrupted-trace", async ({ page }) => {
    await send(page, "partial");
    assert.equal(await page.locator('.tool-badge[data-status="interrupted"]').count(), 1);
    assert.match(await page.locator(".tool-badge").innerText(), /结果未确认/);
  }); // 断流保留未完成徽章的真实状态。
  await scenario("stopped-trace", async ({ page }) => {
    await send(page, "stopped", false);
    await page.locator('.tool-badge[data-status="running"]').waitFor();
    await page.getByRole("button", { name: "停止回复", exact: true }).click();
    await page.waitForFunction(() => !document.querySelector("#message-input").disabled); // 用户停止后等待读取器清理。
    assert.equal(await page.locator('.tool-badge[data-status="interrupted"]').count(), 1);
    assert.equal(await page.locator(".support-action").count(), 0);
  }); // 中止生成不确认动作。
  await scenario("citations-feedback-keyboard", async ({ page, records }) => {
    await send(page, "citation");
    const source = page.locator(".citation-button");
    await source.focus();
    await page.keyboard.press("Enter");
    await page.locator("#source-dialog[open]").waitFor();
    assert.equal(await page.locator("#source-answer").innerText(), "原文答案 <script>不执行</script>");
    await page.keyboard.press("Escape");
    assert.equal(await source.evaluate((node) => node === document.activeElement), true); // 原生 dialog 关闭恢复引用键盘焦点。
    await page.getByRole("button", { name: "有帮助", exact: true }).click();
    assert.equal(await page.locator(".feedback-button:disabled").count(), 2);
    assert.equal(await page.locator(".feedback-button.selected").count(), 1);
    assert.equal(records.length, 0);
  }); // 原文与一次反馈保持可用。
  await scenario("narrow-layout-focus", async ({ page }) => {
    await send(page, "traces");
    await send(page, "complaint");
    const bounds = await page.locator("#message-input").boundingBox();
    assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= 390 && bounds.y + bounds.height <= 844);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true); // 窄屏不得出现页面水平溢出。
    const handoff = page.getByRole("button", { name: "转人工", exact: true });
    await handoff.focus();
    page.once("dialog", (dialog) => dialog.dismiss()); // 键盘 Enter 取消保持原按钮可用。
    await page.keyboard.press("Enter");
    assert.equal(await handoff.isEnabled(), true);
  }, 0, { width: 390, height: 844 }); // 输入框、徽章与按钮在窄屏保留可访问布局。
  return results;
}

// 解析真实服务器的完整SSE原文，保留错误/截断，不用页面文字推测完成。
function parseEvents(text) {
  return text.replace(/\r\n/g, "\n").split("\n\n").filter((block) => block.trim()).map((block) => {
    const lines = block.split("\n");
    return { event: lines.find((line) => line.startsWith("event: "))?.slice(7),
      data: JSON.parse(lines.filter((line) => line.startsWith("data: ")).map((line) => line.slice(6)).join("\n")) };
  });
}

// 仅用已创建的自有会话ID执行只读SQL快照，隐藏子进程且不读出环境密钥。
function ownedSqlSnapshot(conversationId, output, name) {
  const target = path.join(output, `${name}-sql.json`);
  const executable = process.env.WORKFLOW_PYTHON_PATH || path.join(root, ".venv", "Scripts", "python.exe");
  require("node:child_process").execFileSync(executable, ["-m", "evals.evaluate_workflow", "--mode", "chat", "--live", "--snapshot-conversation", conversationId, "--output", target], { cwd: root, windowsHide: true, timeout: 20000, encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } });
  return JSON.parse(fs.readFileSync(target, "utf8"));
}

// live 不拦截任何请求；每轮最多240秒，首次错误停止相同链路且保留独立场景。
async function runLive(browser, url, output) {
  const cases = [
    ["policy", "knowledge", "退货政策是什么？"],
    ["logistics", "business", "订单1001的包裹到哪里了？"],
    ["two-step", "business", "先查订单1001的状态，再按订单查物流"],
    ["complaint", "complaint", "我要投诉客服态度"],
    ["social", "social", "你好"],
    ["usage-help", "business", "新买的商品不太会用，能帮我看看吗？"],
    ["mh-lp200", "knowledge", "MH-LP200 能装多少猫砂？"],
    ["out-of-library", "knowledge", "你们提供宠物洗澡美容服务吗，具体价格是多少？"],
    ["complaint-ticket-only", "complaint", "我要投诉客服态度"],
    ["restart-offer", "complaint", "我要投诉客服态度"],
  ];
  const results = [], stopped = new Set();
  for (const [name, family, question] of cases) {
    if (stopped.has(family)) { results.push({ name, question, status: "NOT_EXECUTED", reason: "同链路首次失败后停止" }); continue; }
    const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, reducedMotion: "reduce" });
    page.setDefaultTimeout(240000);
    const record = { name, question, status: "FAIL", requests: [], actions: [], events: [] };
    const pending = [];
    page.on("request", (request) => { if (new URL(request.url()).pathname.startsWith("/api/")) record.requests.push({ url: request.url(), method: request.method(), body: request.postData() }); }); // 仅记录当前页面自有业务请求。
    page.on("response", (response) => {
      const pathname = new URL(response.url()).pathname;
      if (pathname === "/api/conversations" || pathname === "/api/chat" || pathname.endsWith("/actions/ticket")) {
        pending.push((async () => {
          const text = await response.text();
          if (pathname === "/api/conversations") record.conversation_id = JSON.parse(text).conversation_id;
          else if (pathname === "/api/chat") { record.raw_sse = text; record.events = parseEvents(text); record.http_status = response.status(); }
          else record.actions.push({ request: response.request().postDataJSON(), status: response.status(), response: JSON.parse(text) });
        })().catch((error) => { record.capture_error = error.message; })); // 读取完成原文，不修改SSE或绕过真实后端。
      }
    });
    try {
      await page.goto(url);
      await send(page, question);
      await Promise.all(pending);
      assert.equal(record.capture_error, undefined);
      assert.equal(record.http_status, 200);
      assert.equal(record.events.filter((event) => event.event === "error").length, 0, "真实聊天返回error");
      assert.equal(record.events.at(-1)?.event, "done", "必须正常done结束");
      assert.equal(await page.locator(".message-note.error").count(), 0, "真实聊天不应出现页面错误");
      record.answer = await page.locator(".answer-text").last().innerText();
      assert.ok(record.answer.trim());
      record.tool_badges = await page.locator(".tool-badge").allTextContents();
      record.sql_before_actions = ownedSqlSnapshot(record.conversation_id, output, `${name}-before`);
      assert.equal(record.sql_before_actions.tickets.length, 0, "建议出现时不得自动建工单");
      if (family === "knowledge") {
        assert.ok(record.events.some((event) => event.event === "status" && event.data.origin === "workflow" && event.data.tool_name === "query_faq"));
        if (name !== "out-of-library") {
          assert.ok(await page.locator(".citation-button").count(), "可答知识应有可定位引用");
          await page.locator(".citation-button").first().click();
          await page.locator("#source-dialog[open]").waitFor();
          record.source = await page.locator("#source-answer").innerText();
          await page.keyboard.press("Escape");
        }
      }
      if (name === "mh-lp200") assert.match(record.answer, /12\s*(?:L|升|l)/, "MH-LP200应有12L原文事实");
      if (name === "two-step") {
        assert.deepEqual(record.events.filter((event) => event.event === "status" && event.data.phase === "tool_running").map((event) => event.data.tool_name), ["query_order", "query_logistics"]);
        assert.equal(await page.locator('.tool-badge[data-status="success"]').count(), 2);
      }
      if (family === "social") assert.equal(record.tool_badges.length, 0);
      if (family === "complaint") {
        assert.equal(await page.locator(".support-action").count(), 2);
        const handoff = page.getByRole("button", { name: "转人工", exact: true });
        const ticket = page.getByRole("button", { name: "建工单", exact: true });
        const before = record.requests.length;
        await confirmClick(page, handoff, false);
        await confirmClick(page, ticket, false);
        assert.equal(record.requests.length, before, "取消确认不得写接口");
        if (name === "complaint") {
          await confirmClick(page, handoff, true);
          assert.equal(record.requests.length, before, "模拟转人工零HTTP");
          assert.equal(await ticket.isEnabled(), true);
          assert.equal(await page.locator(".handoff-line").count(), 2);
        }
        if (name !== "restart-offer") {
          await confirmClick(page, ticket, true);
          await page.getByText(/工单已创建 ·/).waitFor();
          await Promise.all(pending);
          assert.equal(record.actions.length, 1);
          assert.equal(record.actions[0].status, 200);
          assert.deepEqual(Object.keys(record.actions[0].request).sort(), ["assistant_message_id", "checkpoint_id"]);
          assert.equal(await page.getByText("已转接人工客服", { exact: true }).count(), name === "complaint" ? 1 : 0);
          record.sql_after_actions = ownedSqlSnapshot(record.conversation_id, output, `${name}-after`);
          assert.equal(record.sql_after_actions.tickets.length, 1);
          assert.equal(record.sql_after_actions.conversation_status, "进行中");
          assert.equal(record.sql_after_actions.tickets[0].description, question);
        }
      }
      record.status = "PASS";
    } catch (error) { record.error = error.message; stopped.add(family); }
    record.screenshot = path.join(output, `${name}.png`);
    await page.screenshot({ path: record.screenshot, fullPage: true });
    results.push(record);
    fs.writeFileSync(path.join(output, "partial-results.json"), JSON.stringify({ mode: "live", url, run_id: liveRunId, results }, null, 2) + "\n");
    console.log(`${record.status} ${name}${record.error ? ": " + record.error.split("\n")[0] : ""}`);
    await page.close();
  }
  return results;
}

// 每次真实验收拥有独立运行身份与目录，保留首次失败证据不覆盖。
const liveRunId = require("node:crypto").randomUUID();

// 明确模式与 URL 后运行，服务器/浏览器属于本脚本且均在 finally 清理。
async function main() {
  const args = process.argv.slice(2);
  const url = args[args.indexOf("--url") + 1];
  const mode = args[args.indexOf("--mode") + 1];
  assert.ok(args.includes("--url") && args.includes("--mode") && ["controlled", "live"].includes(mode), "用法: --url http://127.0.0.1:8002/ --mode controlled|live");
  const output = path.join(root, ".cache", "workflow-browser", mode, ...(mode === "live" ? [liveRunId] : []));
  fs.mkdirSync(output, { recursive: true });
  const { chromium } = loadPlaywright();
  const executablePath = browserPath(chromium);
  console.log(`MODE=${mode}; Playwright=${requireVersion()}; Chromium=${executablePath || "managed"}`);
  const servers = [];
  let browser;
  try {
    let transport;
    if (mode === "controlled") {
      const fixtureServer = createFixtureServer();
      const port = await listen(fixtureServer, 0);
      servers.push(fixtureServer);
      transport = `http://127.0.0.1:${port}`;
      const target = new URL(url);
      if (target.hostname === "127.0.0.1" && target.port === "8002") {
        const staticServer = createFixtureServer();
        try { await listen(staticServer, 8002); servers.push(staticServer); console.log("OWNED static fixture server 127.0.0.1:8002"); }
        catch (error) { if (error.code !== "EADDRINUSE") throw error; console.log("8002 already occupied: preserving existing server"); }
      }
    }
    browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
    const results = mode === "controlled" ? await runControlled(browser, url, transport, output) : await runLive(browser, url, output);
    fs.writeFileSync(path.join(output, "results.json"), JSON.stringify({ mode, url, run_id: mode === "live" ? liveRunId : null, results }, null, 2) + "\n");
    const failed = results.filter((item) => item.status === "FAIL");
    const passed = results.filter((item) => item.status === "PASS").length;
    const notExecuted = results.filter((item) => item.status === "NOT_EXECUTED").length;
    console.log(`${mode}: ${passed}/${results.length} PASS; failed=${failed.length}; not_executed=${notExecuted}; screenshots=${output}`);
    process.exitCode = failed.length ? 1 : 0;
  } finally {
    if (browser) await browser.close();
    for (const server of servers) { server.closeAllConnections(); await new Promise((resolve) => server.close(resolve)); } // 仅清理本进程创建的服务器。
  }
}

// 展示实际加载库版本，避免文档示例版本被当成安装版本。
function requireVersion() {
  try { return require("playwright/package.json").version; } catch {}
  return JSON.parse(fs.readFileSync(path.join(process.env.USERPROFILE || process.env.HOME || "", ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules", "playwright", "package.json"))).version;
}
main().catch((error) => { console.error(error.message); process.exitCode = 1; }); // 启动错误保留非零退出码。
