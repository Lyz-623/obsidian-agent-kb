// Minimal stand-in for the Dataview and Obsidian APIs that 90 System/home/view.js calls, so the real,
// unmodified view.js can run in a plain browser page (home.html). Only what view.js touches exists:
//   dv.app, dv.container, dv.current(), dv.pages() -> DataArray (.where / .sort / .array),
//   dv.el(tag, markdown, {cls}), dv.component.registerEvent
//   app.vault.adapter.list / exists / read (for kb.config.json), app.vault.getAbstractFileByPath,
//   app.workspace.openLinkText / trigger / on, app.plugins.plugins['kb-open-home'] (getRecent / resume).
// The kb-open-home entry is FAKE: it returns a fixed, invented reading history (below) so that the
// "Continue reading" card, the recent row and the read-status dots have something to show.
(function () {
  const D = window.KB_DATA;
  const HOME = D.config.home || 'Home.md';
  const NOW = Date.now();
  const MIN = 60000;

  // ------------------------------------------------------------ DataArray (subset)
  const cmp = (a, b) => (a == null && b == null) ? 0 : a == null ? -1 : b == null ? 1 : a < b ? -1 : a > b ? 1 : 0;
  class DataArray {
    constructor(values) { this.values = values; }
    where(fn) { return new DataArray(this.values.filter(fn)); }
    filter(fn) { return this.where(fn); }
    map(fn) { return new DataArray(this.values.map(fn)); }
    sort(key, dir) {
      const s = dir === 'desc' ? -1 : 1;
      return new DataArray([...this.values].sort((a, b) => s * cmp(key(a), key(b))));
    }
    array() { return [...this.values]; }
    get length() { return this.values.length; }
    [Symbol.iterator]() { return this.values[Symbol.iterator](); }
  }

  // Link values: Dataview Link objects expose .path; toString gives the wiki-link form.
  const asLink = (v) => (v && typeof v === 'object' && !Array.isArray(v) && 'path' in v)
    ? Object.assign(Object.create({ toString() { return '[[' + this.path.replace(/\.md$/, '') + ']]'; } }), v) : v;
  const pages = D.pages.map(p => {
    const o = {};
    for (const [k, v] of Object.entries(p)) o[k] = Array.isArray(v) ? v.map(asLink) : asLink(v);
    o.file = Object.assign({}, p.file, { link: asLink({ path: p.file.path }) });
    return o;
  });
  const byPath = Object.fromEntries(pages.map(p => [p.file.path, p]));

  // ------------------------------------------------------------ fake reading history (kb-open-home)
  // Invented for the screenshots: one article finished, one in progress, two other notes opened.
  const first = (type, seq) => pages.find(p => p.type === type && (seq == null || p.seq === seq));
  const T = D.config.types || {};
  const history = [
    [first(T.article, 2), { heading: 'Sharpness and the quality factor', line: 96, pct: 0.58, t: NOW - 25 * MIN }],
    [pages.find(p => p.file.name === 'Quality factor'), { heading: '', line: 0, pct: 1, t: NOW - 140 * MIN }],
    [first(T.literature), { heading: 'Reading notes', line: 14, pct: 0.45, t: NOW - 26 * 60 * MIN }],
    [first(T.article, 1), { heading: 'The quality factor', line: 170, pct: 0.97, t: NOW - 28 * 60 * MIN }],
    [first(T.series), { heading: '', line: 0, pct: 1, t: NOW - 50 * 60 * MIN }],
  ].filter(([p]) => p).map(([p, e]) => Object.assign({ path: p.file.path }, e));

  const go = (path) => { window.location.href = window.KBR.noteUrl(path); };
  const kbOpenHome = {
    getRecent(n) { return history.slice().sort((a, b) => b.t - a.t).slice(0, n || 40).map(e => Object.assign({}, e)); },
    resume(path) { go(path || history[0].path); },
  };

  // ------------------------------------------------------------ app
  const files = new Set(D.files);
  const app = {
    vault: {
      adapter: {
        list: async () => ({ folders: D.topFolders.slice(), files: D.files.filter(f => !f.includes('/')) }),
        exists: async (p) => files.has(p),
        read: async (p) => {
          if (p === D.configPath) return JSON.stringify(D.config);
          if (D.notes[p] != null) return D.notes[p];
          throw new Error('not available in the preview: ' + p);
        },
      },
      getAbstractFileByPath: (p) => files.has(p) ? { path: p } : null,
    },
    workspace: {
      openLinkText: (path) => go(byPath[path] ? path : (window.KBR.resolve(path) || path)),
      trigger: () => {},
      on: () => ({}),
    },
    plugins: { plugins: { 'kb-open-home': kbOpenHome } },
  };

  const container = document.getElementById('dv-container');
  window.dv = {
    app,
    container,
    component: { registerEvent: () => {} },
    current: () => byPath[HOME],
    pages: () => new DataArray(pages.slice()),
    // Dataview renders the markdown into a new element appended to dv.container.
    el: (tag, text, opts) => {
      const el = document.createElement(tag);
      if (opts && opts.cls) el.className = opts.cls;
      el.innerHTML = window.KBR.renderInline(String(text));
      container.appendChild(el);
      return el;
    },
  };
  // view.js tries require('obsidian') as a fallback renderer; it is not available here.
  window.require = (m) => { throw new Error('module not available in the preview: ' + m); };
})();
