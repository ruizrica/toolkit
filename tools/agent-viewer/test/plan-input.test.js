const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { normalizePlanPayload, resolvePlanInput } = require('../lib/run-plan-viewer.js');

function withTempDir(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'agent-viewer-plan-'));
  try {
    fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test('resolvePlanInput loads markdown from --file and infers title from filename', () => {
  withTempDir((dir) => {
    const filePath = path.join(dir, 'roadmap.md');
    fs.writeFileSync(filePath, '# Roadmap\n', 'utf8');

    const result = resolvePlanInput({ file: filePath, title: null, input: null });
    assert.equal(result.filePath, path.resolve(filePath));
    assert.equal(result.title, 'roadmap');
    assert.equal(result.markdown, '# Roadmap\n');
  });
});

test('normalizePlanPayload prefers explicit title and inline markdown', () => {
  withTempDir((dir) => {
    const filePath = path.join(dir, 'ignored.md');
    fs.writeFileSync(filePath, '# Ignored\n', 'utf8');

    const result = normalizePlanPayload({
      title: 'Provided Title',
      filePath,
      markdown: '# Inline\n',
    }, { title: null });

    assert.equal(result.filePath, path.resolve(filePath));
    assert.equal(result.title, 'Provided Title');
    assert.equal(result.markdown, '# Inline\n');
  });
});

test('normalizePlanPayload falls back to file contents and basename title', () => {
  withTempDir((dir) => {
    const filePath = path.join(dir, 'release-plan.md');
    fs.writeFileSync(filePath, '# Release\n', 'utf8');

    const result = normalizePlanPayload({ filePath }, { title: null });
    assert.equal(result.filePath, path.resolve(filePath));
    assert.equal(result.title, 'release-plan');
    assert.equal(result.markdown, '# Release\n');
  });
});

test('normalizePlanPayload falls back to generic title when no file or title is provided', () => {
  const result = normalizePlanPayload({ markdown: '# Draft\n' }, { title: null });
  assert.equal(result.filePath, null);
  assert.equal(result.title, 'Plan Viewer');
  assert.equal(result.markdown, '# Draft\n');
});

test('CLI supports --input before the plan command', () => {
  const { parseCliArgs } = require('../lib/cli-args.js');
  const parsed = parseCliArgs(['--json', 'plan', '--input', 'examples/plan-payload.json']);
  assert.equal(parsed.command, 'plan');
  assert.equal(parsed.input, 'examples/plan-payload.json');
  assert.equal(parsed.json, true);
});
