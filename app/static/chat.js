"use strict";

// 页面保存当前会话及每条回复独立的渲染/动作快照；多轮历史由后端从数据库读取。
// 缓存 HTML 中的交互节点，后续状态更新复用引用，避免反复查询 DOM。
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const messages = document.querySelector("#messages");
const scrollArea = document.querySelector("#chat-scroll");
const bottomButton = document.querySelector("#scroll-to-bottom");
const welcome = document.querySelector("#welcome");
const newButtons = [document.querySelector("#new-chat"), document.querySelector("#mobile-new-chat")];
const hint = document.querySelector("#composer-hint");
const sourceDialog = document.querySelector("#source-dialog");
const sourceClose = document.querySelector("#source-close");
let sourceTrigger = null;
const handoffDialog = document.querySelector("#handoff-dialog");
const handoffClose = document.querySelector("#handoff-close");
const handoffCancel = document.querySelector("#handoff-cancel");
const handoffConfirm = document.querySelector("#handoff-confirm");
let handoffDraft = null;
const ticketDialog = document.querySelector("#ticket-dialog");
const ticketForm = document.querySelector("#ticket-form");
const ticketType = document.querySelector("#ticket-type");
const ticketDescription = document.querySelector("#ticket-description");
const ticketFields = document.querySelector("#ticket-fields");
const ticketError = document.querySelector("#ticket-error");
const ticketSubmit = document.querySelector("#ticket-submit");
const ticketClose = document.querySelector("#ticket-close");
const ticketCancel = document.querySelector("#ticket-cancel");
let ticketDraft = null;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let conversationId = null;
let active = null;
let followBottom = true;
let composing = false;
const refundDialog = document.querySelector("#refund-dialog");
const refundForm = document.querySelector("#refund-form");
const refundReason = document.querySelector("#refund-reason");
const refundError = document.querySelector("#refund-error");
const refundSubmit = document.querySelector("#refund-submit");
const refundClose = document.querySelector("#refund-close");
const refundCancel = document.querySelector("#refund-cancel");
const refundFields = document.querySelector("#refund-fields");
let refundDraft = null;
const selectionGroups = new Set();
let refundLocators = [];
const sessionKey = "mewhelp-intent-session-v1";
const reasonLabels = { unwanted: "不想要了", quality: "质量问题", not_as_described: "与描述不符", wrong_or_missing: "发错/漏发", damaged: "运输破损", other: "其他" };

// 只缓存结构定位用于刷新后服务端重验，不缓存金额、订单事实或退款许可。
function saveSession() {
  try { sessionStorage.setItem(sessionKey, JSON.stringify({ conversationId, refundLocators })); } catch { /* 隐私模式不支持存储时仍可当页使用。 */ }
}

// UUID与SQL主键均保持字符串，杜绝大整数浮点截断。
function validUuid(value) {
  return typeof value === "string" && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value);
}

// 演示订单只接受服务端摘要，金额以整数分校验并格式化为只读展示。
function validCard(card) {
  return card && validId(card.order_id) && ["product_name", "model", "status", "as_of"].every((key) => typeof card[key] === "string") &&
    card.mock === true && card.as_of === "2026-10-15" && card.currency === "CNY" && Number.isSafeInteger(card.amount_cents) && card.amount_cents >= 0;
}

// 以整数分展示金额，不接受浏览器更改金额作为申请输入。
function orderAmount(card) {
  return "¥" + (card.amount_cents / 100).toFixed(2);
}

// 核对待选公开定位与候选，只有完整paused之后才允许点击。
function validateSelection(payload) {
  if (!payload || !validId(payload.turn_id) || !validUuid(payload.selection_id) || !validUuid(payload.checkpoint_id) ||
      typeof payload.prompt !== "string" || !Array.isArray(payload.cards) || !payload.cards.every(validCard) ||
      new Set(payload.cards.map((card) => card.order_id)).size !== payload.cards.length) throw new Error("订单选择格式异常，请刷新重试。");
  return payload;
}

// 新问句或选择提交后锁定旧卡，同组无法再次发送恢复请求。
function lockSelections(label = "这组订单已失效，请使用最新的订单选择。") {
  for (const group of selectionGroups) {
    group.locked = true;
    group.buttons.forEach((button) => { button.disabled = true; });
    group.status.textContent = label;
  }
}

// 在聊天流内展示订单摘要；按钮恢复原轮，不新增用户问句。
function showSelection(state, payload) {
  const section = document.createElement("section");
  section.className = "order-selection";
  section.setAttribute("aria-label", "选择本次咨询订单");
  const cards = document.createElement("div");
  cards.className = "order-cards";
  const status = document.createElement("p");
  status.className = "order-selection-status";
  status.setAttribute("role", "status");
  status.textContent = "演示订单 · 业务日期 2026-10-15";
  const group = { state, payload, buttons: [], status, locked: false };
  for (const card of payload.cards) {
    const item = document.createElement("div");
    item.className = "order-card";
    const title = document.createElement("h3");
    title.textContent = card.product_name;
    item.append(title);
    for (const text of ["订单 " + card.order_id, card.model + " · " + card.status, orderAmount(card), "签收：" + (card.signed_at || "未签收")]) {
      const line = document.createElement("p");
      line.textContent = text;
      item.append(line);
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "support-action order-select";
    button.textContent = "选择此订单";
    button.addEventListener("click", () => {
      if (active || group.locked || !state.bubble.isConnected) return;
      lockSelections("已选择订单 " + card.order_id + "，正在继续处理…");
      const next = createReplyState();
      next.conversationId = state.conversationId;
      active = next;
      busy(true);
      next.animation = requestAnimationFrame((time) => tick(next, time));
      void readReply(next, null, { turn_id: payload.turn_id, selection_id: payload.selection_id, checkpoint_id: payload.checkpoint_id, order_id: card.order_id });
    });
    group.buttons.push(button);
    item.append(button);
    cards.append(item);
  }
  section.append(cards, status);
  state.bubble.append(section);
  selectionGroups.add(group);
  if (!payload.cards.length) status.textContent = "没有可选演示订单，请补充订单信息。";
}

// 校验服务器公开许可，文本提及退款不能产生表单入口。
function acceptRefund(payload, state) {
  if (state.refundOffer || !payload || !validId(payload.assistant_message_id) || !validUuid(payload.checkpoint_id) || !validUuid(payload.offer_id) ||
      !validCard(payload.order) || !["eligible", "needs_review"].includes(payload.refund_decision) || typeof payload.decision_reason !== "string" ||
      !Array.isArray(payload.reasons) || payload.reasons.length !== 6 ||
      new Set(payload.reasons.map((reason) => reason.code)).size !== 6 ||
      payload.reasons.some((reason) => !Object.hasOwn(reasonLabels, reason.code) || reasonLabels[reason.code] !== reason.label)) throw new Error("退款入口格式异常，请刷新重试。");
  state.refundOffer = payload;
}

// 仅完整成功回答或刷新后服务器重验的许可显示退款入口。
function addRefundEntry(state) {
  if (!state.done || state.error || state.stopped || !state.refundOffer || state.refundChoice) return;
  const section = document.createElement("div");
  section.className = "refund-entry";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "support-action";
  button.textContent = "申请退款";
  const choice = { button, pending: false, completed: false };
  state.refundChoice = choice;
  button.addEventListener("click", () => openRefundForm(state, choice));
  section.append(button);
  state.bubble.append(section);
  const locator = { assistant_message_id: state.refundOffer.assistant_message_id, checkpoint_id: state.refundOffer.checkpoint_id };
  if (!refundLocators.some((item) => item.assistant_message_id === locator.assistant_message_id && item.checkpoint_id === locator.checkpoint_id)) refundLocators.push(locator);
  saveSession();
}

// 每次打开新表单原因初始空白，订单与金额只读并绑定原完成回答。
function openRefundForm(state, choice) {
  if (choice.pending || choice.completed || refundDialog.open || ticketDialog.open || handoffDialog.open || !state.bubble.isConnected) return;
  refundDraft = { state, choice };
  const offer = state.refundOffer;
  document.querySelector("#refund-order").textContent = offer.order.product_name + " · 订单 " + offer.order.order_id;
  document.querySelector("#refund-amount").textContent = orderAmount(offer.order);
  const empty = new Option("请选择退款原因", "", true, true);
  empty.disabled = true;
  refundReason.replaceChildren(empty, ...offer.reasons.map((reason) => new Option(reason.label, reason.code)));
  refundError.hidden = true;
  refundDialog.showModal();
  refundReason.focus();
}

// 取消与Escape只关闭本地表单；请求进行中保持防重与焦点约束。
function closeRefundForm() {
  if (!refundDraft?.choice.pending) refundDialog.close();
}
refundClose.addEventListener("click", closeRefundForm);
refundCancel.addEventListener("click", closeRefundForm);
refundDialog.addEventListener("cancel", (event) => { if (refundDraft?.choice.pending) event.preventDefault(); });
refundDialog.addEventListener("close", () => {
  const trigger = refundDraft?.choice.button;
  refundDraft = null;
  (trigger?.isConnected && !trigger.disabled ? trigger : input).focus({ preventScroll: true });
});

// 明确提交只传四个授权字段；失败保留所选原因，成功另起待审核通知气泡。
async function submitRefund(event) {
  event.preventDefault();
  const draft = refundDraft;
  if (!draft || draft.choice.pending || draft.choice.completed || !refundForm.reportValidity()) return;
  const { state, choice } = draft;
  choice.pending = true;
  choice.button.disabled = refundSubmit.disabled = refundClose.disabled = refundCancel.disabled = refundFields.disabled = true;
  refundSubmit.textContent = "正在提交…";
  refundError.hidden = true;
  try {
    const offer = state.refundOffer;
    const response = await fetch("/api/conversations/" + state.conversationId + "/actions/refund", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assistant_message_id: offer.assistant_message_id, checkpoint_id: offer.checkpoint_id, offer_id: offer.offer_id, reason: refundReason.value }),
    });
    if (!response.ok) throw new Error(response.status === 409 ? "这笔订单已有申请或许可已失效，请核对原申请后重试。" : "申请提交失败，请稍后重试。");
    const receipt = await response.json();
    if (!receipt || typeof receipt.request_no !== "string" || !receipt.request_no.trim() || receipt.request_no.length > 128 || receipt.status !== "待审核" ||
        receipt.order_id !== offer.order.order_id || receipt.amount_cents !== offer.order.amount_cents || receipt.currency !== "CNY") throw new Error("申请回执异常，请稍后重试。");
    choice.completed = true;
    if (state.bubble.isConnected) addMessage("assistant", "退款申请已提交\n申请号：" + receipt.request_no + "\n状态：待审核\n订单：" + receipt.order_id + " · " + orderAmount(receipt), "服务通知");
    refundLocators = refundLocators.filter((item) => item.assistant_message_id !== offer.assistant_message_id || item.checkpoint_id !== offer.checkpoint_id);
    saveSession();
    if (refundDraft === draft) refundDialog.close();
  } catch (error) {
    if (refundDraft === draft) { refundError.textContent = error.message || "申请提交失败，请稍后重试。"; refundError.hidden = false; }
  } finally {
    choice.pending = false;
    choice.button.disabled = choice.completed;
    refundSubmit.disabled = refundClose.disabled = refundCancel.disabled = refundFields.disabled = false;
    refundSubmit.textContent = "提交申请 · 待审核";
    scrollBottom();
  }
}
refundForm.addEventListener("submit", submitRefund);

// 刷新读取待选当前根；失败提供显式重试，绝不把旧候选重新解锁。
async function restorePending(id) {
  const response = await fetch("/api/conversations/" + id + "/pending-order");
  if (!response.ok) throw new Error("待选订单暂时无法恢复，请重试。");
  const result = await response.json();
  if (conversationId !== id || !result.pending) return;
  const payload = validateSelection(result.pending);
  lockSelections();
  welcome.hidden = true;
  const state = createReplyState(payload.prompt);
  state.conversationId = id;
  showSelection(state, payload);
}

// 恢复失败独立呈现重试按钮，每次点击只重新读取服务端当前待选。
function pendingRetry(id, message) {
  if (conversationId !== id) return;
  welcome.hidden = true;
  const state = addMessage("assistant", message);
  const button = document.createElement("button");
  button.type = "button";
  button.className = "support-action";
  button.textContent = "重新读取待选订单";
  button.addEventListener("click", async () => {
    if (active || conversationId !== id) return;
    button.disabled = true;
    active = { restoring: true };
    busy(true);
    sendButton.disabled = true;
    try { await restorePending(id); state.note.textContent = "已核对当前待选订单。"; }
    catch (error) { state.note.textContent = error.message; button.disabled = false; }
    finally { active = null; busy(false); }
  });
  state.bubble.append(button);
}

// 页面刷新仅用结构身份恢复待选与退款入口，每个退款定位都重新GET核验。
async function restoreSession() {
  let saved;
  try { saved = JSON.parse(sessionStorage.getItem(sessionKey)); } catch { return; }
  if (!saved || !validId(saved.conversationId)) return;
  conversationId = saved.conversationId;
  const id = conversationId;
  refundLocators = Array.isArray(saved.refundLocators) ? saved.refundLocators.filter((item) => validId(item.assistant_message_id) && validUuid(item.checkpoint_id)) : [];
  const locators = [...refundLocators];
  active = { restoring: true };
  busy(true);
  sendButton.disabled = true;
  try {
    try { await restorePending(id); } catch (error) { pendingRetry(id, error.message); }
    for (const locator of locators) {
      try {
        const query = new URLSearchParams(locator);
        const response = await fetch("/api/conversations/" + id + "/refund-offer?" + query);
        if (!response.ok) throw new Error("原退款入口未能通过服务器核验，请重新咨询。");
        const offer = await response.json();
        if (offer.assistant_message_id !== locator.assistant_message_id || offer.checkpoint_id !== locator.checkpoint_id) throw new Error("原退款入口定位不一致。");
        const state = createReplyState("已重新核验原回复的退款申请入口。");
        state.conversationId = id;
        acceptRefund(offer, state);
        state.done = true;
        addRefundEntry(state);
        welcome.hidden = true;
      } catch (error) { welcome.hidden = true; addMessage("assistant", error.message); }
    }
  } finally { active = null; busy(false); }
}
// 后端工具名保持协议原值，页面仅把已注册工具映射为中文展示名称。
const toolLabels = {
  query_order: "查询订单",
  query_product: "查询商品",
  query_logistics: "查询物流",
  query_faq: "查询常见问题",
  create_ticket: "创建人工工单",
};
// 动作名称与展示文案由页面固定，不接受模型提供 URL、HTML 或任意工具名。
const actionLabels = { handoff: "转人工", create_ticket: "建工单" };

// 用户仍在底部跟随模式时滚到最新消息，避免打断向上翻阅历史。
function scrollBottom() {
  if (followBottom) scrollArea.scrollTop = scrollArea.scrollHeight;
}

// 距底部不足 80 像素视为继续跟随，向上翻阅时显示“查看最新消息”。
scrollArea.addEventListener("scroll", () => {
  followBottom = scrollArea.scrollHeight - scrollArea.scrollTop - scrollArea.clientHeight < 80;
  bottomButton.hidden = followBottom;
});
// 点击回到底部后重新开启自动跟随。
bottomButton.addEventListener("click", () => {
  followBottom = true;
  bottomButton.hidden = true;
  scrollBottom();
});

// 按输入内容调整高度（最大 142 像素），同时同步空消息的发送按钮状态。
function resizeInput() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 142) + "px";
  sendButton.disabled = !active && !input.value.trim();
}
input.addEventListener("input", resizeInput);
// 中文输入法选词期间标记组合输入，防止 Enter 被当作发送。
input.addEventListener("compositionstart", () => { composing = true; });
// 选词结束后恢复正常键盘发送规则。
input.addEventListener("compositionend", () => { composing = false; });
// Enter 发送、Shift+Enter 换行；兼容输入法的组合事件与旧版键码。
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing && !composing && event.keyCode !== 229) {
    event.preventDefault();
    if (!active && input.value.trim()) form.requestSubmit();
  }
});

// 创建一条消息气泡，返回正文、工具徽章和提示节点，供后续流式更新。
function addMessage(role, text, labelText) {
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
  label.textContent = labelText || (role === "user" ? "你" : "MewHelp · 智能客服");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const tools = document.createElement("div");
  tools.className = "tool-traces";
  tools.hidden = true;
  tools.setAttribute("aria-label", "本轮工具记录");
  const answer = document.createElement("div");
  answer.className = "answer-text";
  // 模型正文按纯文本显示，既保留工具徽章，也不会把回答中的 HTML 执行掉。
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

// 切换输入禁用状态及发送/停止按钮，让同一时刻只进行一轮聊天。
function busy(value) {
  input.disabled = value;
  // 回复期间同步禁用桌面和移动端的新会话按钮。
  newButtons.forEach((button) => { button.disabled = value; });
  sendButton.setAttribute("aria-label", value ? "停止回复" : "发送消息");
  sendButton.innerHTML = value ? '<span class="stop-symbol" aria-hidden="true"></span>' : '<svg aria-hidden="true"><use href="#icon-send"/></svg>';
  hint.textContent = value ? "正在回复，你可以随时停止" : "Enter 发送 · Shift + Enter 换行";
  resizeInput();
}

// 首批正文出现时仅清除一次等待动画，再进入逐字显示状态。
function beginText(state) {
  if (state.startedText) return;
  state.startedText = true;
  state.text.replaceChildren();
  state.note.textContent = "";
  state.bubble.classList.remove("waiting");
  state.bubble.classList.add("typing");
}

// 标识始终作为规范十进制字符串保存；BigInt 仅校验范围，不转成浮点数。
function validId(value, maximum = 18446744073709551615n) {
  return typeof value === "string" && /^[1-9]\d{0,19}$/.test(value) && BigInt(value) <= maximum;
}

// 引用属于各自回答的映射，弹窗用 textContent 显示原文，避免执行文档内的 HTML。
function openSource(citation, trigger) {
  sourceTrigger = trigger;
  document.querySelector("#source-title").textContent = "知识来源 [" + citation.n + "]";
  document.querySelector("#source-path").textContent = citation.section_path || "未标注章节路径";
  document.querySelector("#source-question").textContent = citation.question;
  document.querySelector("#source-answer").textContent = citation.answer;
  document.querySelector("#source-id").textContent = "知识块编号 " + citation.chunk_id;
  if (!sourceDialog.open) sourceDialog.showModal();
  sourceClose.focus();
}

// 关闭后恢复到仍在页面上的引用按钮，流式重绘替换按钮时回到输入框。
function closeSource() {
  sourceDialog.close();
}
sourceClose.addEventListener("click", closeSource);
// Escape 的原生 dialog 行为也会触发 close，统一恢复键盘焦点。
sourceDialog.addEventListener("close", () => {
  const target = sourceTrigger?.isConnected ? sourceTrigger : input;
  target.focus({ preventScroll: true });
  sourceTrigger = null;
});
// 仅点击弹窗外的遮罩时关闭，点击正文留在原文阅读区域。
sourceDialog.addEventListener("click", (event) => {
  if (event.target !== sourceDialog) return;
  const bounds = sourceDialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom) closeSource();
});

// 重绘已收到的正文，完整且存在于本轮映射的 [n] 才变成可访问按钮。
// 增量末尾的半个编号先隐藏，下一批到齐后再显示，其他文字仍按原文逐字绘制。
function renderAnswer(state) {
  let visible = state.visible;
  if (!state.networkFinished || state.queue.length) visible = visible.replace(/\[\d*$/, "");
  const fragment = document.createDocumentFragment();
  let offset = 0;
  for (const match of visible.matchAll(/\[([1-9]\d*)\]/g)) {
    const citation = state.citations.get(match[1]);
    if (!citation) continue;
    fragment.append(document.createTextNode(visible.slice(offset, match.index)));
    const button = document.createElement("button");
    button.type = "button";
    button.className = "citation-button";
    button.textContent = match[0];
    button.setAttribute("aria-label", "查看来源 " + citation.n + "：" + (citation.section_path || citation.question));
    // 点击闭包绑定当前回答的来源对象，后续回复的同号引用不会覆盖它。
    button.addEventListener("click", () => openSource(citation, button));
    fragment.append(button);
    offset = match.index + match[0].length;
  }
  fragment.append(document.createTextNode(visible.slice(offset)));
  state.text.replaceChildren(fragment);
}

// 仅完整成功回复可反馈，第一次选择后锁定；信号只留在本页面，不发送网络请求。
function addFeedback(state) {
  if (state.feedback || !state.done || state.error || state.stopped) return;
  const feedback = document.createElement("div");
  feedback.className = "answer-feedback";
  feedback.setAttribute("aria-label", "评价本次回复");
  const label = document.createElement("span");
  label.className = "feedback-label";
  label.textContent = "这次回复有帮助吗？";
  const choices = [];
  for (const [value, icon, title] of [["helpful", "👍", "有帮助"], ["unhelpful", "👎", "没有帮助"]]) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "feedback-button";
    button.textContent = icon;
    button.setAttribute("aria-label", title);
    button.setAttribute("aria-pressed", "false");
    // 两个按钮共用本轮选择值，重复点击不能改变已经采集的反馈。
    button.addEventListener("click", () => {
      if (state.feedbackChoice) return;
      state.feedbackChoice = value;
      button.classList.add("selected");
      button.setAttribute("aria-pressed", "true");
      choices.forEach((choice) => { choice.disabled = true; });
      label.textContent = "已反馈";
      feedback.dataset.choice = value;
    });
    choices.push(button);
  }
  feedback.append(...choices, label);
  state.bubble.append(feedback);
  state.feedback = feedback;
}

// 网络已结束且文字队列已显示完时收尾，保留错误/停止提示并恢复输入。
function finishVisual(state) {
  if (state.startedText) renderAnswer(state);
  state.bubble.classList.remove("typing", "waiting");
  for (const trace of state.toolBadges.values()) {
    if (trace.badge.dataset.status === "running") {
      trace.badge.dataset.status = "interrupted";
      trace.badge.textContent = trace.label + " · 结果未确认";
    }
  }
  if (!state.visible && !state.queue.length) state.text.textContent = state.paused ? state.selection.prompt : state.stopped ? "本轮已停止。" : "这次没有收到完整回复。";
  if (!state.error && !state.stopped) state.note.textContent = "";
  if (state.error) {
    state.note.className = "message-note error";
    state.note.textContent = state.error;
  } else if (state.stopped) {
    state.note.textContent = state.done ? "已显示收到的完整回复" : "已停止 · 本轮未完整结束，请重新描述问题";
  }
  addFeedback(state);
  addActions(state);
  addRefundEntry(state);
  if (state.paused && !state.error && !state.stopped) showSelection(state, state.selection);
  active = null;
  busy(false);
  scrollBottom();
  input.focus({ preventScroll: true });
}

// 每帧按时间预算消费文字队列；减少动态效果模式直接显示已收到的全部文字。
function tick(state, now) {
  state.animation = null;
  const elapsed = Math.min(now - state.lastPaint, 100);
  // 按 Unicode 码点处理文字，避免逐字队列拆坏中文或代理对字符。
  const count = reducedMotion ? state.queue.length : Math.floor(elapsed / 17);
  if (state.queue.length && count > 0) {
    beginText(state);
    state.visible += state.queue.splice(0, Math.max(1, count)).join("");
    renderAnswer(state);
    state.lastPaint = now;
    scrollBottom();
  } else if (!state.queue.length) {
    state.lastPaint = now;
  }
  if (state.networkFinished && !state.queue.length) {
    finishVisual(state);
  } else {
    // 队列暂时为空也继续等下一帧，网络后续仍可能送来正文片段。
    state.animation = requestAnimationFrame((time) => tick(state, time));
  }
}

// 停止尚未完成的网络请求，并立即显示已经收到、尚未绘制的文字。
function stopReply() {
  const state = active;
  if (!state || state.restoring) return;
  state.stopped = true;
  // 收到 done 后，历史已完成提交；此时只需显示完已经收到的文字。
  if (!state.done) state.controller.abort();
  if (state.queue.length) {
    beginText(state);
    state.visible += state.queue.splice(0).join("");
    renderAnswer(state);
  }
}

// 按本轮调用 ID 保存独立工具徽章，工具名称/来源与完成顺序不能被后续帧改写。
function acceptStatus(payload, state) {
  const phase = payload.phase;
  if (!["selecting", "answering", "checking", "tool_running", "tool_completed"].includes(phase) ||
      Object.keys(payload).some((key) => !["phase", "tool_name", "tool_call_id", "status", "origin"].includes(key)) ||
      (payload.origin !== undefined && !["workflow", "agent"].includes(payload.origin))) {
    throw new Error("阶段状态格式异常，请重新尝试。");
  }
  if (phase === "selecting") {
    state.note.textContent = "正在理解你的问题…";
    return;
  }
  if (phase === "answering") {
    state.note.textContent = "正在组织回复…";
    return;
  }
  if (phase === "checking") {
    state.note.textContent = "正在核对回答依据…";
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
  let trace = state.toolBadges.get(payload.tool_call_id);
  if (!trace) {
    if (phase !== "tool_running") throw new Error("工具结果顺序异常，请重新尝试。");
    const badge = document.createElement("span");
    badge.className = "tool-badge";
    state.tools.append(badge);
    state.tools.hidden = false;
    const label = payload.origin === "workflow" && payload.tool_name === "query_faq" ? "知识检索" : toolLabels[payload.tool_name];
    trace = { badge, toolName: payload.tool_name, origin: payload.origin, label };
    state.toolBadges.set(payload.tool_call_id, trace);
  }
  if (trace.toolName !== payload.tool_name || trace.origin !== payload.origin ||
      ["success", "error"].includes(trace.badge.dataset.status)) {
    throw new Error("工具调用身份或顺序异常，请重新尝试。");
  }
  const status = phase === "tool_running" ? "running" : payload.status;
  const suffix = status === "running" ? "执行中" : status === "success" ? "已完成" : "未完成";
  trace.badge.dataset.status = status;
  trace.badge.textContent = trace.label + " · " + suffix;
  state.note.textContent = status === "running" ? "正在" + trace.label + "…" : "";
  scrollBottom();
}

// 完成建议只能出现一次且紧接终帧；回复身份、官方 UUID 和固定选项全部严格校验。
function acceptActions(payload, state) {
  if (state.actions || !state.hasDelta || !payload ||
      Object.keys(payload).sort().join(",") !== "assistant_message_id,checkpoint_id,options" ||
      !validId(payload.assistant_message_id) || typeof payload.checkpoint_id !== "string" ||
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(payload.checkpoint_id) ||
      !Array.isArray(payload.options) || payload.options.length > 2) {
    throw new Error("回复操作格式异常，请重新尝试。");
  }
  const choices = new Set();
  for (const option of payload.options) {
    if (!option || Object.keys(option).sort().join(",") !== "action,label" ||
        !Object.hasOwn(actionLabels, option.action) || option.label !== actionLabels[option.action] ||
        choices.has(option.action)) throw new Error("回复操作选项异常，请重新尝试。");
    choices.add(option.action);
  }
  state.actions = payload;
}

// 每次打开空白表单，定位始终绑定原回复；打开或取消不产生任何写请求。
function openTicketForm(state, choice) {
  if (choice.pending || choice.completed || ticketDialog.open || handoffDialog.open) return;
  ticketDraft = { state, choice };
  ticketForm.reset();
  ticketDescription.setCustomValidity("");
  ticketFields.disabled = false;
  ticketSubmit.disabled = ticketClose.disabled = ticketCancel.disabled = false;
  ticketSubmit.textContent = "提交工单";
  ticketError.hidden = true;
  ticketDialog.showModal();
  ticketType.focus();
}

// 保存中的表单保持打开，取消只关闭本地表单，不执行后台工单工具。
function closeTicketForm() {
  if (!ticketDraft?.choice.pending) ticketDialog.close();
}
ticketClose.addEventListener("click", closeTicketForm);
ticketCancel.addEventListener("click", closeTicketForm);
// 原生Escape关闭同样遵守提交中不可取消的边界。
ticketDialog.addEventListener("cancel", (event) => {
  if (ticketDraft?.choice.pending) event.preventDefault();
});
// 关闭时恢复原按钮焦点；旧会话已离开则回到当前输入框。
ticketDialog.addEventListener("close", () => {
  const trigger = ticketDraft?.choice.button;
  ticketDraft = null;
  (trigger?.isConnected && !trigger.disabled ? trigger : input).focus({ preventScroll: true });
});
// 输入时撤销此前的空白描述提示，便于用户直接修正后再次提交。
ticketDescription.addEventListener("input", () => ticketDescription.setCustomValidity(""));

// 表单提交才传递用户所填类别/描述及原回复定位，重试复用同一工单身份。
async function submitTicket(event) {
  event.preventDefault();
  const draft = ticketDraft;
  if (!draft || draft.choice.pending || draft.choice.completed) return;
  const { state, choice } = draft;
  const description = ticketDescription.value.trim();
  ticketDescription.setCustomValidity(description ? "" : "请填写问题描述，不能只输入空白。");
  if (!ticketForm.reportValidity()) return;
  choice.pending = true;
  choice.button.disabled = true;
  ticketFields.disabled = true;
  ticketSubmit.disabled = ticketClose.disabled = ticketCancel.disabled = true;
  ticketSubmit.textContent = "正在提交…";
  ticketError.hidden = true;
  try {
    const response = await fetch("/api/conversations/" + state.conversationId + "/actions/ticket", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assistant_message_id: state.actions.assistant_message_id,
        checkpoint_id: state.actions.checkpoint_id, ticket_type: ticketType.value, description }),
    });
    if (!response.ok) {
      const failure = await response.json().catch(() => ({}));
      throw new Error(failure.code === "ticket_conflict" ? "这条回复已提交过不同内容的工单，请使用原信息重试。" :
        response.status === 422 ? "请检查工单类别和问题描述后重试。" : "工单创建失败，请重试。");
    }
    const result = await response.json();
    if (!result || Object.keys(result).sort().join(",") !== "status,ticket_no" ||
        typeof result.ticket_no !== "string" || !result.ticket_no.trim() || result.ticket_no.length > 128 ||
        !["待处理", "已处理"].includes(result.status)) throw new Error("ticket_failed");
    choice.completed = true;
    // 结果作为新的聊天消息，离开原会话后不把旧结果插进新会话。
    if (state.bubble.isConnected) addMessage("assistant", "工单已创建 · " + result.ticket_no, "服务通知");
    if (ticketDraft === draft) ticketDialog.close();
  } catch (error) {
    if (ticketDraft === draft) {
      ticketError.textContent = error.message === "ticket_failed" ? "工单创建失败，请重试。" : error.message || "工单创建失败，请重试。";
      ticketError.hidden = false;
    }
  } finally {
    choice.pending = false;
    choice.button.disabled = choice.completed;
    if (ticketDraft === draft) {
      ticketFields.disabled = false;
      ticketSubmit.disabled = ticketClose.disabled = ticketCancel.disabled = false;
      ticketSubmit.textContent = "提交工单";
    }
    scrollBottom();
  }
}
ticketForm.addEventListener("submit", submitTicket);

// 打开主题内确认框，原回复与两个动作在用户确认前均保持原状。
function openHandoffForm(state, choice) {
  if (choice.completed || handoffDialog.open || ticketDialog.open || !state.bubble.isConnected) return;
  handoffDraft = { state, choice };
  handoffDialog.showModal();
  handoffCancel.focus();
}

// 取消或Escape仅关闭弹窗，恢复原按钮焦点，不执行任何接入动作。
function closeHandoffForm() {
  handoffDialog.close();
}
handoffClose.addEventListener("click", closeHandoffForm);
handoffCancel.addEventListener("click", closeHandoffForm);
handoffDialog.addEventListener("close", () => {
  const trigger = handoffDraft?.choice.button;
  handoffDraft = null;
  (trigger?.isConnected && !trigger.disabled ? trigger : input).focus({ preventScroll: true });
});

// 确认后新增独立通知与人工气泡，纯前端模拟，不能写工单或向旧会话追加结果。
function confirmHandoff() {
  const draft = handoffDraft;
  if (!draft || draft.choice.completed || !draft.state.bubble.isConnected) return;
  const { choice } = draft;
  choice.completed = true;
  choice.button.disabled = true;
  addMessage("assistant", "已接入人工客服", "服务通知");
  addMessage("assistant", "您好，我是客服小猫，请问有什么可以帮您的", "客服小猫 · 人工客服");
  handoffDialog.close();
  scrollBottom();
}
handoffConfirm.addEventListener("click", confirmHandoff);

// 流完全成功结束后才显示动作；每条旧回复闭包绑定自己的会话、快照和独立按钮状态。
function addActions(state) {
  if (!state.done || state.error || state.stopped || !state.actions || state.actionChoices.size || !state.actions.options.length) return;
  const section = document.createElement("div");
  section.className = "support-actions";
  section.setAttribute("aria-label", "可确认的客服操作");
  for (const option of state.actions.options) {
    const group = document.createElement("div");
    group.className = "support-action-group";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "support-action";
    button.textContent = actionLabels[option.action];
    const result = document.createElement("div");
    result.className = "support-action-result";
    result.setAttribute("role", "status");
    const choice = { button, result, pending: false, completed: false };
    state.actionChoices.set(option.action, choice);
    // 每个按钮只访问自身状态，后续聊天不会替换这条回复的动作身份。
    button.addEventListener("click", () => {
      if (option.action === "handoff") openHandoffForm(state, choice);
      else openTicketForm(state, choice);
    });
    group.append(button, result);
    section.append(group);
  }
  state.bubble.append(section);
}

// 只接受正文开始前的一份来源全集，严格保留编号和字符串主键。
function acceptCitations(payload, state) {
  if (state.hasCitations || state.hasDelta || !payload || Object.keys(payload).length !== 1 ||
      !Array.isArray(payload.citations) || payload.citations.length > 10) {
    throw new Error("回答来源格式异常，请重新尝试。");
  }
  const mapping = new Map();
  const identifiers = new Set();
  for (const citation of payload.citations) {
    if (!citation || Object.keys(citation).sort().join(",") !== "answer,chunk_id,n,question,section_path" ||
        !Number.isInteger(citation.n) || citation.n < 1 || citation.n > payload.citations.length ||
        mapping.has(String(citation.n)) || !validId(citation.chunk_id, 9223372036854775807n) ||
        identifiers.has(citation.chunk_id) || typeof citation.question !== "string" ||
        typeof citation.answer !== "string" ||
        !(citation.section_path === null || typeof citation.section_path === "string")) {
      throw new Error("回答来源格式异常，请重新尝试。");
    }
    mapping.set(String(citation.n), citation);
    identifiers.add(citation.chunk_id);
  }
  state.citations = mapping;
  state.hasCitations = true;
}

// 解析完整 SSE 帧，把正文加入码点队列，校验 done 身份并记录安全错误提示。
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
  if (state.refundOffer && !["done", "error"].includes(event) || state.actions && !["refund_offer", "done", "error"].includes(event)) throw new Error("回复操作之后收到多余事件，请重新尝试。");
  if (event === "status" && payload && typeof payload === "object") {
    if (state.hasDelta) throw new Error("正文开始后收到阶段事件，请重新尝试。");
    acceptStatus(payload, state);
  } else if (event === "citations") {
    acceptCitations(payload, state);
  } else if (event === "delta" && typeof payload?.delta === "string") {
    state.hasDelta = true;
    state.queue.push(...Array.from(payload.delta));
  } else if (event === "actions") {
    acceptActions(payload, state);
  } else if (event === "order_selection" && !state.hasDelta && !state.selection) {
    state.selection = validateSelection(payload);
  } else if (event === "paused" && state.selection && !state.hasDelta && payload?.reason === "order_selection" &&
      ["turn_id", "selection_id", "checkpoint_id"].every((key) => payload[key] === state.selection[key])) {
    state.terminal = true;
    state.paused = true;
  } else if (event === "refund_offer" && state.hasDelta) {
    acceptRefund(payload, state);
  } else if (event === "done" && payload?.conversation_id === state.conversationId &&
             validId(payload.message_id) && Object.keys(payload).sort().join(",") === "conversation_id,message_id" &&
             !state.selection && (!state.actions || state.actions.assistant_message_id === payload.message_id) &&
             (!state.refundOffer || state.refundOffer.assistant_message_id === payload.message_id) &&
             (!state.actions || !state.refundOffer || state.actions.checkpoint_id === state.refundOffer.checkpoint_id)) {
    state.terminal = true;
    state.done = true;
    state.messageId = payload.message_id;
  } else if (event === "error" && typeof payload?.message === "string") {
    state.terminal = true;
    state.error = payload.message;
  } else {
    throw new Error("收到的回复事件异常，请重新尝试。");
  }
}

// 首轮创建会话，再 POST 聊天请求并持续读取 SSE；后续轮次复用会话身份。
// 网络读取和逐字动画独立进行，EOF 必须有终止帧才算完整结束。
async function readReply(state, message, selection = null) {
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
      if (!validId(id)) {
        throw new Error("会话创建结果异常，请稍后重试。");
      }
      conversationId = id;
      saveSession();
    }
    state.conversationId = conversationId;
    const response = await fetch(selection ? "/api/conversations/" + state.conversationId + "/actions/select-order" : "/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
      body: JSON.stringify(selection || { conversation_id: state.conversationId, message }),
      signal: state.controller.signal,
    });
    if (!response.ok) {
      if (selection) state.recoverSelection = true;
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
    // 流式解码保留跨网络包拆开的中文字节，不能把每个包单独转成字符串。
    const decoder = new TextDecoder("utf-8", { fatal: true });
    let buffer = "";
    // 仅消费以空行结束的完整事件；残余半帧留在 buffer 等待下一包。
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
    if (selection && !state.done && !state.paused) state.recoverSelection = true;
    if (!state.stopped) state.error = error instanceof TypeError ? "连接失败，请检查服务是否启动后重试。" : error.message || "回复失败，请稍后重试。";
  } finally {
    if (reader) {
      try { await reader.cancel(); } catch { /* 中止请求可能已经关闭了读取器。 */ }
      reader.releaseLock();
    }
    state.networkFinished = true;
    if (state.recoverSelection && !state.stopped) pendingRetry(state.conversationId, "订单选择未确认，请重新读取服务器当前待选后继续。");
  }
}

// 新消息与选单恢复复用同一渲染状态，刷新摘要无需启动动画或伪造问句。
function createReplyState(text = "") {
  const assistant = addMessage("assistant", text);
  return { ...assistant, controller: new AbortController(), queue: [], visible: text, citations: new Map(), toolBadges: new Map(), actions: null, actionChoices: new Map(), hasCitations: false, hasDelta: false, lastPaint: performance.now(), networkFinished: false, terminal: false, done: false, stopped: false, error: "", startedText: false, animation: null };
}

// 提交时创建用户与助手气泡；回复进行中再次点击提交则调用停止逻辑。
form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (active) { stopReply(); return; }
  const message = input.value.trim();
  if (!message) return;
  lockSelections();
  if (messages.childElementCount === 0) document.querySelector("#conversation-title").textContent = message;
  welcome.hidden = true;
  followBottom = true;
  bottomButton.hidden = true;
  addMessage("user", message);
  const state = createReplyState();
  state.bubble.classList.add("waiting");
  for (let index = 0; index < 3; index += 1) {
    const dot = document.createElement("span");
    dot.className = "thinking-dot";
    state.text.append(dot);
  }
  active = state;
  input.value = "";
  busy(true);
  // 动画负责显示队列，readReply 负责填充队列，二者共享本轮 state。
  state.animation = requestAnimationFrame((time) => tick(state, time));
  void readReply(state, message);
});

// 为两个新会话入口绑定重置动作，清空页面身份后下一条消息重新创建会话。
newButtons.forEach((button) => button.addEventListener("click", () => {
  if (active) return;
  if (sourceDialog.open) closeSource();
  if (handoffDialog.open) handoffDialog.close();
  if (ticketDialog.open) ticketDialog.close();
  if (refundDialog.open) refundDialog.close();
  conversationId = null;
  selectionGroups.clear();
  refundLocators = [];
  saveSession();
  messages.replaceChildren();
  welcome.hidden = false;
  document.querySelector("#conversation-title").textContent = "新的客服对话";
  input.value = "";
  followBottom = true;
  resizeInput();
  scrollArea.scrollTop = 0;
  input.focus({ preventScroll: true });
}));
// 示例问题只填入输入框，由用户确认后发送。
document.querySelectorAll("[data-prompt]").forEach((button) => button.addEventListener("click", () => {
  input.value = button.dataset.prompt;
  resizeInput();
  input.focus({ preventScroll: true });
}));

// 用五秒超时探测健康接口，更新页面连接提示。
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
void restoreSession();
