# agent-viewer

A lightweight standalone CLI for editable browser-based report review.

`agent-viewer` currently supports:
- **plan** — editable implementation plan review
- **spec** — editable multi-document spec review

The project is intended to grow into a broader JSON-driven report platform covering plan, spec, completion, and reports-style viewers, with Mermaid support and standalone export.

## Why this exists

`agent-viewer` packages a simple local workflow: load structured markdown or JSON, open a browser review UI on `127.0.0.1`, collect edits/comments, and emit a machine-readable result back to the calling tool or shell script.

It is designed to stay small, local-first, and easy to extend.

## Repository Layout

```text
agent-viewer/
├── assets/vendor/           # local Mermaid bundle
├── bin/                     # CLI entrypoint
├── examples/                # runnable sample payloads and markdown
├── lib/                     # viewer runtime and HTML generators
├── test/                    # lightweight Node-based tests and smoke checks
├── install.sh               # optional local installer
└── package.json
```

## Installation

### Development install

```bash
git clone https://github.com/your-org/agent-viewer.git
cd agent-viewer
npm install
npm link
```

Then verify the CLI:

```bash
agent-viewer --help
```

### Local convenience installer

If you want a simple local wrapper without `npm link`:

```bash
bash install.sh
```

By default this writes `agent-viewer` to `/usr/local/bin`. Override with `TARGET_DIR=/your/bin/path bash install.sh` if needed.

### Published package (future)

```bash
npm install -g agent-viewer
```

## Quick start

### Plan viewer from a markdown file

```bash
agent-viewer plan --file examples/sample-plan.md --json
```

### Plan viewer from a JSON payload

```bash
cat examples/plan-payload.json | agent-viewer plan --stdin --json
```

### Spec viewer from a folder

```bash
agent-viewer spec --folder examples/sample-spec --json
```

### Spec viewer from a JSON payload

```bash
cat examples/spec-payload.json | agent-viewer spec --stdin --json
```

## Usage

```bash
agent-viewer --help
agent-viewer plan --file .context/todo.md --json
agent-viewer spec --folder ~/.claude/plans/my-spec --json
```

## Development and Testing

This project uses Node's built-in test runner (`--test`) to keep setup minimal and dependency-conscious.

### Run tests

```bash
npm test        # Unit tests for CLI behavior, metadata, and parsing helpers
npm run smoke   # CLI smoke checks
npm run check   # Run all: test + smoke
```

Current automated coverage focuses on:
- package metadata and publishability checks
- CLI help and failure behavior
- plan input normalization
- spec discovery ordering and labels

All tests must pass before opening a pull request:

```bash
npm run check
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full contributor guidance and [CHANGELOG.md](./CHANGELOG.md) for release notes.

## Current Status

### Working
- CLI entrypoint
- Plan viewer
- Spec viewer
- Local Mermaid asset serving
- JSON/stdin/file input paths

### Planned next
- Completion viewer
- Reports index viewer
- Standalone HTML export for all report families
- Richer review/report contracts

## Notes

- The CLI serves browser UIs locally on `127.0.0.1`
- Mermaid is served from local vendored assets, not a CDN
- Results can be emitted as machine-readable JSON via `--json`
- The current implementation was split out from work originally incubated in `agent-toolkit`
