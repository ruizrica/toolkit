const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { getMermaidNormalizationBrowserScript } = require("./mermaid-normalization.js");

function ensureDesktop() {
  const desktop = path.join(os.homedir(), "Desktop");
  fs.mkdirSync(desktop, { recursive: true });
  return desktop;
}

function timestampForFileName() {
  return new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
}

function saveStandaloneExport(filePrefix, html) {
  const desktop = ensureDesktop();
  const fileName = `${filePrefix}-${timestampForFileName()}.html`;
  const filePath = path.join(desktop, fileName);
  fs.writeFileSync(filePath, html, "utf8");
  return { filePath, fileName };
}

function baseDocument({ title, label, body, script }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(title)} — Export</title>
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
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    --mono: "SF Mono", "Fira Code", "JetBrains Mono", Consolas, monospace;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; min-height: 100%; background: var(--bg); color: var(--text); font-family: var(--font); }
  body { padding: 24px; }
  .shell { max-width: 1080px; margin: 0 auto; }
  .header {
    display: flex; align-items: center; gap: 14px; padding: 16px 20px; margin-bottom: 18px;
    background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 8px;
  }
  .badge {
    display: inline-flex; align-items: center; justify-content: center; border: 1px solid var(--accent); color: var(--accent);
    border-radius: 4px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 1px; font-family: var(--mono); text-transform: uppercase;
  }
  .title { flex: 1; font-size: 16px; font-weight: 600; }
  .meta { font-size: 12px; color: var(--text-muted); font-family: var(--mono); }
  .panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px; }
  .section + .section { margin-top: 24px; }
  .section-header { margin-bottom: 12px; }
  .section-label { color: var(--accent); font-size: 12px; letter-spacing: 0.8px; font-family: var(--mono); text-transform: uppercase; }
  .section-path { margin-top: 4px; color: var(--text-dim); font-size: 12px; font-family: var(--mono); }
  .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 { color: var(--text); margin: 28px 0 12px; line-height: 1.3; }
  .markdown-body h1 { color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 10px; font-size: 24px; }
  .markdown-body h2 { color: var(--accent); font-size: 17px; text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--mono); }
  .markdown-body p, .markdown-body li { color: var(--text-muted); font-size: 14px; line-height: 1.7; }
  .markdown-body ul, .markdown-body ol { padding-left: 24px; }
  .markdown-body code { background: var(--surface2); color: var(--accent); padding: 2px 6px; border-radius: 4px; font-family: var(--mono); font-size: 12px; }
  .markdown-body pre { background: #171a20; border: 1px solid var(--border); border-radius: 6px; padding: 16px; overflow: auto; }
  .markdown-body pre code { background: transparent; padding: 0; color: var(--text-muted); }
  .markdown-body blockquote { border-left: 3px solid var(--accent); background: var(--accent-dim); padding: 12px 16px; border-radius: 0 6px 6px 0; color: var(--text-muted); }
  .markdown-body table { width: 100%; border-collapse: collapse; margin: 12px 0; }
  .markdown-body th, .markdown-body td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
  .markdown-body th { color: var(--accent); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-family: var(--mono); }
  .footer-note { margin-top: 18px; color: var(--text-dim); font-size: 12px; text-align: center; font-family: var(--mono); }
  .mermaid-container { background: transparent; border: none; border-radius: 6px; padding: 20px; margin: 12px 0; text-align: center; overflow: hidden; position: relative; }
</style>
</head>
<body>
  <div class="shell">
    <div class="header">
      <span class="badge">${escapeHtml(label)}</span>
      <div class="title">${escapeHtml(title)}</div>
      <div class="meta">Read-only standalone export</div>
    </div>
    <div class="panel">${body}</div>
    <div class="footer-note">This export is standalone and read-only.</div>
  </div>
  <script src="./mermaid.min.js"><\/script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"><\/script>
  <script>
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#2a2d35', primaryBorderColor: '#5a9fd4', primaryTextColor: '#e2e8f0', lineColor: '#5a9fd4',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '16px'
      },
      flowchart: { curve: 'basis', padding: 20 },
      securityLevel: 'loose'
    });
  }
  ${getMermaidNormalizationBrowserScript()}
  ${script}
  <\/script>
</body>
</html>`;
}

function createPlanStandaloneExport({ title, markdown }) {
  const state = JSON.stringify({ markdown }).replace(/<\//g, '<\\/');
  const body = `<div class="section"><div class="markdown-body" id="content"></div></div>`;
  const script = `
const state = ${state};
if (typeof marked !== 'undefined') marked.setOptions({ gfm: true, breaks: true });
const root = document.getElementById('content');
root.innerHTML = marked.parse(state.markdown || '');
renderMermaidDiagrams(root);
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
`;
  return baseDocument({ title, label: 'Plan', body, script });
}

function createSpecStandaloneExport({ title, documents }) {
  const docs = JSON.stringify(documents).replace(/<\//g, '<\\/');
  const body = `<div id="specContent"></div>`;
  const script = `
const docs = ${docs};
if (typeof marked !== 'undefined') marked.setOptions({ gfm: true, breaks: true });
const root = document.getElementById('specContent');
root.innerHTML = docs.map(function(doc) {
  return '<section class="section"><div class="section-header"><div class="section-label">' + escapeHtml(doc.label) + '</div><div class="section-path">' + escapeHtml(doc.filePath) + '</div></div><div class="markdown-body">' + marked.parse(doc.markdown || '') + '</div></section>';
}).join('');
renderMermaidDiagrams(root);
function escapeHtml(value) { return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
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
`;
  return baseDocument({ title, label: 'Spec', body, script });
}

function copyMermaidAsset(destinationDir) {
  const source = path.join(__dirname, "../assets/vendor/mermaid.min.js");
  const target = path.join(destinationDir, "mermaid.min.js");
  fs.copyFileSync(source, target);
  return target;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;");
}

module.exports = {
  saveStandaloneExport,
  createPlanStandaloneExport,
  createSpecStandaloneExport,
  copyMermaidAsset,
};
