const path = require('node:path');
const { createViewerServer, openBrowser } = require('./viewer-server.js');
const { readStdin, readJsonFile, emitResult } = require('./io.js');
const { generateCompletionViewerHtml } = require('./completion-viewer-html.js');

async function runCompletionViewer(parsed) {
  let payload = null;
  if (parsed.input) payload = readJsonFile(path.resolve(parsed.input));
  else if (parsed.stdin) payload = JSON.parse(await readStdin());
  if (!payload) throw new Error('completion requires --input or --stdin');

  const handle = await createViewerServer({
    getHtml: (port) => generateCompletionViewerHtml({ report: payload, port }),
  });

  const url = `http://127.0.0.1:${handle.port}`;
  if (parsed.debug) process.stderr.write(`[agent-viewer] opening ${url}\n`);
  openBrowser(url);
  const rawResult = await handle.waitForResult();
  try { handle.server.close(); } catch {}
  emitResult(rawResult || { action: 'closed', rolledBackFiles: [] }, parsed.json);
}

module.exports = {
  runCompletionViewer,
};
