# Contributing to agent-viewer

Thanks for your interest in improving `agent-viewer`.

## Development setup

```bash
git clone <your-fork-or-repo-url>
cd agent-viewer
npm install
npm test
npm run smoke
```

For local development without publishing, you can link the CLI into your shell:

```bash
npm link
agent-viewer --help
```

You can also use the convenience installer:

```bash
bash install.sh
```

## Project structure

- `bin/` — CLI entrypoint
- `lib/` — viewer runtime, server, and HTML generators
- `assets/vendor/` — local frontend assets such as Mermaid
- `examples/` — runnable sample payloads and markdown files
- `test/` — lightweight Node-based tests and smoke checks

## Development expectations

- Keep the runtime lightweight and dependency-conscious.
- Prefer small, readable modules over framework-heavy abstractions.
- Add or update tests when changing CLI behavior, payload parsing, or file persistence.
- Keep README examples accurate and runnable.

## Validation

Before opening a pull request, run:

```bash
npm run check
```

This project currently uses Node's built-in test runner to keep setup small.

## Pull requests

Please include:

- a short summary of the change
- why the change is needed
- any CLI output or screenshots that help explain the behavior
- updates to docs/examples if the user-facing workflow changed
