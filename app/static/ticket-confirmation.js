/* Chat-native preview. No model/user HTML is interpreted. */
window.MewTicketConfirmationUI = {
  render({ container, preview, onDecision }) {
    const section = document.createElement('section');
    section.className = 'ticket-preview';
    section.setAttribute('aria-label', '确认工单');
    const eyebrow = document.createElement('p');
    eyebrow.className = 'ticket-preview-eyebrow';
    eyebrow.textContent = '人工协助 · 提交前确认';
    const title = document.createElement('h3');
    title.textContent = '请核对这份工单';
    const type = document.createElement('p');
    type.className = 'ticket-preview-type';
    type.textContent = '工单类型：' + preview.ticket_type;
    const description = document.createElement('p');
    description.className = 'ticket-preview-description';
    description.textContent = preview.description;
    const status = document.createElement('p');
    status.className = 'ticket-preview-status';
    status.setAttribute('role', 'status');
    status.textContent = '确认后才会提交给客服处理。';
    const actions = document.createElement('div');
    actions.className = 'ticket-preview-actions';
    const confirm = document.createElement('button');
    const cancel = document.createElement('button');
    confirm.type = cancel.type = 'button';
    confirm.className = 'support-action ticket-preview-confirm';
    cancel.className = 'support-action';
    confirm.textContent = '确认提交';
    cancel.textContent = '取消';
    let pending = false;
    let finished = false;
    const lock = (message) => {
      finished = true;
      confirm.disabled = cancel.disabled = true;
      status.textContent = message;
    };
    for (const [button, decision] of [[confirm, 'confirm'], [cancel, 'cancel']]) {
      button.addEventListener('click', async () => {
        if (pending || finished) return;
        pending = true;
        confirm.disabled = cancel.disabled = true;
        status.textContent = decision === 'confirm' ? '正在提交这份工单…' : '正在取消…';
        try {
          await onDecision(decision);
          lock(decision === 'confirm' ? '本次确认已处理，请查看下方回执。' : '已取消，本次未创建工单。');
        } catch (error) {
          status.textContent = error.message || '结果尚未确认，可以重试同一申请。';
          finished = Boolean(error.permanent);
          confirm.disabled = cancel.disabled = finished;
        } finally {
          pending = false;
        }
      });
    }
    actions.append(confirm, cancel);
    section.append(eyebrow, title, type, description, actions, status);
    container.append(section);
    return { invalidate: lock, section };
  },
};
