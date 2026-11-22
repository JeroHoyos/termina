// ───────────── viewer ─────────────
function paintViewer(fresh) {
  if (mode === 'new') { if (fresh) paintNew(); return; }
  if (mode === 'talk') { if (fresh && !$('#f-talk')) paintNewTalk(); return; }
  if (mode === 'find') { if (fresh && !$('#f-find')) paintFind(); return; }
  if (mode === 'details') { if (fresh && !$('#f-details')) paintDetails(); return; }
  const s = current();
  if (!s) {
    releaseVideos();
    $('#viewer').innerHTML = data ? '<div class="empty-state"><b>Pick a slide</b>They are on the left, in the order of the talk</div>' : '';
    return;
  }
  if (!s.active) { if (fresh || !$('#o-restore')) paintOut(s); return; }
  if (fresh || !$('#screen')) {
    mode = 'view';
    $('#viewer').innerHTML = `<div class="column">
      <div class="viewer-head">
        <h1><span class="pos">${esc(s.pos)}</span><span id="v-name"></span></h1>
        <span class="chips" id="v-chips"></span>
        <span class="spacer"></span>
        <button class="btn icon subtle" id="b-actions" aria-label="More actions" aria-haspopup="menu" title="More actions">${icon('more')}</button>
      </div>
      <div class="viewer-meta" id="v-group"></div>
      <div class="screen" id="screen"><div class="stack" id="stack"></div><div class="video-note" id="v-note" hidden></div></div>
      <div class="timeline empty" id="timeline" role="slider" tabindex="0" aria-label="Position in the slide" aria-valuemin="0" aria-valuemax="0" aria-valuenow="0">
        <div class="segments" id="segments"></div>
        <div class="playhead" id="playhead"><i></i></div>
        <div class="tl-tip" id="tl-tip" hidden></div>
      </div>
      <div class="controls">
        <button class="btn icon" id="p-play" aria-label="Play">${icon('play')}</button>
        <button class="btn icon subtle" id="p-prev" aria-label="Previous pause" title="Previous pause (←)">${icon('skip-back')}</button>
        <button class="btn icon subtle" id="p-next" aria-label="Next pause" title="Next pause (→)">${icon('skip-fwd')}</button>
        <span class="time" id="v-time"></span>
        <span class="pauses" id="v-pauses" aria-live="polite"></span>
        <span class="spacer"></span>
        <button class="btn" id="b-canvas" title="Move, change and add objects on the slide">${icon('pencil')}Edit on the slide</button>
        <button class="btn" id="b-render"></button>
        <button class="btn" id="b-present" title="Present the talk from this slide">${icon('play')}Present from here</button>
      </div>
      <p class="status-line"><span class="dot" id="v-dot"></span><span id="v-status"></span><span class="hint" id="v-rendered"></span>
        <span class="spacer"></span>
        <select id="v-resolution" aria-label="Resolution of this slide" title="Resolution of this slide"></select></p>
      <section class="review" aria-labelledby="t-review">
        <div class="review-head"><h2 id="t-review">Review</h2><span class="hint" id="v-review"></span></div>
        <textarea id="note" aria-labelledby="t-review" placeholder="What would you change? Write it as you would tell Claude: “make the title bigger”, “remove the second sentence”…"></textarea>
        <div class="c-attachments" id="r-images" hidden></div>
        <input type="file" id="r-file" accept="image/*" multiple hidden>
        <div class="review-actions">
          <button class="btn" id="b-approve">${icon('check')}Approve</button>
          <button class="btn subtle" id="b-mark" title="Point, draw or show where to move something, on the slide">${icon('mark')}Mark on the slide</button>
          <button class="btn subtle" id="b-image" title="Attach images to the note, you can also paste or drop them">${icon('image')}Attach image</button>
          <span class="spacer"></span>
          <button class="btn subtle" id="b-save-note" title="Save the note to send it later together with others">${icon('pencil')}Save note</button>
          <button class="btn primary" id="b-send" title="Send the request to Claude">${icon('send')}Send to Claude</button>
        </div>
      </section></div>`;
    $('#note').value = noteDrafts.get(noteKey(s)) ?? (s.review.note || '');
    $('#note').oninput = e => { const now = current(); if (now) noteDrafts.set(noteKey(now), e.target.value); };
    wireNoteImages();
    wirePlayer();
    $('#v-resolution').onchange = e => setResolution(current(), e.target.value);
  }
  if (mode !== 'rename') $('#v-name').textContent = s.name;
  const rev = REVIEW[s.review.status];
  $('#v-chips').innerHTML = [
    `<span class="chip ${esc(s.status)}"><span class="dot s-${esc(s.status)}"></span>${esc(LABEL[s.status])}</span>`,
    s.quality && s.status !== 'new' ? `<span class="chip">${esc(s.quality)}</span>` : '',
    rev ? `<span class="chip ${rev.cls}">${rev.icon ? icon(rev.icon) : ''}${rev.text}</span>` : '',
    openedByClaude === s.name ? '<span class="chip claude">Claude opened it</span>' : '',
  ].join('');
  $('#v-group').textContent = s.group;
  $('#v-dot').className = `dot s-${s.status}`;
  $('#v-status').textContent = EXPLAIN[s.status](s);
  $('#v-rendered').textContent = s.rendered_at ? `Rendered ${new Date(s.rendered_at).toLocaleString('en', {dateStyle: 'medium', timeStyle: 'short'})}` : '';
  $('#v-review').textContent = s.review.date ? `${rev?.text ?? 'Note'} on ${new Date(s.review.date).toLocaleDateString('en', {dateStyle: 'medium'})}` : '';
  const sr = $('#v-resolution');
  if (document.activeElement !== sr) {
    sr.innerHTML = `<option value="">The talk's resolution (${quality})</option>` +
      QUALITIES.map(r => `<option value="${r}">This one at ${r}</option>`).join('');
    sr.value = s.resolution || '';
  }
  // “Render” is the main action only when something is pending.
  const br = $('#b-render');
  br.className = 'btn' + (s.status !== 'up_to_date' ? ' primary' : '');
  br.innerHTML = `${icon('layers')}Render`;
  br.disabled = rendering().has(s.name);
  $('#b-present').disabled = !s.parts.length;
  $('#b-canvas').disabled = !s.parts.length;
  loadVideo();
}

// Find and replace in the text of the slides and in the speaker notes.
let findQuery = '';
function paintFind() {
  releaseVideos();
  $('#viewer').innerHTML = `<form class="form" id="f-find" autocomplete="off">
    <div><h1>Find in the slides</h1>
      <p class="hint">It looks in the text of the slides and in the speaker notes</p></div>
    <div class="field"><label for="q-find">Find</label><input type="text" id="q-find" required></div>
    <div class="field"><label for="q-replace">Replace with <span class="optional">optional</span></label>
      <input type="text" id="q-replace"></div>
    <div class="checks"><label><input type="checkbox" id="q-case">Match case</label>
      <label><input type="checkbox" id="q-word">Whole words</label></div>
    <div class="actions">
      <button type="button" class="btn subtle" id="q-close">Close</button>
      <button type="button" class="btn" id="q-all">Replace all</button>
      <button type="submit" class="btn primary">${icon('search')}Find</button>
    </div>
    <div id="q-results" aria-live="polite"></div></form>`;
  const query = $('#q-find');
  const run = async replace => {
    findQuery = query.value;
    if (!findQuery) { query.focus(); return null; }
    try {
      const r = await invoke('find', {talk, query: findQuery, replace, case: $('#q-case').checked, word: $('#q-word').checked});
      $('#q-results').innerHTML = r.matches.length ? r.matches.map(m => `<button type="button" class="found" data-k="${esc(m.key)}">
        <b>${esc(m.slide)}</b>${m.notes ? '<span class="tag">speaker notes</span>' : ''}<span>${esc(m.text)}</span></button>`).join('')
        : '<div class="empty-state"><b>Nothing found</b>Try with other words</div>';
      return r;
    } catch (e) { toast(String(e)); return null; }
  };
  query.value = findQuery;
  query.focus(); query.select();
  if (findQuery) run(null);
  $('#f-find').onsubmit = e => { e.preventDefault(); run(null); };
  $('#q-close').onclick = () => { mode = 'view'; paintViewer(true); };
  $('#q-all').onclick = async () => {
    const to = $('#q-replace').value;
    if (!query.value || !confirm(`Replace every “${query.value}” with “${to}” in the slides and the speaker notes?`)) return;
    const r = await run(to);
    if (r) { toast(`Replaced ${r.replaced} time${r.replaced === 1 ? '' : 's'}`); refresh(); }
  };
  $('#q-results').onclick = e => select((e.target as Element).closest('.found')?.dataset.k);
}

function paintOut(s) {
  releaseVideos();
  $('#viewer').innerHTML = `<div class="out-view">
    <div class="viewer-head"><h1>${esc(s.name)}</h1><span class="chip">commented out</span></div>
    <p>This slide is commented out in the talk, put it back or delete it</p>
    <div class="actions">
      <button class="btn primary" id="o-restore">${icon('again')}Put it back</button>
      <button class="btn danger" id="o-delete">${icon('trash')}Delete…</button>
    </div></div>`;
}

function paintNew() {
  releaseVideos();
  const a = actives();
  const ref = current()?.active ? current() : a[a.length - 1];
  $('#viewer').innerHTML = `<form class="form" id="f-new" autocomplete="off">
    <h1>New slide</h1>
    <div class="field"><label for="n-name">Name</label>
      <input type="text" id="n-name" required placeholder="For example: git stash">
      <span class="hint" id="n-preview">This is how it will show up in the list</span></div>
    <div class="field"><label for="n-after">Goes after</label>
      <select id="n-after">${a.map(x => `<option value="${esc(x.name)}" ${x === ref ? 'selected' : ''}>${esc(x.pos)} ${esc(x.name)}</option>`).join('')}</select></div>
    <div class="field"><label for="n-what">What it should show <span class="optional">optional</span></label>
      <textarea id="n-what" placeholder="Claude makes it with this, for example: “the three areas of git with an arrow for each command”"></textarea>
      <span class="hint">If you leave it empty, it is created with a placeholder title and you fill it in later</span></div>
    <div class="actions">
      <button type="button" class="btn subtle" id="n-cancel">Cancel</button>
      <button type="submit" class="btn primary" id="n-create">${icon('plus')}Create slide</button>
    </div></form>`;
  const name = $('#n-name');
  name.focus();
  name.oninput = () => {
    const n = toName(name.value);
    $('#n-preview').textContent = n ? `It will show up as ${n}` : 'This is how it will show up in the list';
  };
  $('#n-cancel').onclick = () => { mode = 'view'; paintViewer(true); };
  $('#f-new').onsubmit = async e => {
    e.preventDefault();
    if (!/^[a-z]/.test(toName(name.value))) { name.focus(); toast('The name has to start with a letter'); return; }
    const after = $('#n-after').value;
    const what = $('#n-what').value.trim();
    $('#n-create').disabled = true;
    try {
      const r = JSON.parse(await invoke('edit', {talk, args: ['new', '--json', ...(after ? ['--after', after] : []), '--', name.value.trim()]}));
      mode = 'view'; filter = 'all';
      await refresh();
      select(r.name);
      if (what) sendToClaude(`/slides ${talk} ${r.name}: it is a new slide, already created and placed in the talk, make it with this: ${what}`);
      else toast(`Created ${r.name} at position ${r.pos}`);
    } catch (err) {
      $('#n-create').disabled = false;
      toast(String(err));
    }
  };
}

const LANGUAGES = [['es', 'Spanish'], ['en', 'English']];
const languageOptions = chosen => (LANGUAGES.some(([c]) => c === chosen) ? LANGUAGES : [...LANGUAGES, [chosen, chosen]])
  .map(([c, n]) => `<option value="${esc(c)}" ${c === chosen ? 'selected' : ''}>${esc(n)}</option>`).join('');
const leaveForm = () => { mode = 'view'; newTalkDraft = null; if (talk) paintViewer(true); else paintNoTalks(); };

// A new talk goes in a folder of its own, wherever the user wants: everything of the talk lives
// there (its slides, their code, its videos and its termina.json).
function paintNewTalk() {
  releaseVideos();
  const draft = newTalkDraft || {};
  let place = draft.place || load('studio.place', '') || root;
  let named = !!draft.folder;  // the folder name was written by hand: the title no longer changes it
  $('#viewer').innerHTML = `<form class="form" id="f-talk" autocomplete="off">
    <div><h1>New talk</h1>
      <p class="hint">It starts with a title slide and a closing slide, then you add slides here or with Claude</p></div>
    <div class="field"><label for="t-kind">What you make</label>
      <select id="t-kind"><option value="slides">Talk to present</option><option value="video">Video 16:9</option><option value="reel">Reel 9:16</option></select>
      <span class="hint">A video has no pauses: its scenes play one after the other in one MP4. A reel is a vertical video, for the phone</span></div>
    <div class="field"><label for="t-title">Title</label>
      <input type="text" id="t-title" required placeholder="For example: Docker from scratch"></div>
    <div class="field"><label for="t-topic">What it is about <span class="optional">optional</span></label>
      <textarea id="t-topic" placeholder="Who it is for and what it covers, for example: “for beginners, what a container is, images, volumes and docker compose”"></textarea>
      <span class="hint">It is saved with the talk; if you write it, Claude proposes the slides and waits for your approval before making them</span></div>
    <div class="field"><label for="t-language">Language of the slides</label>
      <select id="t-language">${languageOptions(load('studio.language', 'es'))}</select></div>
    <div class="field"><span class="field-name" id="t-where">Where</span>
      <div class="place" role="group" aria-labelledby="t-where"><span class="place-path" id="t-place"></span>
        <button type="button" class="btn" id="t-choose">Choose folder</button></div></div>
    <div class="field"><label for="t-folder">Folder of the talk</label>
      <input type="text" id="t-folder" required spellcheck="false" placeholder="For example: charla-docker">
      <span class="hint" id="t-folder-hint"></span></div>
    <div class="actions">
      <button type="button" class="btn subtle" id="t-cancel">Cancel</button>
      <button type="submit" class="btn primary" id="t-create">${icon('plus')}Create talk</button>
    </div></form>`;
  const title = $('#t-title'), folder = $('#t-folder');
  const paintPlace = () => {
    $('#t-place').textContent = shortPath(place);
    $('#t-place').title = place;
    $('#t-folder-hint').textContent = draft.folder && folder.value === draft.folder && place === draft.place
      ? 'That folder is empty, the talk goes in it'
      : 'A new folder inside the one above, with everything of the talk';
  };
  folder.value = draft.folder || '';
  paintPlace();
  title.focus();
  const kind = $('#t-kind');
  title.oninput = kind.onchange = () => { if (!named) { folder.value = folderName(title.value, kind.value); paintPlace(); } };
  folder.oninput = () => { named = !!folder.value.trim(); paintPlace(); };
  $('#t-choose').onclick = async () => {
    const picked = await pickFolder('Choose where the new talk goes', place);
    if (picked) { place = picked.path; paintPlace(); }
  };
  $('#t-cancel').onclick = leaveForm;
  $('#f-talk').onsubmit = async e => {
    e.preventDefault();
    const t = title.value.trim(), topic = $('#t-topic').value.trim();
    if (!/[a-z0-9]/i.test(t.normalize('NFKD'))) { title.focus(); toast('The title needs at least one letter or number'); return; }
    if (!folder.value.trim()) { folder.focus(); toast('The talk needs a folder name'); return; }
    $('#t-create').disabled = true;
    try {
      const r = await invoke('new_talk', {
        title: t, about: topic, language: $('#t-language').value,
        place, folder: folder.value.trim(), kind: kind.value,
      });
      save('studio.place', place);
      save('studio.language', $('#t-language').value);
      // A new talk starts at the resolution that the user chose last.
      const q = load('studio.quality', '');
      if (QUALITIES.includes(q) && q !== r.resolution) await invoke('save_talk', {talk: r.id, fields: {resolution: q}});
      newTalkDraft = null;
      await enterTalk(r);
      const video = kind.value !== 'slides', what = {slides: 'talk', video: 'video', reel: 'reel'}[kind.value];
      const start = video ? 'a title scene and an end scene' : 'a title slide and a closing slide';
      if (topic) sendToClaude(`/slides ${r.id}: it is a new ${what}, “${t}”, already created with ${start}. What it is about is in its termina.json: ${topic}. Propose the list of ${video ? 'scenes' : 'slides'} first and wait for my approval before creating them`);
      else toast(video ? 'Video made, render its pending scenes to see it' : 'Talk created, render its pending slides to see it');
    } catch (err) {
      $('#t-create').disabled = false;
      toast(String(err));
    }
  };
}

const THEMES = [['dark', 'Dark'], ['light', 'Light'], ['night', 'Night'], ['paper', 'Paper']];

// What the talk is, from its termina.json: Claude reads the same file.
function paintDetails() {
  releaseVideos();
  const p = data?.project;
  if (!p) { mode = 'view'; paintViewer(true); return; }
  $('#viewer').innerHTML = `<form class="form" id="f-details" autocomplete="off">
    <div><h1>Talk details</h1>
      <p class="hint">They are saved with the talk, in its own file, and Claude reads them before making slides</p></div>
    <div class="field"><label for="d-title">Title</label>
      <input type="text" id="d-title" required>
      <span class="hint">How the talk shows up here, the title slide keeps its own text</span></div>
    <div class="field"><label for="d-about">What it is about <span class="optional">optional</span></label>
      <textarea id="d-about" placeholder="Who it is for and what it covers"></textarea></div>
    <div class="field"><label for="d-author">Who gives it <span class="optional">optional</span></label>
      <input type="text" id="d-author"></div>
    <div class="field"><label for="d-language">Language of the slides</label>
      <select id="d-language">${languageOptions(p.language || 'es')}</select></div>
    ${data.theme === null ? '' : `<div class="field"><label for="d-theme">Colors of the slides</label>
      <select id="d-theme">${data.theme ? '' : '<option value="">Its own colors</option>'}${THEMES.map(([v, n]) => `<option value="${v}">${n}</option>`).join('')}</select>
      <span class="hint">A change of colors needs a new render of the slides</span></div>`}
    <div class="checks"><label><input type="checkbox" id="d-numbers">Number the slides</label></div>
    <div class="field"><label for="d-engine">Render with</label>
      <select id="d-engine"><option value="auto">ManimGX, then Manim CE</option><option value="manim-ce">Only Manim CE</option></select>
      <span class="hint">ManimGX is faster, Manim CE draws what it cannot</span></div>
    ${(p.kind || 'slides') === 'slides' ? '' : `<div class="field"><label for="d-kind">Shape</label>
      <select id="d-kind"><option value="video">Video 16:9</option><option value="reel">Reel 9:16</option></select>
      <span class="hint">A change of shape needs a new render of the scenes</span></div>
    <div class="field"><label for="d-music">Music <span class="optional">optional</span></label>
      <div class="place"><input type="text" id="d-music" spellcheck="false" placeholder="For example: music.mp3">
        <button type="button" class="btn" id="d-chiptune">Make 8-bit music</button></div>
      <span class="hint">A sound file in the folder of the video, it plays again and again under the whole MP4</span></div>`}
    <div class="field"><span class="field-name" id="d-where">Folder</span>
      <div class="place" role="group" aria-labelledby="d-where"><span class="place-path" id="d-place"></span>
        <button type="button" class="btn" id="d-show">Show in folder</button></div></div>
    <div class="actions">
      <button type="button" class="btn danger" id="d-forget">Remove from the list…</button>
      <span class="spacer"></span>
      <button type="button" class="btn subtle" id="d-cancel">Cancel</button>
      <button type="submit" class="btn primary" id="d-save">${icon('check')}Save</button>
    </div></form>`;
  const fields = ['title', 'about', 'author', 'language', 'engine', ...($('#d-kind') ? ['kind', 'music'] : [])];
  for (const f of fields) $(`#d-${f}`).value = p[f] || '';
  $('#d-engine').value = p.engine || 'auto';
  if ($('#d-chiptune')) $('#d-chiptune').onclick = async e => {
    e.target.disabled = true;
    try {
      toast(await invoke('edit', {talk, args: ['chiptune']}));
      p.music = $('#d-music').value = 'music-8bit.wav';
    } catch (err) { toast(String(err)); }
    e.target.disabled = false;
  };
  $('#d-language').value = p.language || 'es';
  $('#d-numbers').checked = p.numbers === 'on';
  if ($('#d-theme')) $('#d-theme').value = data.theme;
  $('#d-place').textContent = shortPath(data.path);
  $('#d-place').title = data.path;
  $('#d-title').focus();
  $('#d-show').onclick = () => act(invoke('show_talk_folder', {talk}));
  $('#d-cancel').onclick = leaveForm;
  $('#d-forget').onclick = async () => {
    if (!confirm(`Remove “${p.title}” from the list? Its folder, its slides and its videos stay where they are, and you can open it again whenever you want`)) return;
    try {
      toast(await invoke('forget_talk', {talk}));
      mode = 'view';
      await reloadTalks();
      await refresh();
    } catch (e) { toast(String(e)); }
  };
  $('#f-details').onsubmit = async e => {
    e.preventDefault();
    const changed: Record<string, string> = {};
    for (const f of fields) {
      const v = $(`#d-${f}`).value.trim();
      if (v !== (p[f] || '')) changed[f] = v;
    }
    if (changed.title === '') { $('#d-title').focus(); toast('The talk needs a title'); return; }
    $('#d-save').disabled = true;
    try {
      const numbers = $('#d-numbers').checked ? 'on' : 'off', colors = $('#d-theme')?.value;
      if (numbers !== (p.numbers || 'off')) changed.numbers = numbers;
      if (Object.keys(changed).length) await invoke('save_talk', {talk, fields: changed});
      if (colors && colors !== data.theme) await invoke('edit', {talk, args: ['theme', colors]});
      mode = 'view';
      if (changed.title) { talks = await invoke('talks'); paintTalks(); }
      await refresh();
      paintViewer(true);
      toast('Saved');
    } catch (err) {
      $('#d-save').disabled = false;
      toast(String(err));
    }
  };
}
