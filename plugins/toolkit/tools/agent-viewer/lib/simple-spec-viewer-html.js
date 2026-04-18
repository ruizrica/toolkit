function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function generateSpecViewerHtml({ title, reviewId, documents, existingComments }) {
  const docsJson = JSON.stringify(documents);
  const commentsJson = JSON.stringify(existingComments || []);
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(title)}</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0b1020; color: #e5e7eb; }
    header { padding: 16px 20px; border-bottom: 1px solid #263041; background: #111827; }
    .layout { display: grid; grid-template-columns: 260px 1fr; min-height: calc(100vh - 74px); }
    nav { border-right: 1px solid #263041; padding: 16px; background: #0f172a; }
    nav button { display: block; width: 100%; margin-bottom: 8px; background: #1e293b; color: #e5e7eb; border: 0; border-radius: 8px; padding: 10px; text-align: left; cursor: pointer; }
    main { padding: 18px; }
    textarea { width: 100%; min-height: 56vh; background: #0f172a; color: #e5e7eb; border: 1px solid #334155; border-radius: 8px; padding: 12px; font: 14px/1.5 ui-monospace, SFMono-Regular, monospace; }
    .comments { margin-top: 14px; }
    .comment { background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; }
    .row { display:flex; gap:10px; margin-top: 12px; flex-wrap: wrap; }
    button.action { border: 0; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 600; }
    .approve { background: #22c55e; color: #052e16; }
    .changes { background: #f59e0b; color: #1f1300; }
    .save { background: #60a5fa; color: #0b1020; }
    input[type=text] { width: 100%; margin-top: 8px; padding: 10px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e5e7eb; }
    .meta { color: #94a3b8; font-size: 13px; }
  </style>
</head>
<body>
  <header>
    <h1 style="margin:0; font-size:20px;">${escapeHtml(title)}</h1>
    <div class="meta">Review ID: ${escapeHtml(reviewId)}</div>
  </header>
  <div class="layout">
    <nav id="doc-nav"></nav>
    <main>
      <h2 id="doc-title"></h2>
      <textarea id="markdown"></textarea>
      <input type="text" id="comment-input" placeholder="Add a comment for the current document" />
      <div class="comments" id="comments"></div>
      <div class="row">
        <button class="action save" onclick="submitResult('declined')">Save Draft</button>
        <button class="action changes" onclick="submitResult('changes_requested')">Request Changes</button>
        <button class="action approve" onclick="submitResult('approved')">Approve</button>
      </div>
    </main>
  </div>
  <script>
    const docs = ${docsJson};
    const comments = ${commentsJson};
    const initialDocs = JSON.parse(JSON.stringify(docs));
    let currentIndex = 0;

    function renderNav() {
      const nav = document.getElementById('doc-nav');
      nav.innerHTML = '';
      docs.forEach((doc, index) => {
        const btn = document.createElement('button');
        btn.textContent = doc.label;
        btn.onclick = () => { saveCurrent(); currentIndex = index; renderCurrent(); };
        nav.appendChild(btn);
      });
    }

    function saveCurrent() {
      docs[currentIndex].markdown = document.getElementById('markdown').value;
    }

    function renderCurrent() {
      const doc = docs[currentIndex];
      document.getElementById('doc-title').textContent = doc.label;
      document.getElementById('markdown').value = doc.markdown;
      renderComments();
    }

    function renderComments() {
      const doc = docs[currentIndex];
      const el = document.getElementById('comments');
      el.innerHTML = '';
      comments.filter(c => c.document === doc.filePath).forEach((comment) => {
        const div = document.createElement('div');
        div.className = 'comment';
        div.textContent = comment.text;
        el.appendChild(div);
      });
    }

    document.getElementById('comment-input').addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        const value = event.target.value.trim();
        if (!value) return;
        comments.push({ id: String(Date.now()), document: docs[currentIndex].filePath, text: value });
        event.target.value = '';
        renderComments();
      }
    });

    async function submitResult(action) {
      saveCurrent();
      const markdownChanges = {};
      let modified = false;
      docs.forEach((doc, index) => {
        if (doc.markdown !== initialDocs[index].markdown) {
          markdownChanges[doc.filePath] = doc.markdown;
          modified = true;
        }
      });
      await fetch('/result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, modified, markdownChanges, comments })
      });
      window.close();
    }

    renderNav();
    renderCurrent();
  </script>
</body>
</html>`;
}

module.exports = {
  generateSpecViewerHtml,
};
