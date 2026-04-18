# Design: Shared Runtime and Report-Specific Renderers

## Architecture Overview

```mermaid
graph LR
  A[Input Payload] --> B[Normalizer]
  B --> C[Plan Runtime]
  B --> D[Spec Runtime]
  B --> E[Completion Runtime]
  B --> F[Reports Runtime]
  C --> G[Viewer Server]
  D --> G
  E --> G
  F --> G
  G --> H[Browser UI]
```

## Design Notes

- Shared runtime should handle argument parsing, server lifecycle, browser launch, and JSON result emission.
- Report-specific renderers should own layout and interaction details.
- Standalone export should reuse the same report-family structure wherever possible.
