const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

const CLI = path.resolve(__dirname, '..', 'bin', 'agent-viewer.js');
const URL_RE = /\[agent-viewer\] opening (http:\/\/\S+)/;

function mkTmpDir(prefix) {
  return fs.mkdtempSync(path.join(os.tmpdir(), prefix));
}

function createBrowserStubDir() {
  const dir = mkTmpDir('av-stub-');
  for (const name of ['open', 'xdg-open', 'start']) {
    const stub = path.join(dir, name);
    fs.writeFileSync(stub, '#!/bin/sh\nexit 0\n');
    fs.chmodSync(stub, 0o755);
  }
  return dir;
}

async function waitForUrl(child, stderrRef, timeoutMs) {
  return await new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill('SIGKILL');
      reject(new Error(`timeout waiting for URL after ${timeoutMs}ms. stderr so far:\n${stderrRef.value}`));
    }, timeoutMs);
    const onData = () => {
      const match = stderrRef.value.match(URL_RE);
      if (match) {
        clearTimeout(timer);
        child.stderr.off('data', onData);
        resolve(match[1]);
      }
    };
    child.stderr.on('data', onData);
  });
}

async function waitForExit(child, timeoutMs) {
  return await new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill('SIGKILL');
      reject(new Error(`timeout waiting for CLI exit after ${timeoutMs}ms`));
    }, timeoutMs);
    child.on('exit', (code) => {
      clearTimeout(timer);
      resolve(code);
    });
  });
}

async function drive(args, { cwd, postBody, stdin, timeoutMs = 10000 } = {}) {
  const stubDir = createBrowserStubDir();
  const env = { ...process.env, PATH: `${stubDir}:${process.env.PATH}` };
  const fullArgs = [CLI, ...args, '--debug', '--json'];
  const child = spawn('node', fullArgs, {
    cwd,
    env,
    stdio: [stdin !== undefined ? 'pipe' : 'ignore', 'pipe', 'pipe'],
  });

  const stderrRef = { value: '' };
  let stdout = '';
  child.stdout.on('data', (c) => { stdout += c.toString(); });
  child.stderr.on('data', (c) => { stderrRef.value += c.toString(); });

  if (stdin !== undefined) {
    child.stdin.write(stdin);
    child.stdin.end();
  }

  const url = await waitForUrl(child, stderrRef, timeoutMs);

  // Verify server is live
  const pageResp = await fetch(url);
  assert.equal(pageResp.status, 200, 'GET / should return 200');
  const html = await pageResp.text();
  assert.match(html, /<textarea|<button/i, 'page HTML should contain UI elements');

  // POST /result with the simulated user action
  const postResp = await fetch(new URL('/result', url).toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postBody),
  });
  assert.equal(postResp.status, 200, `/result should 200. got: ${await postResp.text()}`);

  const exitCode = await waitForExit(child, timeoutMs);

  fs.rmSync(stubDir, { recursive: true, force: true });

  return { stdout, stderr: stderrRef.value, exitCode, url };
}

// ----------------------------------------------------------------------------
// Plan viewer — 3 cases
// ----------------------------------------------------------------------------

test('plan e2e — approve with no edits leaves file unchanged', async () => {
  const dir = mkTmpDir('e2e-plan-approve-');
  const planPath = path.join(dir, 'plan.md');
  const original = '# Plan\n\nPhase 1: do the thing\n';
  fs.writeFileSync(planPath, original, 'utf8');

  const { stdout, exitCode } = await drive(
    ['plan', '--file', planPath, '--title', 'Test'],
    {
      postBody: {
        action: 'approved',
        modified: false,
        markdown: original,
        comments: [],
      },
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'approved');
  assert.equal(result.modified, false);
  assert.equal(fs.readFileSync(planPath, 'utf8'), original, 'file content should be unchanged');

  fs.rmSync(dir, { recursive: true, force: true });
});

test('plan e2e — edit-then-approve writes new markdown back to disk', async () => {
  const dir = mkTmpDir('e2e-plan-edit-');
  const planPath = path.join(dir, 'plan.md');
  fs.writeFileSync(planPath, '# Original\n', 'utf8');

  const edited = '# Edited in viewer\n\nNew Phase 1\n';
  const { stdout, exitCode } = await drive(
    ['plan', '--file', planPath],
    {
      postBody: {
        action: 'approved',
        modified: true,
        markdown: edited,
        comments: [],
      },
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'approved');
  assert.equal(result.modified, true);
  assert.equal(result.markdown, edited);
  assert.equal(
    fs.readFileSync(planPath, 'utf8'),
    edited,
    'edited markdown must round-trip to disk',
  );

  // sidecar metadata should also exist
  const sidecar = `${planPath}.agent-viewer.json`;
  assert.ok(fs.existsSync(sidecar), 'sidecar .agent-viewer.json should be written');
  const sidecarData = JSON.parse(fs.readFileSync(sidecar, 'utf8'));
  assert.equal(sidecarData.lastAction, 'approved');

  fs.rmSync(dir, { recursive: true, force: true });
});

test('plan e2e — decline surfaces declined action without mutating file', async () => {
  const dir = mkTmpDir('e2e-plan-decline-');
  const planPath = path.join(dir, 'plan.md');
  const original = '# Plan to reject\n';
  fs.writeFileSync(planPath, original, 'utf8');

  const { stdout, exitCode } = await drive(
    ['plan', '--file', planPath],
    {
      postBody: {
        action: 'declined',
        modified: false,
        markdown: original,
        comments: [],
      },
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'declined');
  assert.equal(fs.readFileSync(planPath, 'utf8'), original);

  fs.rmSync(dir, { recursive: true, force: true });
});

// ----------------------------------------------------------------------------
// Spec viewer — 2 cases
// ----------------------------------------------------------------------------

function seedSpecFolder() {
  const dir = mkTmpDir('e2e-spec-');
  fs.writeFileSync(path.join(dir, 'requirements.md'), '# Requirements\n\nUser SHALL...\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'design.md'), '# Design\n\nArchitecture...\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'tasks.md'), '# Tasks\n\n- [ ] Task 1\n', 'utf8');
  return dir;
}

test('spec e2e — approve returns approved and leaves docs unchanged', async () => {
  const dir = seedSpecFolder();
  const originalReq = fs.readFileSync(path.join(dir, 'requirements.md'), 'utf8');

  const { stdout, exitCode } = await drive(
    ['spec', '--folder', dir, '--title', 'Test Spec'],
    {
      postBody: {
        action: 'approved',
        modified: false,
        markdownChanges: {},
        comments: [],
      },
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'approved');
  assert.equal(fs.readFileSync(path.join(dir, 'requirements.md'), 'utf8'), originalReq);

  fs.rmSync(dir, { recursive: true, force: true });
});

test('spec e2e — request-changes returns comments and optional doc edits', async () => {
  const dir = seedSpecFolder();
  const editedDesign = '# Design (revised)\n\nUpdated architecture section\n';

  const { stdout, exitCode } = await drive(
    ['spec', '--folder', dir],
    {
      postBody: {
        action: 'changes_requested',
        modified: true,
        markdownChanges: { 'design.md': editedDesign },
        comments: [
          { text: 'Clarify the data model', docKey: 'design.md', index: 0 },
        ],
      },
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'changes_requested');
  assert.equal(result.comments.length, 1);
  assert.equal(result.comments[0].text, 'Clarify the data model');
  assert.equal(
    fs.readFileSync(path.join(dir, 'design.md'), 'utf8'),
    editedDesign,
    'spec edits must round-trip to disk',
  );

  // sidecar spec-comments.json
  const sidecar = path.join(dir, 'spec-comments.json');
  assert.ok(fs.existsSync(sidecar));
  const sidecarData = JSON.parse(fs.readFileSync(sidecar, 'utf8'));
  assert.equal(sidecarData.lastAction, 'changes_requested');

  fs.rmSync(dir, { recursive: true, force: true });
});

// ----------------------------------------------------------------------------
// Completion viewer — 1 case
// ----------------------------------------------------------------------------

test('completion e2e — done action returns cleanly', async () => {
  const payload = {
    title: 'Completion Test',
    summary: '## Shipped\n\nDone.',
    baseRef: 'HEAD',
    totalAdditions: 0,
    totalDeletions: 0,
    taskMarkdown: '- [x] Task 1',
    files: [],
  };

  const { stdout, exitCode } = await drive(
    ['completion', '--stdin'],
    {
      postBody: { action: 'done', rolledBackFiles: [] },
      stdin: JSON.stringify(payload),
    }
  );

  assert.equal(exitCode, 0);
  const result = JSON.parse(stdout);
  assert.equal(result.action, 'done');
});
