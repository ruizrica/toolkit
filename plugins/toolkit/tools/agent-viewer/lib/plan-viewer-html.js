const { getMermaidNormalizationBrowserScript } = require("./mermaid-normalization.js");

function generatePlanViewerHtml(opts) {
  const { markdown, title, mode = "plan", port } = opts;
  const escapedMarkdown = JSON.stringify(markdown).replace(/<\//g, '<\\/');
  const escapedMode = JSON.stringify(mode).replace(/<\//g, '<\\/');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} — Plan Viewer</title>
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
    --accent-hover: #3a9ad5;
    --accent-dim: rgba(41, 128, 185, 0.12);
    --success: #48d889;
    --warning: #f0b429;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    --mono: "SF Mono", "Fira Code", "JetBrains Mono", Consolas, monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { height: 100%; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 15px;
    line-height: 1.65;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    margin: 12px 16px 0;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
  }
  .badge {
    background: transparent;
    color: var(--accent);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border: 1px solid var(--accent);
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: var(--mono);
  }
  .badge.questions { color: var(--success); border-color: var(--success); }
  .title { font-size: 15px; font-weight: 600; color: var(--text); flex: 1; }
  .modified-badge {
    font-size: 10px;
    font-family: var(--mono);
    font-weight: 600;
    color: var(--warning);
    border: 1px solid var(--warning);
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: none;
  }
  .toggle-bar {
    display: flex;
    justify-content: flex-end;
    padding: 8px 16px 0;
    flex-shrink: 0;
  }
  .view-toggle {
    display: flex;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
  }
  .view-toggle button {
    padding: 5px 16px;
    font-size: 11px;
    font-family: var(--mono);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: transparent;
    color: var(--text-dim);
    border: none;
    cursor: pointer;
  }
  .view-toggle button.active {
    background: var(--accent-dim);
    color: var(--accent);
    font-weight: 600;
  }
  .content {
    flex: 1;
    width: 100%;
    padding: 12px 24px 100px;
    min-height: 0;
    height: calc(100vh - 140px);
    overflow: auto;
  }
  .markdown-body h1, .markdown-body h2, .markdown-body h3,
  .markdown-body h4, .markdown-body h5, .markdown-body h6 {
    color: var(--text);
    margin: 28px 0 12px;
    font-weight: 600;
    line-height: 1.3;
  }
  .markdown-body h1 {
    font-size: 22px;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
  }
  .markdown-body h2 {
    font-size: 16px;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: var(--mono);
    font-weight: 700;
  }
  .markdown-body p { margin: 8px 0; color: var(--text-muted); font-size: 14px; }
  .markdown-body ul, .markdown-body ol { margin: 8px 0; padding-left: 24px; }
  .markdown-body li { margin: 4px 0; color: var(--text-muted); font-size: 14px; }
  .markdown-body code {
    background: var(--surface2);
    color: var(--accent);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: var(--mono);
    font-size: 12px;
  }
  .markdown-body pre {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 12px 0;
  }
  .markdown-body pre code {
    background: none;
    padding: 0;
    color: var(--text);
    font-size: 12px;
    line-height: 1.6;
  }
  .markdown-body table {
    border-collapse: collapse;
    margin: 12px 0;
    width: 100%;
    font-size: 13px;
  }
  .markdown-body th, .markdown-body td {
    border: 1px solid var(--border);
    padding: 8px 12px;
    text-align: left;
  }
  .markdown-body th {
    background: var(--surface);
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
    font-family: var(--mono);
  }
  .mermaid-container {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 20px;
    margin: 12px 0;
    text-align: center;
    overflow: hidden;
    position: relative;
  }
  .raw-view {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px;
    min-height: 0;
    height: 100%;
  }
  .raw-view.active { display: flex; flex-direction: column; }
  .raw-view textarea {
    width: 100%;
    flex: 1;
    min-height: 100%;
    height: 100%;
    background: transparent;
    color: var(--text-muted);
    border: none;
    outline: none;
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.7;
    resize: none;
  }
  .footer-wrapper {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
  }
  .footer {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .footer .spacer { flex: 1; }
  .btn {
    padding: 7px 18px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text-muted);
    transition: all 0.15s;
    font-family: var(--font);
  }
  .btn-primary {
    background: transparent;
    color: var(--accent);
    border-color: var(--accent);
    font-weight: 600;
  }
  .toast {
    position: fixed;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--surface);
    color: var(--accent);
    border: 1px solid var(--accent);
    padding: 8px 20px;
    border-radius: 4px;
    font-size: 13px;
    font-family: var(--mono);
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
    z-index: 200;
  }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="header">
  <span class="badge ${mode === "questions" ? "questions" : ""}">${mode === "questions" ? "QUESTIONS" : "PLAN"}</span>
  <span class="title">${title}</span>
  <span class="modified-badge" id="modifiedBadge">modified</span>
</div>
<div class="toggle-bar">
  <div class="view-toggle">
    <button class="active" id="btnRendered" onclick="setView('rendered')">Rendered</button>
    <button id="btnRaw" onclick="setView('raw')">Markdown</button>
  </div>
</div>
<div class="content">
  <div id="renderedView" class="markdown-body"></div>
  <div id="rawView" class="raw-view">
    <textarea id="rawEditor" spellcheck="false"></textarea>
  </div>
</div>
<div id="viewer-debug" style="display:none;position:fixed;top:12px;right:12px;z-index:9999;background:#2b0f13;color:#ffb4b4;border:1px solid #e85858;padding:8px 12px;border-radius:6px;font:12px/1.4 monospace;max-width:460px;white-space:pre-wrap;"></div>
<div class="toast" id="toast"></div>
<div class="footer-wrapper">
  <div class="footer">
    <button class="btn" onclick="copyToClipboard()">Copy</button>
    <div class="spacer"></div>
    <button class="btn" onclick="decline()">Close</button>
    <button class="btn btn-primary" onclick="approve()">${mode === "questions" ? "Submit Answers" : "Approve Plan"}</button>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"><\/script>
<script src="/vendor/mermaid.min.js"><\/script>
<script>
(function() {
  const PORT = ${port};
  window.addEventListener('error', function(e) { var el = document.getElementById('viewer-debug'); if (el) { el.textContent = 'JS error: ' + e.message; el.style.display = 'block'; } });
  const MODE = ${escapedMode};
  let markdown = ${escapedMarkdown};
  let originalMarkdown = markdown;
  let currentView = 'rendered';

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

  function render() {
    var html = marked.parse(markdown || '');
    document.getElementById('renderedView').innerHTML = html;
    renderMermaidDiagrams(document.getElementById('renderedView'));
    document.getElementById('rawEditor').value = markdown;
    document.getElementById('modifiedBadge').style.display = markdown !== originalMarkdown ? 'inline' : 'none';
  }

  window.setView = function(view) {
    currentView = view;
    document.getElementById('btnRendered').classList.toggle('active', view === 'rendered');
    document.getElementById('btnRaw').classList.toggle('active', view === 'raw');
    document.getElementById('renderedView').style.display = view === 'rendered' ? 'block' : 'none';
    document.getElementById('rawView').classList.toggle('active', view === 'raw');
    if (view === 'rendered') {
      markdown = document.getElementById('rawEditor').value;
      render();
    }
  };

  window.copyToClipboard = function() {
    navigator.clipboard.writeText(currentView === 'raw' ? document.getElementById('rawEditor').value : markdown).then(function() {
      var toast = document.getElementById('toast');
      toast.textContent = 'Copied to clipboard';
      toast.classList.add('show');
      setTimeout(function() { toast.classList.remove('show'); }, 1500);
    });
  };

  window.approve = function() {
    if (currentView === 'raw') markdown = document.getElementById('rawEditor').value;
    fetch('http://127.0.0.1:' + PORT + '/result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'approved', markdown: markdown, modified: markdown !== originalMarkdown, comments: [] })
    }).then(function() { window.close(); });
  };

  window.decline = function() {
    if (currentView === 'raw') markdown = document.getElementById('rawEditor').value;
    fetch('http://127.0.0.1:' + PORT + '/result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'declined', markdown: markdown, modified: markdown !== originalMarkdown, comments: [] })
    }).then(function() { window.close(); });
  };

  render();
})();
<\/script>
</body>
</html>`;
}

module.exports = {
  generatePlanViewerHtml,
};
