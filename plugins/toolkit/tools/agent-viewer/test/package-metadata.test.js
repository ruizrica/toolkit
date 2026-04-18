const test = require('node:test');
const assert = require('node:assert/strict');
const pkg = require('../package.json');

test('package metadata is ready for open-source distribution', () => {
  assert.equal(pkg.name, 'agent-viewer');
  assert.equal(pkg.private, undefined);
  assert.equal(pkg.license, 'MIT');
  assert.equal(pkg.type, 'commonjs');
  assert.equal(pkg.bin['agent-viewer'], './bin/agent-viewer.js');
  assert.ok(pkg.repository && pkg.repository.url);
  assert.ok(pkg.homepage);
  assert.ok(pkg.bugs && pkg.bugs.url);
  assert.ok(Array.isArray(pkg.files) && pkg.files.length > 0);
  assert.ok(pkg.engines && pkg.engines.node);
  assert.ok(pkg.scripts && pkg.scripts.test);
});
