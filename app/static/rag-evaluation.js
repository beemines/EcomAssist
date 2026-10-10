"use strict";
const API = "/api/rag-evaluations";
const strategies = ["dense","bm25","hybrid","hybrid_rerank"];
const names = {dense:"vector",bm25:"bm25",hybrid:"hybrid",hybrid_rerank:"hybrid_rerank"};
const tones = {dense:"#498d79",bm25:"#b8945e",hybrid:"#6f91a8",hybrid_rerank:"#807ca8"};
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
const state = {datasets:[],enabled:false,ready:false,history:[],selected:"",snapshot:null,active:"",writing:false,timer:null,epoch:0,casesEpoch:0,detailEpoch:0,offset:0,total:0,unloaded:false,controllers:new Set()};
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
 if(dialog.open)dialog.close();state.selected=runId;state.snapshot=null;state.offset=0;el("report").hidden=true;controls();await refreshRun(state.epoch);
}
// GET 完成后再等 2 秒，无重叠轮询；终态停止并重新核验全量资格。
async function refreshRun(epoch) {
 if(state.unloaded||epoch!==state.epoch)return;
 try{
  const snapshot=await request("/runs/"+encodeURIComponent(state.selected));if(state.unloaded||epoch!==state.epoch)return;
  state.snapshot=snapshot;state.active=activeStates.has(snapshot.run.state)?snapshot.run.run_id:"";
  renderRun();renderMatrix();renderQuality();await loadCases();if(epoch!==state.epoch||state.unloaded)return;
  if(!state.active){await loadDatasets();await loadHistory();if(state.active&&state.active!==state.selected){await selectRun(state.active);return;}}
 }catch(error){if(epoch===state.epoch&&error.name!=="AbortError")notice(error.message+" 状态尚未确认，未自动重跑。可刷新历史重试读取。");}
 if(!state.unloaded&&epoch===state.epoch&&state.active)state.timer=setTimeout(()=>refreshRun(epoch),2000);
}
// 公开 manifest 表达计划分母、清理与错误，进度不伪造评分。
function renderRun() {
 const {run,schema_version:version}=state.snapshot;const counts=run.counts;const planned=run.planned_records??counts.total;
 el("report").hidden=false;el("report-select").value=state.selected;el("run-status").textContent=labels[run.state]||run.state;
 el("scope-note").textContent=version===1?"旧版只读 v1：XM 30 题 / 84 块历史语料，仅 hybrid_rerank 有额外重排分门槛。历史值与新 content_ablation 口径不可直接比较；新组、要点和拒答指标 N/A。不能重跑旧版本。":"当前 "+(run.config.scope==="pilot"?"10 题试运行":"300 题全量")+" · content_ablation · "+run.config.dataset_id+" · "+run.run_id+"。模型与预算使用本次冻结配置。";
 el("run-progress").max=Math.max(1,planned);el("run-progress").value=(counts.completed||0)+(counts.errors||0)+(counts.cancelled||0);
 el("progress-text").textContent=(labels[run.state]||run.state)+" · 阶段 "+(run.stage||"历史")+" · 已尝试 "+(counts.attempted??counts.total-counts.not_attempted)+" / "+planned+" · 完整完成 "+counts.completed+" · 错误 "+counts.errors+" · 未执行 "+counts.not_attempted;
 el("cleanup-note").textContent=version===1?"历史只读，不执行资源清理。":run.state==="cancelling"?"已请求协作取消，等待资源清理与最终报告发布；尚未结束。":"清理："+(run.cleanup?.ok?"成功":"未确认成功")+"。"+(run.cleanup?.errors||[]).join("；")+(run.cleanup?.unverified||[]).join("；")+(run.error?" 运行错误："+JSON.stringify(run.error):"");
 el("run-config").textContent=JSON.stringify({config:run.config??"v1 没有新配置出处",request_counts:run.request_counts??"N/A",cleanup:run.cleanup??"N/A",outcome:run.outcome??null},null,2);
 const data=[["计划策略记录",planned,"含缺席计划项；不补造逐题记录"],["完整完成",counts.completed,"包含生成和联合裁判"],["错误",counts.errors,"保留错误，不填满分"],["未执行",counts.not_attempted,"尚未启动或无检查点"]];
 el("cards").replaceChildren();for(const [label,value,sub]of data){const card=node("article",undefined,"card");card.append(node("div",label,"label"),node("div",value,"value"),node("div",sub,"sub"));el("cards").append(card);}
 for(const option of el("metric-select").options)option.disabled=option.value.startsWith("legacy_")&&version!==1;
 if(version!==1&&el("metric-select").value.startsWith("legacy_"))el("metric-select").value="recall_at_5";controls();
}
// 严格消费 v2 对象；v1 原值只在明确历史指标入口显示。
function metric(row,key) {
 if(key.startsWith("legacy_")&&state.snapshot.schema_version===1){const old=key.slice(7);return {value:row?.[old],valid_n:row?.[old+"_n"],excluded:{}};}
 return state.snapshot.schema_version===2?row?.metrics?.[key]??{value:null,valid_n:0,excluded:{}}:{value:null,valid_n:null,excluded:{legacy_missing:"v1 无新口径"}};
}
// 桶名兼容只查找现有汇总，不重新聚合或改变分母。
function summary(bucket,strategy,common=false) {
 const rows=state.snapshot.schema_version===1?state.snapshot.summary:common?state.snapshot.summary.common_generation.rows:state.snapshot.summary.rows;
 return rows.find(row=>bucketName(row.bucket)===bucket&&row.strategy===strategy);
}
// 分数和分母一起显示，缺分母与实际零样本不同。
function metricText(row,key){const value=metric(row,key);return score(value.value)+" / n="+(value.valid_n??"N/A");}
// 当前指标所有并列最优均标注，误拒答率按较低值领先。
function renderMatrix() {
 if(!state.snapshot)return;const key=el("metric-select").value;el("metric-description").textContent=metrics[key][1];el("metric-table").replaceChildren();
 for(const [bucket,label]of Object.entries(buckets)){
  const values=strategies.map(strategy=>metric(summary(bucket,strategy),key));const finite=values.map(item=>item.value).filter(value=>typeof value==="number");const best=finite.length?(key==="answerable_false_refusal_rate"?Math.min(...finite):Math.max(...finite)):null;
  const row=node("tr");row.append(node("th",label));
  values.forEach((value,index)=>{const cell=node("td");const leading=typeof value.value==="number"&&Math.abs(value.value-best)<1e-10;cell.append(node("span",score(value.value),"metric-value"),node("span","n="+(value.valid_n??"N/A"),"sample"));if(leading)cell.append(node("span",finite.filter(item=>Math.abs(item-best)<1e-10).length>1?"并列领先":"指标领先","leader"));cell.append(node("div","排除："+(Object.entries(value.excluded||{}).map(([reason,count])=>reason+" "+count).join("；")||(typeof value.value==="number"?"无":"无有效记录")),"sample exclusion"));const bar=node("div",undefined,"bar");bar.setAttribute("aria-hidden","true");const fill=node("span");fill.style.setProperty("--width",(typeof value.value==="number"?value.value*100:0)+"%");fill.style.setProperty("--tone",tones[strategies[index]]);bar.append(fill);cell.append(bar);row.append(cell);});el("metric-table").append(row);
 }
}
// 各策略有效样本与四路共同有效子集分表，均保留每指标分母。
function renderQuality() {
 el("quality-table").replaceChildren();el("common-table").replaceChildren();const keys=["answer_point_coverage","faithfulness","absent_refusal_rate","answerable_false_refusal_rate"];
 for(const strategy of strategies){const row=summary("overall",strategy);const tr=node("tr");for(const value of [names[strategy],(row?.completed??0)+" / "+(row?.total??0),row?.errors??0,...keys.map(key=>metricText(row,key))])tr.append(node("td",value));el("quality-table").append(tr);const commonRow=node("tr");for(const value of [names[strategy],...keys.map(key=>metricText(summary("overall",strategy,true),key))])commonRow.append(node("td",value));el("common-table").append(commonRow);}
 const common=state.snapshot.schema_version===2?state.snapshot.summary.common_generation:null;
 el("common-note").textContent=common?"四路均完整完成的共同题目："+common.valid_n+"。各指标仍使用自己的 valid_n；没有断言或不适用题不进入相应分母。":"N/A：v1 不提供四路共同有效子集。";
 el("common-ids").textContent=common?common.eval_ids.join("、")||"无共同有效题目":"N/A";
 el("policy-note").textContent=state.snapshot.schema_version===1?"v1 新生成指标均 N/A。可切换明确标注的历史指标；不补算新组覆盖和要点。":"只读汇总实际检查点。计划记录分母见进度；裁判失败的合法回答仍可进入拒答率分母，错误数单独保留。";
}
// 分页筛选只发送 GET；版本令牌阻止旧条件响应覆盖新条件。
async function loadCases() {
 const token=++state.casesEpoch;const runId=state.selected;const params=new URLSearchParams({offset:String(state.offset),limit:"20"});
 for(const [field,id]of [["bucket","bucket-filter"],["strategy","strategy-filter"],["status","status-filter"],["query","query-filter"]])if(el(id).value)params.set(field,el(id).value);
 el("cases-table").setAttribute("aria-busy","true");
 try{const page=await request("/runs/"+runId+"/cases?"+params);if(token!==state.casesEpoch||runId!==state.selected||state.unloaded)return;
  state.total=page.total;el("cases-table").replaceChildren();
  for(const record of page.items){const row=node("tr");for(const value of [record.eval_id,record.query??"未保存问题",names[record.strategy],score(record.metrics?.mrr_at_10),labels[record.status]||record.status])row.append(node("td",value));const cell=node("td");const button=node("button","查看","detail-link");button.setAttribute("aria-label","查看 "+record.eval_id+" "+names[record.strategy]+" 的评估详情");button.addEventListener("click",()=>openDetail(record,button));cell.append(button);row.append(cell);el("cases-table").append(row);}
  if(!page.items.length){const cell=node("td","没有匹配的实际检查点记录。");cell.colSpan=6;const row=node("tr");row.append(cell);el("cases-table").append(row);}
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
 for(const [key,label]of Object.entries(buckets))if(key!=="overall"){const option=node("option",label);option.value=key;el("bucket-filter").append(option);}
 for(const strategy of strategies){const option=node("option",names[strategy]);option.value=strategy;el("strategy-filter").append(option);const legend=node("span");const swatch=node("i",undefined,"swatch");swatch.style.setProperty("--tone",tones[strategy]);legend.append(swatch,node("span",names[strategy]));el("legend").append(legend);}
 for(const key of ["completed","running","not_attempted","cancelled","rewrite_error","retrieval_error","self_check_error","answer_error","judge_error","ok","error"]){const option=node("option",labels[key]);option.value=key;el("status-filter").append(option);}
 try{await loadDatasets();await loadHistory();if(state.history.length)await selectRun(state.active||state.history[0].run_id);}catch(error){notice(error.message+" 工作台未加载，启动保持禁用。");}
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
