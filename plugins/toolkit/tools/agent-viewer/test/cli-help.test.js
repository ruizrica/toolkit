const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');

const cliPath = path.resolve(__dirname, '../bin/agent-viewer.js');

function run(args) {
  return spawnSync(process.execPath, [cliPath, ...args], {
    encoding: 'utf8',
  });
}

test('top-level help prints available commands', () => {
  const result = run(['--help']);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /plan/);
  assert.match(result.stdout, /spec/);
});

test('plan help prints command-specific options', () => {
  const result = run(['plan', '--help']);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /--file <path>/);
  assert.match(result.stdout, /--stdin/);
});

test('unknown command fails with a clear error', () => {
  const result = run(['nope']);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Unknown command/);
});
