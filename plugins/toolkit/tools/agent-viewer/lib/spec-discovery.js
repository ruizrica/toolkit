const fs = require("node:fs");
const path = require("node:path");

function discoverSpecDocuments(folderPath) {
  const preferred = [
    "1-requirements.md",
    "requirements.md",
    "2-design.md",
    "design.md",
    "3-tasks.md",
    "tasks.md",
  ];

  const found = [];
  for (const name of preferred) {
    const absolutePath = path.join(folderPath, name);
    if (fs.existsSync(absolutePath) && fs.statSync(absolutePath).isFile()) {
      found.push({
        filePath: name,
        label: labelFor(name),
        markdown: fs.readFileSync(absolutePath, "utf8"),
      });
    }
  }

  if (found.length > 0) return dedupe(found);

  const entries = fs.readdirSync(folderPath)
    .filter((name) => name.endsWith(".md"))
    .sort();

  return entries.map((name) => ({
    filePath: name,
    label: labelFor(name),
    markdown: fs.readFileSync(path.join(folderPath, name), "utf8"),
  }));
}

function labelFor(name) {
  return name
    .replace(/\.md$/i, "")
    .replace(/^\d+-/, "")
    .replace(/[-_]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function dedupe(items) {
  const seen = new Set();
  return items.filter((item) => {
    if (seen.has(item.filePath)) return false;
    seen.add(item.filePath);
    return true;
  });
}

module.exports = {
  discoverSpecDocuments,
  labelFor,
};
