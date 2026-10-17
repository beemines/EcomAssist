"use strict";

// Owns only navigation/list rendering. Chat retains history, SSE and business state.
class ConversationSidebar {
  constructor({ onSelect, onNew, getBusy }) {
    this.list = document.querySelector("#conversation-list");
    this.activeId = null;
    this.busy = false;
    this.revision = 0;
    this.getBusy = getBusy;
    const sidebar = document.querySelector(".sidebar");
    const toggle = document.querySelector("#conversation-toggle");
    const close = () => { sidebar.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); };
    toggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.querySelector("#conversation-close").addEventListener("click", close);
    document.querySelector("#conversation-backdrop").addEventListener("click", close);
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && sidebar.classList.contains("open")) { close(); toggle.focus(); } });
    this.list.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-conversation-id]");
      if (!button || this.busy || getBusy()) return;
      if (await onSelect(button.dataset.conversationId)) close();
    });
    for (const button of document.querySelectorAll("#new-chat, #mobile-new-chat")) button.addEventListener("click", async () => {
      if (!this.busy && !getBusy() && await onNew()) close();
    });
  }

  async refresh() {
    const revision = ++this.revision;
    const items = [], ids = new Set(), cursors = new Set();
    let before = null;
    try {
      do {
        const query = new URLSearchParams({ limit: "50" });
        if (before) query.set("before_id", before);
        const response = await fetch("/api/conversations?" + query);
        if (!response.ok) return;
        const page = await response.json();
        if (!Array.isArray(page.items)) return;
        for (const item of page.items) {
          if (!item || typeof item.id !== "string" || !/^[1-9]\d{0,19}$/.test(item.id) || BigInt(item.id) > 18446744073709551615n || ids.has(item.id) || typeof item.first_question_preview !== "string") return;
          ids.add(item.id); items.push(item);
        }
        before = page.next_before_id;
        if (before !== null && (typeof before !== "string" || !/^[1-9]\d{0,19}$/.test(before) || cursors.has(before))) return;
        cursors.add(before);
      } while (before);
      if (revision !== this.revision) return;
      const fragment = document.createDocumentFragment();
      for (const item of items) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "conversation-item";
        button.dataset.conversationId = item.id;
        const preview = document.createElement("span");
        preview.textContent = item.first_question_preview || "新对话";
        button.append(preview);
        if (item.has_summary) {
          const badge = document.createElement("small"); badge.textContent = "已摘要"; button.append(badge);
        }
        fragment.append(button);
      }
      this.list.replaceChildren(fragment);
      this.setActive(this.activeId);
      this.setBusy(this.busy);
    } catch { /* The navigation service must never block sending a question. */ }
  }

  setActive(id) {
    this.activeId = id;
    for (const button of this.list.querySelectorAll("[data-conversation-id]")) button.setAttribute("aria-current", String(button.dataset.conversationId === id));
  }

  setBusy(value) {
    this.busy = value;
    for (const button of this.list.querySelectorAll("button")) button.disabled = value;
  }
}
