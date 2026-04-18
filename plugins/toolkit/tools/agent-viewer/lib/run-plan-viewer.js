const fs = require("node:fs");
const path = require("node:path");
const { createViewerServer, openBrowser } = require("./viewer-server.js");
const { readStdin, readJsonFile, writeJsonFile, emitResult } = require("./io.js");
const { generatePlanViewerHtml } = require("./plan-viewer-html.js");
const { createPlanStandaloneExport, saveStandaloneExport, copyMermaidAsset } = require("./standalone-export.js");

function resolvePlanInput(parsed) {
  if (parsed.file) {
    const filePath = path.resolve(parsed.file);
    const markdown = fs.readFileSync(filePath, "utf8");
    return {
      title: parsed.title || path.basename(filePath, path.extname(filePath)),
      filePath,
      markdown,
    };
  }

  if (parsed.input) {
    const payload = readJsonFile(path.resolve(parsed.input));
    return normalizePlanPayload(payload, parsed);
  }

  return null;
}

function normalizePlanPayload(payload, parsed) {
  const filePath = payload.filePath ? path.resolve(payload.filePath) : null;
  const markdown = payload.markdown ?? (filePath ? fs.readFileSync(filePath, "utf8") : "");
  return {
    title: parsed.title || payload.title || (filePath ? path.basename(filePath, path.extname(filePath)) : "Plan Viewer"),
    filePath,
    markdown,
  };
}

async function runPlanViewer(parsed) {
  let input = resolvePlanInput(parsed);
  if (!input && parsed.stdin) {
    const raw = await readStdin();
    input = normalizePlanPayload(JSON.parse(raw), parsed);
  }

  if (!input) {
    throw new Error("plan requires --file, --input, or --stdin");
  }

  const reviewId = parsed.reviewId || `plan-${Date.now()}`;
  const sidecarPath = input.filePath ? `${input.filePath}.agent-viewer.json` : null;
  const existingMeta = sidecarPath && fs.existsSync(sidecarPath)
    ? JSON.parse(fs.readFileSync(sidecarPath, "utf8"))
    : null;

  const handle = await createViewerServer({
    getHtml: (port) => generatePlanViewerHtml({
      title: input.title,
      markdown: input.markdown,
      reviewId,
      port,
      priorMeta: existingMeta,
    }),
    routes: [
      {
        method: "POST",
        path: "/export-standalone",
        handler: async (req, res) => {
          let body = "";
          req.on("data", (chunk) => { body += chunk; });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              const html = createPlanStandaloneExport({
                title: input.title,
                markdown: data.markdown || input.markdown,
              });
              const saved = saveStandaloneExport("plan-standalone", html);
              copyMermaidAsset(require("node:path").dirname(saved.filePath));
              res.writeHead(200, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ ok: true, filePath: saved.filePath, fileName: saved.fileName }));
            } catch (error) {
              res.writeHead(500, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ error: error.message }));
            }
          });
        },
      },
    ],
  });

  const url = `http://127.0.0.1:${handle.port}`;
  if (parsed.debug) process.stderr.write(`[agent-viewer] opening ${url}\n`);
  openBrowser(url);

  const rawResult = await handle.waitForResult();
  try { handle.server.close(); } catch {}

  const result = {
    action: rawResult?.action || "declined",
    reviewId,
    modified: Boolean(rawResult?.modified),
    filePath: input.filePath,
    markdown: rawResult?.markdown || input.markdown,
    comments: rawResult?.comments || [],
  };

  if (input.filePath && result.modified) {
    fs.writeFileSync(input.filePath, result.markdown, "utf8");
  }

  if (sidecarPath) {
    writeJsonFile(sidecarPath, {
      reviewId,
      lastAction: result.action,
      updatedAt: new Date().toISOString(),
      comments: result.comments,
    });
  }

  emitResult(result, parsed.json);
}

module.exports = {
  resolvePlanInput,
  normalizePlanPayload,
  runPlanViewer,
};
