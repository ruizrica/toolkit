const { getMermaidNormalizationBrowserScript } = require('./mermaid-normalization.js');

function generateCompletionViewerHtml({ report, port }) {
  const escapedReport = JSON.stringify(report).replace(/<\//g, '<\\/');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${report.title} — Completion Report</title>
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
    --success: #48d889;
    --error: #e85858;
    --warning: #f0b429;
    --diff-add-bg: rgba(72,216,137,0.08);
    --diff-del-bg: rgba(232,88,88,0.08);
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --mono: "SF Mono", "Fira Code", "JetBrains Mono", Consolas, monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 15px; line-height: 1.65; }
  .header { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--success); border-radius: 6px; margin: 12px 16px 0; padding: 14px 20px; display: flex; align-items: center; gap: 14px; }
  .badge { color: var(--success); border: 1px solid var(--success); border-radius: 4px; padding: 3px 10px; font-size: 11px; font-family: var(--mono); font-weight: 700; text-transform: uppercase; }
  .title { flex: 1; font-size: 15px; font-weight: 600; }
  .stats { font-size: 12px; font-family: var(--mono); color: var(--text-muted); display: flex; gap: 12px; }
  .content { padding: 12px 16px 100px; }
  .summary-section { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 20px; margin-bottom: 16px; }
  .summary-section h2 { font-size: 13px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--mono); font-weight: 700; margin-bottom: 12px; }
  .markdown-body h1, .markdown-body h2, .markdown-body h3 { color: var(--text); margin: 16px 0 8px; line-height: 1.3; }
  .markdown-body h1 { color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 8px; font-size: 20px; }
  .markdown-body h2 { color: var(--accent); font-size: 16px; text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--mono); }
  .markdown-body p, .markdown-body li { color: var(--text-muted); font-size: 14px; }
  .markdown-body ul, .markdown-body ol { padding-left: 24px; }
  .markdown-body code { background: var(--surface2); color: var(--accent); padding: 2px 6px; border-radius: 3px; font-family: var(--mono); font-size: 12px; }
  .markdown-body pre { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 16px; overflow-x: auto; margin: 12px 0; }
  .task-overview { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
  .task-stat { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px 20px; flex: 1; min-width: 120px; text-align: center; }
  .task-stat .value { font-size: 28px; font-weight: 700; font-family: var(--mono); }
  .task-stat .label { font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-family: var(--mono); }
  .files-section { margin-bottom: 16px; }
  .files-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .files-header h2 { font-size: 13px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--mono); font-weight: 700; }
  .file-card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 8px; overflow: hidden; }
  .file-header { display: flex; align-items: center; gap: 10px; padding: 10px 16px; }
  .file-status { font-size: 10px; font-weight: 700; font-family: var(--mono); padding: 2px 6px; border-radius: 3px; border: 1px solid var(--border); text-transform: uppercase; }
  .file-path { font-family: var(--mono); font-size: 13px; color: var(--text); flex: 1; }
  .file-stats { font-family: var(--mono); font-size: 11px; display: flex; gap: 8px; }
  .diff-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 12px; }
  .diff-table td { padding: 0 12px; white-space: pre-wrap; word-break: break-all; vertical-align: top; }
  .diff-add { background: var(--diff-add-bg); }
  .diff-del { background: var(--diff-del-bg); }
  .footer-wrapper { position: fixed; bottom: 0; left: 0; right: 0; }
  .footer { background: var(--surface); border-top: 1px solid var(--border); padding: 10px 20px; display: flex; align-items: center; gap: 8px; }
  .footer .spacer { flex: 1; }
  .btn { padding: 7px 18px; border-radius: 4px; font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border); background: var(--surface2); color: var(--text-muted); }
  .btn-success { background: transparent; color: var(--success); border-color: var(--success); font-weight: 600; }
  .toast { position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); background: var(--surface); color: var(--accent); border: 1px solid var(--accent); padding: 8px 20px; border-radius: 4px; font-size: 13px; font-family: var(--mono); opacity: 0; transition: opacity 0.3s; pointer-events: none; }
  .toast.show { opacity: 1; }
  .mermaid-container { background: transparent; border: none; border-radius: 6px; padding: 20px; margin: 12px 0; text-align: center; overflow: hidden; position: relative; }
</style>
</head>
<body>
<div class="header">
  <span class="badge">REPORT</span>
  <span class="title" id="titleText"></span>
  <div class="stats" id="headerStats"></div>
</div>
<div class="content">
  <div class="task-overview" id="taskOverview"></div>
  <div class="summary-section" id="summarySection" style="display:none;"><h2>Summary</h2><div class="markdown-body" id="summaryContent"></div></div>
  <div class="summary-section" id="taskSection" style="display:none;"><h2>Tasks Completed</h2><div class="markdown-body" id="taskContent"></div></div>
  <div class="files-section"><div class="files-header"><h2>Files Changed</h2></div><div id="filesList"></div></div>
</div>
<div class="toast" id="toast"></div>
<div class="footer-wrapper"><div class="footer"><div class="spacer"></div><button class="btn btn-success" onclick="done()">Done</button></div></div>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"><\/script>
<script src="/vendor/mermaid.min.js"><\/script>
<script>
(function() {
  const PORT = ${port};
  const report = ${escapedReport};
  if (typeof marked !== 'undefined') marked.setOptions({ gfm: true, breaks: true });
  if (typeof mermaid !== 'undefined') mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
  ${getMermaidNormalizationBrowserScript()}
  function sourceLooksLikeMermaid(source) {
    var trimmed = String(source || '').trim();
    return /^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|mindmap|timeline|pie|quadrantChart|gitGraph|requirementDiagram|block-beta)\\b/i.test(trimmed);
  }
  function isMermaidCodeBlock(codeEl, preEl) {
    var className = ((preEl && preEl.className) || '') + ' ' + ((codeEl && codeEl.className) || '');
    if (/(^|\\s)(language-|lang-)?mermaid(\\s|$)/i.test(className)) return true;
    return sourceLooksLikeMermaid((codeEl && codeEl.textContent) || (preEl && preEl.textContent) || '');
  }
  function renderMermaidDiagrams(container) {
    if (!container || typeof mermaid === 'undefined') return;
    Array.from(container.querySelectorAll('pre')).forEach(function(preEl, idx) {
      var codeEl = preEl.querySelector('code');
      if (!isMermaidCodeBlock(codeEl, preEl)) return;
      var source = normalizeMermaidSource((codeEl && codeEl.textContent) || preEl.textContent || '');
      var wrapper = document.createElement('div');
      wrapper.className = 'mermaid-container';
      var id = 'mermaid-diagram-' + idx + '-' + Date.now();
      try {
        mermaid.render(id, source).then(function(result) {
          if (!preEl.parentNode) return;
          wrapper.innerHTML = result.svg;
          preEl.parentNode.replaceChild(wrapper, preEl);
        }).catch(function() {});
      } catch (e) {}
    });
  }
  function renderMarkdown(md) { return marked.parse(md || ''); }
  document.getElementById('titleText').textContent = report.title;
  document.getElementById('headerStats').innerHTML = '<span>+' + report.totalAdditions + '</span><span>-' + report.totalDeletions + '</span><span>' + report.files.length + ' files</span>';
  document.getElementById('taskOverview').innerHTML = '<div class="task-stat"><div class="value">' + report.files.length + '</div><div class="label">Files</div></div><div class="task-stat"><div class="value">+' + report.totalAdditions + '</div><div class="label">Additions</div></div><div class="task-stat"><div class="value">-' + report.totalDeletions + '</div><div class="label">Deletions</div></div>';
  if (report.summary) {
    document.getElementById('summarySection').style.display = 'block';
    document.getElementById('summaryContent').innerHTML = renderMarkdown(report.summary);
    renderMermaidDiagrams(document.getElementById('summaryContent'));
  }
  if (report.taskMarkdown) {
    document.getElementById('taskSection').style.display = 'block';
    document.getElementById('taskContent').innerHTML = renderMarkdown(report.taskMarkdown);
    renderMermaidDiagrams(document.getElementById('taskContent'));
  }
  document.getElementById('filesList').innerHTML = (report.files || []).map(function(file) {
    return '<div class="file-card"><div class="file-header"><span class="file-status">' + file.status + '</span><span class="file-path">' + file.path + '</span><span class="file-stats"><span>+' + file.additions + '</span><span>-' + file.deletions + '</span></span></div><div><table class="diff-table"><tr><td>' + escapeHtml(file.diff || '') + '</td></tr></table></div></div>';
  }).join('');
  function escapeHtml(value) { return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  window.done = function() {
    fetch('http://127.0.0.1:' + PORT + '/result', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'done', rolledBackFiles: [] }) }).then(function() { window.close(); });
  };
})();
<\/script>
</body>
</html>`;
}

module.exports = {
  generateCompletionViewerHtml,
};
