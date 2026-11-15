// Small local plugin for an agent-maintained knowledge base:
// 1. Opens the home note at startup; adds an "Open home" command and ribbon button.
// 2. Records the reading position: while you scroll a note it remembers the top line, the current
//    section and the progress, stored in this plugin's data.json. The "Continue reading" command,
//    the ribbon button and the home dashboard use it to jump back to where you stopped.
// Folder names, the home note and every user-visible string come from <system folder>/kb.config.json
// (the first `*/kb.config.json` one level below the vault root).
const { Plugin, MarkdownView, TFile, Notice, debounce } = require('obsidian');
const MAX = 40;          // how many notes keep a remembered position
const SETTLE_MS = 1200;  // scrolls within this time after opening a note are programmatic and ignored
const DEFAULT_CONFIG = {
  home: 'Home.md',
  folders: { series: '10 Series', articles: '20 Articles', terms: '30 Terms', literature: '40 Literature' },
  ui: {},
};
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

module.exports = class KbOpenHome extends Plugin {
  async onload() {
    this.data = Object.assign({ positions: {} }, (await this.loadData()) || {});
    await this.loadConfig();
    this.openedAt = 0;
    this.saveSoon = debounce(() => this.saveData(this.data), 1500, true);
    this.captureSoon = debounce((target) => this.guard('scroll', () => this.capture(target)), 400, true);

    this.addCommand({ id: 'open-home', name: this.t('plugin_open_home'), callback: () => this.openHome(false) });
    this.addRibbonIcon('home', this.t('plugin_open_home'), () => this.openHome(false));
    this.addCommand({ id: 'resume-reading', name: this.t('plugin_resume'), callback: () => this.resume() });
    this.addRibbonIcon('book-open', this.t('plugin_resume_ribbon'), () => this.resume());
    this.addCommand({ id: 'reading-diagnose', name: this.t('plugin_diagnose'), callback: () => this.diagnose() });

    this.registerDomEvent(document, 'scroll', (evt) => this.captureSoon(evt.target), { capture: true, passive: true });
    // Fallback: check the active note's position every 2 s, independent of scroll events reaching document.
    this.registerInterval(window.setInterval(() => this.guard('interval', () => this.capture(null)), 2000));
    this.registerEvent(this.app.workspace.on('file-open', (file) => this.guard('open', () => this.onOpen(file))));
    this.registerEvent(this.app.workspace.on('quit', () => { this.guard('quit', () => this.capture(null)); this.saveData(this.data); }));
    this.registerEvent(this.app.vault.on('rename', (file, oldPath) => this.guard('rename', () => this.onRename(file, oldPath))));
    this.registerEvent(this.app.vault.on('delete', (file) => this.guard('delete', () => this.onDelete(file))));
    // Re-read the config when it changes (command names keep their startup language until reload).
    this.registerEvent(this.app.vault.on('modify', (file) => { if (file && file.path === this.configPath) this.loadConfig(); }));
    this.app.workspace.onLayoutReady(() => { this.guard('seed', () => this.seedFromHistory()); this.openHome(true); });
  }

  // ------------------------------------------------------------ config
  async findConfig() {
    const adapter = this.app.vault.adapter;
    try {
      const top = await adapter.list('/');
      for (const f of (top.folders || []).sort()) {
        const p = f.replace(/^\/+/, '') + '/kb.config.json';
        if (await adapter.exists(p)) return p;
      }
    } catch (_) { /* ignore */ }
    return null;
  }

  async loadConfig() {
    let cfg = null;
    try {
      this.configPath = await this.findConfig();
      if (this.configPath) cfg = JSON.parse(await this.app.vault.adapter.read(this.configPath));
    } catch (err) {
      console.error('[kb-open-home] cannot read kb.config.json', err);
    }
    cfg = cfg || {};
    this.config = Object.assign({}, DEFAULT_CONFIG, cfg);
    const F = Object.assign({}, DEFAULT_CONFIG.folders, cfg.folders || {});
    this.home = this.config.home || DEFAULT_CONFIG.home;
    this.articlesPrefix = F.articles + '/';
    const tracked = [F.series, F.articles, F.terms, F.literature].filter(Boolean).map(escapeRe);
    this.track = new RegExp('^(' + tracked.join('|') + ')/');
    this.ui = this.config.ui || {};
  }

  // UI string from kb.config.json with {placeholders} filled; a missing key shows its own name.
  t(key, vars) {
    const s = this.ui && this.ui[key] != null ? this.ui[key] : key;
    return String(s).replace(/\{(\w+)\}/g, (m, k) => (vars && vars[k] != null) ? String(vars[k]) : m);
  }

  isTracked(path) { return !!path && this.track.test(path); }

  // On error, keep the latest error in data.json (field `diag`) for troubleshooting.
  guard(where, fn) {
    try { return fn(); } catch (err) {
      console.error('[kb-open-home]', where, err);
      this.data.diag = { where, error: String(err && err.stack || err).slice(0, 600), at: new Date().toISOString() };
      this.saveSoon();
    }
  }

  diagnose() {
    const view = this.app.workspace.getActiveViewOfType(MarkdownView);
    const lines = [
      this.t('plugin_diag_tracked', { n: Object.keys(this.data.positions).length }),
      this.t('plugin_diag_current', { path: view && view.file ? view.file.path : this.t('plugin_none') }),
      this.t('plugin_diag_line', { line: view ? this.readLine(view) : '-', mode: view ? view.getMode() : '-' }),
      this.t('plugin_diag_is_tracked', { yes: view && view.file && this.isTracked(view.file.path) ? this.t('plugin_yes') : this.t('plugin_no') }),
      this.t('plugin_diag_error', { error: this.data.diag ? this.data.diag.where + ' · ' + this.data.diag.error.split('\n')[0] : this.t('plugin_none') }),
    ];
    new Notice(lines.join('\n'), 12000);
  }

  // First run has no records: seed them from Obsidian's own "recently opened" list (position = top).
  seedFromHistory() {
    if (Object.keys(this.data.positions).length) return;
    let recent = [];
    try { recent = this.app.workspace.getLastOpenFiles() || []; } catch (_) { return; }
    const now = Date.now();
    recent.filter(p => this.isTracked(p) && p.endsWith('.md') && this.app.vault.getAbstractFileByPath(p) instanceof TFile)
      .forEach((p, i) => { this.data.positions[p] = { line: 0, heading: '', pct: 0, t: now - (i + 1) * 60000, seeded: true }; });
    if (Object.keys(this.data.positions).length) this.changed();
  }

  onunload() { this.saveData(this.data); }

  async openHome(startup) {
    const file = this.app.vault.getAbstractFileByPath(this.home);
    if (!file) return;
    const existing = this.app.workspace.getLeavesOfType('markdown')
      .find(l => l.view && l.view.file && l.view.file.path === this.home);
    if (existing) { this.app.workspace.setActiveLeaf(existing, { focus: true }); return; }
    // At startup reuse the current tab; when opened by hand use a new tab.
    const leaf = this.app.workspace.getLeaf(startup ? false : 'tab');
    await leaf.openFile(file, { active: true });
  }

  // ------------------------------------------------------------ reading position
  // Opening a note counts as "recently read": new notes get a record at once; notes read before only
  // update their time and keep the remembered position.
  onOpen(file) {
    this.openedAt = Date.now();
    this.openPath = file ? file.path : null;
    this.openLine = null;
    if (!file || !this.isTracked(file.path)) return;
    const e = this.data.positions[file.path];
    if (e) e.t = this.stamp();
    else this.data.positions[file.path] = { line: 0, heading: '', pct: 0, t: this.stamp() };
    this.changed();
    // A note read before and reopened normally (landing at the top): offer to jump back.
    if (e && e.line > 3 && (e.pct || 0) < 0.97 && this.resuming !== file.path) {
      const path = file.path, saved = Object.assign({}, e);
      window.setTimeout(() => this.guard('prompt', () => {
        const v = this.app.workspace.getActiveViewOfType(MarkdownView);
        if (!v || !v.file || v.file.path !== path) return;
        const cur = this.readLine(v);
        if (cur == null || cur > 2) return;   // opened via a heading link, or already elsewhere: stay quiet
        this.promptResume(path, saved);
      }), 700);
    }
  }

  promptResume(path, e) {
    const frag = document.createDocumentFragment();
    const where = e.heading ? this.t('plugin_at_heading', { heading: e.heading }) : this.t('plugin_at_line', { n: Math.round(e.line) });
    const t = document.createElement('div');
    t.textContent = this.t('plugin_last_read', { where, pct: Math.round(100 * (e.pct || 0)) });
    const b = document.createElement('div');
    b.textContent = this.t('plugin_jump_back');
    b.style.cssText = 'margin-top:4px;font-weight:600;color:var(--text-accent);';
    frag.append(t, b);
    const n = new Notice(frag, 8000);
    const el = n.noticeEl || n.messageEl;
    if (el) { el.style.cursor = 'pointer'; el.addEventListener('click', () => this.resume(path)); }
  }

  readLine(view) {
    let line = null;
    try { const st = view.getEphemeralState(); if (st && typeof st.scroll === 'number') line = st.scroll; } catch (_) { /* ignore */ }
    if (line == null) { try { line = view.currentMode.getScroll(); } catch (_) { /* ignore */ } }
    if (line == null) { try { line = view.previewMode.getScroll(); } catch (_) { /* ignore */ } }
    return (typeof line === 'number' && line >= 0) ? Math.round(line * 10) / 10 : null;
  }

  capture(target) {
    const view = this.app.workspace.getActiveViewOfType(MarkdownView);
    if (!view || !view.file || !this.isTracked(view.file.path)) return;
    if (target && target.nodeType === 1 && !view.containerEl.contains(target)) return;
    const line = this.readLine(view);
    if (line == null) return;
    const path = view.file.path;
    // The position right after opening (top, or the section a link pointed to) is the baseline;
    // the stored position is overwritten only after the reader actually moves.
    if (Date.now() - this.openedAt < SETTLE_MS) return;
    if (this.openPath !== path || this.openLine == null) { this.openPath = path; this.openLine = line; }
    const old = this.data.positions[path];
    const moved = Math.abs(line - this.openLine) >= 1;
    if (old && old.line > 0 && !moved) return;          // reopened but not read further: keep old position
    if (old && Math.abs(old.line - line) < 0.5) return;  // unchanged: do not rewrite

    const cache = this.app.metadataCache.getFileCache(view.file) || {};
    const heads = (cache.headings || []).filter(h => h.level >= 2 && h.level <= 3);
    let heading = '';
    for (const h of heads) { if (h.position.start.line <= line + 2) heading = h.heading; else break; }
    const sections = cache.sections || [];
    const total = sections.length ? sections[sections.length - 1].position.end.line : 0;
    let pct = total ? line / total : 0;
    try {
      const scroller = view.containerEl.querySelector(view.getMode() === 'preview' ? '.markdown-preview-view' : '.cm-scroller');
      if (scroller && scroller.scrollHeight > scroller.clientHeight + 4) pct = scroller.scrollTop / (scroller.scrollHeight - scroller.clientHeight);
    } catch (_) { /* keep line-based estimate */ }
    pct = Math.max(0, Math.min(1, pct));

    this.data.positions[view.file.path] = { line, heading, pct: Math.round(pct * 1000) / 1000, t: this.stamp() };
    this.changed();
  }

  // Monotonic timestamp: two records within the same millisecond still have an order.
  stamp() { this.lastT = Math.max(Date.now(), (this.lastT || 0) + 1); return this.lastT; }

  changed() {
    const keep = Object.entries(this.data.positions).sort((a, b) => b[1].t - a[1].t).slice(0, MAX);
    this.data.positions = Object.fromEntries(keep);
    this.saveSoon();
    this.app.workspace.trigger('kb-reading:changed');
  }

  onRename(file, oldPath) {
    const e = this.data.positions[oldPath];
    if (!e) return;
    delete this.data.positions[oldPath];
    if (this.isTracked(file.path)) this.data.positions[file.path] = e;
    this.changed();
  }

  onDelete(file) {
    if (!this.data.positions[file.path]) return;
    delete this.data.positions[file.path];
    this.changed();
  }

  // Recently read notes, newest first; only files that still exist.
  getRecent(n) {
    return Object.entries(this.data.positions)
      .filter(([p]) => this.app.vault.getAbstractFileByPath(p) instanceof TFile)
      .sort((a, b) => b[1].t - a[1].t).slice(0, n || MAX)
      .map(([path, e]) => Object.assign({ path }, e));
  }

  // Open `path` (default: the most recently read article) and scroll to the remembered position.
  async resume(path, newTab) {
    if (!path) {
      const last = this.getRecent().find(e => e.path.startsWith(this.articlesPrefix)) || this.getRecent(1)[0];
      if (!last) { new Notice(this.t('plugin_no_history')); return; }
      path = last.path;
    }
    const file = this.app.vault.getAbstractFileByPath(path);
    if (!(file instanceof TFile)) { new Notice(this.t('plugin_not_found', { path })); return; }
    const e = this.data.positions[path] || { line: 0 };
    const existing = this.app.workspace.getLeavesOfType('markdown').find(l => l.view && l.view.file && l.view.file.path === path);
    const leaf = existing || this.app.workspace.getLeaf(newTab ? 'tab' : false);
    this.resuming = path;
    window.setTimeout(() => { if (this.resuming === path) this.resuming = null; }, 1500);
    await leaf.openFile(file, { active: true, eState: { scroll: e.line } });
    this.openedAt = Date.now();
    // Reading view renders lazily: position once more shortly after, so it lands on the stored line.
    for (const ms of [150, 600]) {
      window.setTimeout(() => {
        const v = leaf.view;
        if (v instanceof MarkdownView && v.file && v.file.path === path) {
          try { v.setEphemeralState({ scroll: e.line }); } catch (_) { /* ignore */ }
          this.openedAt = Date.now();
        }
      }, ms);
    }
  }
};
