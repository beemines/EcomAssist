"use strict";
const $=id=>document.getElementById(id);
const node=(tag,text,className)=>{const element=document.createElement(tag);if(text!==undefined)element.textContent=String(text);if(className)element.className=className;return element;};
const sources={retrieval_low_conf:"检索置信度低",self_check:"模型自评不足",user_feedback:"用户反馈没解决"};
const number=value=>Number.isFinite(value)?value.toLocaleString("zh-CN"):"—";
const percent=value=>Number.isFinite(value)?(value*100).toFixed(1)+"%":"待启用";
let summary=null,selected=null,offset=0,revision=0,pageRevision=0;
async function api(path){const response=await fetch(path,{cache:"no-store"});let data;try{data=await response.json();}catch{throw Error("无法读取服务响应，请稍后刷新。");}if(!response.ok)throw Error(response.status===503?"主题统计暂时不可用，请检查数据库和当前模型配置。":data.message||"筛选条件无法处理，请检查时间范围。");return data;}
function filters(){const values=new URLSearchParams();if($("source").value)values.set("source",$("source").value);for(const key of ["since","until"])if($(key).value)values.set(key,$(key).value+"+08:00");return values;}
function card(label,value,detail){const result=node("article",undefined,"kpi");result.append(node("span",label,"label"),node("strong",number(value)),node("small",detail));return result;}
function when(value){if(!value)return "尚无";return new Intl.DateTimeFormat("zh-CN",{dateStyle:"short",timeStyle:"short",timeZone:"Asia/Shanghai"}).format(new Date(value+(/(?:Z|[+-]\d\d:\d\d)$/.test(value)?"":"Z")));}
function renderSummary(data){
  summary=data;
  $("hit-topic-count").textContent=data.status==="ready"?"已命中 "+data.topics.filter(item=>item.count>0).length+" / 17 类":"待启用";
  $("kpis").replaceChildren(card("问题总数",data.pool_total,"当前筛选范围"),card("已归类",data.effective,"当前有效分类"),card("待归类",data.unclassified,"未分类或分类已失效"));
  const state=$("model-state");state.replaceChildren();
  if(data.status!=="ready"){
    state.append(node("strong","当前模型尚未配置"),node("p","模型启用后显示主题分布。"));selected=null;
  }else{
    state.append(node("strong","当前模型 · "+data.identity.model_version.slice(0,18)+"…"),node("p","术语版本 "+data.identity.taxonomy_version+" · 旧模型或输入失效 "+number(data.stale)+" 条 · 版本未知或标签无效 "+number(data.unknown)+" 条 · 最近归类 "+when(data.latest)),node("p","待人工复核 "+number(data.pending_review)+" 条 · "+(data.receipts_status==="available"?"不含暂时网络故障":"回执不可用或范围超出，数量未知")));
    if(!selected)selected=[...data.topics].sort((a,b)=>b.count-a.count)[0]?.name;
  }
  const bars=$("topic-bars");bars.replaceChildren();
  for(const item of [...data.topics].sort((a,b)=>(b.count??0)-(a.count??0))){
    const bar=node("button",undefined,"topic-bar");bar.type="button";bar.disabled=data.status!=="ready";bar.setAttribute("aria-pressed",String(item.name===selected));
    const track=node("span",undefined,"topic-track"),fill=node("i",undefined,"topic-fill");fill.style.width=(Number.isFinite(item.share)?Math.max(0,Math.min(100,item.share*100)):0)+"%";track.append(fill);
    bar.append(node("span",item.name),track,node("span",number(item.count)+" · "+percent(item.share),"topic-value"));bar.onclick=()=>{selected=item.name;offset=0;renderSummary(summary);loadQuestions();};bars.append(bar);
  }
}
async function loadQuestions(){const token=++pageRevision,filterRevision=revision;$("questions-title").textContent=selected?selected+" · 原话":"主题原话";$("previous").disabled=$("next").disabled=true;$("question-count").textContent="";$("page-number").textContent="";if(!selected||summary?.status!=="ready"){$("questions").replaceChildren(node("p","模型启用后，可点击左侧主题，查看经过脱敏的原话与对应知识缺口。","topic-empty"));return;}try{const query=filters();query.set("label",selected);query.set("offset",String(offset));query.set("limit","20");const data=await api("/api/topics/questions?"+query);if(token!==pageRevision||filterRevision!==revision)return;if(data.items.some(item=>item.model_version!==summary.identity.model_version))throw Error("当前模型已切换，请重新查询分布。");const target=$("questions");target.replaceChildren();for(const item of data.items){const article=node("article",undefined,"topic-question"),head=node("div",undefined,"topic-question-head");head.append(node("span",sources[item.source]||item.source),node("span",when(item.classified_at)));const labels=node("div",undefined,"topic-labels");for(const label of item.labels)labels.append(node("span",label,"badge"));if(item.matched_review_id){const link=node("a","查看归并缺口 →");link.href="/review?review_id="+encodeURIComponent(item.matched_review_id);labels.append(link);}article.append(head,node("p",item.text),labels);target.append(article);}if(!data.items.length)target.append(node("p","当前筛选下还没有这个主题的有效分类。","topic-empty"));$("question-count").textContent="共 "+number(data.total)+" 条";$("previous").disabled=offset===0;$("next").disabled=offset+20>=data.total;$("page-number").textContent=data.total?Math.floor(offset/20)+1+" / "+Math.ceil(data.total/20):"0 / 0";}catch(error){if(token===pageRevision&&filterRevision===revision){$("notice").textContent=error.message;$("questions").replaceChildren(node("p","暂时无法加载原话，请重新查询。","topic-empty"));}}}
async function refresh(){const token=++revision;++pageRevision;$("refresh").disabled=true;$("notice").textContent="";offset=0;try{const data=await api("/api/topics/summary?"+filters());if(token!==revision)return;renderSummary(data);await loadQuestions();}catch(error){if(token===revision){summary=null;$("notice").textContent=error.message;$("kpis").replaceChildren();$("topic-bars").replaceChildren();$("model-state").textContent="本次查询失败，未将故障显示为零条。";$("questions").replaceChildren();}}finally{if(token===revision)$("refresh").disabled=false;}}
$("filters").onsubmit=event=>{event.preventDefault();refresh();};$("clear").onclick=()=>{$("source").value=$("since").value=$("until").value="";refresh();};$("previous").onclick=()=>{offset=Math.max(0,offset-20);loadQuestions();};$("next").onclick=()=>{offset+=20;loadQuestions();};
api("/health").then(data=>{$("demo-notice").hidden=data.background_tasks_enabled!==false;}).catch(()=>{});refresh();
