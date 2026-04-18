# Changelog

All notable changes to `agent-viewer` will be documented in this file.

## [0.1.0] - 2025-04-12

### Added
- Publishable package metadata and npm scripts for `test`, `smoke`, and `check`
- Explicit MIT `LICENSE` file and `CONTRIBUTING.md`
- GitHub CI workflow plus issue and pull request templates
- Runnable example plan/spec payloads and sample markdown/spec folders
- Node built-in tests for package metadata, CLI help, plan input normalization, and spec discovery

### Changed
- `install.sh` now works relative to the cloned repository and can target a configurable bin directory
- `README.md` now documents development install, quick start flows, and validation commands
- CLI version output now reads from `package.json`

### Notes
- This release remains intentionally lightweight and dependency-free at runtime.
- Future phases will focus on deeper viewer tests, shared runtime cleanup, and new viewer families.
