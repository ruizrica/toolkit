const { spawnSync } = require('node:child_process');
const path = require('node:path');

const cliPath = path.resolve(__dirname, '../bin/agent-viewer.js');

function check(args) {
  const result = spawnSync(process.execPath, [cliPath, ...args], { encoding: 'utf8' });
  if (result.status !== 0) {
    process.stderr.write(result.stderr || `Command failed: ${args.join(' ')}\n`);
    process.exit(result.status || 1);
  }
}

check(['--help']);
check(['--version']);
check(['plan', '--help']);
check(['spec', '--help']);
process.stdout.write('smoke checks passed\n');
