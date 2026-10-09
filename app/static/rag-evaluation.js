"use strict";
// 当前页面只展示白名单导出的真实历史报告，不启动模型调用或写入反馈。
const strategies = ["dense", "bm25", "hybrid", "hybrid_rerank"];
const names = {dense:"vector", bm25:"bm25", hybrid:"hybrid", hybrid_rerank:"hybrid_rerank"};
const tones = {dense:"#498d79", bm25:"#b8945e", hybrid:"#6f91a8", hybrid_rerank:"#807ca8"};
const buckets = {overall:"总体", A_policy:"政策类", B_model:"型号类", C_colloquial:"口语类", D_unanswerable:"库外问题", E_multi:"跨文档类"};
const descriptions = {mrr_at_10:"首条相关块在前十中的倒数排名；值越高，首条相关证据越靠前。",recall_at_10:"前十条命中的物理金标块比例；本历史版按物理块计，不是新语料的证据组口径。",recall_at_50:"前五十候选命中的物理金标块比例，观察召回阶段的证据遗漏。",prompt_recall:"真正装入生成 Prompt 的物理金标块覆盖率，不是答案要点覆盖度。",faithfulness:"裁判判为受实际证据支持的断言比例；无断言拒答为不适用。"};
let report = null;
let detailTrigger = null;
const detailDialog = document.querySelector("#detail-dialog");

// 所有报告正文按文本放入节点，避免模型回答或知识原文成为可执行 HTML。
function node(tag, text, className) {
  const value = document.createElement(tag);
  if (text !== undefined) value.textContent = String(text);
  if (className) value.className = className;
  return value;
}

// 有效值保留三位小数；缺失和非法数值明确显示不适用。
function score(value) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(3) : "—";
}

// 对每项指标匹配它自己的分母，不能借用完整题数伪造评估范围。
function metricText(row, metric) {
  return score(row[metric]) + " / " + (row[metric + "_n"] ?? 0);
}

// 从冻结的汇总表按桶和策略读取，不在浏览器重算模型或裁判得分。
function summary(bucket, strategy) {
  return report.summary.find((row) => row.bucket === bucket && row.strategy === strategy);
}

// 概览区报告并列最优、实际完成与错误，而不以单一最高值宣布总体胜者。
function renderCards() {
  const overall = strategies.map((strategy) => summary("overall", strategy));
  const valid = overall.filter((row) => typeof row.mrr_at_10 === "number");
  const best = valid.length ? Math.max(...valid.map((row) => row.mrr_at_10)) : null;
  const tied = valid.filter((row) => Math.abs(row.mrr_at_10 - best) < 1e-10).map((row) => names[row.strategy]).join("、");
  const data = [
    ["最高 MRR@10",score(best),tied + "；仅比较有效检索样本"],
    ["知识库 / 题目",report.knowledge_count + " / " + report.question_count,"本轮冻结的历史 XM 合成资料"],
    ["生成与裁判完整完成",report.completed + " / " + report.records.length,"检索完成不等于整条生成链成功"],
    ["错误项",report.errors,"未执行 " + report.not_attempted + " 项；错误不计满分"],
  ];
  const cards = document.querySelector("#cards");
  cards.replaceChildren();
  for (const [label,value,sub] of data) {
    const card = node("article",undefined,"card");
    card.append(node("div",label,"label"),node("div",value,"value"),node("div",sub,"sub"));
    cards.append(card);
  }
}

// 指标切换保留原报告数值和分母；条形长度只表示该值，不隐藏小样本。
function renderMatrix() {
  const metric = document.querySelector("#metric-select").value;
  document.querySelector("#metric-description").textContent = descriptions[metric];
  const table = document.querySelector("#metric-table");
  table.replaceChildren();
  for (const [bucket,label] of Object.entries(buckets)) {
    const row = node("tr");
    row.append(node("th",label));
    for (const strategy of strategies) {
      const data = summary(bucket,strategy);
      const cell = node("td");
      cell.append(node("span",score(data[metric]),"metric-value"),node("span","n=" + (data[metric + "_n"] ?? 0),"sample"));
      const bar = node("div",undefined,"bar");
      bar.setAttribute("aria-hidden","true");
      const fill = node("span");
      const value = typeof data[metric] === "number" ? Math.min(1,Math.max(0,data[metric])) : 0;
      fill.style.setProperty("--width",value * 100 + "%");
      fill.style.setProperty("--tone",tones[strategy]);
      bar.append(fill); cell.append(bar); row.append(cell);
    }
    table.append(row);
  }
}

// 生成汇总同时展示完整完成和拒答分母，避免把少量成功裁判代表全量。
function renderQuality() {
  const table = document.querySelector("#quality-table");
  for (const strategy of strategies) {
    const data = summary("overall",strategy);
    const row = node("tr");
    for (const value of [names[strategy],data.completed + "/" + data.total,data.errors,metricText(data,"faithfulness"),score(data.refusal_accuracy) + " / " + data.refusal_n]) row.append(node("td",value));
    table.append(row);
  }
  document.querySelector("#policy-note").textContent = "该历史版仅 hybrid_rerank 使用额外重排分门槛，三条基线只做内容自评；生成差异不能全部归因于排序。19 项错误包含 14 项裁判错误、5 项答案校验错误。本页未重新运行历史实验。";
}

// 逐题详情绑定本记录，展示实际供给模型的证据全集和原裁判，避免引用跨轮混淆。
function openDetail(record, trigger) {
  detailTrigger = trigger;
  document.querySelector("#detail-title").textContent = record.eval_id + " · " + names[record.strategy] + " · " + buckets[record.bucket];
  const body = document.querySelector("#detail-body");
  body.replaceChildren();
  const sections = [
    ["问题",record.query],
    ["答案必需事实（原历史标注）",record.required_facts],
    ["检索排名与证据覆盖",{gold_ids:record.gold_ids,ranked_ids:record.ranked_ids,recall_at_10:record.recall_at_10,mrr_at_10:record.mrr_at_10,prompt_recall:record.prompt_recall}],
    ["实际回答",record.answer ?? "未保存有效回答"],
    ["实际证据全集",record.citations ?? []],
    ["充分性自评",record.self_check ?? "无有效自评记录"],
    ["忠实度裁判",record.judge ?? "裁判未完成或不适用；不伪造得分"],
    ["状态与错误",{status:record.status,error_stage:record.error_stage,error_code:record.error_code,refused:record.refused,latency_seconds:record.latency_seconds}],
  ];
  for (const [title,value] of sections) {
    const section = node("section",undefined,"detail-section");
    section.append(node("h3",title),node("pre",typeof value === "string" ? value : JSON.stringify(value,null,2)));
    body.append(section);
  }
  detailDialog.showModal();
  document.querySelector("#detail-close").focus();
}

// 桶、策略、状态与关键词共同筛选记录；筛选只影响展示，不改报告统计。
function renderCases() {
  const bucket = document.querySelector("#bucket-filter").value;
  const strategy = document.querySelector("#strategy-filter").value;
  const status = document.querySelector("#status-filter").value;
  const query = document.querySelector("#query-filter").value.trim().toLowerCase();
  const rows = report.records.filter((r) => (bucket === "all" || r.bucket === bucket) && (strategy === "all" || r.strategy === strategy) && (status === "all" || r.status === status) && (!query || (r.eval_id + " " + r.query).toLowerCase().includes(query)));
  const table = document.querySelector("#cases-table");
  table.replaceChildren();
  for (const record of rows) {
    const row = node("tr");
    row.append(node("td",record.eval_id),node("td",record.query,"case-query"),node("td",names[record.strategy]),node("td",score(record.mrr_at_10)),node("td",record.status === "ok" ? "完整完成" : "错误","status-" + record.status));
    const cell = node("td");
    const button = node("button","查看","detail-link");
    button.setAttribute("aria-label","查看 " + record.eval_id + " " + names[record.strategy] + " 的评估详情");
    // 点击闭包使用这一行的记录，不依赖后续筛选产生的数组下标。
    button.addEventListener("click",() => openDetail(record,button));
    cell.append(button); row.append(cell); table.append(row);
  }
  document.querySelector("#result-count").textContent = "显示 " + rows.length + " / " + report.records.length + " 条策略结果";
}

// 读取固定同源公开报告，校验结构后绘制；失败显示诊断而不填零分。
async function loadReport() {
  try {
    const response = await fetch("/static/rag-evaluation-history.json",{cache:"no-store"});
    if (!response.ok) throw new Error("report_unavailable");
    report = await response.json();
    if (!Array.isArray(report.records) || !Array.isArray(report.summary) || !report.summary.some((r) => r.bucket === "overall")) throw new Error("invalid_report");
    const choice = document.querySelector("#report-select");
    choice.replaceChildren(node("option","历史 XM 语料 · 30 题 · " + report.started_at.slice(0,10)));
    document.querySelector("#run-status").textContent = "已结束 · 有错误";
    document.querySelector("#run-status").classList.add("warning");
    document.querySelector("#scope-note").textContent = "当前展示：已保存的真实历史报告（30 题、84 块），不是新一轮 MH 型号 300 题结果。全部 120 项已尝试，101 项完整完成、19 项错误。";
    document.querySelector("#draft-note").textContent = "八篇草稿离线切分为 " + report.draft_chunk_count + " 块；五桶各 60 题尚待逐项审标。尚未建库、调用新一轮模型或产生分数。";
    for (const [bucket,label] of Object.entries(buckets)) if (bucket !== "overall") {
      const option = node("option",label); option.value = bucket; document.querySelector("#bucket-filter").append(option);
    }
    for (const strategy of strategies) {
      const option = node("option",names[strategy]); option.value = strategy; document.querySelector("#strategy-filter").append(option);
      const legend = node("span"); const swatch = node("i",undefined,"swatch"); swatch.style.setProperty("--tone",tones[strategy]); legend.append(swatch,node("span",names[strategy])); document.querySelector("#legend").append(legend);
    }
    renderCards(); renderMatrix(); renderQuality(); renderCases();
    document.querySelector("#report").hidden = false;
  } catch {
    const error = document.querySelector("#load-error"); error.hidden = false; error.textContent = "评估报告暂时无法读取，请刷新页面或核对报告文件。未加载的指标不会显示为零。";
  }
}

// 指标与筛选控制只重新绘制本地快照，不发送模型请求。
document.querySelector("#metric-select").addEventListener("change",renderMatrix);
for (const id of ["bucket-filter","strategy-filter","status-filter"]) document.querySelector("#" + id).addEventListener("change",renderCases);
document.querySelector("#query-filter").addEventListener("input",renderCases);
// 关闭弹窗与 Escape 共享焦点恢复，便于键盘继续浏览逐题结果。
document.querySelector("#detail-close").addEventListener("click",() => detailDialog.close());
detailDialog.addEventListener("close",() => { if (detailTrigger?.isConnected) detailTrigger.focus(); });
loadReport();
