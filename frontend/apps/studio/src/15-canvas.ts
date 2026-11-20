// ───────────── editing on the slide ─────────────
// The render says what each pause shows: every object and its box. Here you drag an object to move
// it, double-click a text to change it, or add an element. Each change is a small change to the
// code of the slide, and the slide renders again to show it.
let canvas = null;  // {s, pause, frame, items, layer, adding}: while the slide is being edited
const ELEMENTS = [['text', 'Text'], ['formula', 'Formula'], ['rectangle', 'Rectangle'], ['circle', 'Circle'],
  ['arrow', 'Arrow'], ['picture', 'Picture'], ['sphere', 'Sphere'], ['cube', 'Cube'], ['axes', '3D axes']];

async function startCanvas() {
  const v = vid(), screen = $('#screen'), s = current();
  if (canvas) endCanvas();
  if (mark || !screen || !s) return;
  if (!v || v.readyState < 2) { toast('Render the slide first, then edit on it'); return; }
  let found;
  try { found = await invoke('objects', {talk, line: s.line}); } catch (e) { toast(String(e)); return; }
  if (!found.fresh) { toast('Render the slide again to edit on it'); return; }
  player.playing = false;
  v.pause();
  v.currentTime = Math.max(0, v.duration - 0.05);  // the end of the pause: what the objects are
  const layer = document.createElement('div');
  layer.id = 'canvas-layer';
  const bar = document.createElement('div');
  bar.id = 'canvas-bar';
  bar.innerHTML = `<select id="canvas-add" aria-label="Add an element"><option value="">Add an element…</option>${
    ELEMENTS.map(([k, n]) => `<option value="${k}">${n}</option>`).join('')}</select>
    <span class="hint" id="canvas-hint"></span><span class="spacer"></span>
    <button type="button" class="btn small" id="canvas-close">Close</button>`;
  screen.append(layer);
  screen.after(bar);
  canvas = {s, pause: part, frame: found.frame, items: found.pauses[part] || [], layer, adding: ''};
  $('#canvas-add').onchange = e => { canvas.adding = e.target.value; paintCanvas(); };
  $('#canvas-close').onclick = endCanvas;
  wireCanvas(layer);
  paintCanvas();
}

function endCanvas() {
  canvas = null;
  $('#canvas-layer')?.remove();
  $('#canvas-bar')?.remove();
}

function paintCanvas() {
  const pct = v => `${Math.max(v, 0.012) * 100}%`;
  canvas.layer.classList.toggle('adding', !!canvas.adding);
  canvas.layer.innerHTML = canvas.items.map((o, i) => o.kind === 'group' ? ''
    : `<div class="obj" data-i="${i}" style="left:${o.box[0] * 100}%;top:${o.box[1] * 100}%;width:${pct(o.box[2])};height:${pct(o.box[3])}"></div>`).join('');
  $('#canvas-hint').textContent = canvas.adding ? 'Click the slide where the element goes'
    : 'Drag an object to move it, double-click a text to change it';
}

// Runs a change, closes the editor and renders the slide again. `run` gives the answer of the
// engine, or null if a dialog was closed.
async function canvasEdit(run) {
  const {s} = canvas;
  try {
    const answer = await run;
    if (answer === null) return;
    endCanvas();
    toast(`${answer}, rendering the slide again…`);
    await invoke('render', {talk, what: [s.name], quality: s.resolution || quality});
    await refresh();
  } catch (e) {
    toast(String(e));
    if (canvas) paintCanvas();
  }
}

function wireCanvas(layer) {
  const at = e => {
    const r = layer.getBoundingClientRect();
    return {x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height};
  };
  const order = (name, ...rest) => invoke('edit', {talk, args: [name, '--line', String(canvas.s.line), ...rest]});
  let drag = null;  // {el, from}
  layer.onpointerdown = e => {
    if (e.button !== 0) return;
    const p = at(e), [fw, fh] = canvas.frame;
    if (canvas.adding) {
      const where = `${((p.x - 0.5) * fw).toFixed(2)},${((0.5 - p.y) * fh).toFixed(2)}`;
      const pause = String(canvas.pause);
      canvasEdit(canvas.adding === 'picture'
        ? invoke('insert_picture', {talk, line: canvas.s.line, pause: canvas.pause, at: where})
        : order('insert', '--kind', canvas.adding, '--pause', pause, `--at=${where}`));
      return;
    }
    const el = (e.target as Element).closest('.obj') as HTMLElement;
    if (!el) return;
    layer.setPointerCapture(e.pointerId);
    drag = {el, from: p};
    el.classList.add('dragging');
  };
  layer.onpointermove = e => {
    if (!drag) return;
    const p = at(e), r = layer.getBoundingClientRect();
    drag.el.style.transform = `translate(${(p.x - drag.from.x) * r.width}px, ${(p.y - drag.from.y) * r.height}px)`;
  };
  layer.onpointerup = e => {
    if (!drag) return;
    const p = at(e), [fw, fh] = canvas.frame, {el, from} = drag;
    drag = null;
    el.classList.remove('dragging');
    const dx = p.x - from.x, dy = p.y - from.y;
    if (Math.hypot(dx, dy) < 0.01) { el.style.transform = ''; return; }  // a click, not a drag
    canvasEdit(order('move-object', '--pause', String(canvas.pause), '--index', el.dataset.i,
      `--by=${(dx * fw).toFixed(2)},${(-dy * fh).toFixed(2)}`));
  };
  layer.ondblclick = e => {
    const el = (e.target as Element).closest('.obj') as HTMLElement;
    const o = el && canvas.items[Number(el.dataset.i)];
    if (!o || !o.text) { if (o) toast('Only a text or a formula changes here, use Code for the others'); return; }
    const fresh = prompt('New text', o.text);
    if (fresh === null || fresh === o.text) return;
    canvasEdit(order('retext', '--', o.text, fresh));
  };
}
