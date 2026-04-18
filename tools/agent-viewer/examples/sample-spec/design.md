# Design

```mermaid
graph LR
  CLI[agent-viewer] --> Server[viewer-server]
  Server --> Browser[local browser]
  Browser --> Result[/result POST]
```

The spec viewer loads markdown files, renders them in the browser, and posts structured review results back to the local server.
