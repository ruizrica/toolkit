const http = require("node:http");
const { execSync } = require("node:child_process");

function createViewerServer({ getHtml, routes = [], onResult }) {
  return new Promise((resolveSetup) => {
    let resolveResult;
    let resultResolved = false;
    const resultPromise = new Promise((res) => {
      resolveResult = res;
    });

    const routeMap = new Map();
    for (const route of routes) {
      const key = `${route.method} ${route.path}`;
      routeMap.set(key, route.handler);
    }

    const server = http.createServer(async (req, res) => {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type");

      if (req.method === "OPTIONS") {
        res.writeHead(204);
        res.end();
        return;
      }

      const url = new URL(req.url || "/", "http://127.0.0.1");
      const key = `${req.method} ${url.pathname}`;

      if (req.method === "GET" && url.pathname === "/") {
        const port = server.address().port;
        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        res.end(getHtml(port));
        return;
      }

      if (req.method === "GET" && url.pathname === "/vendor/mermaid.min.js") {
        try {
          const fs = require("node:fs");
          const path = require("node:path");
          const mermaidPath = path.resolve(__dirname, "../assets/vendor/mermaid.min.js");
          const data = fs.readFileSync(mermaidPath);
          res.writeHead(200, { "Content-Type": "application/javascript; charset=utf-8", "Cache-Control": "public, max-age=3600" });
          res.end(data);
        } catch (error) {
          res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
          res.end("mermaid asset not found");
        }
        return;
      }

      if (req.method === "POST" && url.pathname === "/result") {
        let body = "";
        req.on("data", (chunk) => { body += chunk; });
        req.on("end", () => {
          try {
            const data = body.trim() ? JSON.parse(body) : {};
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ ok: true }));
            if (!resultResolved) {
              resultResolved = true;
              if (onResult) onResult(data);
              resolveResult(data);
            }
          } catch (error) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: error.message }));
          }
        });
        return;
      }

      const handler = routeMap.get(key);
      if (handler) {
        try {
          await handler(req, res, url);
          return;
        } catch (error) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: error.message }));
          return;
        }
      }

      res.writeHead(404);
      res.end("Not found");
    });

    server.on("close", () => {
      if (!resultResolved) {
        resultResolved = true;
        resolveResult(undefined);
      }
    });

    server.listen(0, "127.0.0.1", () => {
      resolveSetup({
        server,
        port: server.address().port,
        waitForResult: () => resultPromise,
      });
    });
  });
}

function openBrowser(url) {
  try {
    execSync(`open "${url}"`, { stdio: "ignore" });
    return;
  } catch {}
  try {
    execSync(`xdg-open "${url}"`, { stdio: "ignore" });
    return;
  } catch {}
  try {
    execSync(`start "${url}"`, { stdio: "ignore" });
  } catch {}
}

module.exports = {
  createViewerServer,
  openBrowser,
};
