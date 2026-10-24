"use strict";
// Local navigation only: no fetch, storage writes, form submission or model work.
for (const group of document.querySelectorAll('[data-workspace-tabs]')) {
  const buttons = [...group.querySelectorAll('[data-panel]')];
  const panels = buttons.map(button => document.getElementById(button.dataset.panel));
  if (!panels.every(Boolean)) continue;
  buttons.forEach((button, index) => {
    button.id = panels[index].id + '-tab';
    panels[index].setAttribute('role', 'tabpanel');
    panels[index].setAttribute('aria-labelledby', button.id);
  });
  const select = (index, focus = false) => {
    buttons.forEach((button, i) => {
      const active = i === index;
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
      panels[i].hidden = !active;
      if (active && focus) button.focus();
    });
  };
  buttons.forEach((button, index) => {
    button.onclick = () => select(index);
    button.onkeydown = event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % buttons.length;
      if (event.key === 'ArrowLeft') next = (index + buttons.length - 1) % buttons.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (next !== undefined) { event.preventDefault(); select(next, true); }
    };
  });
  select(0);
}
if (location.pathname === '/observability') document.body.classList.add('ui-observability');
