// Markdown pipeline of the preview harness: an approximation of Obsidian's reading view for the
// syntax this vault uses. markdown-it renders CommonMark (with Obsidian's default soft line breaks),
// KaTeX renders $…$ / $$…$$ (Obsidian itself uses MathJax), and this file adds the Obsidian-only parts:
// callouts (> [!kind] Title), wiki links, image embeds ![[file.png|720]], ==highlights==, %%comments%%,
// hidden block ids (^id) and the two Dataview query shapes used by term and literature notes.
// Used by note.html and by dv.el() in dv-shim.js. Not used by Obsidian.
(function () {
  const D = window.KB_DATA;
  const md = window.markdownit({ html: true, breaks: true, linkify: false, typographer: false });
  const byName = {};
  const byBase = {};
  for (const f of D.files) {
    const base = f.split('/').pop();
    if (!(base in byBase)) byBase[base] = f;
    if (f.endsWith('.md')) { const n = base.slice(0, -3); if (!(n in byName)) byName[n] = f; }
  }
  const pageByPath = Object.fromEntries(D.pages.map(p => [p.file.path, p]));
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const resolve = (t) => byName[t] || byName[t.replace(/\.md$/, '')] || byBase[t] || null;
  const noteUrl = (path, sub) => 'note.html?n=' + encodeURIComponent(path) + (sub ? '#' + encodeURIComponent(sub) : '') +
    (window.KB_THEME === 'dark' ? '&theme=dark' : '');
  const assetUrl = (path) => '../../' + path.split('/').map(encodeURIComponent).join('/');

  function katex(tex, display) {
    try {
      return window.katex.renderToString(tex, { displayMode: display, throwOnError: false, output: 'html', strict: 'ignore' });
    } catch (e) {
      return '<code>' + esc(tex) + '</code>';
    }
  }

  // Obsidian link text: [[Note#Heading|Alias]]; without alias it shows "Note > Heading".
  function wikiLink(inner) {
    const raw = inner.replace(/\\\|/g, '|');
    const bar = raw.indexOf('|');
    const target = bar >= 0 ? raw.slice(0, bar) : raw;
    let alias = bar >= 0 ? raw.slice(bar + 1) : null;
    const hash = target.indexOf('#');
    const note = (hash >= 0 ? target.slice(0, hash) : target).trim();
    const sub = hash >= 0 ? target.slice(hash + 1).trim() : '';
    const path = note ? resolve(note) : (window.KB_CURRENT || '');
    if (alias == null) alias = (note || '') + (sub ? (note ? ' > ' : '') + sub.replace(/^\^/, '') : '');
    const cls = 'internal-link' + (path ? '' : ' is-unresolved');
    return '<a class="' + cls + '" data-href="' + esc(target) + '" href="' + (path ? esc(noteUrl(path, sub)) : '#') + '">' + esc(alias) + '</a>';
  }

  function embed(inner) {
    const [target, opt] = inner.split('|');
    const path = resolve(target.trim());
    if (!path) return '<span class="internal-embed is-unresolved">' + esc(target) + '</span>';
    if (/\.(png|jpe?g|gif|svg|webp)$/i.test(path)) {
      const w = opt && /^\d+$/.test(opt.trim()) ? ' width="' + opt.trim() + '"' : '';
      return '<span class="internal-embed media-embed image-embed is-loaded" src="' + esc(target) + '"' + w + '>' +
        '<img src="' + esc(assetUrl(path)) + '" alt="' + esc(target) + '"' + w + '></span>';
    }
    return wikiLink(inner);
  }

  // Inline transforms on text that has already had its math and code protected.
  function inlineSyntax(s) {
    return s
      .replace(/!\[\[([^\]\n]+?)\]\]/g, (m, x) => embed(x))
      .replace(/\[\[([^\]\n]+?)\]\]/g, (m, x) => wikiLink(x))
      .replace(/==(?=\S)([^=\n]+?)==/g, '<mark>$1</mark>');
  }

  // Protect math and inline code with placeholders, transform, render, restore.
  function protect(src, store) {
    src = src.replace(/`[^`\n]+`/g, (m) => { store.push({ html: md.renderInline(m) }); return '@@P' + (store.length - 1) + '@@'; });
    src = src.replace(/\$\$([\s\S]+?)\$\$/g, (m, tex) => {
      store.push({ html: '<div class="math math-block is-loaded">' + katex(tex.trim(), true) + '</div>', block: true });
      return '\n\n@@P' + (store.length - 1) + '@@\n\n';
    });
    src = src.replace(/\$(?=\S)([^$\n]+?)(?<=\S)\$/g, (m, tex) => {
      store.push({ html: '<span class="math math-inline is-loaded">' + katex(tex, false) + '</span>' });
      return '@@P' + (store.length - 1) + '@@';
    });
    return src;
  }
  function restore(html, store) {
    for (let k = 0; k < 3; k++) {
      html = html.replace(/<p>@@P(\d+)@@<\/p>\n?/g, (m, i) => store[+i].html)
        .replace(/@@P(\d+)@@/g, (m, i) => store[+i].html);
    }
    return html;
  }

  function renderInline(src) {
    const store = [];
    return restore(md.renderInline(inlineSyntax(protect(src, store))), store);
  }

  // Dataview: only the two query shapes the vault's term and literature notes use.
  function dataview(query, ctx) {
    const cur = ctx.path;
    const q = query.replace(/\s+/g, ' ').trim();
    const arts = D.pages.filter(p => p.type === (D.config.types || {}).article && p.file.outlinks.some(l => l.path === cur))
      .sort((a, b) => (a.seq || 0) - (b.seq || 0));
    const link = (p) => '<a class="internal-link" href="' + esc(noteUrl(p.file.path)) + '">' + esc(p.file.name) + '</a>';
    if (/^LIST summary FROM \[\[\]\]/.test(q)) {
      if (!arts.length) return '<div class="dataview dataview-error-box"><p class="dataview dataview-error-message">Dataview: No results to show for list query.</p></div>';
      return '<ul class="dataview list-view-ul">' + arts.map(p => '<li><span>' + link(p) + ': ' + renderInline(p.summary || '') + '</span></li>').join('') + '</ul>';
    }
    if (/^TABLE WITHOUT ID file\.link AS "Article", summary AS "Summary" FROM \[\[\]\]/.test(q)) {
      return '<div class="table-wrapper"><table class="dataview table-view-table"><thead><tr><th>Article</th><th>Summary</th></tr></thead><tbody>' +
        arts.map(p => '<tr><td>' + link(p) + '</td><td>' + renderInline(p.summary || '') + '</td></tr>').join('') + '</tbody></table></div>';
    }
    return '<pre><code>' + esc(query) + '</code></pre>';
  }

  function callout(kind, fold, title, body, ctx) {
    const k = kind.toLowerCase();
    const t = title.trim() || (k.charAt(0).toUpperCase() + k.slice(1));
    return '<div data-callout-metadata="" data-callout-fold="' + esc(fold) + '" data-callout="' + esc(k) + '" class="callout">' +
      '<div class="callout-title" dir="auto"><div class="callout-icon"></div><div class="callout-title-inner">' + renderInline(t) + '</div></div>' +
      '<div class="callout-content">' + renderMarkdown(body, ctx) + '</div></div>';
  }

  // Block level: fences and callouts first (recursively), then markdown-it on the rest.
  function renderMarkdown(src, ctx) {
    ctx = ctx || {};
    const blocks = [];
    const hold = (html) => { blocks.push(html); return '@@B' + (blocks.length - 1) + '@@'; };
    src = src.replace(/\r\n/g, '\n').replace(/%%[\s\S]*?%%/g, '');
    const lines = src.split('\n');
    const out = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const fence = line.match(/^(\s*)(```+|~~~+)\s*([\w-]*)/);
      if (fence) {
        const buf = [];
        let j = i + 1;
        while (j < lines.length && !lines[j].trim().startsWith(fence[2])) buf.push(lines[j++]);
        i = j;
        const lang = fence[3];
        if (lang === 'dataview') out.push('', hold(dataview(buf.join('\n'), ctx)), '');
        else if (lang === 'dataviewjs') out.push('', hold(ctx.dataviewjs ? ctx.dataviewjs(buf.join('\n')) : ''), '');
        else out.push('', hold('<pre><code>' + esc(buf.join('\n')) + '</code></pre>'), '');
        continue;
      }
      const co = line.match(/^>\s?\[!([\w-]+)\]([+-]?)\s*(.*)$/);
      if (co) {
        const body = [];
        let j = i + 1;
        while (j < lines.length && /^>/.test(lines[j])) body.push(lines[j++].replace(/^> ?/, ''));
        i = j - 1;
        out.push('', hold(callout(co[1], co[2], co[3], body.join('\n'), ctx)), '');
        continue;
      }
      if (/^\s*\^[\w-]+\s*$/.test(line)) continue;           // block id on its own line
      out.push(line.replace(/\s+\^[\w-]+\s*$/, ''));        // trailing block id
    }
    const store = [];
    let text = inlineSyntax(protect(out.join('\n'), store));
    let html = md.render(text);
    html = restore(html, store);
    html = html.replace(/<p>@@B(\d+)@@<\/p>\n?/g, (m, i) => blocks[+i]).replace(/@@B(\d+)@@/g, (m, i) => blocks[+i]);
    html = html.replace(/<table>/g, '<div class="table-wrapper"><table>').replace(/<\/table>/g, '</table></div>');
    return html;
  }

  // Lucide icons (ISC licence) for the callout icon names that the vault's CSS assigns via --callout-icon.
  const ICONS = {
    'lucide-book-marked': '<path d="M10 2v8l3-3 3 3V2"/><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    'lucide-bookmark-check': '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z"/><path d="m9 10 2 2 4-4"/>',
    'lucide-star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'lucide-sigma': '<path d="M18 7V5a1 1 0 0 0-1-1H6.5a.5.5 0 0 0-.4.8l4.5 6a2 2 0 0 1 0 2.4l-4.5 6a.5.5 0 0 0 .4.8H17a1 1 0 0 0 1-1v-2"/>',
    'lucide-lightbulb': '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    'lucide-triangle-alert': '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    'lucide-check-check': '<path d="M18 6 7 17l-5-5"/><path d="m22 10-7.5 7.5L13 16"/>',
    'lucide-route': '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    'lucide-book-open': '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    'lucide-scroll-text': '<path d="M15 12h-5"/><path d="M15 8h-5"/><path d="M19 17V5a2 2 0 0 0-2-2H4"/><path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3"/>',
    'lucide-info': '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    'lucide-help-circle': '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    'lucide-pencil': '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
    'lucide-image': '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  };
  function decorate(root) {
    for (const c of root.querySelectorAll('.callout')) {
      const icon = c.querySelector(':scope > .callout-title > .callout-icon');
      if (!icon || icon.firstChild) continue;
      const name = getComputedStyle(c).getPropertyValue('--callout-icon').trim();
      const body = ICONS[name] || ICONS['lucide-pencil'];
      icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="svg-icon">' + body + '</svg>';
    }
    for (const h of root.querySelectorAll('h1,h2,h3,h4,h5,h6')) if (!h.id) h.id = h.textContent.trim();
  }

  window.KBR = { renderMarkdown, renderInline, decorate, noteUrl, pageByPath, resolve };
})();
