function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function generatePlanViewerHtml({ title, markdown, reviewId, priorMeta }) {
  const safeTitle = escapeHtml(title);
  const safeMarkdown = escapeHtml(markdown);
  const priorAction = priorMeta && priorMeta.lastAction ? escapeHtml(priorMeta.lastAction) : "none";
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${safeTitle}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #0b1020; color: #e5e7eb; }
    header { padding: 16px 20px; border-bottom: 1px solid #263041; background: #111827; }
    main { padding: 20px; }
    textarea { width: 100%; min-height: 65vh; background: #0f172a; color: #e5e7eb; border: 1px solid #334155; border-radius: 8px; padding: 12px; font: 14px/1.5 ui-monospace, SFMono-Regular, monospace; }
    .row { display: flex; gap: 10px; margin: 12px 0 0; flex-wrap: wrap; }
    button { border: 0; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 600; }
    .approve { background: #22c55e; color: #052e16; }
    .decline { background: #f59e0b; color: #1f1300; }
    .save { background: #60a5fa; color: #0b1020; }
    .meta { color: #94a3b8; font-size: 13px; }
  </style>
</head>
<body>
  <header>
    <h1 style="margin:0; font-size: 20px;">${safeTitle}</h1>
    <div class="meta">Review ID: ${escapeHtml(reviewId)} · Previous action: ${priorAction}</div>
  </header>
  <main>
    <textarea id="markdown">${safeMarkdown}</textarea>
    <div class="row">
      <button class="save" onclick="submitResult('declined', true)">Save Draft</button>
      <button class="decline" onclick="submitResult('declined', true)">Request Changes / Not Approved</button>
      <button class="approve" onclick="submitResult('approved', true)">Approve</button>
    </div>
  </main>
  <script>
    const initial = document.getElementById('markdown').value;
    async function submitResult(action, includeMarkdown) {
      const markdown = document.getElementById('markdown').value;
      const modified = markdown !== initial;
      await fetch('/result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, markdown: includeMarkdown ? markdown : initial, modified, comments: [] })
      });
      window.close();
    }
  </script>
</body>
</html>`;
}

module.exports = {
  generatePlanViewerHtml,
};
