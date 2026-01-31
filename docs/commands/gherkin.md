<p align="center">
  <img src="../../assets/gherkin.png" alt="Gherkin" width="120">
</p>

# /gherkin

Capture business logic from code into living Gherkin documentation. This command analyzes projects to extract rules, behaviors, and validation criteria, then generates feature files with proper scenarios.

## Usage

```bash
/gherkin [folder path] [--url http://...] [--output .specs] [--validate --against spec.feature]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| folder path | Yes (capture) | Directory to analyze |
| `--url` | No | URL for visual/browser analysis |
| `--output` | No | Output directory (default: `.specs/`) |
| `--validate` | No | Enable validation mode |
| `--against` | With validate | Spec file to validate against |

## Modes of Operation

### Capture Mode (Default)

Analyze code and extract business rules into Gherkin specs:

```bash
# Code analysis only
/gherkin ./src/pages

# Code + visual analysis
/gherkin ./src --url http://localhost:3000

# Custom output directory
/gherkin ./src --output ./docs/specs
```

### Validate Mode

Check if code/UI matches documented business rules:

```bash
/gherkin validate ./new-login --against .specs/authentication/login.feature
/gherkin validate --url http://localhost:3000/login --against .specs/authentication/login.feature
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  OPUS ORCHESTRATOR                       │
│              Orchestration & Synthesis                   │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┬───────────────┐
           ▼               ▼               ▼               ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │ HAIKU: Page/  │ │ HAIKU:        │ │ HAIKU: API/   │ │ HAIKU: Visual │
   │ Route         │ │ Component     │ │ Contract      │ │ Browser       │
   │ Discovery     │ │ Analysis      │ │ Analysis      │ │ Analysis      │
   └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
                           │
                           ▼
               ┌─────────────────────┐
               │    OPUS: Rule       │
               │    Synthesis        │
               └─────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │ HAIKU: Gen    │ │ HAIKU: Gen    │ │ HAIKU: Gen    │
   │ Domain 1      │ │ Domain 2      │ │ Domain N      │
   └───────────────┘ └───────────────┘ └───────────────┘
```

## Output Structure

```
.specs/
├── _index.md                    # Domain overview, rule summary
├── authentication/
│   ├── login.feature            # Login page rules
│   ├── register.feature         # Registration rules
│   └── password-reset.feature   # Password reset flow
├── payments/
│   ├── checkout.feature         # Checkout process
│   └── refunds.feature          # Refund handling
└── _visual/                     # Screenshots from agent-browser
    ├── login.png
    └── checkout.png
```

## Feature File Format

```gherkin
@business-rules @authentication @login
Feature: User Login
  The login page allows registered users to authenticate
  and access their personalized dashboard.

  Source: src/pages/Login.tsx, src/api/auth.ts
  URL: /login

  # === BUSINESS RULES ===

  @rule:AUTH-001 @validation
  Rule: Email must be in valid format
    - Required field
    - Must match email format
    - Error: "Please enter a valid email"

  @rule:AUTH-002 @security
  Rule: Account locks after 5 failed attempts
    - Temporary lock for 15 minutes
    - Shows "Too many attempts. Try again later."

  # === SCENARIOS ===

  @happy-path
  Scenario: Successful login with valid credentials
    Given I am a registered user with email "user@example.com"
    When I enter my email and password
    And I click "Sign in"
    Then I am redirected to the dashboard

  @validation @data-driven @rule:AUTH-001
  Scenario Outline: Email validation
    When I enter email "<input>"
    Then validation result is "<result>"

    Examples:
      | input            | result  |
      | user@example.com | valid   |
      |                  | invalid |
      | not-an-email     | invalid |
```

## Tag Strategy

| Tag Type | Examples | Purpose |
|----------|----------|---------|
| Domain | `@authentication`, `@payments` | Group by feature area |
| Rule | `@rule:AUTH-001` | Link to specific rule |
| Type | `@happy-path`, `@error-handling`, `@validation` | Scenario category |
| Execution | `@smoke`, `@regression`, `@manual` | Test planning |

## Validation Report

When running in validate mode:

```markdown
# Validation Report: login.feature

## Summary
- Rules checked: 4
- Compliant: 3
- Deviations: 1

## Details

### ✅ AUTH-001: Email validation
Implemented as documented in src/components/LoginForm.tsx:23

### ⚠️ AUTH-003: Password requirements
DEVIATION: Spec requires 8+ chars, code requires 6+ chars
```

## Requirements

- **agent-browser** - For visual analysis (auto-installed if missing)
- **Node.js** - For agent-browser installation

## When to Use

- Documenting existing business logic
- Creating living specifications
- Validating implementations against specs
- Onboarding new team members
- Compliance documentation

## See Also

- [/handbook](handbook.md) - Project documentation
- [cursor-agent](../agents/cursor.md) - Code review
