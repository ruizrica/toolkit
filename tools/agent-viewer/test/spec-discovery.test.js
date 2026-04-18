const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { discoverSpecDocuments, labelFor } = require('../lib/spec-discovery.js');

function withTempDir(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'agent-viewer-spec-'));
  try {
    fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test('discoverSpecDocuments prefers requirements/design/tasks files in canonical order', () => {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, 'tasks.md'), '# Tasks\n');
    fs.writeFileSync(path.join(dir, 'design.md'), '# Design\n');
    fs.writeFileSync(path.join(dir, 'requirements.md'), '# Requirements\n');
    fs.writeFileSync(path.join(dir, 'notes.md'), '# Notes\n');

    const docs = discoverSpecDocuments(dir);
    assert.deepEqual(docs.map((doc) => doc.filePath), [
      'requirements.md',
      'design.md',
      'tasks.md',
    ]);
    assert.deepEqual(docs.map((doc) => doc.label), [
      'Requirements',
      'Design',
      'Tasks',
    ]);
  });
});

test('discoverSpecDocuments falls back to sorted markdown files when preferred files are absent', () => {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, 'z-last.md'), '# Z\n');
    fs.writeFileSync(path.join(dir, 'a-first.md'), '# A\n');

    const docs = discoverSpecDocuments(dir);
    assert.deepEqual(docs.map((doc) => doc.filePath), ['a-first.md', 'z-last.md']);
    assert.deepEqual(docs.map((doc) => doc.label), ['A First', 'Z Last']);
  });
});

test('discoverSpecDocuments includes both numbered and non-numbered preferred matches when present', () => {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, '1-requirements.md'), '# Requirements\n');
    fs.writeFileSync(path.join(dir, 'requirements.md'), '# Alternate Requirements\n');

    const docs = discoverSpecDocuments(dir);
    assert.deepEqual(docs.map((doc) => doc.filePath), [
      '1-requirements.md',
      'requirements.md',
    ]);
  });
});

test('discoverSpecDocuments accepts numbered preferred files', () => {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, '1-requirements.md'), '# Requirements\n');
    fs.writeFileSync(path.join(dir, '2-design.md'), '# Design\n');
    fs.writeFileSync(path.join(dir, '3-tasks.md'), '# Tasks\n');

    const docs = discoverSpecDocuments(dir);
    assert.deepEqual(docs.map((doc) => doc.filePath), [
      '1-requirements.md',
      '2-design.md',
      '3-tasks.md',
    ]);
  });
});

test('discoverSpecDocuments ignores non-markdown files during fallback discovery', () => {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, 'overview.md'), '# Overview\n');
    fs.writeFileSync(path.join(dir, 'notes.txt'), 'ignore');

    const docs = discoverSpecDocuments(dir);
    assert.deepEqual(docs.map((doc) => doc.filePath), ['overview.md']);
  });
});

test('labelFor normalizes filenames into readable labels', () => {
  assert.equal(labelFor('1-api_design.md'), 'Api Design');
  assert.equal(labelFor('tasks.md'), 'Tasks');
});
