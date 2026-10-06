"use strict";

const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const messages = document.querySelector("#messages");
const scrollArea = document.querySelector("#chat-scroll");
const bottomButton = document.querySelector("#scroll-to-bottom");
const welcome = document.querySelector("#welcome");
const newButtons = [document.querySelector("#new-chat"), document.querySelector("#mobile-new-chat")];
const hint = document.querySelector("#composer-hint");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let conversationId = null;
let active = null;
let followBottom = true;
let composing = false;
const toolLabels = {
  query_order: "查询订单",
  query_product: "查询商品",
  query_logistics: "查询物流",
  query_faq: "查询常见问题",
  create_ticket: "创建人工工单",
};

function scrollBottom() {
  if (followBottom) scrollArea.scrollTop = scrollArea.scrollHeight;
}

scrollArea.addEventListener("scroll", () => {
  followBottom = scrollArea.scrollHeight - scrollArea.scrollTop - scrollArea.clientHeight < 80;
  bottomButton.hidden = followBottom;
});
bottomButton.addEventListener("click", () => {
  followBottom = true;
  bottomButton.hidden = true;
  scrollBottom();
});

function resizeInput() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 142) + "px";
  sendButton.disabled = !active && !input.value.trim();
}
input.addEventListener("input", resizeInput);
input.addEventListener("compositionstart", () => { composing = true; });
input.addEventListener("compositionend", () => { composing = false; });
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing && !composing && event.keyCode !== 229) {
    event.preventDefault();
    if (!active && input.value.trim()) form.requestSubmit();
  }
});

function addMessage(role, text) {
  const row = document.createElement("article");
  row.className = "message " + role;
  if (role === "assistant") {
    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.innerHTML = '<svg aria-hidden="true"><use href="#icon-bag"/></svg>';
    row.append(avatar);
  }
  const content = document.createElement("div");
  content.className = "message-content";
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "user" ? "你" : "MewHelp · 智能客服";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const tools = document.createElement("div");
  tools.className = "tool-traces";
  tools.hidden = true;
  tools.setAttribute("aria-label", "本轮工具记录");
  const answer = document.createElement("div");
  answer.className = "answer-text";
  answer.textContent = text;
  bubble.append(tools, answer);
  const note = document.createElement("p");
  note.className = "message-note";
  content.append(label, bubble, note);
  row.append(content);
  messages.append(row);
  scrollBottom();
  return { bubble, text: answer, tools, note };
}

function busy(value) {
  input.disabled = value;
  newButtons.forEach((button) => { button.disabled = value; });
  sendButton.setAttribute("aria-label", value ? "停止回复" : "发送消息");
  sendButton.innerHTML = value ? '<span class="stop-symbol" aria-hidden="true"></span>' : '<svg aria-hidden="true"><use href="#icon-send"/></svg>';
  hint.textContent = value ? "正在回复，你可以随时停止" : "Enter 发送 · Shift + Enter 换行";
  resizeInput();
}

function beginText(state) {
  if (state.startedText) return;
  state.startedText = true;
  state.text.replaceChildren();
  state.note.textContent = "";
  state.bubble.classList.remove("waiting");
  state.bubble.classList.add("typing");
}

function finishVisual(state) {
  state.bubble.classList.remove("typing", "waiting");
  if (state.toolBadge?.dataset.status === "running") {
    state.toolBadge.dataset.status = "interrupted";
    state.toolBadge.textContent = toolLabels[state.toolName] + " · 结果未确认";
  }
  if (!state.visible && !state.queue.length) state.text.textContent = state.stopped ? "本轮已停止。" : "这次没有收到完整回复。";
  if (!state.error && !state.stopped) state.note.textContent = "";
  if (state.error) {
    state.note.className = "message-note error";
    state.note.textContent = state.error;
  } else if (state.stopped) {
    state.note.textContent = state.done ? "已显示收到的完整回复" : "已停止 · 本轮未完整结束，请重新描述问题";
  }
  active = null;
  busy(false);
  scrollBottom();
  input.focus({ preventScroll: true });
}

function tick(state, now) {
  state.animation = null;
  const elapsed = Math.min(now - state.lastPaint, 100);
  // 按 Unicode 码点处理文字，避免逐字队列拆坏中文或代理对字符。
  const count = reducedMotion ? state.queue.length : Math.floor(elapsed / 17);
  if (state.queue.length && count > 0) {
    beginText(state);
    state.visible += state.queue.splice(0, Math.max(1, count)).join("");
    state.text.textContent = state.visible;
    state.lastPaint = now;
    scrollBottom();
  } else if (!state.queue.length) {
    state.lastPaint = now;
  }
  if (state.networkFinished && !state.queue.length) {
    finishVisual(state);
  } else {
    state.animation = requestAnimationFrame((time) => tick(state, time));
  }
}

function stopReply() {
  const state = active;
  if (!state) return;
  state.stopped = true;
  // 收到 done 后，历史已完成提交；此时只需显示完已经收到的文字。
  if (!state.done) state.controller.abort();
  if (state.queue.length) {
    beginText(state);
    state.visible += state.queue.splice(0).join("");
    state.text.textContent = state.visible;
  }
}

function acceptStatus(payload, state) {
  const phase = payload.phase;
  if (phase === "selecting") {
    state.note.textContent = "正在理解你的问题…";
    return;
  }
  if (phase === "answering") {
    state.note.textContent = "正在组织回复…";
    return;
  }
  if (!["tool_running", "tool_completed"].includes(phase) ||
      !Object.hasOwn(toolLabels, payload.tool_name) ||
      typeof payload.tool_call_id !== "string" || !payload.tool_call_id ||
      payload.tool_call_id.length > 64) {
    throw new Error("工具状态格式异常，请重新尝试。");
  }
  if (phase === "tool_completed" && !["success", "error"].includes(payload.status)) {
    throw new Error("工具结果状态异常，请重新尝试。");
  }
  if (!state.toolBadge) {
    const badge = document.createElement("span");
    badge.className = "tool-badge";
    state.tools.append(badge);
    state.tools.hidden = false;
    state.toolBadge = badge;
    state.toolCallId = payload.tool_call_id;
    state.toolName = payload.tool_name;
  }
  if (state.toolCallId !== payload.tool_call_id || state.toolName !== payload.tool_name) {
    throw new Error("这轮收到多个工具调用，请重新尝试。");
  }
  const status = phase === "tool_running" ? "running" : payload.status;
  const suffix = status === "running" ? "执行中" : status === "success" ? "已完成" : "未完成";
  state.toolBadge.dataset.status = status;
  state.toolBadge.textContent = toolLabels[payload.tool_name] + " · " + suffix;
  state.note.textContent = status === "running" ? "正在" + toolLabels[payload.tool_name].split(" · ")[0] + "…" : "";
  scrollBottom();
}

function acceptFrame(frame, state) {
  const lines = frame.split(/\r?\n/);
  let event = "message";
  const data = [];
  for (const line of lines) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^ /, ""));
  }
  if (!data.length) return; // SSE 注释或保活帧不包含数据载荷。
  if (state.terminal) throw new Error("回复结束后收到多余事件，请重新尝试。");
  let payload;
  try { payload = JSON.parse(data.join("\n")); }
  catch { throw new Error("收到的回复格式异常，请重新尝试。"); }
  if (event === "status" && payload && typeof payload === "object") {
    acceptStatus(payload, state);
  } else if (event === "delta" && typeof payload?.delta === "string") {
    state.queue.push(...Array.from(payload.delta));
  } else if (event === "done" && payload?.conversation_id === state.conversationId) {
    state.terminal = true;
    state.done = true;
  } else if (event === "error" && typeof payload?.message === "string") {
    state.terminal = true;
    state.error = payload.message;
  } else {
    throw new Error("收到的回复事件异常，请重新尝试。");
  }
}

async function readReply(state, message) {
  let reader;
  try {
    if (!conversationId) {
      const created = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo-user" }),
        signal: state.controller.signal,
      });
      if (!created.ok) throw new Error("暂时无法开启对话，请稍后重试。");
      const identity = await created.json();
      const id = identity?.conversation_id;
      // 始终保留字符串，避免 BIGINT 会话号在浏览器中丢失精度。
      if (typeof id !== "string" || !/^[1-9]\d{0,19}$/.test(id) ||
          BigInt(id) > 18446744073709551615n) {
        throw new Error("会话创建结果异常，请稍后重试。");
      }
      conversationId = id;
    }
    state.conversationId = conversationId;
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
      body: JSON.stringify({ conversation_id: state.conversationId, message }),
      signal: state.controller.signal,
    });
    if (!response.ok) {
      let payload;
      try { payload = await response.json(); } catch { /* 解析失败时使用安全的默认提示。 */ }
      throw new Error(typeof payload?.message === "string" ? payload.message :
        response.status === 422 ? "问题为空或超过输入限制，请缩短后重试。" :
        response.status === 404 ? "这段会话已不存在，请开启新对话。" :
        response.status === 409 ? "这段会话暂时无法继续，请稍后重试或开启新对话。" :
        "暂时无法获取回复，请稍后重试。");
    }
    if (!response.body || !response.headers.get("content-type")?.includes("text/event-stream")) {
      throw new Error("服务返回的回复格式异常，请稍后重试。");
    }
    reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8", { fatal: true });
    let buffer = "";
    const drain = () => {
      let boundary;
      while ((boundary = /\r?\n\r?\n/.exec(buffer))) {
        const frame = buffer.slice(0, boundary.index);
        buffer = buffer.slice(boundary.index + boundary[0].length);
        acceptFrame(frame, state);
      }
    };
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      drain();
    }
    buffer += decoder.decode();
    drain();
    if (buffer.trim() || !state.terminal) throw new Error("连接中断，回复未完整结束。请重新描述问题。");
    if (state.done && !state.visible.trim() && !state.queue.join("").trim()) throw new Error("这次没有收到有效回复，请重新尝试。");
  } catch (error) {
    if (!state.stopped) state.error = error instanceof TypeError ? "连接失败，请检查服务是否启动后重试。" : error.message || "回复失败，请稍后重试。";
  } finally {
    if (reader) {
      try { await reader.cancel(); } catch { /* 中止请求可能已经关闭了读取器。 */ }
      reader.releaseLock();
    }
    state.networkFinished = true;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (active) { stopReply(); return; }
  const message = input.value.trim();
  if (!message) return;
  if (messages.childElementCount === 0) document.querySelector("#conversation-title").textContent = message;
  welcome.hidden = true;
  followBottom = true;
  bottomButton.hidden = true;
  addMessage("user", message);
  const assistant = addMessage("assistant", "");
  assistant.bubble.classList.add("waiting");
  for (let index = 0; index < 3; index += 1) {
    const dot = document.createElement("span");
    dot.className = "thinking-dot";
    assistant.text.append(dot);
  }
  const state = { ...assistant, controller: new AbortController(), queue: [], visible: "", lastPaint: performance.now(), networkFinished: false, terminal: false, done: false, stopped: false, error: "", startedText: false, animation: null };
  active = state;
  input.value = "";
  busy(true);
  state.animation = requestAnimationFrame((time) => tick(state, time));
  void readReply(state, message);
});

newButtons.forEach((button) => button.addEventListener("click", () => {
  if (active) return;
  conversationId = null;
  messages.replaceChildren();
  welcome.hidden = false;
  document.querySelector("#conversation-title").textContent = "新的客服对话";
  input.value = "";
  followBottom = true;
  resizeInput();
  scrollArea.scrollTop = 0;
  input.focus({ preventScroll: true });
}));
document.querySelectorAll("[data-prompt]").forEach((button) => button.addEventListener("click", () => {
  input.value = button.dataset.prompt;
  resizeInput();
  input.focus({ preventScroll: true });
}));

async function checkConnection() {
  try {
    const response = await fetch("/health", { signal: AbortSignal.timeout(5000) });
    if (!response.ok) throw new Error();
    document.querySelector("#connection").classList.remove("offline");
    document.querySelector("#connection-text").textContent = "服务已就绪";
  } catch {
    document.querySelector("#connection").classList.add("offline");
    document.querySelector("#connection-text").textContent = "服务未连接";
  }
}
void checkConnection();
resizeInput();
