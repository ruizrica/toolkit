const { getMermaidNormalizationBrowserScript } = require("./mermaid-normalization.js");

function generateSpecViewerHtml(opts) {
  const { documents, title, port, existingComments = [] } = opts;
  const escapedDocs = JSON.stringify(documents).replace(/<\//g, '<\\/');
  const escapedComments = JSON.stringify(existingComments).replace(/<\//g, '<\\/');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} — Spec Viewer</title>
<style>
  :root {
    --bg: #1a1d23;
    --surface: #1e2228;
    --surface2: #252a32;
    --border: #2e343e;
    --text: #e2e8f0;
    --text-muted: #8892a0;
    --text-dim: #555d6e;
    --accent: #2980b9;
    --accent-dim: rgba(41, 128, 185, 0.12);
    --success: #48d889;
    --warning: #f0b429;
    --warning-bg: rgba(240, 180, 41, 0.08);
    --comment-accent: var(--accent);
    --comment-dim: var(--accent-dim);
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    --mono: "SF Mono", "Fira Code", "JetBrains Mono", Consolas, monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { height: 100%; }
  body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 15px; line-height: 1.65; height: 100%; display: flex; flex-direction: column; overflow: hidden; }
  .header { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 6px; margin: 12px 16px 0; padding: 14px 20px; display: flex; align-items: center; gap: 14px; flex-shrink: 0; }
  .header .badge { background: transparent; color: var(--accent); font-size: 11px; font-weight: 700; padding: 3px 10px; border: 1px solid var(--accent); border-radius: 4px; text-transform: uppercase; letter-spacing: 1px; font-family: var(--mono); }
  .header .title { font-size: 15px; font-weight: 600; color: var(--text); flex: 1; }
  .header .comment-count { font-size: 12px; font-family: var(--mono); color: var(--comment-accent); display: none; }
  .header .comment-count.has-comments { display: inline; }
  .header .modified-badge { font-size: 10px; font-family: var(--mono); font-weight: 600; color: var(--warning); border: 1px solid var(--warning); padding: 2px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; display: none; }
  .step-bar { display: flex; align-items: center; gap: 4px; margin: 8px 16px 0; padding: 6px 8px; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; flex-shrink: 0; overflow-x: auto; }
  .step-bar.single-doc { display: none; }
  .step-item { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; font-family: var(--mono); font-weight: 500; color: var(--text-dim); transition: all 0.15s; white-space: nowrap; border: 1px solid transparent; position: relative; }
  .step-item.active { color: var(--accent); background: var(--accent-dim); border-color: var(--accent); }
  .step-num { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: 700; border: 1.5px solid var(--text-dim); color: var(--text-dim); flex-shrink: 0; }
  .step-item.active .step-num { border-color: var(--accent); color: var(--accent); }
  .step-connector { width: 16px; height: 1px; background: var(--border); flex-shrink: 0; }
  .step-comment-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--comment-accent); display: none; position: absolute; top: 4px; right: 4px; }
  .step-item.has-comments .step-comment-dot { display: block; }
  .toggle-bar { display: flex; justify-content: flex-end; padding: 6px 16px 0; flex-shrink: 0; }
  .view-toggle { display: flex; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
  .view-toggle button { padding: 5px 16px; font-size: 11px; font-family: var(--mono); text-transform: uppercase; letter-spacing: 0.5px; background: transparent; color: var(--text-dim); border: none; cursor: pointer; }
  .view-toggle button.active { background: var(--accent-dim); color: var(--accent); font-weight: 600; }
  .content-wrapper { flex: 1; display: flex; min-height: 0; height: calc(100vh - 180px); overflow: hidden; }
  .content { flex: 1; padding: 12px 24px 100px; overflow-y: auto; min-height: 0; height: 100%; display: flex; flex-direction: column; }
  .comment-sidebar { width: 280px; flex-shrink: 0; padding: 12px 12px 100px 0; overflow-y: auto; display: none; }
  .comment-sidebar.visible { display: block; }
  .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 { color: var(--text); margin: 28px 0 12px; font-weight: 600; line-height: 1.3; }
  .markdown-body h1 { font-size: 22px; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 10px; }
  .markdown-body h2 { font-size: 16px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--mono); font-weight: 700; }
  .markdown-body p { margin: 8px 0; color: var(--text-muted); font-size: 14px; }
  .markdown-body ul, .markdown-body ol { margin: 8px 0; padding-left: 24px; }
  .markdown-body li { margin: 4px 0; color: var(--text-muted); font-size: 14px; }
  .markdown-body code { background: var(--surface2); color: var(--accent); padding: 2px 6px; border-radius: 3px; font-family: var(--mono); font-size: 12px; }
  .markdown-body pre { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 16px; overflow-x: auto; margin: 12px 0; }
  .markdown-body pre code { background: none; padding: 0; color: var(--text-muted); font-size: 12px; line-height: 1.6; }
  .markdown-body blockquote { border-left: 3px solid var(--accent); background: var(--accent-dim); padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 12px 0; color: var(--text-muted); font-size: 14px; }
  .markdown-body table { border-collapse: collapse; margin: 12px 0; width: 100%; font-size: 13px; }
  .markdown-body th, .markdown-body td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
  .markdown-body th { background: var(--surface); font-weight: 600; color: var(--accent); text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; font-family: var(--mono); }
  .commentable { position: relative; border-left: 2px solid transparent; padding-left: 12px; margin-left: -14px; transition: border-color 0.15s, background 0.15s; cursor: pointer; border-radius: 0 4px 4px 0; }
  .commentable:hover { border-left-color: var(--comment-accent); background: var(--comment-dim); }
  .commentable.has-comment { border-left-color: var(--comment-accent); }
  .commentable .comment-badge { position: absolute; top: 2px; right: -8px; width: 18px; height: 18px; border-radius: 50%; background: var(--comment-accent); color: var(--bg); font-size: 10px; font-weight: 700; display: none; align-items: center; justify-content: center; font-family: var(--mono); }
  .commentable.has-comment .comment-badge { display: flex; }
  .comment-card { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--comment-accent); border-radius: 6px; padding: 12px; margin-bottom: 8px; font-size: 13px; position: relative; }
  .comment-card .comment-section-ref { font-size: 11px; font-family: var(--mono); color: var(--comment-accent); margin-bottom: 6px; }
  .comment-card .comment-text { color: var(--text-muted); line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
  .comment-card .comment-time { font-size: 10px; font-family: var(--mono); color: var(--text-dim); margin-top: 6px; }
  .comment-input-popup { position: fixed; z-index: 150; background: var(--surface); border: 1px solid var(--comment-accent); border-radius: 6px; padding: 12px; width: 320px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); display: none; }
  .comment-input-popup textarea { width: 100%; min-height: 60px; background: var(--bg); border: 1px solid var(--border); border-radius: 4px; color: var(--text); font-family: var(--font); font-size: 13px; padding: 8px; outline: none; resize: vertical; }
  .comment-input-actions { display: flex; justify-content: flex-end; gap: 6px; margin-top: 8px; }
  .visuals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; padding: 12px 0; }
  .visual-card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
  .visual-card img { width: 100%; height: auto; display: block; background: var(--surface2); }
  .visual-card iframe { width: 100%; height: 300px; border: none; background: #fff; }
  .visual-card .visual-caption { padding: 8px 12px; font-size: 12px; font-family: var(--mono); color: var(--text-dim); }
  .mermaid-container { background: transparent; border: none; border-radius: 6px; padding: 20px; margin: 12px 0; text-align: center; overflow: hidden; position: relative; }
  .raw-view { display: none; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 20px; flex: 1; min-height: 0; height: 100%; }
  .raw-view.active { display: flex; flex-direction: column; }
  .raw-view textarea { width: 100%; flex: 1; min-height: 100%; height: 100%; background: transparent; color: var(--text-muted); border: none; outline: none; font-family: var(--mono); font-size: 13px; line-height: 1.7; resize: none; }
  .footer-wrapper { position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; }
  .footer { background: var(--surface); border-top: 1px solid var(--border); padding: 10px 20px; display: flex; align-items: center; gap: 8px; }
  .footer .spacer { flex: 1; }
  .btn { padding: 7px 18px; border-radius: 4px; font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border); background: var(--surface2); color: var(--text-muted); }
  .btn-primary { background: transparent; color: var(--accent); border-color: var(--accent); font-weight: 600; }
  .btn-success { background: transparent; color: var(--success); border-color: var(--success); font-weight: 600; }
  .btn-warning { background: transparent; color: var(--warning); border-color: var(--warning); font-weight: 600; }
  .toast { position: fixed; bottom: 70px; left: 50%; transform: translateX(-50%); background: var(--surface); color: var(--accent); border: 1px solid var(--accent); padding: 8px 20px; border-radius: 4px; font-size: 13px; font-family: var(--mono); opacity: 0; transition: opacity 0.3s; pointer-events: none; z-index: 200; }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="header">
  <span class="badge">SPEC</span>
  <span class="title">${title}</span>
  <span class="comment-count" id="commentCount"></span>
  <span class="modified-badge" id="modifiedBadge">modified</span>
</div>
<div class="step-bar" id="stepBar"></div>
<div class="toggle-bar" id="toggleBar">
  <div class="view-toggle">
    <button class="active" id="btnRendered" onclick="setView('rendered')">Rendered</button>
    <button id="btnRaw" onclick="setView('raw')">Markdown</button>
  </div>
</div>
<div class="content-wrapper">
  <div class="content" id="contentArea">
    <div id="renderedView" class="markdown-body"></div>
    <div id="visualsView" style="display:none;"></div>
    <div id="rawView" class="raw-view"><textarea id="rawEditor" spellcheck="false"></textarea></div>
  </div>
  <div class="comment-sidebar" id="commentSidebar"></div>
</div>
<div class="comment-input-popup" id="commentPopup">
  <textarea id="commentInput" placeholder="Add a comment..." rows="3"></textarea>
  <div class="comment-input-actions">
    <button class="btn" onclick="closeCommentPopup()">Cancel</button>
    <button class="btn btn-primary" onclick="submitComment()">Add Comment</button>
  </div>
</div>
<div id="viewer-debug" style="display:none;position:fixed;top:12px;right:12px;z-index:9999;background:#2b0f13;color:#ffb4b4;border:1px solid #e85858;padding:8px 12px;border-radius:6px;font:12px/1.4 monospace;max-width:460px;white-space:pre-wrap;"></div>
<div class="toast" id="toast"></div>
<div class="footer-wrapper">
  <div class="footer">
    <button class="btn" onclick="copyToClipboard()">Copy</button>
    <button class="btn" onclick="toggleComments()">Comments</button>
    <div class="spacer"></div>
    <button class="btn" onclick="decline()">Close</button>
    <button class="btn btn-warning" onclick="requestChanges()">Request Changes</button>
    <button class="btn btn-success" onclick="approve()">Approve Spec</button>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"><\/script>
<script src="/vendor/mermaid.min.js"><\/script>
<script>
(function() {
  const PORT = ${port};
  window.addEventListener('error', function(e) { var el = document.getElementById('viewer-debug'); if (el) { el.textContent = 'JS error: ' + e.message; el.style.display = 'block'; } });
  const documents = ${escapedDocs};
  let comments = ${escapedComments};
  let currentStep = 0;
  let currentView = 'rendered';
  let modified = {};
  let docMarkdown = {};
  let originalMarkdown = {};
  let commentPopupTarget = null;

  documents.forEach(function(doc) {
    docMarkdown[doc.key] = doc.markdown || '';
    originalMarkdown[doc.key] = doc.markdown || '';
    modified[doc.key] = false;
  });

  if (typeof marked !== 'undefined') {
    marked.setOptions({ gfm: true, breaks: true });
  }

  if (typeof mermaid !== 'undefined') {
    window.__viewerDebug = { marked: typeof marked !== 'undefined', mermaid: typeof mermaid !== 'undefined' };
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#2a2d35',
        primaryBorderColor: '#5a9fd4',
        primaryTextColor: '#e2e8f0',
        lineColor: '#5a9fd4',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: '16px'
      },
      flowchart: { curve: 'basis', padding: 20 },
      securityLevel: 'loose'
    });
  }

  ${getMermaidNormalizationBrowserScript()}

  function sourceLooksLikeMermaid(source) {
    var trimmed = String(source || '').trim();
    return /^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|mindmap|timeline|pie|quadrantChart|gitGraph|requirementDiagram|block-beta)\b/i.test(trimmed);
  }

  function isMermaidCodeBlock(codeEl, preEl) {
    var className = ((preEl && preEl.className) || '') + ' ' + ((codeEl && codeEl.className) || '');
    if (/(^|\s)(language-|lang-)?mermaid(\s|$)/i.test(className)) return true;
    return sourceLooksLikeMermaid((codeEl && codeEl.textContent) || (preEl && preEl.textContent) || '');
  }

  function renderMermaidDiagrams(container) {
    if (!container || typeof mermaid === 'undefined') return;
    var blocks = Array.from(container.querySelectorAll('pre')).map(function(preEl) {
      return { preEl: preEl, codeEl: preEl.querySelector('code') };
    }).filter(function(entry) {
      return isMermaidCodeBlock(entry.codeEl, entry.preEl);
    });

    blocks.forEach(function(entry, idx) {
      var preEl = entry.preEl;
      var codeEl = entry.codeEl;
      var source = normalizeMermaidSource((codeEl && codeEl.textContent) || preEl.textContent || '');
      var wrapper = document.createElement('div');
      wrapper.className = 'mermaid-container';
      var id = 'mermaid-diagram-' + idx + '-' + Date.now();
      try {
        mermaid.render(id, source).then(function(result) {
          if (!preEl.parentNode) return;
          wrapper.innerHTML = result.svg; window.__viewerDebug.lastMermaid = 'rendered';
          preEl.parentNode.replaceChild(wrapper, preEl);
        }).catch(function(err) {
          window.__viewerDebug.lastMermaid = 'error'; console.warn('Mermaid render error', err);
        });
      } catch (e) {
        console.warn('Mermaid render error', e);
      }
    });
  }

  function getCommentsForDoc(docKey) { return comments.filter(function(c) { return c.document === docKey; }); }
  function getCommentsForSection(docKey, sectionId) { return comments.filter(function(c) { return c.document === docKey && c.sectionId === sectionId; }); }

  function renderStepBar() {
    const bar = document.getElementById('stepBar');
    if (documents.length <= 1) {
      bar.classList.add('single-doc');
      return;
    }
    let html = '';
    documents.forEach(function(doc, idx) {
      if (idx > 0) html += '<div class="step-connector"></div>';
      html += '<div class="step-item' + (idx === currentStep ? ' active' : '') + (getCommentsForDoc(doc.key).length ? ' has-comments' : '') + '" onclick="goToStep(' + idx + ')"><span class="step-num">' + (idx + 1) + '</span>' + doc.label + '<div class="step-comment-dot"></div></div>';
    });
    bar.innerHTML = html;
  }

  window.goToStep = function(idx) {
    syncCurrentDoc();
    currentStep = idx;
    render();
  };

  function render() {
    const doc = documents[currentStep];
    renderStepBar();
    renderCommentSidebar();
    updateCommentCount();
    document.getElementById('toggleBar').style.display = doc.isVisuals ? 'none' : 'flex';
    if (currentView === 'raw' && !doc.isVisuals) renderRawView(doc);
    else {
      currentView = 'rendered';
      document.getElementById('btnRendered').classList.add('active');
      document.getElementById('btnRaw').classList.remove('active');
      if (doc.isVisuals) renderVisuals(doc); else renderMarkdown(doc);
    }
    updateGlobalModifiedState();
  }

  function renderMarkdown(doc) {
    const rendered = document.getElementById('renderedView');
    rendered.style.display = 'block';
    document.getElementById('visualsView').style.display = 'none';
    document.getElementById('rawView').classList.remove('active');
    rendered.innerHTML = marked.parse(docMarkdown[doc.key] || '');
    renderMermaidDiagrams(rendered);
    makeCommentable(rendered, doc.key);
  }

  function renderVisuals(doc) {
    document.getElementById('renderedView').style.display = 'none';
    const visualsView = document.getElementById('visualsView');
    visualsView.style.display = 'block';
    document.getElementById('rawView').classList.remove('active');
    const files = doc.visualFiles || [];
    visualsView.innerHTML = files.map(function(filePath) {
      const url = 'http://127.0.0.1:' + PORT + '/file?path=' + encodeURIComponent(filePath);
      const ext = filePath.split('.').pop().toLowerCase();
      if (ext === 'html' || ext === 'htm') return '<div class="visual-card"><iframe src="' + url + '"></iframe><div class="visual-caption">' + filePath + '</div></div>';
      return '<div class="visual-card"><img src="' + url + '" alt="' + filePath + '"><div class="visual-caption">' + filePath + '</div></div>';
    }).join('');
  }

  function renderRawView(doc) {
    document.getElementById('renderedView').style.display = 'none';
    document.getElementById('visualsView').style.display = 'none';
    document.getElementById('rawView').classList.add('active');
    document.getElementById('rawEditor').value = docMarkdown[doc.key] || '';
  }

  function makeCommentable(container, docKey) {
    const elements = container.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, blockquote, table');
    elements.forEach(function(el, idx) {
      const sectionId = docKey + '-s' + idx;
      const wrapper = document.createElement('div');
      wrapper.className = 'commentable' + (getCommentsForSection(docKey, sectionId).length ? ' has-comment' : '');
      const badge = document.createElement('span');
      badge.className = 'comment-badge';
      badge.textContent = getCommentsForSection(docKey, sectionId).length || '';
      wrapper.appendChild(badge);
      el.parentNode.insertBefore(wrapper, el);
      wrapper.appendChild(el);
      wrapper.addEventListener('click', function() {
        openCommentPopup(docKey, sectionId, (el.textContent || '').substring(0, 80), wrapper.getBoundingClientRect());
      });
    });
  }

  function openCommentPopup(docKey, sectionId, sectionText, rect) {
    commentPopupTarget = { docKey, sectionId, sectionText };
    const popup = document.getElementById('commentPopup');
    popup.style.top = Math.min(rect.bottom + 4, window.innerHeight - 160) + 'px';
    popup.style.left = Math.max(20, Math.min(rect.right - 160, window.innerWidth - 340)) + 'px';
    popup.style.display = 'block';
    document.getElementById('commentInput').value = '';
    document.getElementById('commentInput').focus();
  }

  window.closeCommentPopup = function() {
    document.getElementById('commentPopup').style.display = 'none';
    commentPopupTarget = null;
  };

  window.submitComment = function() {
    const text = document.getElementById('commentInput').value.trim();
    if (!text || !commentPopupTarget) return;
    comments.push({
      id: 'c' + Date.now(),
      document: commentPopupTarget.docKey,
      sectionId: commentPopupTarget.sectionId,
      sectionText: commentPopupTarget.sectionText,
      text,
      timestamp: new Date().toISOString()
    });
    closeCommentPopup();
    render();
  };

  function renderCommentSidebar() {
    const sidebar = document.getElementById('commentSidebar');
    const doc = documents[currentStep];
    const docComments = getCommentsForDoc(doc.key);
    sidebar.innerHTML = docComments.length === 0
      ? '<div style="text-align:center;padding:20px;color:var(--text-dim);font-size:12px;">Click on any section to add a comment</div>'
      : docComments.map(function(c) {
          return '<div class="comment-card"><div class="comment-section-ref">' + c.sectionText + '</div><div class="comment-text">' + c.text + '</div><div class="comment-time">' + new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + '</div></div>';
        }).join('');
  }

  function updateCommentCount() {
    const el = document.getElementById('commentCount');
    if (comments.length > 0) {
      el.textContent = comments.length + ' comment' + (comments.length > 1 ? 's' : '');
      el.classList.add('has-comments');
    } else {
      el.classList.remove('has-comments');
    }
  }

  window.toggleComments = function() {
    document.getElementById('commentSidebar').classList.toggle('visible');
  };

  window.setView = function(view) {
    const doc = documents[currentStep];
    if (doc.isVisuals) return;
    if (view === 'raw') {
      currentView = 'raw';
      document.getElementById('btnRendered').classList.remove('active');
      document.getElementById('btnRaw').classList.add('active');
      renderRawView(doc);
    } else {
      docMarkdown[doc.key] = document.getElementById('rawEditor').value;
      updateModifiedState(doc.key);
      currentView = 'rendered';
      document.getElementById('btnRendered').classList.add('active');
      document.getElementById('btnRaw').classList.remove('active');
      renderMarkdown(doc);
    }
  };

  function updateModifiedState(docKey) {
    modified[docKey] = docMarkdown[docKey] !== originalMarkdown[docKey];
    updateGlobalModifiedState();
  }

  function updateGlobalModifiedState() {
    document.getElementById('modifiedBadge').style.display = Object.values(modified).some(Boolean) ? 'inline' : 'none';
  }

  function syncCurrentDoc() {
    const doc = documents[currentStep];
    if (currentView === 'raw' && !doc.isVisuals) {
      docMarkdown[doc.key] = document.getElementById('rawEditor').value;
      updateModifiedState(doc.key);
    }
  }

  window.copyToClipboard = function() {
    syncCurrentDoc();
    const doc = documents[currentStep];
    navigator.clipboard.writeText(doc.isVisuals ? '(visuals step)' : (docMarkdown[doc.key] || ''));
  };

  function sendResult(action) {
    syncCurrentDoc();
    const markdownChanges = {};
    Object.keys(docMarkdown).forEach(function(key) {
      if (docMarkdown[key] !== originalMarkdown[key]) {
        const doc = documents.find(function(item) { return item.key === key; });
        if (doc) markdownChanges[doc.filePath] = docMarkdown[key];
      }
    });
    fetch('http://127.0.0.1:' + PORT + '/result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, modified: Object.keys(markdownChanges).length > 0, markdownChanges, comments })
    }).then(function() { window.close(); });
  }

  window.approve = function() { sendResult('approved'); };
  window.requestChanges = function() { sendResult('changes_requested'); };
  window.decline = function() { sendResult('declined'); };

  render();
})();
<\/script>
</body>
</html>`;
}

module.exports = {
  generateSpecViewerHtml,
};
