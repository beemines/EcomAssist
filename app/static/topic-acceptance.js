"use strict";
const $ = id => document.getElementById(id);
const el = (tag, text, className) => {
  const result = document.createElement(tag);
  if (text !== undefined) result.textContent = String(text);
  if (className) result.className = className;
  return result;
};
const fixed = value => Number.isFinite(value) ? value.toFixed(4) : "—";
const count = value => Number.isFinite(value) ? value.toLocaleString("zh-CN") : "未知";
const when = value => {
  const date = new Date(value);
  return Number.isFinite(date.getTime()) ? new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "short", timeStyle: "short", timeZone: "Asia/Shanghai"
  }).format(date) : "未知";
};
const bytes = value => value >= 1024 ** 2 ? (value / 1024 ** 2).toFixed(1) + " MiB" :
  value >= 1024 ? (value / 1024).toFixed(1) + " KiB" : value + " B";
function link(label, href) { const a = el("a", label); a.href = href; return a; }
function card(title, value, detail) {
  const article = el("article", undefined, "kpi");
  article.append(el("span", title, "label"), el("strong", value), el("small", detail));
  return article;
}
async function get(path) {
  const response = await fetch(path, {cache: "no-store"});
  if (!response.ok) throw Error("当前无法读取状态（HTTP " + response.status + "），请进入对应页面核对。");
  return response.json();
}

async function portal() {
  try {
    const s = await get("/api/topics/summary");
    $("portal-topics").textContent = s.status === "ready" ?
      "池流水 " + count(s.pool_total) + " · 有效分类 " + count(s.effective) + " · 命中 " +
        s.topics.filter(t => t.count > 0).length + "/17 类" : "当前模型未配置，进入主题页查看准备状态。";
  } catch (error) { $("portal-topics").textContent = "统计暂不可用，进入主题页排查；未将故障显示为零。"; }
}

let evidence = null, refreshVersion = 0;
const tabs = ["overview", "evaluation", "data", "errors"];
function selectTab(name, focus = false) {
  if (!tabs.includes(name)) name = "overview";
  for (const key of tabs) {
    const selected = name === key, button = $("tab-" + key);
    $(key).hidden = !selected;
    button.setAttribute("aria-selected", String(selected)); button.tabIndex = selected ? 0 : -1;
    if (selected && focus) button.focus();
  }
}
function gate(index, title, state, description, destination, buttonLabel) {
  const item = el("article", undefined, "gate"), head = el("div", undefined, "gate-head");
  const heading = el("h3"); heading.append(el("span", String(index).padStart(2, "0"), "gate-number"), document.createTextNode(title));
  head.append(heading, el("span", state, state === "已知问题" || state === "AI 代审" ? "badge caution" : "badge"));
  item.append(head, el("p", description), link(buttonLabel || "查看证据 →", destination));
  return item;
}
function renderOverview(d) {
  const score = d.metrics.silver;
  $("overview-kpis").replaceChildren(card("银标 Macro-F1", fixed(score.macro_f1), "187 条 · 各类等权"),
    card("银标 Micro-F1", fixed(score.micro_f1), "17 类标签一起统计"),
    card("固定诊断", d.probes.filter(p => p.passed).length + " / " + d.probes.length, "已保存的真实推理证据，非总体质量"),
    card("本轮评测复核", "102 条", "用户授权 AI 代审 · 非独立人工"));
  $("gates").replaceChildren(
    gate(1, "权威类目", "证据齐备", "17 类及边界来自同一术语表，模型、服务与统计绑定同一版本。", "#data"),
    gate(2, "数据血缘", "证据齐备", "原池 29 行，含 20 条来源未核实种子；本轮冻结 2369 原句，增强只进训练。", "#data"),
    gate(3, "分组与隔离", "已知问题", "已发现 1 对历史训练 / 验证近重复。原数据和模型保留，不追认验证完全独立。", "#errors"),
    gate(4, "全参数训练", "证据齐备", "102280721 个参数全部参与训练；7 轮后早停，验证选 epoch 5。", "#data"),
    gate(5, "留出评测", "证据齐备", "完整 187 条、17 类 P/R/F1 与 2×2 矩阵；银标与代审子集分别展示。", "#evaluation"),
    gate(6, "阈值与多标签", "证据齐备", "逐类验证阈值已冻结。“买大了想退”命中退换货与尺码；全未过线则待复核。", "#evaluation"),
    gate(7, "导出与独立服务", "证据齐备", "CPU 重载 2 条最大差为 0，固定诊断 8/8。8103 实时在线状态请另查 health。", "http://127.0.0.1:8103/health", "打开实时 health →"),
    gate(8, "错例复核", "AI 代审", "测试 68 条与额外错例 34 条已逐项代审：81 保留、20 改标、1 排除；不是人工 gold。", "#errors"),
    gate(9, "旁路批次与主题", "证据齐备", "既定 20 条落表；同批重放新增 0、跳过 20。统计按问题池流水计数。", "/topics", "打开主题分布 →")
  );
}
function scoreCell(value, unavailable = false) {
  const td = el("td"), box = el("span", undefined, "score-value"), track = el("span", undefined, "track"), fill = el("i");
  fill.style.width = Math.max(0, Math.min(100, value * 100)) + "%"; track.append(fill);
  box.append(el("span", unavailable ? "—" : fixed(value)), track); td.append(box);
  if (unavailable) td.title = "此范围该项分母为 0；原报告按 0 计入聚合，不能当作满分。";
  return td;
}
function renderMetrics(key) {
  const m = evidence.metrics[key];
  $("cohort-description").textContent = m.description;
  $("metric-kpis").replaceChildren(card("评测样本", count(m.sample_count), m.title),
    card("Macro-F1", fixed(m.macro_f1), "每类 F1 简单平均，零分母处理沿用原报告"),
    card("Micro-F1", fixed(m.micro_f1), "所有标签决策汇总计算"),
    card("全标签完全匹配", m.exact_count + " / " + m.sample_count, "同一道题的所有标签恰好一致"));
  for (const type of ["micro", "macro"]) {
    const target = $(type + "-card");
    target.replaceChildren(el("h3", type === "micro" ? "Micro · 汇总所有标签" : "Macro · 各类等权平均"),
      el("p", "P " + fixed(m[type + "_precision"]) + "　R " + fixed(m[type + "_recall"]) + "　F1 " + fixed(m[type + "_f1"])),
      el("p", type === "micro" ? "样本多的类影响较大。" : "先各类计算再平均；Macro-F1 不是用平均 P/R 再计算。", "muted"));
  }
  const rows = [], matrices = [];
  for (const r of m.per_class) {
    const tr = el("tr");
    tr.append(el("th", r.label), scoreCell(r.precision, r.undefined_denominators.some(v => v.includes("精确率"))),
      scoreCell(r.recall, r.support === 0), scoreCell(r.f1, r.undefined_denominators.some(v => v.includes("F1"))), el("td", count(r.support)));
    tr.firstChild.scope = "row"; rows.push(tr);
    const box = el("article", undefined, "matrix"), cells = el("div", undefined, "cells");
    const [[tn, fp], [fn, tp]] = r.confusion;
    for (const [name, number, text, wrong] of [["TN", tn, "正确未标", false], ["FP", fp, "多标", true], ["FN", fn, "漏标", true], ["TP", tp, "正确命中", false]]) {
      const cell = el("div", undefined, "cell" + (wrong && number > 0 ? " wrong" : ""));
      cell.append(el("small", name + " · " + text), el("strong", count(number))); cells.append(cell);
    }
    box.append(el("h3", r.label), cells); matrices.push(box);
  }
  $("class-metrics").replaceChildren(...rows); $("matrices").replaceChildren(...matrices);
  $("matrix-summary").textContent = "本范围共 " + count(m.sample_count * 17) + " 个标签决策；多标 FP " +
    m.false_positive_labels + " 次、漏标 FN " + m.false_negative_labels + " 次。矩阵不是互斥的 17×17 分类表。";
}
function renderThresholds(d) {
  const rows = [];
  d.thresholds.forEach(r => { const tr = el("tr"); tr.append(el("th", r.label), el("td", r.threshold.toFixed(2)),
    el("td", fixed(r.validation_f1)), el("td", r.positive_support + " / " + r.negative_support)); rows.push(tr); });
  $("thresholds").replaceChildren(...rows);
  $("example-result").textContent = "实际标签：" + d.example.labels.join(" ＋ ") + "（已保存的 HTTP 结果）";
  const probabilities = d.labels.map((label, index) => {
    const p = d.example.probabilities[index], t = d.thresholds[index].threshold, hit = d.example.labels.includes(label);
    const row = el("div", undefined, "probability-row" + (hit ? " hit" : "")), track = el("span", undefined, "progress-track"), fill = el("i");
    fill.style.width = p * 100 + "%"; track.append(fill);
    row.append(el("span", label), track, el("span", p.toFixed(3) + " / " + t.toFixed(2) + (hit ? " 命中" : ""), "score")); return row;
  });
  $("probabilities").replaceChildren(...probabilities);
}
function epochChart(rows, best) {
  const ns = "http://www.w3.org/2000/svg", svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 760 190"); svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "验证 Macro-F1 随训练轮次变化，第 " + best + " 轮最佳；历史验证存在一对近重复。");
  const points = rows.map((r, i) => [46 + i * (668 / Math.max(rows.length - 1, 1)), 150 - r.eval_macro_f1 * 125]);
  for (const y of [25, 87.5, 150]) { const line = document.createElementNS(ns, "line");
    Object.entries({x1:46,x2:714,y1:y,y2:y,stroke:"#e4ebe1"}).forEach(([k,v]) => line.setAttribute(k,v)); svg.append(line); }
  const path = document.createElementNS(ns, "polyline");
  path.setAttribute("points", points.map(p => p.join(",")).join(" ")); path.setAttribute("fill", "none");
  path.setAttribute("stroke", "#679c7e"); path.setAttribute("stroke-width", "3"); svg.append(path);
  points.forEach(([x,y], i) => {
    const circle = document.createElementNS(ns, "circle");
    Object.entries({cx:x,cy:y,r:rows[i].epoch===best?5:3,fill:rows[i].epoch===best?"#286659":"#97b7a0"}).forEach(([k,v]) => circle.setAttribute(k,v));
    const text = document.createElementNS(ns, "text"); text.setAttribute("x", x); text.setAttribute("y", 177); text.setAttribute("text-anchor", "middle");
    text.textContent = "epoch " + rows[i].epoch; svg.append(circle, text);
    if (rows[i].epoch === best) { const label = document.createElementNS(ns,"text"); label.setAttribute("x",x);label.setAttribute("y",Math.max(15,y-14));
      label.setAttribute("text-anchor","middle");label.setAttribute("class","best-label");label.textContent="最佳 "+fixed(rows[i].eval_macro_f1);svg.append(label); }
  });
  return svg;
}
function renderData(d) {
  const steps = [["问题池种子", "29 / 20", "29 条流水；20 条来源未核实种子"], ["本轮冻结原句", count(d.dataset.original_samples), "历史已审句＋多轮合成补足"],
    ["训练 / 验证 / 测试", "1887 / 295 / 187", "按组冻结，保留历史版本及已知限制"], ["仅训练集增强", "+143 → 2030", "增强不进入验证或测试"]];
  $("lineage").replaceChildren(...steps.map(([label,value,detail]) => { const block = el("article", undefined, "lineage-step"); block.append(el("span",label),el("strong",value),el("small",detail));return block; }));
  $("origins").textContent = "来源：训练原句为 20 条来源未核实＋1867 条合成；验证 295 与测试 187 条均为合成。没有确认真实客户 gold 留出集。";
  const t = d.training;
  $("training-kpis").replaceChildren(card("参与训练参数", count(t.trainable_parameters), "与全部参数相同，全参数微调"),
    card("实际训练轮次", count(t.epochs.length), "最多 8 轮，早停 patience 2"), card("最佳轮次", "epoch " + t.best_epoch, "仅由验证 Macro-F1 选择"),
    card("训练耗时", (t.duration_seconds / 60).toFixed(1) + " 分钟", "实际记录；显存峰值 " + bytes(t.peak_allocated_bytes)));
  $("training-note").textContent = "固定 seed " + t.seed + "；编码器前后权重 hash " + (t.encoder_changed ? "已变化" : "未证明变化") +
    "。验证最佳 Macro-F1 " + fixed(t.best_macro_f1) + "；已知近重复使该验证分数有乐观偏差风险，不能与测试分数混用。";
  const chart = el("div", undefined, "epoch-plot"); chart.append(epochChart(t.epochs,t.best_epoch)); $("epoch-chart").replaceChildren(chart);
  $("epochs").replaceChildren(...t.epochs.map(row => {const tr=el("tr");tr.append(el("th",row.epoch),el("td",fixed(row.eval_macro_f1)),el("td",fixed(row.eval_micro_f1)),el("td",row.epoch===t.best_epoch?"保留的最佳权重":""));return tr;}));
  $("deployment").textContent = "模型包：权重＋tokenizer＋逐类阈值＋身份清单。CPU 重载核对 " + d.cpu_roundtrip.sample_count +
    " 条，最大绝对差 " + d.cpu_roundtrip.max_abs_difference + "；固定诊断 " + d.probes.filter(p=>p.passed).length + "/" + d.probes.length +
    " 通过。模型版本 " + d.model_version + "。";
  $("artifacts").replaceChildren(...d.files.map(file => {
    const tr=el("tr"), path=el("td",file.path,"artifact-path"), hash=el("td",undefined,"hash-cell"), details=el("details"), summary=el("summary",file.sha256.slice(0,12)+"…");
    path.append(el("small",file.group));details.append(summary,el("code",file.sha256,"code-hash"));hash.append(details);
    tr.append(path,el("td",bytes(file.bytes)),el("td",when(file.modified_at)),hash);return tr;
  }));
}
function renderErrors(d) {
  $("review-counts").replaceChildren(...[["test-review","测试复核包"],["error-review","额外错例包"]].map(([key,title]) => {
    const r=d.reviews[key], article=el("article");article.append(el("h3",title+" · "+r.count+" 条"),el("p","保留 "+r.accepted+" · 改标 "+r.corrected+" · 排除 "+r.excluded));return article;
  }));
  const rows=[...d.metrics.silver.per_class].sort((a,b)=>(b.confusion[0][1]+b.confusion[1][0])-(a.confusion[0][1]+a.confusion[1][0]));
  const largest=Math.max(1,...rows.map(r=>r.confusion[0][1]+r.confusion[1][0]));
  $("error-bars").replaceChildren(...rows.map(r=>{
    const fp=r.confusion[0][1],fn=r.confusion[1][0],row=el("div",undefined,"error-row"),track=el("div",undefined,"error-track");
    const a=el("i",undefined,"fp"),b=el("i",undefined,"fn");a.style.width=100*fp/largest+"%";b.style.width=100*fn/largest+"%";track.append(a,b);
    row.append(el("span",r.label),track,el("span","多标 "+fp+" · 漏标 "+fn,"error-count"));return row;
  }));
}
async function refreshLive() {
  const version=++refreshVersion;$("refresh").disabled=true;
  try {
    const s=await get("/api/topics/summary");if(version!==refreshVersion)return;
    if(s.status!=="ready")$("live-state").textContent="模型未配置，当前展示已保存报告。";
    else if(s.identity.model_version!==evidence.model_version)$("live-state").textContent="当前模型与报告版本不同，以下为历史结果。";
    else $("live-state").textContent="已归类 "+s.effective+" / "+s.pool_total+" 条 · 覆盖 "+s.topics.filter(t=>t.count>0).length+" / 17 类";
  } catch(error) { if(version===refreshVersion)$("live-state").textContent="实时统计暂不可用，仍可查看已保存报告。"; }
  finally { if(version===refreshVersion)$("refresh").disabled=false; }
}
async function acceptance() {
  try {
    const d=await get("/static/topic-acceptance-data.json?v=20261024");
    if(d.schema_version!==1||d.labels.length!==17||new Set(d.labels).size!==17||d.kind!=="immutable_evidence_summary")throw Error("验收汇总格式无法识别，请核对产物。");
    evidence=d;$("report").hidden=false;
    $("evidence-time").textContent="证据核对："+when(d.evidence_verified_at)+"（上海时间）· 固定报告";
    $("identity").textContent="模型 "+d.model_version.slice(0,18)+"… · "+d.taxonomy_version;
    $("identity").title=d.model_version;
    renderOverview(d);renderThresholds(d);renderData(d);renderErrors(d);renderMetrics("silver");
    $("cohort").onchange=()=>renderMetrics($("cohort").value);
    $("budget").textContent="账本快照 "+d.budget.attempts+"/"+d.budget.attempt_limit+" 次 · 保守占用 ¥"+d.budget.conservative_cny.toFixed(2)+" / ¥10（含 1 历史未知）";
    for(const [index,name] of tabs.entries()) {
      const button=$("tab-"+name);
      button.onclick=()=>{location.hash=name;};
      button.onkeydown=event=>{
        let next=null;if(event.key==="ArrowRight")next=(index+1)%tabs.length;if(event.key==="ArrowLeft")next=(index+tabs.length-1)%tabs.length;
        if(event.key==="Home")next=0;if(event.key==="End")next=tabs.length-1;
        if(next!==null){event.preventDefault();location.hash=tabs[next];selectTab(tabs[next],true);}
      };
    }
    window.addEventListener("hashchange",()=>selectTab(location.hash.slice(1)));
    selectTab(location.hash.slice(1));$("refresh").onclick=refreshLive;await refreshLive();
  } catch(error) { $("load-error").hidden=false;$("load-error").textContent="验收证据无法完整读取："+error.message;$("report").hidden=true;$("refresh").disabled=true; }
}
if(document.body.dataset.view==="admin")portal();else acceptance();
