(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('reviewData').textContent);
  const $ = id => document.getElementById(id);
  const reviewKind = data.purpose === 'test' ? 'test-review' : data.purpose === 'errors' ? 'error-review' : 'pilot-review';
  const aiDelegated = data.review_kind === 'delegated_ai';
  const reviewTitle = (data.round_label ? data.round_label + ' · ' : '') +
    (aiDelegated ? (data.purpose === 'test' ? '测试题 AI 代审结果' : '错例 AI 代审结果') :
      data.purpose === 'test' ? '测试集人工复核' : data.purpose === 'errors' ? '错例人工复核' : '样本人工审核');
  $('reviewTitle').textContent = reviewTitle;
  document.title = 'MewHelp · ' + reviewTitle;
  $('hostedReviewLink').href = data.hosted_origin + '/topics/' + reviewKind;
  if (data.purpose === 'test') $('purposeHint').textContent = '本批来自冻结留出测试集，预标标签仍需人工核对。复核结果形成独立 gold 子集报告，原模型和阈值保留。';
  if (data.purpose === 'errors') $('purposeHint').textContent = '本批是固定模型与 silver 预标不一致的错例。请判断原句的真实标签；已在测试复核包中的问题家族不会重复出现。';
  if (data.round_label === '否定语义修复' && data.purpose === 'pilot') $('purposeHint').textContent = '本批为新合成训练对照，请核对真正肯定的诉求，否定或取消的操作不计标签。实际保存后才可重训，旧76条复核不用重做。';
  if (data.round_label === '组合覆盖修复' && data.purpose === 'pilot') $('purposeHint').textContent = '本批逐条核对两类：大小不合适且实际要退换；取消退换、实际仅问大小适配。取消退但仍要换的，依然要标退换货。此前审核不重做，实际保存和覆盖检查通过后才训练。';
  if (aiDelegated) {
    $('purposeHint').textContent = '依用户授权由 Codex AI 逐条代审，尚未经过独立人工复核。修正标签只用于追加参考评测，未回流本轮训练或改变阈值；原银标报告保留。';
    document.querySelector('.attestation').hidden = true;
  }
  const key = 'mewhelp-topic-review-v1:' + data.pack_hash;
  const validNames = data.taxonomy.map(t => t.name);
  let choices = {}, submitted = Boolean(data.submitted), saving = false, editing = null;
  function node(tag, text, className) {
    const result = document.createElement(tag);
    if (text !== undefined) result.textContent = text;
    if (className) result.className = className;
    return result;
  }
  function validChoice(choice, sample) {
    if (!choice || choice.sample_id !== sample.id || !['accept','correct','exclude'].includes(choice.decision)
        || !Array.isArray(choice.final_labels) || typeof choice.notes !== 'string' || choice.notes.length > 1024) return false;
    const labels = choice.final_labels;
    if (new Set(labels).size !== labels.length || labels.some(t => !validNames.includes(t))
        || (labels.includes('其他') && labels.length !== 1)) return false;
    if (choice.decision === 'exclude') return labels.length === 0;
    return labels.length > 0 && (choice.decision !== 'accept' || JSON.stringify(labels) === JSON.stringify(sample.labels));
  }
  if (submitted) {
    data.submitted.decisions.forEach(c => { choices[c.sample_id] = {sample_id:c.sample_id, decision:c.decision, final_labels:c.final_labels, notes:c.notes}; });
    $('reviewer').value = data.submitted.decisions[0]?.reviewer || '';
    $('attested').checked = !aiDelegated;
  } else {
    try {
      const draft = JSON.parse(localStorage.getItem(key) || 'null');
      if (draft && draft.pack_hash === data.pack_hash) {
        data.samples.forEach(s => { const c = draft.choices?.[s.id]; if (validChoice(c, s)) choices[s.id] = c; });
        if (typeof draft.reviewer === 'string') $('reviewer').value = draft.reviewer.slice(0,128);
      }
    } catch (_) { $('draftHint').textContent = '浏览器无法保存草稿，请保留当前页面'; }
  }
  function persist() {
    if (submitted) return;
    try { localStorage.setItem(key, JSON.stringify({pack_hash:data.pack_hash, choices, reviewer:$('reviewer').value})); }
    catch (_) { $('draftHint').textContent = '浏览器无法保存草稿，请保留当前页面'; }
  }
  function counts() {
    const resolved = data.samples.filter(s => choices[s.id]);
    return {pending:data.samples.length-resolved.length, corrected:resolved.filter(s=>choices[s.id].decision==='correct').length,
      excluded:resolved.filter(s=>choices[s.id].decision==='exclude').length};
  }
  function update() {
    const c = counts(), ready = !c.pending && $('attested').checked && $('reviewer').value.trim().length > 0;
    $('total').textContent = data.samples.length;
    $('pending').textContent = c.pending;
    $('corrected').textContent = c.corrected;
    $('excluded').textContent = c.excluded;
    $('progress').value = 100*(data.samples.length-c.pending)/data.samples.length;
    $('bulk').disabled = submitted || saving || !$('attested').checked || !c.pending;
    $('submit').disabled = submitted || saving || !ready;
    $('export').disabled = saving || !ready;
    $('reviewer').disabled = submitted || saving;
    $('attested').disabled = submitted || saving;
    if (submitted) {
      document.body.classList.add('review-complete');
      document.body.dataset.reviewSource = aiDelegated ? 'ai' : 'human';
      $('submit').textContent = aiDelegated ? 'AI 代审已保存' : '已提交保存';
      $('submitHint').textContent = aiDelegated ? 'AI 代审结果已保存。' : '审核已保存，可导出备份。';
      $('draftHint').textContent = '已保存到本机';
    } else if (c.pending) $('submitHint').textContent = `还有 ${c.pending} 条待核对。逐条点通过，或看完全部后勾选确认，再点「已核对的其余样本通过」。`;
    else $('submitHint').textContent = '全部已处理。填写一次昵称，勾选逐条核对确认，再提交保存。';
  }
  function decide(sample, decision, labels, notes='') {
    if (submitted || saving) return;
    choices[sample.id] = {sample_id:sample.id, decision, final_labels:labels, notes};
    persist(); render();
  }
  function button(text, className, handler) {
    const b = node('button',text,className); b.type='button'; b.disabled=submitted||saving; b.addEventListener('click',handler); return b;
  }
  function render() {
    $('rows').replaceChildren();
    const filter = $('filter').value, query = $('search').value.trim().toLowerCase();
    let visible = 0;
    data.samples.forEach(s => {
      const choice=choices[s.id], decision=choice?.decision || 'pending';
      if (filter!=='all' && decision!==filter) return;
      if (query && !(`${s.index} ${s.text} ${s.id}`.toLowerCase().includes(query))) return;
      visible++;
      const card=node('article',undefined,'sample'); card.dataset.sampleId=s.id;
      const top=node('div',undefined,'sample-top');
      top.append(node('span',String(s.index).padStart(2,'0'),'number'),
        node('span',({synthetic:'合成题',unverified:'问题池 · 未核实',real:'已核实问题池',demo:'演示题'})[s.origin]||s.origin,'origin'),
        node('span',({pending:'待核对',accept:'已通过',correct:'已修正',exclude:'已排除'})[decision],'decision '+decision));
      card.append(top,node('p',s.text,'question'));
      const labels=node('div',undefined,'labels');
      labels.append(node('span',decision==='correct'?'最终标签':'预标标签','muted'));
      (decision==='correct'?choice.final_labels:s.labels).forEach(t=>labels.append(node('span',t,'chip')));
      card.append(labels);
      if (s.mismatch) card.append(node('p','造数场景与独立预标不同，请重点复核。','warning'));
      const bottom=node('div',undefined,'sample-bottom');
      const details=node('details');
      details.append(node('summary',s.note || choice?.notes ? '预测与备注' : '样本 ID'));
      if (s.note) details.append(node('p',s.note,'notes'));
      if (choice?.notes) details.append(node('p','审核备注：'+choice.notes,'notes'));
      details.append(node('code',s.id));
      const actions=node('div',undefined,'sample-actions');
      actions.append(button('通过','secondary',()=>decide(s,'accept',[...s.labels])),
        button('修改标签','secondary',()=>openEditor(s)),
        button('排除','exclude-button',()=>decide(s,'exclude',[])));
      if (choice) actions.append(button('撤回','text-button',()=>{delete choices[s.id];persist();render();}));
      bottom.append(details,actions); card.append(bottom); $('rows').append(card);
    });
    if (!visible) $('rows').append(node('p','没有符合条件的样本。','muted'));
    update();
  }
  function openEditor(sample) {
    editing=sample;
    $('editTitle').textContent=`第 ${sample.index} 条 · 修改标签`;
    $('editText').textContent=sample.text;
    $('editNotes').value=choices[sample.id]?.notes||'';
    $('editError').textContent=''; $('labelChoices').replaceChildren();
    const selected=choices[sample.id]?.decision==='correct'?choices[sample.id].final_labels:sample.labels;
    data.taxonomy.forEach(t=>{
      const label=node('label'); label.title=t.boundary;
      const input=node('input'); input.type='checkbox'; input.value=t.name; input.checked=selected.includes(t.name);
      input.addEventListener('change',()=>{
        if (input.checked) $('labelChoices').querySelectorAll('input').forEach(other=>{
          if (other!==input && (input.value==='其他'||other.value==='其他')) other.checked=false;
        });
      });
      label.append(input,node('span',t.name)); $('labelChoices').append(label);
    });
    $('editor').showModal();
  }
  $('editForm').addEventListener('submit',event=>{
    event.preventDefault();
    const labels=Array.from($('labelChoices').querySelectorAll('input:checked'),i=>i.value);
    if (!labels.length) { $('editError').textContent='至少选择一个标签；不采用这条样本请点「排除」。'; return; }
    const decision=JSON.stringify(labels)===JSON.stringify(editing.labels)?'accept':'correct';
    decide(editing,decision,labels,$('editNotes').value.trim()); $('editor').close();
  });
  $('closeEditor').addEventListener('click',()=>$('editor').close());
  $('bulk').addEventListener('click',()=>{
    if (submitted||saving||!$('attested').checked) return;
    data.samples.forEach(s=>{if(!choices[s.id])choices[s.id]={sample_id:s.id,decision:'accept',final_labels:[...s.labels],notes:''};});
    persist(); render(); $('status').textContent='其余样本已标为通过，已修正和已排除的项目保持不变。请确认后提交保存。';
  });
  $('reviewer').addEventListener('input',()=>{persist();update();});
  $('attested').addEventListener('change',update);
  $('filter').addEventListener('change',render);
  $('search').addEventListener('input',render);
  function submission() {
    return {pack_hash:data.pack_hash,reviewer:$('reviewer').value.trim(),attested:$('attested').checked,
      items:data.samples.map(s=>choices[s.id])};
  }
  function exportDecisions() {
    const value=submission(), now=new Date().toISOString();
    const rows=submitted?data.submitted.decisions:value.items.map(c=>({...c,pack_hash:data.pack_hash,reviewer:value.reviewer,reviewed_at:now}));
    const blob=new Blob([rows.map(r=>JSON.stringify(r)).join('\n')+'\n'],{type:'application/x-ndjson;charset=utf-8'});
    const url=URL.createObjectURL(blob), a=node('a'); a.href=url; a.download='decisions-reviewed.jsonl';
    document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  $('export').addEventListener('click',exportDecisions);
  $('submit').addEventListener('click',async()=>{
    if (submitted||saving||$('submit').disabled) return;
    if (!data.hosted) {exportDecisions();$('status').textContent='审核结果已导出。此文件页没有直接写回权限，请保留下载文件并告诉我已导出。';return;}
    saving=true;render();$('submit').textContent='正在保存…';
    try {
      const response=await fetch('/api/topics/' + reviewKind,{method:'POST',headers:{'Content-Type':'application/json'},
        credentials:'same-origin',body:JSON.stringify(submission())});
      if (!response.ok) throw new Error(response.status===409?'该批已有提交或正在保存，请刷新核对。':'保存未完成，草稿仍在。请稍后再试或导出备份。');
      const result=await response.json();
      // Reload displays the server's immutable receipt and original timestamps, including after a lost response.
      $('status').textContent=`已保存 ${result.total} 条审核结果，正在读取本机回执…`;
      window.location.reload();
    } catch(error) { $('status').textContent=error.message || '连接失败，草稿仍在，请稍后重试。';saving=false;$('submit').textContent='确认提交并保存';render(); }
  });
  data.taxonomy.forEach(t=>$('taxonomy').append(node('dt',t.name),node('dd',t.boundary)));
  $('packHash').textContent=data.pack_hash;
  $('fileNotice').hidden=data.hosted;
  if (!data.hosted) $('submit').textContent='确认并导出结果';
  if (submitted) $('status').textContent=`${aiDelegated?'AI 代审已保存（非人工）':'审核已保存'} · 保留 ${data.submitted.samples.length} 条 · 排除 ${data.submitted.excluded_ids.length} 条`;
  render();
})();
