// Home dashboard, called from Home.md as `await dv.view("90 System/home")`.
// Styling lives in .obsidian/snippets/kb-home.css (always loaded; works in reading view and live preview).
// Everything shown comes from note frontmatter (type / series / seq / summary / words ...) and from
// 90 System/kb.config.json (folder names, note types, labels and every user-visible string).
// New notes appear automatically. To translate or rename, edit kb.config.json, not this file.
// The whole script runs inside one async function, so a runtime error is shown in the note
// instead of disappearing as an unhandled promise rejection.
const kbHome = async () => {
  const app = dv.app;
  const root = dv.container;
  const here = dv.current().file.path;
  const adapter = app.vault.adapter;

  // ---------------------------------------------------------------- config
  // Location: `input.config` if Home.md passes one, otherwise the first `<folder>/kb.config.json`
  // found one level below the vault root.
  const findConfig = async () => {
    if (typeof input !== 'undefined' && input && input.config) return input.config;
    try {
      const top = await adapter.list('/');
      for (const f of (top.folders || []).sort()) {
        const p = f.replace(/^\/+/, '') + '/kb.config.json';
        if (await adapter.exists(p)) return p;
      }
    } catch (e) { }
    return null;
  };
  const configPath = await findConfig();
  let C = null;
  try { C = configPath ? JSON.parse(await adapter.read(configPath)) : null; } catch (e) { C = null; }
  if (!C) {
    const warn = document.createElement('p');
    warn.textContent = 'kb.config.json not found or invalid (expected e.g. "90 System/kb.config.json").';
    root.appendChild(warn);
    return;
  }
  const F = C.folders || {};
  const T = C.types || {};
  const UI = C.ui || {};
  const R = Object.assign({ words_per_minute: 230, words_unit: 1000, locale: 'en', finished_at: 0.9 }, C.reading || {});
  // t('key', {n: 3}) -> UI string with {placeholders} filled; a missing key shows its own name.
  const t = (key, vars) => String(UI[key] ?? key).replace(/\{(\w+)\}/g, (m, k) => (vars && vars[k] != null) ? String(vars[k]) : m);
  const inFolder = (path, folder) => !!folder && path.startsWith(folder + '/');

  const h = (tag, cls, text) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  };
  const open = (path, evt) => app.workspace.openLinkText(path, here, !!(evt && (evt.ctrlKey || evt.metaKey)));
  const link = (path, text, cls) => {
    const a = h('a', 'internal-link' + (cls ? ' ' + cls : ''), text);
    a.setAttribute('data-href', path);
    a.setAttribute('href', path);
    a.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); open(path, e); });
    a.addEventListener('mouseover', (e) => app.workspace.trigger('hover-link', {
      event: e, source: 'preview', hoverParent: root, targetEl: a, linktext: path, sourcePath: here }));
    return a;
  };
  const plink = (p, text, cls) => link(p.file.path, text ?? p.file.name, cls);
  const lp = (l) => (l && l.path) ? l.path : String(l || '');
  const base = (l) => lp(l).split('/').pop().replace(/\.md$/, '');
  let MarkdownRenderer = null;
  try { MarkdownRenderer = require('obsidian').MarkdownRenderer; } catch (e) { }
  // Render text containing $...$ math. Dataview's own renderer (dv.el) works inside
  // dv.view; require('obsidian') may not resolve there, so it is only a fallback.
  const md = (el, text) => {
    if (/\$/.test(text)) {
      try {
        const span = dv.el('span', text, { cls: 'kb-md' }); // created inside dv.container
        el.appendChild(span);                                // move it into the card
        return el;
      } catch (e) { }
      if (MarkdownRenderer) {
        try {
          if (MarkdownRenderer.render) MarkdownRenderer.render(app, text, el, here, dv.component);
          else MarkdownRenderer.renderMarkdown(text, el, here, dv.component);
          return el;
        } catch (e) { }
      }
    }
    el.textContent = text.replace(/\$/g, '');
    return el;
  };
  const minutes = (w) => Math.max(1, Math.round((w || 0) / R.words_per_minute));
  const section = (title, sub, extraCls) => {
    const s = h('section', 'kb-section' + (extraCls ? ' ' + extraCls : ''));
    const head = h('div', 'kb-section-head');
    head.appendChild(h('h2', 'kb-h2', title));
    if (sub) head.appendChild(h('p', 'kb-sub', sub));
    s.appendChild(head);
    return s;
  };
  const button = (text, fn, cls) => { const b = h('button', 'kb-btn' + (cls ? ' ' + cls : ''), text); b.addEventListener('click', fn); return b; };

  // ---------------------------------------------------------------- data
  // Notes in the templates and system folders are ignored (templates carry a type and would be
  // counted as articles / terms / literature). Only files that still exist on disk are kept:
  // after an external rename or delete the Dataview index can hold stale entries for a while.
  const vault = app.vault;
  const exists = (p) => !vault || vault.getAbstractFileByPath(p.file.path) != null;
  const all = dv.pages().where(p => !inFolder(p.file.path, F.templates) && !inFolder(p.file.path, F.system) && exists(p));
  const arts = all.where(p => p.type === T.article).sort(p => p.seq, 'asc').array();
  // One series map per series number (guards against duplicates / stale index rows).
  const seriesMaps = Object.values(Object.fromEntries(all.where(p => p.type === T.series).sort(p => p.file.mtime, 'asc').array()
    .map(p => [p.series_no, p]))).sort((x, y) => x.series_no - y.series_no);
  const artSeq = {};
  const terms0 = all.where(p => p.type === T.term).array();
  const lits = all.where(p => p.type === T.literature).array();
  for (const a of arts) artSeq[a.file.name] = a.seq;
  // Terms follow the reading order of the article that first explains them, then by name.
  const terms = terms0.sort((x, y) => (artSeq[base(x.defined_in)] || 999) - (artSeq[base(y.defined_in)] || 999)
    || String(x.term || x.file.name).localeCompare(String(y.term || y.file.name), R.locale));
  const front = Object.fromEntries(all.where(p => p.type === T.front).array().map(p => [p.file.name, p]));
  const citeCount = {};
  for (const a of arts) for (const s of (a.sources || [])) { const k = base(s); citeCount[k] = (citeCount[k] || 0) + 1; }
  const nWords = arts.reduce((x, a) => x + (a.words || 0), 0);
  const nFig = arts.reduce((x, a) => x + (a.figures || 0), 0);
  const nEq = arts.reduce((x, a) => x + (a.equations || 0), 0);
  const nPdf = lits.filter(l => lp(l.pdf)).length;
  const TONES = ['blue', 'violet', 'teal', 'amber', 'rose', 'green', 'slate'];
  const tone = (n) => 'kb-tone-' + TONES[((n || 1) - 1) % TONES.length];
  const seriesTitle = Object.fromEntries(seriesMaps.map(s => [s.series_no, s.title]));
  const byPath = Object.fromEntries(all.array().map(p => [p.file.path, p]));
  const artIdx = Object.fromEntries(arts.map((a, i) => [a.file.path, i]));
  const cc = (l) => citeCount[l.file.name] || 0;
  const words = (w) => t('words_fmt', { n: (w / R.words_unit).toFixed(1) });
  const venue = (l) => l.venue || l.journal || l.publisher;

  // Reading positions come from the local plugin kb-open-home.
  const kb = app.plugins && app.plugins.plugins && app.plugins.plugins['kb-open-home'];
  const hasKb = !!(kb && typeof kb.getRecent === 'function');
  const readMap = () => hasKb ? Object.fromEntries(kb.getRecent(200).map(e => [e.path, e])) : {};
  const status = (rm, path) => { const e = rm[path]; return !e ? 'new' : (e.pct || 0) >= R.finished_at ? 'done' : 'open'; };
  const ago = (ts) => {
    const m = Math.floor((Date.now() - ts) / 60000);
    if (m < 1) return t('just_now');
    if (m < 60) return t('minutes_ago', { n: m });
    if (m < 1440) return t('hours_ago', { n: Math.floor(m / 60) });
    if (m < 1440 * 30) return t('days_ago', { n: Math.floor(m / 1440) });
    return new Date(ts).toISOString().slice(0, 10);
  };
  const kind = (p) => p.type === T.article ? String(p.seq).padStart(2, '0') + ' · ' + (seriesTitle[p.series_no] || '')
    : p.type === T.term ? t('kind_term') : p.type === T.literature ? t('kind_literature')
    : p.type === T.series ? t('kind_series') : (p.type || t('kind_note'));
  const where = (e) => e.heading ? e.heading : (e.line > 0 ? t('near_start') : t('at_start'));
  const resume = (path, evt) => { evt.preventDefault(); evt.stopPropagation(); if (hasKb) kb.resume(path, !!(evt.ctrlKey || evt.metaKey)); else open(path, evt); };
  const progress = (pct, extra) => {
    const row = h('div', 'kb-prog');
    const track = h('div', 'kb-bar-track'); const fill = h('div', 'kb-bar');
    fill.style.width = (100 * (pct || 0)).toFixed(1) + '%'; track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(h('span', 'kb-bar-val', Math.round(100 * (pct || 0)) + '%' + (extra ? ' · ' + extra : '')));
    return row;
  };
  const ring = (frac, label) => {
    const r = h('div', 'kb-ring');
    r.style.setProperty('--p', String(Math.round(360 * Math.max(0, Math.min(1, frac)))));
    r.appendChild(h('span', null, label));
    return r;
  };

  const dash = h('div', 'kb-home');
  root.appendChild(dash);

  // ================================================================ top: hero + continue reading + recent
  const top = h('div', 'kb-top');
  dash.appendChild(top);
  {
    const hero = h('header', 'kb-hero');
    if (C.eyebrow) hero.appendChild(h('div', 'kb-eyebrow', C.eyebrow));
    hero.appendChild(h('h1', 'kb-title', C.title || ''));
    if (C.lede) hero.appendChild(h('p', 'kb-lede', C.lede));
    const stats = h('dl', 'kb-stats');
    const stat = (n, label) => { const d = h('div', 'kb-stat'); d.appendChild(h('dt', null, label)); d.appendChild(h('dd', null, String(n))); stats.appendChild(d); };
    stat(arts.length, t('stat_articles'));
    stat(t('stat_words_value', { n: (nWords / R.words_unit).toFixed(1) }), t('stat_words'));
    stat(nFig + ' / ' + nEq, t('stat_fig_eq'));
    stat(terms.length, t('stat_terms'));
    stat(lits.length, t('stat_literature'));
    stat(nPdf, t('stat_pdf'));
    hero.appendChild(stats);
    top.appendChild(hero);
  }
  const resumeSlot = h('div', 'kb-resume-slot');
  const recentSlot = h('div', 'kb-recent-slot');
  top.append(resumeSlot, recentSlot);

  const renderResume = () => {
    resumeSlot.replaceChildren(); recentSlot.replaceChildren();
    const rec = hasKb ? kb.getRecent(20).filter(e => byPath[e.path]) : [];
    const main = rec.find(e => byPath[e.path].type === T.article);
    const card = h('div', 'kb-resume');
    resumeSlot.appendChild(card);
    const head = h('div', 'kb-resume-head');
    card.appendChild(head);
    if (!main) {
      const a = arts[0];
      if (!a) return;
      card.classList.add(tone(a.series_no));
      head.appendChild(h('span', 'kb-label', hasKb ? t('start_here') : t('start_reading')));
      head.appendChild(h('span', 'kb-read', t('minutes_fmt', { n: minutes(a.words) })));
      card.appendChild(h('div', 'kb-kicker', kind(a)));
      card.appendChild(h('div', 'kb-resume-title', a.file.name));
      card.appendChild(h('p', 'kb-resume-at', hasKb ? t('no_history') : t('no_plugin')));
      const act = h('div', 'kb-resume-act');
      act.appendChild(button(t('start_button'), (evt) => open(a.file.path, evt), 'is-primary'));
      card.appendChild(act);
      card.addEventListener('click', (evt) => { if (evt.target === card) open(a.file.path, evt); });
      return;
    }
    const a = byPath[main.path];
    card.classList.add(tone(a.series_no), 'is-live');
    card.addEventListener('click', (evt) => resume(main.path, evt));
    head.appendChild(h('span', 'kb-label', t('continue_label')));
    head.appendChild(h('span', 'kb-read', ago(main.t)));
    card.appendChild(h('div', 'kb-kicker', kind(a)));
    card.appendChild(h('div', 'kb-resume-title', a.file.name));
    const at = h('p', 'kb-resume-at');
    at.appendChild(h('span', 'kb-pill', t('read_at')));
    at.append(' ' + where(main));
    card.appendChild(at);
    const left = Math.round((a.words || 0) * (1 - (main.pct || 0)) / R.words_per_minute);
    card.appendChild(progress(main.pct, left >= 1 ? t('left_fmt', { n: left }) : t('finished')));
    const act = h('div', 'kb-resume-act');
    act.appendChild(button(t('continue_button'), (evt) => resume(main.path, evt), 'is-primary'));
    const nxt = arts[(artIdx[main.path] ?? -2) + 1];
    if (nxt && (main.pct || 0) >= R.finished_at) {
      const b = button(t('next_fmt', { title: nxt.file.name }), (evt) => { evt.stopPropagation(); open(nxt.file.path, evt); }, 'is-quiet kb-next');
      b.title = nxt.file.name;
      act.appendChild(b);
    }
    card.appendChild(act);

    const others = rec.filter(e => e !== main).slice(0, 4);
    if (!others.length) return;
    const row = h('div', 'kb-recent-row');
    row.appendChild(h('div', 'kb-label kb-recent-label', t('recent')));
    for (const e of others) {
      const p = byPath[e.path];
      const c = h('div', 'kb-mini ' + tone(p.series_no));
      c.title = p.file.name + ' · ' + where(e);
      c.addEventListener('click', (evt) => resume(e.path, evt));
      const mm = h('div', 'kb-meta');
      mm.appendChild(h('span', 'kb-kicker', kind(p)));
      mm.appendChild(h('span', 'kb-read', ago(e.t)));
      c.appendChild(mm);
      c.appendChild(h('div', 'kb-mini-title', p.file.name));
      c.appendChild(h('div', 'kb-resume-at', where(e)));
      c.appendChild(progress(e.pct));
      row.appendChild(c);
    }
    recentSlot.appendChild(row);
  };

  // ================================================================ learning path: series cards + overview
  const pathSec = section(t('path_title'), t('path_sub', { n: seriesMaps.length }));
  const pathGrid = h('div', 'kb-path');
  pathSec.appendChild(pathGrid);
  dash.appendChild(pathSec);
  const renderPath = () => {
    pathGrid.replaceChildren();
    const rm = readMap();
    const done = arts.filter(a => status(rm, a.file.path) === 'done').length;
    const opened = arts.filter(a => status(rm, a.file.path) === 'open').length;
    const cur = hasKb ? (kb.getRecent(40).find(e => byPath[e.path] && byPath[e.path].type === T.article) || {}).path : null;

    // overview card
    const ov = h('div', 'kb-overview');
    const ovTop = h('div', 'kb-overview-top');
    ovTop.appendChild(ring(arts.length ? done / arts.length : 0, done + '/' + arts.length));
    const ovTxt = h('div', 'kb-overview-txt');
    ovTxt.appendChild(h('div', 'kb-series-title', t('progress_title')));
    ovTxt.appendChild(h('p', 'kb-series-q', hasKb ? t('progress_fmt', { done, open: opened }) : t('progress_no_plugin')));
    ovTop.appendChild(ovTxt);
    ov.appendChild(ovTop);
    const legend = h('div', 'kb-legend');
    for (const [cls, key] of [['done', 'legend_done'], ['open', 'legend_open'], ['new', 'legend_new']]) {
      const s = h('span'); s.appendChild(h('i', 'kb-st kb-st-' + cls)); s.append(t(key)); legend.appendChild(s);
    }
    ov.appendChild(legend);
    const left = arts.filter(a => status(rm, a.file.path) !== 'done').reduce((x, a) => x + (a.words || 0) * (1 - ((rm[a.file.path] || {}).pct || 0)), 0);
    const tot = h('dl', 'kb-overview-stats');
    for (const [k, v] of [[t('total'), t('total_fmt', { n: arts.length, words: words(nWords) })],
                          [t('remaining'), t('remaining_fmt', { h: Math.round(left / R.words_per_minute / 60 * 10) / 10 })]]) {
      const d = h('div'); d.appendChild(h('dt', null, k)); d.appendChild(h('dd', null, v)); tot.appendChild(d);
    }
    ov.appendChild(tot);
    const links = h('div', 'kb-overview-links');
    for (const n of (C.front_notes || [])) {
      const p = (F.series ? F.series + '/' : '') + n + '.md';
      if (front[n] || byPath[p]) links.appendChild(link(front[n] ? front[n].file.path : p, n, 'kb-chiplink'));
    }
    ov.appendChild(links);

    for (const s of seriesMaps) {
      const list = arts.filter(a => a.series_no === s.series_no);
      const card = h('div', 'kb-series ' + tone(s.series_no));
      const head = h('div', 'kb-series-head');
      head.appendChild(h('span', 'kb-series-no', String(s.series_no)));
      const ttl = h('div', 'kb-series-title'); ttl.appendChild(plink(s, s.title || s.file.name)); head.appendChild(ttl);
      const nd = list.filter(a => status(rm, a.file.path) === 'done').length;
      if (hasKb) head.appendChild(h('span', 'kb-series-count' + (nd === list.length && nd ? ' is-done' : ''), nd + '/' + list.length));
      card.appendChild(head);
      if (s.question) card.appendChild(h('p', 'kb-series-q', s.question));
      const ol = h('ol', 'kb-series-list');
      for (const a of list) {
        const li = h('li', a.file.path === cur ? 'is-current' : null);
        if (a.file.path === cur) li.title = t('current_title');
        const st = status(rm, a.file.path);
        li.appendChild(h('i', 'kb-st kb-st-' + st));
        li.appendChild(h('span', 'kb-num', String(a.seq).padStart(2, '0')));
        li.appendChild(plink(a, a.file.name));
        const e = rm[a.file.path];
        if (e && st === 'open' && e.pct > 0.02) li.appendChild(h('small', 'kb-pct', Math.round(100 * e.pct) + '%'));
        ol.appendChild(li);
      }
      card.appendChild(ol);
      const w = list.reduce((x, a) => x + (a.words || 0), 0);
      card.appendChild(h('div', 'kb-series-foot', t('series_foot_fmt', { n: list.length, words: words(w), min: minutes(w) })));
      pathGrid.appendChild(card);
    }
    pathGrid.appendChild(ov);
  };

  // ================================================================ library: articles / terms / literature
  {
    const sec = section(t('library_title'), t('library_sub'));
    const lib = h('div', 'kb-library');
    sec.appendChild(lib);
    const bar = h('div', 'kb-lib-bar');
    const tabs = h('div', 'kb-tabs');
    const input = h('input', 'kb-search'); input.type = 'search';
    bar.append(tabs, input);
    lib.appendChild(bar);
    const filters = h('div', 'kb-lib-filters');
    lib.appendChild(filters);
    const grid = h('div', 'kb-lib-grid');
    lib.appendChild(grid);
    const more = h('div', 'kb-more');
    lib.appendChild(more);

    const TABS = {
      art: { label: t('tab_articles'), n: arts.length, step: 6, ph: t('search_articles'), cls: 'is-art' },
      term: { label: t('tab_terms'), n: terms.length, step: 12, ph: t('search_terms'), cls: 'is-term' },
      lit: { label: t('tab_literature'), n: lits.length, step: 6, ph: t('search_literature'), cls: 'is-lit' },
    };
    let saved = null;
    try { saved = window.localStorage.getItem('kb-home-tab'); } catch (e) { }
    const state = { tab: TABS[saved] ? saved : 'art', s: 0, q: '', limit: 0, sort: 'cite', pdf: false };
    state.limit = TABS[state.tab].step;

    const chip = (parent, label, n, active, fn, cls) => {
      const b = h('button', 'kb-chip' + (cls ? ' ' + cls : '') + (active ? ' is-active' : ''));
      b.append(label); if (n != null) b.appendChild(h('span', 'kb-chip-n', String(n)));
      b.addEventListener('click', fn); parent.appendChild(b);
    };
    const reset = () => { state.limit = TABS[state.tab].step; render(); };

    const artCard = (a) => {
      const c = h('article', 'kb-card kb-article ' + tone(a.series_no));
      const m = h('div', 'kb-meta');
      m.appendChild(h('span', 'kb-kicker', kind(a)));
      m.appendChild(h('span', 'kb-read', t('minutes_fmt', { n: minutes(a.words) })));
      c.appendChild(m);
      const ttl = h('h3', 'kb-h3'); ttl.appendChild(plink(a, a.file.name)); c.appendChild(ttl);
      c.appendChild(h('p', 'kb-summary', a.summary || ''));
      const bits = [];
      if (a.figures) bits.push(t('card_figures', { n: a.figures }));
      if (a.equations) bits.push(t('card_equations', { n: a.equations }));
      if ((a.sources || []).length) bits.push(t('card_sources', { n: (a.sources || []).length }));
      if ((a.terms || []).length) bits.push(t('card_terms', { n: (a.terms || []).length }));
      c.appendChild(h('div', 'kb-foot', bits.join(' · ')));
      return c;
    };
    const termCard = (x) => {
      const c = h('article', 'kb-card kb-term ' + tone(x.series_no));
      const tp = h('div', 'kb-term-top');
      tp.appendChild(plink(x, x.term || x.file.name, 'kb-term-name'));
      if (x.abbr) tp.appendChild(h('span', 'kb-abbr', x.abbr));
      c.appendChild(tp);
      if (x.en) c.appendChild(h('div', 'kb-term-en', x.en));
      const d = h('div', 'kb-term-def'); md(d, x.definition || ''); c.appendChild(d);
      return c;
    };
    const litCard = (l) => {
      const c = h('article', 'kb-card kb-lit');
      const m = h('div', 'kb-meta');
      m.appendChild(h('span', 'kb-kicker', l.cite_as || `${l.first_author || ''} ${l.year || ''}`.trim()));
      if (lp(l.pdf)) m.appendChild(h('span', 'kb-badge', t('badge_pdf')));
      c.appendChild(m);
      const ttl = h('h3', 'kb-h3 kb-lit-title'); ttl.appendChild(plink(l, l.title || l.file.name)); c.appendChild(ttl);
      c.appendChild(h('p', 'kb-summary', [venue(l), l.kind].filter(Boolean).join(' · ')));
      c.appendChild(h('div', 'kb-foot', cc(l) ? t('cited_fmt', { n: cc(l) }) : t('not_cited')));
      return c;
    };

    const render = () => {
      const TB = TABS[state.tab];
      tabs.replaceChildren();
      for (const [k, v] of Object.entries(TABS)) {
        const b = h('button', 'kb-tab' + (k === state.tab ? ' is-active' : ''));
        b.append(v.label); b.appendChild(h('span', 'kb-chip-n', String(v.n)));
        b.addEventListener('click', () => {
          if (state.tab === k) return;
          state.tab = k; state.s = 0;
          try { window.localStorage.setItem('kb-home-tab', k); } catch (e) { }
          reset();
        });
        tabs.appendChild(b);
      }
      input.placeholder = TB.ph;
      grid.className = 'kb-lib-grid ' + TB.cls;

      filters.replaceChildren();
      const q = state.q.trim().toLowerCase();
      let list;
      if (state.tab === 'lit') {
        const sort = h('select', 'kb-select');
        for (const [v, key] of [['cite', 'sort_cite'], ['year', 'sort_year'], ['author', 'sort_author']]) {
          const o = h('option', null, t(key)); o.value = v; if (v === state.sort) o.selected = true; sort.appendChild(o);
        }
        sort.addEventListener('change', () => { state.sort = sort.value; reset(); });
        filters.appendChild(sort);
        chip(filters, t('only_pdf'), nPdf, state.pdf, () => { state.pdf = !state.pdf; reset(); });
        list = lits.filter(l => (!state.pdf || lp(l.pdf)) &&
          (!q || [l.title, l.first_author, venue(l), l.citekey, l.cite_as, ...(l.authors || [])].join(' ').toLowerCase().includes(q)));
        const key = { cite: (a, b) => cc(b) - cc(a) || (b.year || 0) - (a.year || 0), year: (a, b) => (b.year || 0) - (a.year || 0),
          author: (a, b) => String(a.first_author).localeCompare(String(b.first_author), R.locale) }[state.sort];
        list = [...list].sort(key);
      } else {
        const src = state.tab === 'art' ? arts : terms;
        chip(filters, t('all'), src.length, state.s === 0, () => { state.s = 0; reset(); });
        for (const s of seriesMaps) {
          const n = src.filter(x => x.series_no === s.series_no).length;
          if (n) chip(filters, s.title || s.file.name, n, state.s === s.series_no, () => { state.s = state.s === s.series_no ? 0 : s.series_no; reset(); }, tone(s.series_no));
        }
        list = state.tab === 'art'
          ? arts.filter(a => (!state.s || a.series_no === state.s) && (!q || [a.file.name, a.summary, ...(a.sections || [])].join(' ').toLowerCase().includes(q)))
          : terms.filter(x => (!state.s || x.series_no === state.s) && (!q || [x.term, x.file.name, x.en, x.abbr, ...(x.aliases || [])].join(' ').toLowerCase().includes(q)));
      }

      grid.replaceChildren();
      const mk = state.tab === 'art' ? artCard : state.tab === 'term' ? termCard : litCard;
      for (const x of list.slice(0, state.limit)) grid.appendChild(mk(x));
      if (!list.length) grid.appendChild(h('p', 'kb-empty', t('empty_fmt', { label: TB.label })));

      more.replaceChildren();
      if (list.length > TB.step) {
        more.appendChild(h('span', 'kb-count', t('count_fmt', { shown: Math.min(state.limit, list.length), total: list.length })));
        if (list.length > state.limit) {
          more.appendChild(button(t('more_fmt', { n: TB.step }), () => { state.limit += TB.step; render(); }));
          more.appendChild(button(t('expand_all'), () => { state.limit = Infinity; render(); }, 'is-quiet'));
        }
        if (state.limit > TB.step) more.appendChild(button(t('collapse'), () => { state.limit = TB.step; render(); sec.scrollIntoView({ block: 'start' }); }, 'is-quiet'));
      }
    };
    input.addEventListener('input', () => { state.q = input.value; reset(); });
    render();
    dash.appendChild(sec);
  }

  // ================================================================ live refresh of reading state
  renderResume();
  renderPath();
  let timer = 0;
  const later = () => { window.clearTimeout(timer); timer = window.setTimeout(() => { renderResume(); renderPath(); }, 500); };
  if (hasKb && dv.component && typeof dv.component.registerEvent === 'function') {
    dv.component.registerEvent(app.workspace.on('kb-reading:changed', later));
    // Refresh again when the user switches back to Home, so the latest reading state is shown.
    dv.component.registerEvent(app.workspace.on('active-leaf-change', (leaf) => {
      if (leaf && leaf.view && leaf.view.file && leaf.view.file.path === here) later();
    }));
  }
};

kbHome().catch((err) => {
  const pre = document.createElement('pre');
  pre.textContent = 'Home dashboard error: ' + (err && err.stack || err);
  dv.container.appendChild(pre);
});
