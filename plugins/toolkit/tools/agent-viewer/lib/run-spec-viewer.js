const fs = require("node:fs");
const path = require("node:path");
const { createViewerServer, openBrowser } = require("./viewer-server.js");
const { readStdin, readJsonFile, writeJsonFile, emitResult } = require("./io.js");
const { discoverSpecDocuments } = require("./spec-discovery.js");
const { generateSpecViewerHtml } = require("./spec-viewer-html.js");
const { createSpecStandaloneExport, saveStandaloneExport, copyMermaidAsset } = require("./standalone-export.js");

function normalizeSpecPayload(payload, parsed) {
  const folderPath = payload.folderPath ? path.resolve(payload.folderPath) : null;
  const documents = payload.documents || (folderPath ? discoverSpecDocuments(folderPath) : []);
  return {
    title: parsed.title || payload.title || (folderPath ? path.basename(folderPath) : "Spec Viewer"),
    folderPath,
    documents,
  };
}

async function runSpecViewer(parsed) {
  let input = null;

  if (parsed.folder) {
    const folderPath = path.resolve(parsed.folder);
    input = {
      title: parsed.title || path.basename(folderPath),
      folderPath,
      documents: discoverSpecDocuments(folderPath),
    };
  } else if (parsed.input) {
    input = normalizeSpecPayload(readJsonFile(path.resolve(parsed.input)), parsed);
  } else if (parsed.stdin) {
    input = normalizeSpecPayload(JSON.parse(await readStdin()), parsed);
  }

  if (!input) {
    throw new Error("spec requires --folder, --input, or --stdin");
  }

  const reviewId = parsed.reviewId || `spec-${Date.now()}`;
  const sidecarPath = input.folderPath ? path.join(input.folderPath, "spec-comments.json") : null;
  const existingMeta = sidecarPath && fs.existsSync(sidecarPath)
    ? JSON.parse(fs.readFileSync(sidecarPath, "utf8"))
    : { comments: [] };

  const normalizedDocuments = input.documents.map((doc, index) => ({
    key: doc.key || doc.filePath || `doc-${index + 1}`,
    label: doc.label,
    markdown: doc.markdown || "",
    filePath: doc.filePath,
    isVisuals: Boolean(doc.isVisuals),
    visualFiles: doc.visualFiles || [],
  }));

  const handle = await createViewerServer({
    getHtml: (port) => generateSpecViewerHtml({
      title: input.title,
      reviewId,
      documents: normalizedDocuments,
      port,
      existingComments: existingMeta.comments || [],
    }),
    routes: [
      {
        method: "GET",
        path: "/file",
        handler: async (_req, res, url) => {
          const relPath = url.searchParams.get("path");
          if (!relPath || !input.folderPath) {
            res.writeHead(400);
            res.end("Missing path parameter");
            return;
          }
          const absolutePath = path.resolve(input.folderPath, relPath);
          if (!absolutePath.startsWith(path.resolve(input.folderPath))) {
            res.writeHead(403);
            res.end("Access denied");
            return;
          }
          try {
            const data = fs.readFileSync(absolutePath);
            const ext = path.extname(absolutePath).toLowerCase();
            const mime = ext === ".png" ? "image/png"
              : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg"
              : ext === ".gif" ? "image/gif"
              : ext === ".webp" ? "image/webp"
              : ext === ".svg" ? "image/svg+xml"
              : ext === ".html" || ext === ".htm" ? "text/html"
              : "application/octet-stream";
            res.writeHead(200, { "Content-Type": mime });
            res.end(data);
          } catch {
            res.writeHead(404);
            res.end("File not found");
          }
        },
      },
      {
        method: "POST",
        path: "/save",
        handler: async (req, res) => {
          let body = "";
          req.on("data", (chunk) => { body += chunk; });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              if (sidecarPath) {
                writeJsonFile(sidecarPath, { comments: data.comments || [] });
              }
              res.writeHead(200, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ ok: true }));
            } catch (error) {
              res.writeHead(500, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ error: error.message }));
            }
          });
        },
      },
      {
        method: "POST",
        path: "/export-standalone",
        handler: async (req, res) => {
          let body = "";
          req.on("data", (chunk) => { body += chunk; });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              const markdownChanges = data.markdownChanges || {};
              const docsForExport = normalizedDocuments.map((doc) => ({
                label: doc.label,
                filePath: doc.filePath,
                markdown: markdownChanges[doc.filePath] || doc.markdown || "",
              }));
              const html = createSpecStandaloneExport({ title: input.title, documents: docsForExport });
              const saved = saveStandaloneExport("spec-standalone", html);
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

  const markdownChanges = rawResult?.markdownChanges || {};
  if (input.folderPath) {
    for (const [relativePath, markdown] of Object.entries(markdownChanges)) {
      const absolutePath = path.resolve(input.folderPath, relativePath);
      if (absolutePath.startsWith(path.resolve(input.folderPath))) {
        fs.writeFileSync(absolutePath, markdown, "utf8");
      }
    }
  }

  const result = {
    action: rawResult?.action || "declined",
    reviewId,
    modified: Boolean(rawResult?.modified),
    folderPath: input.folderPath,
    markdownChanges,
    comments: rawResult?.comments || [],
  };

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
  runSpecViewer,
};
