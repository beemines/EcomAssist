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
let sessionId = crypto.randomUUID();
let active = null;
let followBottom = true;
let composing = false;

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
  bubble.textContent = text;
  const note = document.createElement("p");
  note.className = "message-note";
  content.append(label, bubble, note);
  row.append(content);
  messages.append(row);
  scrollBottom();
  return { bubble, note };
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
  state.bubble.replaceChildren();
  state.bubble.classList.remove("waiting");
  state.bubble.classList.add("typing");
}

function finishVisual(state) {
  state.bubble.classList.remove("typing", "waiting");
  if (!state.visible && !state.queue.length) state.bubble.textContent = "这次没有收到完整回复。";
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
  // Code points preserve Chinese and surrogate pairs across the typing queue.
  const count = reducedMotion ? state.queue.length : Math.floor(elapsed / 17);
  if (state.queue.length && count > 0) {
    beginText(state);
    state.visible += state.queue.splice(0, Math.max(1, count)).join("");
    state.bubble.textContent = state.visible;
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
  // Once done has arrived, finish displaying received text; history is complete.
  if (!state.done) state.controller.abort();
  if (state.queue.length) {
    beginText(state);
    state.visible += state.queue.splice(0).join("");
    state.bubble.textContent = state.visible;
  }
}

function acceptFrame(frame, state) {
  const lines = frame.split(/\r?\n/);
  let event = "message";
  const data = [];
  for (const line of lines) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^ /, ""));
  }
  if (!data.length) return; // SSE comments/keepalive frames have no payload.
  if (state.terminal) throw new Error("回复结束后收到多余事件，请重新尝试。");
  let payload;
  try { payload = JSON.parse(data.join("\n")); }
  catch { throw new Error("收到的回复格式异常，请重新尝试。"); }
  if (event === "delta" && typeof payload?.delta === "string") {
    state.queue.push(...Array.from(payload.delta));
  } else if (event === "done" && payload?.session_id === sessionId) {
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
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
      body: JSON.stringify({ session_id: sessionId, message }),
      signal: state.controller.signal,
    });
    if (!response.ok) {
      let payload;
      try { payload = await response.json(); } catch { /* Fall back to safe copy. */ }
      throw new Error(typeof payload?.message === "string" ? payload.message : response.status === 422 ? "问题为空或超过输入限制，请缩短后重试。" : "暂时无法获取回复，请稍后重试。");
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
      try { await reader.cancel(); } catch { /* Abort already closed the reader. */ }
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
  assistant.bubble.innerHTML = '<span class="thinking-dot"></span><span class="thinking-dot"></span><span class="thinking-dot"></span>';
  const state = { ...assistant, controller: new AbortController(), queue: [], visible: "", lastPaint: performance.now(), networkFinished: false, terminal: false, done: false, stopped: false, error: "", startedText: false, animation: null };
  active = state;
  input.value = "";
  busy(true);
  state.animation = requestAnimationFrame((time) => tick(state, time));
  void readReply(state, message);
});

newButtons.forEach((button) => button.addEventListener("click", () => {
  if (active) return;
  sessionId = crypto.randomUUID();
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
