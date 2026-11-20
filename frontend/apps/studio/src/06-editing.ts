// ───────────── editing the talk ─────────────
// Runs a studio.py order, refreshes and leaves selected the slide that `then` says.
async function edit(args, then) {
  const r = await invoke('edit', {talk, args});
  await refresh();
  const s = then ? data.slides.find(then) : null;
  if (s) select(key(s));
  return r;
}
const attempt = promise => promise.then(r => r && toast(r)).catch(e => toast(String(e)));

function moveSlide(s, after) {
  const args = ['move', '--line', String(s.line), ...(after ? ['--after', after.name] : ['--first'])];
  attempt(edit(args, x => x.active && x.name === s.name));
}

function moveBy(s, step) {
  const a = actives(), i = a.indexOf(s), j = i + step;
  if (i < 0 || j < 0 || j >= a.length) return;
  moveSlide(s, step < 0 ? a[j - 1] ?? null : a[j]);
}

function startRename() {
  const s = current();
  if (!s?.active || !$('#v-name')) return;
  mode = 'rename';
  const before = s.method.replace(/^slide_/, '');
  $('#v-name').innerHTML = `<input type="text" id="v-new-name" value="${esc(before)}" aria-label="New name">`;
  const field = $('#v-new-name');
  field.focus(); field.select();
  const finish = () => { mode = 'view'; paintViewer(false); };
  field.onkeydown = e => {
    if (e.key === 'Escape') { e.preventDefault(); finish(); }
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const fresh = field.value.trim();
    if (!toName(fresh) || toName(fresh) === before) { finish(); return; }
    const repeated = actives().filter(x => x.method === s.method).length > 1;
    mode = 'view';
    attempt(edit(['rename', '--line', String(s.line), '--', fresh], x => x.line === s.line)
      .then(r => repeated ? `${r}, together with its repetitions` : r));
  };
  field.onblur = () => setTimeout(() => { if (mode === 'rename') finish(); }, 120);
}

// True if a group starts at this slide.
const startsGroup = s => !!s.group && data.slides[data.slides.indexOf(s) - 1]?.group !== s.group;

// A field in the list for the name of the group that starts at `s`: a new group or a new name.
function startGroup(s) {
  const before = startsGroup(s) ? s.group : '';
  if (!before && closedGroups().has(s.group)) toggleGroup(s.group);  // its row has to be in the list
  const place = (before && $(`#list .group[data-line="${s.line}"]`))
    || document.querySelector(`.row[data-k="${CSS.escape(key(s))}"]`);
  if (!place) return;
  const field = document.createElement('input');
  Object.assign(field, {type: 'text', className: 'group-name', value: before, placeholder: 'Group name'});
  field.setAttribute('aria-label', 'Group name');
  place.classList.contains('group') ? place.replaceWith(field) : place.before(field);
  field.focus(); field.select();
  const finish = () => { field.remove(); listSig = ''; paintList(); };
  field.onkeydown = e => {
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); field.blur(); }
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const name = field.value.trim();
    field.onblur = null;
    field.remove();
    if (name === before) { finish(); return; }
    attempt(edit(['group', '--line', String(s.line), '--', name], null));
  };
  field.onblur = finish;
}

function deleteSlide(s) {
  if (!confirm(`Delete ${s.name}? It leaves the talk, its videos are deleted, and its file goes to the recycle bin if nothing else uses it`)) return;
  const pos = s.pos;
  attempt(edit(['delete', '--line', String(s.line)], x => x.active && pos && (x.pos === pos || x.pos === pos - 1)));
}

function setResolution(s, value) {
  if (!s) return;
  attempt(edit(['resolution', '--line', String(s.line), '--', value || 'default'], x => x.line === s.line));
}

// The menu of a slide: with the “⋯” button of the viewer or right click in the list.
function openSlideMenu(s, x, y) {
  const m = $('#slide-menu');
  const a = actives(), i = a.indexOf(s);
  const items = s.active ? [
    ['rename', 'pencil', 'Rename'],
    ['up', 'up', 'Move up', i <= 0],
    ['down', 'down', 'Move down', i >= a.length - 1],
    null,
    ['new', 'plus', 'New slide after this one'],
    ['duplicate', 'doc', 'Duplicate'],
    ['group', 'layers', startsGroup(s) ? 'Rename the group' : 'Start a group here'],
    null,
    ['mp4', 'export', 'Export as video (.mp4)', !s.parts?.length],
    ['gif', 'export', 'Export as GIF', !s.parts?.length],
    null,
    ['hide', 'x', 'Hide from the talk'],
    ['delete', 'trash', 'Delete…', false, 'danger'],
  ] : [
    ['restore', 'again', 'Put it back'],
    ['group', 'layers', startsGroup(s) ? 'Rename the group' : 'Start a group here'],
    ['delete', 'trash', 'Delete…', false, 'danger'],
  ];
  m.innerHTML = items.map(it => it
    ? `<button role="menuitem" data-a="${it[0]}" class="${it[4] || ''}" ${it[3] ? 'disabled' : ''}>${icon(it[1])}${it[2]}</button>`
    : '<hr>').join('');
  m.dataset.k = key(s);
  placeMenu(m, x, y);
  m.querySelector('button:not(:disabled)')?.focus();
}
const closeSlideMenu = () => { $('#slide-menu').hidden = true; };

// The menu of a group, with right click on its name; `s` is the slide the group starts at.
function openGroupMenu(s, x, y) {
  const m = $('#slide-menu');
  m.innerHTML = `<button role="menuitem" data-a="newin">${icon('plus')}New slide in this group</button>
    <hr>
    <button role="menuitem" data-a="group">${icon('pencil')}Rename the group</button>
    <button role="menuitem" data-a="ungroup">${icon('trash')}Remove the group, keep its slides</button>`;
  m.dataset.k = key(s);
  placeMenu(m, x, y);
  m.querySelector('button').focus();
}

// The menu of the empty part of the list: it makes a slide or a group at the selected slide.
function openListMenu(s, x, y) {
  const m = $('#slide-menu');
  m.innerHTML = `<button role="menuitem" data-a="new" ${s.active ? '' : 'disabled'}>${icon('plus')}New slide after ${esc(s.name)}</button>
    <button role="menuitem" data-a="group">${icon('layers')}${startsGroup(s) ? 'Rename the group' : `Start a group at ${esc(s.name)}`}</button>`;
  m.dataset.k = key(s);
  placeMenu(m, x, y);
  m.querySelector('button:not(:disabled)').focus();
}

// The last slide of the group that starts at `s`, without the commented-out ones.
function lastOfGroup(s) {
  let last = null;
  for (let i = data.slides.indexOf(s); data.slides[i]?.group === s.group; i++) {
    if (data.slides[i].active) last = data.slides[i];
  }
  return last;
}

function placeMenu(m, x, y) {
  m.hidden = false;
  m.style.left = Math.max(8, Math.min(x, innerWidth - m.offsetWidth - 8)) + 'px';
  m.style.top = Math.max(8, Math.min(y, innerHeight - m.offsetHeight - 8)) + 'px';
}

function slideAction(action, s) {
  const actions = {
    rename: () => { if (sel !== key(s)) select(key(s)); startRename(); },
    up: () => moveBy(s, -1),
    down: () => moveBy(s, 1),
    new: () => { if (sel !== key(s)) select(key(s)); mode = 'new'; paintViewer(true); },
    duplicate: () => attempt(edit(['duplicate', '--json', '--line', String(s.line)], null)
      .then(r => { const made = JSON.parse(r); select(made.name); return `Created ${made.name}, a copy of ${s.name}`; })),
    mp4: () => act(invoke('export', {talk, format: 'mp4', slide: s.name}), 'Queued: export'),
    gif: () => act(invoke('export', {talk, format: 'gif', slide: s.name}), 'Queued: export'),
    newin: () => { const last = lastOfGroup(s); last ? slideAction('new', last) : toast('Put a slide of the group back first'); },
    group: () => startGroup(s),
    ungroup: () => attempt(edit(['group', '--line', String(s.line), '--'], null)),
    hide: () => attempt(edit(['hide', '--line', String(s.line)], x => x.line === s.line)),
    restore: () => attempt(edit(['restore', '--line', String(s.line)], x => x.line === s.line)),
    delete: () => deleteSlide(s),
  };
  actions[action]?.();
}
