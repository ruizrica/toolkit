const { version: VERSION } = require("../package.json");

function printTopLevelHelp(command) {
  if (command === "plan") {
    console.log(`agent-viewer plan - editable plan review in a local web viewer

Usage:
  agent-viewer plan --file <path> [options]
  cat payload.json | agent-viewer plan --stdin [options]
  agent-viewer plan --input <payload.json> [options]

Options:
  --file <path>        Markdown file to load and update in-place
  --input <path>       JSON payload file with viewer input
  --stdin              Read JSON payload from stdin
  --title <text>       Viewer title
  --review-id <id>     Stable review round identifier
  --json               Emit machine-readable JSON on stdout
  --debug              Emit diagnostic logs to stderr
  --help               Show this help

Payload shape:
  {
    "title": "Implementation Plan",
    "filePath": ".context/todo.md",
    "markdown": "# Plan..."
  }
`);
    return;
  }

  if (command === "spec") {
    console.log(`agent-viewer spec - editable multi-document spec review in a local web viewer

Usage:
  agent-viewer spec --folder <path> [options]
  cat payload.json | agent-viewer spec --stdin [options]
  agent-viewer spec --input <payload.json> [options]

Options:
  --folder <path>      Spec folder containing markdown docs
  --input <path>       JSON payload file with viewer input
  --stdin              Read JSON payload from stdin
  --title <text>       Viewer title
  --review-id <id>     Stable review round identifier
  --json               Emit machine-readable JSON on stdout
  --debug              Emit diagnostic logs to stderr
  --help               Show this help

Payload shape:
  {
    "title": "Auth Spec",
    "folderPath": "~/.claude/plans/auth-spec",
    "documents": [
      { "filePath": "1-requirements.md", "label": "Requirements", "markdown": "# Requirements..." }
    ]
  }
`);
    return;
  }

  if (command === "completion") {
    console.log(`agent-viewer completion - completion/work summary report viewer

Usage:
  agent-viewer completion --input <payload.json> [options]
  cat payload.json | agent-viewer completion --stdin [options]

Options:
  --input <path>       JSON payload file with completion report data
  --stdin              Read JSON payload from stdin
  --json               Emit machine-readable JSON on stdout
  --debug              Emit diagnostic logs to stderr
  --help               Show this help
`);
    return;
  }

  console.log(`agent-viewer - lightweight editable plan/spec web viewer CLI for Claude Code workflows

Usage:
  agent-viewer <command> [options]

Commands:
  plan                 Open editable plan review viewer
  spec                 Open editable spec review viewer
  completion           Open completion/work summary report viewer

Global Options:
  --help               Show this help
  --version, -V        Show version
  --json               Emit machine-readable JSON on stdout
  --debug              Emit diagnostic logs to stderr

Examples:
  agent-viewer plan --file .context/todo.md --json
  agent-viewer --json plan --file .context/todo.md
  cat payload.json | agent-viewer plan --stdin --json
  agent-viewer spec --folder ~/.claude/plans/auth-spec --json
  agent-viewer spec --input spec-payload.json --json
`);
}

function printVersion() {
  console.log(VERSION);
}

function fail(message, code = 1) {
  process.stderr.write(`agent-viewer: ${message}\n`);
  process.exit(code);
}

function parseCliArgs(argv) {
  const parsed = {
    command: null,
    help: false,
    commandHelp: false,
    version: false,
    json: false,
    debug: false,
    file: null,
    folder: null,
    input: null,
    stdin: false,
    title: null,
    reviewId: null,
  };

  const args = [...argv];
  if (args[0] && !args[0].startsWith("-")) {
    parsed.command = args.shift();
  }

  while (args.length > 0) {
    const arg = args.shift();
    switch (arg) {
      case "--help":
      case "-h":
        if (parsed.command) parsed.commandHelp = true;
        else parsed.help = true;
        break;
      case "--version":
      case "-V":
        parsed.version = true;
        break;
      case "--json":
        parsed.json = true;
        break;
      case "--debug":
        parsed.debug = true;
        break;
      case "--file":
        parsed.file = args.shift() || fail("--file requires a path");
        break;
      case "--folder":
        parsed.folder = args.shift() || fail("--folder requires a path");
        break;
      case "--input":
        parsed.input = args.shift() || fail("--input requires a path");
        break;
      case "--stdin":
        parsed.stdin = true;
        break;
      case "--title":
        parsed.title = args.shift() || fail("--title requires text");
        break;
      case "--review-id":
        parsed.reviewId = args.shift() || fail("--review-id requires an id");
        break;
      default:
        if (!parsed.command && (arg === "plan" || arg === "spec")) {
          parsed.command = arg;
          break;
        }
        fail(`Unknown argument: ${arg}`);
    }
  }

  return parsed;
}

module.exports = {
  VERSION,
  parseCliArgs,
  printTopLevelHelp,
  printVersion,
  fail,
};
