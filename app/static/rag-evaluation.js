"use strict";
const API = "/api/rag-evaluations";
const strategies = ["dense","bm25","hybrid","hybrid_rerank"];
const names = {dense:"vector",bm25:"bm25",hybrid:"hybrid",hybrid_rerank:"hybrid_rerank"};
const displayNames = {dense:"纯向量",bm25:"纯 BM25",hybrid:"混合检索",hybrid_rerank:"混合 + 重排"};
const tones = {dense:"#79abc9",bm25:"#81b879",hybrid:"#d98eab",hybrid_rerank:"#e8ae72"};
const chartBuckets = ["A_policy","B_model","C_colloquial","E_multi","overall"];
const buckets = {overall:"总体",A_policy:"政策类",B_model:"型号类",C_colloquial:"口语类",E_multi:"跨文档类",D_absent:"库外问题"};
const labels = {queued:"等待启动",preparing:"准备资料",running:"运行中",cancelling:"取消中 · 等待清理",completed:"完整完成",completed_with_errors:"完成 · 有错误",failed:"运行失败",cancelled:"已取消",interrupted:"已中断",not_attempted:"未执行",rewrite_error:"改写错误",retrieval_error:"检索错误",self_check_error:"自评错误",answer_error:"回答错误",judge_error:"裁判错误",ok:"历史完成",error:"历史错误"};
const activeStates = new Set(["queued","preparing","running","cancelling"]);
const metrics = {
 recall_at_5:["Recall@5 · 完整组覆盖","最终前 5 条覆盖完整金标组的比例。"],
 recall_at_10:["Recall@10 · 完整组覆盖","最终前 10 条覆盖完整金标组的比例。"],
 mrr_at_10:["MRR@10 · 首条相关排名","首条相关块排名倒数；首条命中不代表全部跨文档证据齐全。"],
 all_groups_hit_at_5:["All-groups-hit@5","最终前 5 条是否满足全部金标组。"],
 all_groups_hit_at_10:["All-groups-hit@10","最终前 10 条是否满足全部金标组。"],
 candidate_group_coverage:["候选 Top-50 组覆盖","重排前候选集覆盖完整金标组的比例。"],
 prompt_group_coverage:["Prompt 完整组覆盖","实际送入回答 Prompt 的证据覆盖，不等于前十检索结果。"],
 answer_point_coverage:["答案要点覆盖","联合裁判确认覆盖的要点比例；裁判失败不计有效样本。"],
 faithfulness:["Faithfulness · 忠实度","全部断言中有证据支持的比例；没有断言为 N/A。"],
 absent_refusal_rate:["库外拒答率","预期拒答题中，合法回答实际拒答的比例。"],
 answerable_false_refusal_rate:["可回答误拒答率","可回答题中合法回答错误拒答的比例；越低越好。"],
 legacy_mrr_at_10:["历史 MRR@10 · v1","旧 v1 首条相关块排名，不能与新实验直接比较。"],
 legacy_recall_at_10:["历史 Recall@10 · 物理块","旧物理块召回，不是新完整组指标。"],
 legacy_recall_at_50:["历史 Recall@50 · 物理块","旧候选物理块召回口径。"],
 legacy_prompt_recall:["历史 Prompt 召回 · v1","旧历史证据覆盖口径。"],
 legacy_faithfulness:["历史 Faithfulness · v1","旧裁判口径和原有效分母。"]
};
const state = {datasets:[],enabled:false,ready:false,history:[],selected:"",snapshot:null,comparison:null,active:"",writing:false,timer:null,epoch:0,casesEpoch:0,detailEpoch:0,offset:0,total:0,unloaded:false,controllers:new Set()};
let detailTrigger = null;
const dialog = document.querySelector("#detail-dialog");
// 固定选择器只查找本页面静态节点。
function el(id) { return document.getElementById(id); }
// 外部文本一律写 textContent，问题、证据和模型答案不能执行 HTML。
function node(tag,value,className) { const item=document.createElement(tag); if(value!==undefined)item.textContent=String(value); if(className)item.className=className; return item; }
// 缺失指标保留 N/A，不把错误或无分母当成零分。
function score(value) { return typeof value==="number" && Number.isFinite(value)?value.toFixed(3):"N/A"; }
// 库外桶的两个名称仅作显示兼容，请求使用正式 D_absent。
function bucketName(value) { return value==="D_unanswerable"?"D_absent":value; }
// 统一同源请求，并登记控制器以便卸载时中止。
async function request(path,body) {
 const controller=new AbortController(); state.controllers.add(controller);
 try { const response=await fetch(API+path,{cache:"no-store",signal:controller.signal,...(body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})}); const data=await response.json(); if(!response.ok){const error=new Error(data.message||"评估请求未完成。");error.code=data.code;throw error;} return data; }
 finally { state.controllers.delete(controller); }
}
// 安全错误使用可访问的文本提示。
function notice(message="") { el("load-error").hidden=!message; el("load-error").textContent=message; }
// 只有后端开放的范围可以启动，取消请求不提前解锁。
function controls() {
 const dataset=state.datasets.find(item=>item.dataset_id===el("dataset-select").value); const locked=!state.ready||state.writing||Boolean(state.active); const run=state.snapshot?.run;
 el("dataset-select").disabled=locked||!state.datasets.length;
 el("pilot-start").disabled=locked||!dataset?.available_scopes.includes("pilot");
 el("full-start").disabled=locked||!dataset?.available_scopes.includes("full");
 el("report-select").disabled=locked||!state.history.length;
 el("cancel-run").disabled=state.writing||!run||!activeStates.has(run.state)||run.state==="cancelling"||run.read_only;
 el("rerun").disabled=locked||!run||run.read_only||!state.datasets.some(item=>item.dataset_id===run.config?.dataset_id&&item.available_scopes.includes(run.config?.scope));
 for(const format of ["json","markdown"])el("export-"+format).disabled=!run||activeStates.has(run.state)||state.writing;
 el("gate-note").textContent=!state.enabled?"评估运行功能未启用；仍可读取历史。":locked?"已有运行或清理正在进行，启动与重跑暂时锁定。":dataset?.matching_pilot?"同配置合法试运行已匹配。全量会调用配置中的模型；点击才启动。":"全量需先完成同数据、模型、预算、Prompt 与上游配置的合法 10 题 / 40 条试运行，并确认清理成功。低分不阻止合法匹配。";
}
// 数据集资格只消费 GET，不由浏览器推算或伪造 pilot。
async function loadDatasets() {
 const data=await request("/datasets");state.datasets=data.items;state.enabled=data.enabled;
 const selected=el("dataset-select").value;el("dataset-select").replaceChildren();
 for(const item of data.items){const option=node("option",item.dataset_id+" · "+item.case_count+" 题 / "+item.chunk_count+" 块");option.value=item.dataset_id;el("dataset-select").append(option);}
 if(data.items.some(item=>item.dataset_id===selected))el("dataset-select").value=selected;controls();
}
// 合并图表只读取已交付报告的汇总快照，不创建假运行，也不调用评估接口。
async function loadComparison() {
 const controller=new AbortController();state.controllers.add(controller);
 try{
  const response=await fetch("/static/rag-comparison-summary.json",{cache:"no-store",signal:controller.signal});if(!response.ok)return;
  const data=await response.json();if(data.kind!=="merchant-rag-combined-comparison"||data.combined_schema_version!==1||data.single_continuous_run!==false||!data.summary?.rows||!data.summary?.common_generation||data.source_runs?.length!==2)return;
  state.comparison=data;el("chart-source").options[1].disabled=false;
 }finally{state.controllers.delete(controller);}
}
// 遍历历史分页，409 恢复也检查后续页，避免漏掉实际活动任务。
async function loadHistory() {
 const items=[];let offset=0;let page;
 do{page=await request("/runs?offset="+offset+"&limit=100");items.push(...page.items);offset+=page.items.length;}while(offset<page.total&&page.items.length);
 state.history=items;state.ready=true;el("report-select").replaceChildren();
 for(const run of items){const option=node("option",run.read_only?"旧版只读 · XM 30 题 · v1":(run.config.scope==="pilot"?"试运行":"全量")+" · "+(labels[run.state]||run.state)+" · "+run.run_id+" · "+(run.created_at||""));option.value=run.run_id;el("report-select").append(option);}
 state.active=items.find(run=>activeStates.has(run.state))?.run_id||"";
 if(items.some(run=>run.run_id===state.selected))el("report-select").value=state.selected;controls();return items;
}
// 切换先清旧轮询，版本令牌防止旧响应覆盖新选择。
async function selectRun(runId) {
 clearTimeout(state.timer);state.timer=null;state.epoch++;state.casesEpoch++;state.detailEpoch++;
 if(dialog.open)dialog.close();state.selected=runId;state.snapshot=null;state.offset=0;el("report").hidden=true;el("chart-source").value="current";el("cases-table").replaceChildren();el("result-count").textContent="正在读取当前运行的逐题记录…";controls();await refreshRun(state.epoch);
}
// GET 完成后再等 2 秒，无重叠轮询；终态停止并重新核验全量资格。
async function refreshRun(epoch) {
 if(state.unloaded||epoch!==state.epoch)return;
 try{
  const snapshot=await request("/runs/"+encodeURIComponent(state.selected));if(state.unloaded||epoch!==state.epoch)return;
  state.snapshot=snapshot;state.active=activeStates.has(snapshot.run.state)?snapshot.run.run_id:"";
  renderRun();renderRewrite();renderMatrix();renderQuality();await loadCases();if(epoch!==state.epoch||state.unloaded)return;
  if(!state.active){await loadDatasets();await loadHistory();if(state.active&&state.active!==state.selected){await selectRun(state.active);return;}}
 }catch(error){if(epoch===state.epoch&&error.name!=="AbortError")notice(error.message+" 状态尚未确认，未自动重跑。可刷新历史重试读取。");}
 if(!state.unloaded&&epoch===state.epoch&&state.active)state.timer=setTimeout(()=>refreshRun(epoch),2000);
}
// 公开 manifest 表达计划分母、清理与错误，进度不伪造评分。
function renderRun() {
 const {run,schema_version:version}=state.snapshot;const counts=run.counts;const planned=run.planned_records??counts.total;
 el("report").hidden=false;el("report-select").value=state.selected;el("run-status").textContent=labels[run.state]||run.state;
 el("scope-note").textContent=version===1?"旧版只读 v1：XM 30 题 / 84 块历史语料，仅 hybrid_rerank 有额外重排分门槛。历史值与新 content_ablation 口径不可直接比较；新组、要点和拒答指标 N/A。不能重跑旧版本。":"下方逐题追溯与导出对应所选运行："+(run.planned_cases??"未记录")+" 题 / "+planned+" 条策略结果 · "+run.config.dataset_id+" · "+run.run_id+"。";
 el("run-progress").max=Math.max(1,planned);el("run-progress").value=(counts.completed||0)+(counts.errors||0)+(counts.cancelled||0);
 el("progress-text").textContent=(labels[run.state]||run.state)+" · 阶段 "+(run.stage||"历史")+" · 已尝试 "+(counts.attempted??counts.total-counts.not_attempted)+" / "+planned+" · 完整完成 "+counts.completed+" · 错误 "+counts.errors+" · 未执行 "+counts.not_attempted;
 el("cleanup-note").textContent=version===1?"历史只读，不执行资源清理。":run.state==="cancelling"?"已请求协作取消，等待资源清理与最终报告发布；尚未结束。":"清理："+(run.cleanup?.ok?"成功":"未确认成功")+"。"+(run.cleanup?.errors||[]).join("；")+(run.cleanup?.unverified||[]).join("；")+(run.error?" 运行错误："+JSON.stringify(run.error):"");
 el("run-config").textContent=JSON.stringify({config:run.config??"v1 没有新配置出处",request_counts:run.request_counts??"N/A",cleanup:run.cleanup??"N/A",outcome:run.outcome??null},null,2);
 const data=[["计划策略记录",planned,"含缺席计划项；不补造逐题记录"],["完整完成",counts.completed,"包含生成和联合裁判"],["错误",counts.errors,"保留错误，不填满分"],["未执行",counts.not_attempted,"尚未启动或无检查点"]];
 el("cards").replaceChildren();for(const [label,value,sub]of data){const card=node("article",undefined,"card");card.append(node("div",label,"label"),node("div",value,"value"),node("div",sub,"sub"));el("cards").append(card);}
 for(const option of el("metric-select").options)option.disabled=option.value.startsWith("legacy_")&&version!==1;
 if(version!==1&&el("metric-select").value.startsWith("legacy_"))el("metric-select").value="mrr_at_10";
 el("chart-cohort").options[1].disabled=version!==2||!state.snapshot.summary?.common_generation;
 if(el("chart-cohort").options[1].disabled)el("chart-cohort").value="all";controls();
}
// 改写按唯一题目统计，直接使用服务端汇总，旧报告缺失时保持未记录。
function renderRewrite() {
 const rewrite=state.snapshot.schema_version===2?state.snapshot.summary?.rewrite:null;el("rewrite-cards").replaceChildren();
 if(!rewrite){el("rewrite-note").textContent="N/A：此历史报告未采集共享改写状态，不能补算成功率或降级次数。";return;}
 el("rewrite-note").textContent="已有结果的改写 "+rewrite.attempted_n+" 题；未记录 "+rewrite.unreported_n+" 题。"+(rewrite.degraded_n?"其中 "+rewrite.degraded_n+" 题结构无效，四种策略统一使用原问题继续检索；错误原因保留在逐题详情。":"本轮尚无原问题降级记录。");
 const values=[["已有结果的题数",rewrite.attempted_n,"四种策略只计一次"],["改写成功率",score(rewrite.success_rate),"成功 "+rewrite.success_n+" / 已有结果 "+rewrite.attempted_n],["原问题降级",rewrite.degraded_n,"结构无效，保留失败原因"],["改写失败",rewrite.error_n,"超时或其他调用错误"]];
 for(const [label,value,sub]of values){const card=node("article",undefined,"card");card.append(node("div",label,"label"),node("div",value,"value"),node("div",sub,"sub"));el("rewrite-cards").append(card);}
}
// 单题降级独立于最终完成状态，避免把完成的检索误当成成功改写。
function rewriteLabel(record) {
 if(!record.rewrite)return record.status==="not_attempted"?"未执行":record.status==="running"&&record.stage==="rewrite"?"进行中":"未记录";
 return {success:"成功",degraded:"原问题降级",error:"失败"}[record.rewrite.status]||"未知";
}
// 严格消费 v2 对象；v1 原值只在明确历史指标入口显示。
function metric(row,key,version=state.snapshot.schema_version) {
 if(key.startsWith("legacy_")&&version===1){const old=key.slice(7);return {value:row?.[old],valid_n:row?.[old+"_n"],excluded:{}};}
 return version===2?row?.metrics?.[key]??{value:null,valid_n:0,excluded:{}}:{value:null,valid_n:null,excluded:{legacy_missing:"v1 无新口径"}};
}
// 桶名兼容只查找现有汇总，不重新聚合或改变分母。
function summary(bucket,strategy,common=false) {
 const rows=state.snapshot.schema_version===1?state.snapshot.summary:common?state.snapshot.summary.common_generation?.rows??[]:state.snapshot.summary.rows;
 return rows.find(row=>bucketName(row.bucket)===bucket&&row.strategy===strategy);
}
// 图表与精确数值表共用所选样本范围，不在浏览器重新计算评估分数。
function chartSummary(bucket,strategy,common=el("chart-cohort").value==="common") {
 if(el("chart-source").value==="combined"&&state.comparison){const rows=common?state.comparison.summary.common_generation.rows:state.comparison.summary.rows;return rows.find(row=>bucketName(row.bucket)===bucket&&row.strategy===strategy);}
 return summary(bucket,strategy,common);
}
// 合并快照沿用实际 v2 指标口径，仍明确保留它来自两次运行的事实。
function chartVersion() { return el("chart-source").value==="combined"&&state.comparison?2:state.snapshot.schema_version; }
// 图形使用自身的数据口径，历史 v1 与新合并报告不能互相补数。
function chartMetric(bucket,strategy,key) { return metric(chartSummary(bucket,strategy),key,chartVersion()); }
// 所有图形用安全的 SVG 节点创建，报告文字不经过 HTML 拼接。
function svgNode(tag,attributes={},value) {
 const item=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [key,attribute]of Object.entries(attributes))item.setAttribute(key,String(attribute));
 if(value!==undefined)item.textContent=String(value);return item;
}
// 只有真实有限值可以画柱子和圆弧；缺失值始终显示 N/A。
function validMetric(item) { return typeof item.value==="number"&&Number.isFinite(item.value); }
// 排除原因与分母随图形一起展示，不能把无有效样本解释为零分。
function metricExplanation(item) {
 return "有效样本 n="+(item.valid_n??"N/A")+"；排除："+(Object.entries(item.excluded||{}).map(([reason,count])=>reason+" "+count).join("、")||(validMetric(item)?"无":"无有效记录"));
}
// 有效拒答比例用百分比展示，保留小数，100% 只用于真实满分。
function percent(item) { return validMetric(item)?(item.value===1?"100":(item.value*100).toFixed(1))+"%":"N/A"; }
// 图表只读实际记录；共同完成模式仍保留每个指标自己的分母。
function renderChartScope() {
 const common=el("chart-cohort").value==="common";const run=state.snapshot.run;
 if(el("chart-source").value==="combined"&&state.comparison){
  const data=state.comparison;el("chart-scope").textContent="完整 "+data.question_count+" 题 · "+data.chunk_count+" 块知识 · 两次运行合并（"+data.source_runs.map(item=>item.selected_questions+" 题").join(" + ")+"） · "+data.counts.completed+" 完成 / "+data.counts.errors+" 错误。"+(common?"图表使用四路共同完成的 "+data.summary.common_generation.valid_n+" 题，各指标单独显示有效分母。":"图表使用各策略全部有效样本。");
 }else el("chart-scope").textContent=common?"当前运行四路共同完成 "+state.snapshot.summary.common_generation.valid_n+" 题 · 每个指标单独计算有效分母":"当前运行 "+(run.planned_cases??"未记录")+" 题 · 各策略按自身有效样本计算";
}
// 概览只标注单项指标领先；库外拒答卡与右侧当前策略保持一致。
function renderInsights() {
 el("insight-cards").replaceChildren();const selected=el("quality-strategy").value;
 const cards=[["最高总体 MRR","mrr_at_10"],["最高 Recall@5","recall_at_5"],["最高答案要点覆盖","answer_point_coverage"]];
 for(const [label,key]of cards){
  const values=strategies.map(strategy=>({strategy,item:chartMetric("overall",strategy,key)})).filter(value=>validMetric(value.item));
  const best=values.length?Math.max(...values.map(value=>value.item.value)):null;const leaders=values.filter(value=>Math.abs(value.item.value-best)<1e-10);
  const card=node("article",undefined,"card insight-card");card.append(node("div",label,"label"),node("div",score(best),"value"),node("div",leaders.length?leaders.map(value=>displayNames[value.strategy]+" · n="+value.item.valid_n).join(" / "):"没有有效评分","sub"));el("insight-cards").append(card);
 }
 const refusal=chartMetric("overall",selected,"absent_refusal_rate");const card=node("article",undefined,"card insight-card");card.append(node("div","库外拒答率","label"),node("div",percent(refusal),"value"),node("div",displayNames[selected]+" · n="+(refusal.valid_n??"N/A"),"sub"));el("insight-cards").append(card);
}
// 四条策略共享 0–1 纵轴；总体与分桶分开，N/A 不伪装成零高度柱。
function renderRetrievalChart(key) {
 const root=el("retrieval-chart");root.replaceChildren();const absent=key==="absent_refusal_rate";
 const groups=absent?["D_absent","overall"]:chartBuckets;const width=1000,base=282,plotHeight=232,left=55,groupWidth=(width-left-15)/groups.length;
 const svg=svgNode("svg",{viewBox:"0 0 "+width+" 350",role:"group","aria-label":metrics[key][0]+"，四策略分桶柱状图"});
 svg.append(svgNode("title",{},metrics[key][0]+" · 四策略对比"));
 for(const tick of [0,.25,.5,.75,1]){const y=base-tick*plotHeight;svg.append(svgNode("line",{x1:left,y1:y,x2:width-15,y2:y,class:"chart-grid"}),svgNode("text",{x:left-12,y:y+4,"text-anchor":"end",class:"axis-label"},tick.toFixed(2)));}
 svg.append(svgNode("text",{x:left,y:20,class:"axis-label"},key==="answerable_false_refusal_rate"?"分数 · 越低越好":"分数 · 越高越好"));
 const detailDefault="悬停或用 Tab 聚焦柱子，查看该策略的精确分数、有效样本和排除原因。";el("chart-detail").textContent=detailDefault;
 groups.forEach((bucket,groupIndex)=>{
  const center=left+groupWidth*(groupIndex+.5);const barWidth=27,gap=8,start=center-(barWidth*4+gap*3)/2;
  if(bucket==="overall")svg.append(svgNode("line",{x1:left+groupWidth*groupIndex,y1:34,x2:left+groupWidth*groupIndex,y2:base,"stroke-dasharray":"4 5",class:"chart-divider"}));
  strategies.forEach((strategy,index)=>{
   const item=chartMetric(bucket,strategy,key);const x=start+index*(barWidth+gap);const info=buckets[bucket]+" · "+displayNames[strategy]+" · "+score(item.value)+"；"+metricExplanation(item);
   if(validMetric(item)){
    const height=Math.max(0,Math.min(1,item.value))*plotHeight;const bar=svgNode("rect",{x,y:base-height,width:barWidth,height:Math.max(1,height),rx:3,fill:tones[strategy],class:"chart-bar",tabindex:0,role:"img","aria-label":info});bar.append(svgNode("title",{},info));
    const show=()=>{el("chart-detail").textContent=info;};bar.addEventListener("pointerenter",show);bar.addEventListener("focus",show);bar.addEventListener("pointerleave",()=>{if(document.activeElement!==bar)el("chart-detail").textContent=detailDefault;});bar.addEventListener("blur",()=>{el("chart-detail").textContent=detailDefault;});svg.append(bar,svgNode("text",{x:x+barWidth/2,y:base-height-9,"text-anchor":"middle",class:"bar-score"},item.value.toFixed(2)));
   }else svg.append(svgNode("text",{x:x+barWidth/2,y:base-10,"text-anchor":"middle",class:"missing-score"},"N/A"));
  });
  svg.append(svgNode("text",{x:center,y:308,"text-anchor":"middle",class:"bucket-label"},buckets[bucket]),svgNode("text",{x:center,y:329,"text-anchor":"middle",class:"axis-label"},bucket));
 });root.append(svg);
 for(const button of document.querySelectorAll("[data-metric]"))button.setAttribute("aria-pressed",String(button.dataset.metric===key));
 const values=strategies.map(strategy=>({strategy,item:chartMetric("overall",strategy,key)})).filter(value=>validMetric(value.item));
 if(!values.length){el("chart-reading").textContent="当前报告在该口径下没有有效评分；N/A 表示缺失或不适用。可查看精确表中的原因或切换历史指标。";return;}
 const best=(key==="answerable_false_refusal_rate"?Math.min:Math.max)(...values.map(value=>value.item.value));const leaders=values.filter(value=>Math.abs(value.item.value-best)<1e-10);
 el("chart-reading").textContent="本项总体"+(leaders.length>1?"并列领先：":"领先：")+leaders.map(value=>displayNames[value.strategy]+" "+score(value.item.value)+"（n="+value.item.valid_n+"）").join("、")+"。仅比较当前指标；样本分母和错误请展开查看。";
}
// 忠实度用横条呈现，拒答用环形呈现，并单列可回答题的误拒答率。
function renderGenerationCharts() {
 const strategy=el("quality-strategy").value;const faithRoot=el("faithfulness-chart");faithRoot.replaceChildren();
 for(const bucket of chartBuckets){
  const item=chartMetric(bucket,strategy,"faithfulness");const row=node("div",undefined,"faith-row"+(bucket==="overall"?" faith-overall":""));const heading=node("div",undefined,"faith-heading");heading.append(node("span",buckets[bucket]),node("strong",score(item.value)));const track=node("div",undefined,"faith-track");track.setAttribute("aria-hidden","true");
  if(validMetric(item)){const fill=node("span");fill.style.width=(Math.max(0,Math.min(1,item.value))*100)+"%";fill.style.background=tones[strategy];track.append(fill);}else track.classList.add("missing-track");
  row.append(heading,track,node("div","n="+(item.valid_n??"N/A")+" · "+bucket,"faith-sample"));row.title=metricExplanation(item);faithRoot.append(row);
 }
 const refusal=chartMetric("overall",strategy,"absent_refusal_rate");const falseRefusal=chartMetric("overall",strategy,"answerable_false_refusal_rate");const ringRoot=el("refusal-chart");ringRoot.replaceChildren();ringRoot.append(node("h3","库外问题 · 拒答率"));
 const donut=node("div",undefined,"donut");const svg=svgNode("svg",{viewBox:"0 0 160 160","aria-hidden":"true"});svg.append(svgNode("circle",{cx:80,cy:80,r:64,class:"donut-track"}));
 if(validMetric(refusal))svg.append(svgNode("circle",{cx:80,cy:80,r:64,pathLength:100,"stroke-dasharray":(Math.max(0,Math.min(1,refusal.value))*100)+" 100",class:"donut-fill"}));
 const center=node("div",undefined,"donut-center");center.append(node("strong",percent(refusal)),node("span","拒答率"));donut.append(svg,center);ringRoot.append(donut,node("p",displayNames[strategy],"refusal-strategy"),node("p","D_absent · 有效样本 n="+(refusal.valid_n??"N/A"),"muted"),node("p",validMetric(refusal)?"剩余 "+((1-refusal.value)*100).toFixed(1)+"% 为未拒答的合法回答":"当前报告没有有效库外回答","muted"));
 const falseCard=node("div",undefined,"false-refusal");falseCard.append(node("span","可回答问题 · 误拒答率"),node("strong",percent(falseRefusal)),node("small","n="+(falseRefusal.valid_n??"N/A")+" · 越低越好"));ringRoot.append(falseCard);ringRoot.title=metricExplanation(refusal);renderInsights();
}
// 分数和分母一起显示，缺分母与实际零样本不同。
function metricText(row,key){const value=metric(row,key,chartVersion());return score(value.value)+" / n="+(value.valid_n??"N/A");}
// 当前指标所有并列最优均标注，误拒答率按较低值领先。
function renderMatrix() {
 if(!state.snapshot)return;const version=chartVersion();for(const option of el("metric-select").options)option.disabled=option.value.startsWith("legacy_")&&version!==1;
 if(version!==1&&el("metric-select").value.startsWith("legacy_"))el("metric-select").value="mrr_at_10";
 el("chart-cohort").options[1].disabled=version!==2;if(version!==2)el("chart-cohort").value="all";
 const key=el("metric-select").value;el("metric-description").textContent=metrics[key][1];el("metric-table").replaceChildren();
 for(const [bucket,label]of Object.entries(buckets)){
  const values=strategies.map(strategy=>chartMetric(bucket,strategy,key));const finite=values.filter(validMetric).map(item=>item.value);const best=finite.length?(key==="answerable_false_refusal_rate"?Math.min(...finite):Math.max(...finite)):null;
  const row=node("tr");row.append(node("th",label));
  values.forEach((value,index)=>{const cell=node("td");const leading=typeof value.value==="number"&&Math.abs(value.value-best)<1e-10;cell.append(node("span",score(value.value),"metric-value"),node("span","n="+(value.valid_n??"N/A"),"sample"));if(leading)cell.append(node("span",finite.filter(item=>Math.abs(item-best)<1e-10).length>1?"并列领先":"指标领先","leader"));cell.append(node("div","排除："+(Object.entries(value.excluded||{}).map(([reason,count])=>reason+" "+count).join("；")||(typeof value.value==="number"?"无":"无有效记录")),"sample exclusion"));const bar=node("div",undefined,"bar");bar.setAttribute("aria-hidden","true");const fill=node("span");fill.style.setProperty("--width",(typeof value.value==="number"?value.value*100:0)+"%");fill.style.setProperty("--tone",tones[strategies[index]]);bar.append(fill);cell.append(bar);row.append(cell);});el("metric-table").append(row);
 }
 renderChartScope();renderRetrievalChart(key);
}
// 各策略有效样本与四路共同有效子集分表，均保留每指标分母。
function renderQuality() {
 el("quality-table").replaceChildren();el("common-table").replaceChildren();const keys=["answer_point_coverage","faithfulness","absent_refusal_rate","answerable_false_refusal_rate"];
 for(const strategy of strategies){const row=chartSummary("overall",strategy,false);const tr=node("tr");for(const value of [names[strategy],(row?.completed??0)+" / "+(row?.total??0),row?.errors??0,...keys.map(key=>metricText(row,key))])tr.append(node("td",value));el("quality-table").append(tr);const commonRow=node("tr");for(const value of [names[strategy],...keys.map(key=>metricText(chartSummary("overall",strategy,true),key))])commonRow.append(node("td",value));el("common-table").append(commonRow);}
 const common=chartVersion()===2?(el("chart-source").value==="combined"?state.comparison.summary.common_generation:state.snapshot.summary.common_generation):null;
 el("common-note").textContent=common?"四路均完整完成的共同题目："+common.valid_n+"。各指标仍使用自己的 valid_n；没有断言或不适用题不进入相应分母。":"N/A：v1 不提供四路共同有效子集。";
 el("common-ids").textContent=common?common.eval_ids.join("、")||"无共同有效题目":"N/A";
 el("policy-note").textContent=chartVersion()===1?"v1 新生成指标均 N/A。可切换明确标注的历史指标；不补算新组覆盖和要点。":"数据来源与上方图表选择一致。裁判失败的合法回答仍可进入拒答率分母，错误数单独保留。";
 renderGenerationCharts();
}
// 分页筛选只发送 GET；版本令牌阻止旧条件响应覆盖新条件。
async function loadCases() {
 const token=++state.casesEpoch;const runId=state.selected;const params=new URLSearchParams({offset:String(state.offset),limit:"20"});
 for(const [field,id]of [["bucket","bucket-filter"],["strategy","strategy-filter"],["status","status-filter"],["query","query-filter"]])if(el(id).value)params.set(field,el(id).value);
 el("cases-table").setAttribute("aria-busy","true");
 try{const page=await request("/runs/"+runId+"/cases?"+params);if(token!==state.casesEpoch||runId!==state.selected||state.unloaded)return;
  state.total=page.total;el("cases-table").replaceChildren();
  for(const record of page.items){const row=node("tr");for(const value of [record.eval_id,record.query??"未保存问题",names[record.strategy],score(record.metrics?.mrr_at_10),labels[record.status]||record.status])row.append(node("td",value));const rewriteCell=node("td");rewriteCell.append(node("span",rewriteLabel(record),record.rewrite?.status==="degraded"?"pill warning":"pill"));row.append(rewriteCell);const cell=node("td");const button=node("button","查看","detail-link");button.setAttribute("aria-label","查看 "+record.eval_id+" "+names[record.strategy]+" 的评估详情");button.addEventListener("click",()=>openDetail(record,button));cell.append(button);row.append(cell);el("cases-table").append(row);}
  if(!page.items.length){const cell=node("td","没有匹配的实际检查点记录。");cell.colSpan=7;const row=node("tr");row.append(cell);el("cases-table").append(row);}
  el("result-count").textContent="匹配 "+page.total+" 条策略结果 · 本页 "+page.items.length+" 条；计划未执行数见进度。";
  el("page-number").textContent="第 "+(Math.floor(state.offset/20)+1)+" / "+Math.max(1,Math.ceil(page.total/20))+" 页";el("cases-prev").disabled=!state.offset;el("cases-next").disabled=state.offset+20>=page.total;
 }catch(error){if(token===state.casesEpoch&&error.name!=="AbortError")notice(error.message);}
 finally{if(token===state.casesEpoch)el("cases-table").setAttribute("aria-busy","false");}
}
// 单题 GET 展示全部 AND/OR 组合、Prompt 原文、要点和断言，不截断证据。
async function openDetail(record,trigger) {
 detailTrigger=trigger;const token=++state.detailEpoch;const runId=state.selected;
 try{const data=await request("/runs/"+runId+"/cases/"+encodeURIComponent(record.eval_id)+"/"+record.strategy);if(token!==state.detailEpoch||runId!==state.selected||state.unloaded)return;
  el("detail-title").textContent=data.eval_id+" · "+names[data.strategy]+" · "+(buckets[bucketName(data.bucket)]||"未知桶");el("detail-body").replaceChildren();
  const sections=[["问题",data.query],["共享改写",data.query_plan],["金标组完整组合 · 同组合全部满足 / 替代组合任选其一",data.mapped_groups],["候选 Top-50 与最终前十 · 不是 Prompt",{candidate_ids:data.candidate_ids,final_ids:data.final_ids}],["实际 Prompt 引用完整原文快照",data.prompt_citations],["充分性自评",data.decision],["实际回答",data.answer],["逐点覆盖 · 全部要点与理由",data.point_verdicts],["全部断言 · 支持判定与理由",data.claim_verdicts],["指标",data.metrics],["裁判版本与结束标识",data.judge_snapshot],["状态、错误与耗时",{status:data.status,stage:data.stage,error:data.error,elapsed_ms:data.elapsed_ms,should_refuse:data.should_refuse,refused:data.refused}]];
  sections.push(["共享改写状态与降级原因",data.rewrite??"N/A：未采集改写状态。历史缺失不代表成功。"]);
  if(state.snapshot.schema_version===1)sections.unshift(["旧版只读说明","v1 API 没有公开新金标组合、引用快照和逐点裁判；这些字段 N/A，不从其他运行补齐。"],["历史指标 · 原口径",data.legacy_metrics]);
  if(data.audit)sections.splice(3,0,["稳定金标来源 · 同组合全部满足 / 替代组合任选其一",data.audit.gold_groups],["标准要点原文 · 条件与同义表达",data.audit.answer_points],["实际排序分数 · 不同分数类型不可直接比较",{candidate_ranking:data.audit.candidate_ranking,final_ranking:data.audit.final_ranking}],["本轮完整来源映射 · 清理后仍可核对原文",data.source_map]);
  else sections.unshift(["来源与排序审计","N/A：此历史记录未采集稳定来源映射、标准要点原文或排序分数。"]);
  for(const [title,value]of sections){const section=node("section",undefined,"detail-section");section.append(node("h3",title),node("pre",value===undefined||value===null?"N/A：阶段未完成、缺失或不适用。":typeof value==="string"?value:JSON.stringify(value,null,2)));el("detail-body").append(section);}
  dialog.showModal();el("detail-close").focus();
 }catch(error){if(error.name!=="AbortError")notice(error.message);}
}
// 启动只发一次 POST；409 恢复实际活动运行，不循环重试创建。
async function startRun(scope,datasetId=el("dataset-select").value) {
 if(state.writing||state.active)return;state.writing=true;controls();notice();
 try{const result=await request("/runs",{dataset_id:datasetId,scope});state.active=result.run_id;await loadHistory();await selectRun(result.run_id);}
 catch(error){
  notice(error.message);
  try{
   if(error.code==="run_busy"){state.ready=false;await loadHistory();if(state.active){notice("409：已恢复服务端实际活动运行，未创建重复任务。");await selectRun(state.active);}else{state.ready=false;notice("已有其他进程持有运行或清理锁，当前无可见活动记录。请刷新历史确认；不会自动重试启动。");}}
   else if(error.code==="pilot_required")await loadDatasets();
   else if(!error.code){state.ready=false;notice("请求状态未确认。启动保持锁定，请刷新历史读取真实状态；不会自动重发启动。");}
  }catch(recoveryError){state.ready=false;notice(recoveryError.message+" 无法确认活动状态，启动保持锁定。请刷新历史。");}
 }
 finally{state.writing=false;controls();}
}
// 取消只是接受请求，继续轮询直到清理与终态发布结束。
async function cancelRun() {
 if(state.writing||!state.active)return;state.writing=true;const epoch=++state.epoch;clearTimeout(state.timer);state.timer=null;controls();
 try{await request("/runs/"+state.active+"/cancel",{});await refreshRun(epoch);}catch(error){notice(error.message);await refreshRun(epoch);}finally{state.writing=false;controls();}
}
// 用下载响应确认一致发布，409 不保存成报告文件。
async function exportRun(format) {
 const runId=state.selected;const controller=new AbortController();state.controllers.add(controller);state.writing=true;controls();
 try{const response=await fetch(API+"/runs/"+runId+"/export?format="+format,{cache:"no-store",signal:controller.signal});if(!response.ok){const error=await response.json();throw new Error(error.message||"报告尚未可下载。");}const url=URL.createObjectURL(await response.blob());const link=node("a");link.href=url;link.download=runId+(format==="json"?".json":".md");document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);notice();}
 catch(error){if(error.name!=="AbortError")notice(error.message);}finally{state.controllers.delete(controller);state.writing=false;controls();}
}
// 初始化固定枚举，所有结果只来自任务 8 同源接口。
async function initialize() {
 for(const [key,[label]]of Object.entries(metrics)){const option=node("option",label);option.value=key;el("metric-select").append(option);}
 el("metric-select").value="mrr_at_10";
 for(const [key,label]of Object.entries(buckets))if(key!=="overall"){const option=node("option",label);option.value=key;el("bucket-filter").append(option);}
 for(const strategy of strategies){const option=node("option",names[strategy]);option.value=strategy;el("strategy-filter").append(option);const quality=node("option",displayNames[strategy]+" · "+names[strategy]);quality.value=strategy;el("quality-strategy").append(quality);const legend=node("span");const swatch=node("i",undefined,"swatch");swatch.style.setProperty("--tone",tones[strategy]);legend.append(swatch,node("span",displayNames[strategy]));el("legend").append(legend);}
 el("quality-strategy").value="hybrid_rerank";
 for(const key of ["completed","running","not_attempted","cancelled","rewrite_error","retrieval_error","self_check_error","answer_error","judge_error","ok","error"]){const option=node("option",labels[key]);option.value=key;el("status-filter").append(option);}
 try{await Promise.all([loadDatasets(),loadComparison()]);await loadHistory();if(state.history.length){await selectRun(state.active||state.history[0].run_id);if(state.comparison&&!state.active){el("chart-source").value="combined";el("chart-cohort").value="common";renderMatrix();renderQuality();}}}catch(error){notice(error.message+" 工作台未加载，启动保持禁用。");}
}
// 手动恢复只读历史和资格，活动任务优先展示。
async function refreshHistory() { state.ready=false;controls();try{notice();await loadDatasets();await loadHistory();if(state.history.length)await selectRun(state.active||state.selected||state.history[0].run_id);}catch(error){state.ready=false;controls();notice(error.message);} }
// 筛选归零分页，后台轮询保留用户条件。
function filterCases(){state.offset=0;if(state.snapshot)loadCases();}
el("pilot-start").addEventListener("click",()=>startRun("pilot"));
el("full-start").addEventListener("click",()=>startRun("full"));
el("rerun").addEventListener("click",()=>startRun(state.snapshot.run.config.scope,state.snapshot.run.config.dataset_id));
el("cancel-run").addEventListener("click",cancelRun);
el("history-refresh").addEventListener("click",refreshHistory);
el("dataset-select").addEventListener("change",controls);
el("report-select").addEventListener("change",()=>{notice();selectRun(el("report-select").value);});
el("metric-select").addEventListener("change",renderMatrix);
// 常用指标按钮只切换展示，不启动评估或修改报告。
for(const button of document.querySelectorAll("[data-metric]"))button.addEventListener("click",()=>{el("metric-select").value=button.dataset.metric;if(state.snapshot)renderMatrix();});
el("quality-strategy").addEventListener("change",()=>{if(state.snapshot)renderGenerationCharts();});
el("chart-cohort").addEventListener("change",()=>{if(state.snapshot){renderMatrix();renderQuality();}});
el("chart-source").addEventListener("change",()=>{if(state.snapshot){renderMatrix();renderQuality();}});
for(const id of ["bucket-filter","strategy-filter","status-filter"])el(id).addEventListener("change",filterCases);
el("query-filter").addEventListener("input",filterCases);
el("cases-prev").addEventListener("click",()=>{state.offset=Math.max(0,state.offset-20);loadCases();});
el("cases-next").addEventListener("click",()=>{state.offset+=20;loadCases();});
for(const format of ["json","markdown"])el("export-"+format).addEventListener("click",()=>exportRun(format));
el("detail-close").addEventListener("click",()=>dialog.close());
// Escape 与关闭按钮共享焦点恢复，分页节点消失时回到搜索框。
dialog.addEventListener("close",()=>{(detailTrigger?.isConnected?detailTrigger:el("query-filter")).focus();});
// 卸载立即释放计时器和请求，BFCache 返回时重新核验。
window.addEventListener("pagehide",()=>{state.unloaded=true;state.epoch++;state.casesEpoch++;state.detailEpoch++;clearTimeout(state.timer);state.timer=null;for(const controller of state.controllers)controller.abort();});
window.addEventListener("pageshow",event=>{if(event.persisted){state.unloaded=false;refreshHistory();}});
initialize();
