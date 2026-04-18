# Data Models

## Report Families

| Type | Primary Content | Secondary Content | Output |
|------|------------------|-------------------|--------|
| plan | markdown | metadata | approval result |
| spec | documents[] | comments | changes/approval result |
| completion | summary + files | taskMarkdown | done/rollback result |
| reports | entries[] | search metadata | browser/index result |

## Mermaid-Capable Fields

- `plan.markdown`
- `spec.documents[].markdown`
- `completion.summary`
- `completion.taskMarkdown`
