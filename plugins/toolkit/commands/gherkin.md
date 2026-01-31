---
description: "Capture business logic from code into living Gherkin documentation. Analyze projects to extract rules, behaviors, and validation criteria. Validate implementations against captured rules."
argument-hint: "[folder path] [--url http://...] [--output .specs] [--validate --against spec.feature]"
allowed-tools: ["Task", "Read", "Write", "Glob", "Grep", "Bash", "AskUserQuestion"]
context: fork
agent: general-purpose
---

# Business Logic Capture System

ABOUTME: Extracts business rules from code and generates living Gherkin documentation.
ABOUTME: Uses parallel Haiku agents for analysis and Opus for synthesis.

## Dependency Check

**BEFORE doing anything else, verify required tools are installed:**

```bash
# Check for agent-browser (needed for visual analysis)
which agent-browser || npm install -g agent-browser

# Check for required Node.js (for any JS/TS project analysis)
which node || echo "Node.js required - install from nodejs.org"
```

If `agent-browser` is not found, install it automatically. If installation fails, warn the user but continue with code-only analysis.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MAIN AGENT (Opus)                                │
│                    Orchestration & Synthesis                             │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Phase 1: Discover │
                    │  Project Structure │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┬─────────────────────┐
        ▼                     ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ HAIKU AGENT 1 │   │ HAIKU AGENT 2 │   │ HAIKU AGENT 3 │   │ HAIKU AGENT 4 │
│  Page/Route   │   │   Component   │   │    API/       │   │   Visual/     │
│  Discovery    │   │   Analysis    │   │   Contract    │   │   Browser     │
│  (Code)       │   │   (Code)      │   │   (Code)      │   │(agent-browser)│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │                   │
        └─────────────────┬─┴───────────────────┴───────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    OPUS AGENT       │
              │  Synthesize Rules   │
              └─────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ HAIKU GEN 1   │ │ HAIKU GEN 2   │ │ HAIKU GEN N   │
│ Domain Rules  │ │ Domain Rules  │ │ Domain Rules  │
└───────────────┘ └───────────────┘ └───────────────┘
```

## Modes of Operation

### Mode 1: Capture (Default)
Analyze code and extract business rules into Gherkin specs.

```bash
/gherkin ./src/pages              # Analyze folder, extract business rules
/gherkin ./src --url http://localhost:3000  # Code + visual analysis
/gherkin ./src --output ./docs/specs        # Custom output directory
```

### Mode 2: Validate
Check if code/UI matches documented business rules.

```bash
/gherkin validate ./new-login --against .specs/authentication/login.feature
/gherkin validate --url http://localhost:3000/login --against .specs/authentication/login.feature
```

---

## Execution Flow

### Phase 0: Parse Arguments & Check Dependencies

Parse: **$ARGUMENTS**

Extract:
- `target_path`: The folder/file to analyze (required for capture mode)
- `--url`: Optional URL for visual/browser analysis
- `--output`: Output directory (default: `.specs/` in target path's root)
- `--validate`: Enable validation mode
- `--against`: Spec file to validate against (required with --validate)

**Dependency Check:**
```bash
# Ensure agent-browser is available for visual analysis
if ! command -v agent-browser &> /dev/null; then
    echo "Installing agent-browser..."
    npm install -g agent-browser
fi
```

If a `--url` is provided but `agent-browser` installation fails, ask the user:
- Continue with code-only analysis?
- Abort and fix dependencies?

### Phase 1: Project Discovery (Main Agent - Opus)

Analyze the target path to understand project structure:

1. **Detect project type:**
   - Check for `package.json` (Node/React/Vue/etc.)
   - Check for `requirements.txt` / `pyproject.toml` (Python)
   - Check for `go.mod` (Go)
   - Check for `Cargo.toml` (Rust)
   - Check for `*.csproj` (C#/.NET)

2. **Identify key directories:**
   - Pages/routes: `pages/`, `views/`, `routes/`, `screens/`
   - Components: `components/`, `ui/`, `widgets/`
   - API: `api/`, `handlers/`, `controllers/`, `services/`
   - Models: `models/`, `entities/`, `types/`, `schemas/`

3. **Detect frameworks:**
   - React, Vue, Angular, Svelte (frontend)
   - Express, FastAPI, Django, Rails (backend)
   - Next.js, Nuxt, SvelteKit (fullstack)

4. **Plan analysis scope:**
   - List domains/features to analyze
   - Determine which Haiku agents to launch

---

### Phase 2: Parallel Analysis (Haiku Agents)

Launch 3-4 Haiku agents in parallel using `Task` tool with `model: haiku`:

**Agent 1 - Page/Route Discovery:**
```
Analyze the codebase for pages and routes.

Search patterns:
- Glob: **/pages/**, **/views/**, **/routes/**, **/screens/**
- Grep: "router", "Route", "path:", "createRoute", "defineRoute"

For each page/route found, extract:
- Page name and file path
- URL pattern (e.g., /login, /users/:id)
- Purpose (inferred from name, comments, or content)
- Connected components or handlers
- Any guards/middleware (auth, validation)

Return as structured JSON:
{
  "pages": [
    {
      "name": "Login",
      "file": "src/pages/Login.tsx",
      "url": "/login",
      "purpose": "User authentication",
      "guards": ["guest-only"],
      "components": ["LoginForm", "SocialLogin"]
    }
  ]
}
```

**Agent 2 - Component/Form Analysis:**
```
Analyze components for business logic and validation rules.

Search patterns:
- Glob: **/*Form*, **/*Input*, **/components/**, **/ui/**
- Grep: "validate", "required", "pattern", "minLength", "maxLength",
        "yup", "zod", "joi", "validator", "rules"

For each component/form found, extract:
- Component name and file path
- Input fields with their validation rules
- Error messages (exact text when possible)
- Business rules encoded in the component
- State management patterns

Return as structured JSON:
{
  "components": [
    {
      "name": "LoginForm",
      "file": "src/components/LoginForm.tsx",
      "fields": [
        {
          "name": "email",
          "type": "email",
          "validations": ["required", "email-format"],
          "errorMessages": {
            "required": "Email is required",
            "format": "Please enter a valid email"
          }
        }
      ],
      "businessRules": [
        "Form submits on Enter key",
        "Remember me checkbox persists login"
      ]
    }
  ]
}
```

**Agent 3 - API/Contract Analysis:**
```
Analyze API endpoints and contracts.

Search patterns:
- Glob: **/api/**, **/handlers/**, **/controllers/**, **/routes/**
- Grep: "POST", "GET", "PUT", "DELETE", "router.", "app.",
        "@Controller", "@Route", "def route", "func Handle"

For each endpoint found, extract:
- HTTP method and path
- Request body schema (if POST/PUT)
- Response schema
- Error responses and codes
- Authentication requirements
- Rate limiting or other guards

Return as structured JSON:
{
  "endpoints": [
    {
      "method": "POST",
      "path": "/api/auth/login",
      "file": "src/api/auth.ts:45",
      "request": {
        "email": "string, required",
        "password": "string, required, min 8 chars"
      },
      "responses": {
        "200": "JWT token and user data",
        "401": "Invalid credentials",
        "429": "Too many attempts"
      },
      "auth": "none",
      "rateLimit": "5 attempts per 15 minutes"
    }
  ]
}
```

**Agent 4 - Visual/Browser Analysis (only if --url provided):**
```
Analyze the running application visually using agent-browser.

For each page/URL to analyze:

1. Navigate and capture:
   agent-browser open <url>
   agent-browser snapshot -i
   agent-browser screenshot .specs/_visual/<page-name>.png

2. For each form/interactive area, identify:
   - Input fields with their labels (may differ from code!)
   - Button text and purposes
   - Visible validation messages
   - Error states if testable
   - Navigation links and structure

3. Test basic interactions:
   - Submit empty forms to see validation messages
   - Check tab order and focus behavior
   - Note any loading states or animations

Return as structured JSON:
{
  "pages": [
    {
      "url": "/login",
      "title": "Sign In | MyApp",
      "screenshot": ".specs/_visual/login.png",
      "elements": [
        {"type": "input", "label": "Email address", "ref": "@e3"},
        {"type": "input", "label": "Password", "ref": "@e4"},
        {"type": "button", "text": "Sign in", "ref": "@e5"}
      ],
      "validationMessages": [
        "Please enter your email",
        "Password must be at least 8 characters"
      ],
      "navigation": [
        {"text": "Forgot password?", "href": "/forgot-password"},
        {"text": "Create account", "href": "/register"}
      ]
    }
  ]
}
```

---

### Phase 3: Rule Synthesis (Opus)

Combine all Haiku agent findings into a unified business rules document.

**For each domain/feature identified:**

1. **Cross-reference sources:**
   - Match components to pages
   - Match API endpoints to forms
   - Compare code validation with UI validation messages
   - Flag any discrepancies between code and visual analysis

2. **Extract business rules:**
   - Validation rules with exact constraints
   - Authorization rules (who can do what)
   - State transitions (workflows, statuses)
   - Error handling behaviors
   - Security rules (rate limiting, lockouts, etc.)

3. **Assign rule IDs:**
   - Format: `DOMAIN-NNN` (e.g., AUTH-001, PAY-003)
   - Group by domain for traceability

4. **Identify gaps:**
   - Rules without clear source
   - Conflicting implementations
   - Missing error handling

---

### Phase 4: Gherkin Generation (Parallel Haiku Agents)

For each domain/feature, launch a Haiku agent to generate the feature file.

**Agent prompt for each domain:**
```
Generate a Gherkin feature file for the [DOMAIN] domain.

Use these extracted rules:
[INSERT SYNTHESIZED RULES]

Follow these requirements:

1. Feature header with business description
2. Source annotations (file paths, URLs)
3. Rules section with IDs and descriptions
4. Scenarios covering:
   - Happy paths (@happy-path)
   - Error handling (@error-handling)
   - Validation (@validation)
   - Security (@security if applicable)
5. Data-driven scenarios for validations

Use BUSINESS language, not technical:
- BAD: "When I POST to /api/auth/login"
- GOOD: "When I submit my login credentials"

Include:
- Rule IDs as tags (e.g., @rule:AUTH-001)
- Source file references
- Exact error messages when known
```

---

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
├── users/
│   └── profile.feature          # Profile management
└── _visual/                     # Screenshots from agent-browser
    ├── login.png
    ├── register.png
    └── checkout.png
```

### _index.md Format

```markdown
# Business Rules Index

Generated: 2026-01-30
Source: ./src
URL: http://localhost:3000

## Domains

### Authentication (4 rules)
- [AUTH-001](authentication/login.feature#AUTH-001) - Email format validation
- [AUTH-002](authentication/login.feature#AUTH-002) - Account lockout after failures
- [AUTH-003](authentication/register.feature#AUTH-003) - Password strength requirements
- [AUTH-004](authentication/register.feature#AUTH-004) - Email uniqueness

### Payments (3 rules)
- [PAY-001](payments/checkout.feature#PAY-001) - Card validation
- [PAY-002](payments/checkout.feature#PAY-002) - Minimum order amount
- [PAY-003](payments/refunds.feature#PAY-003) - Refund window

## Discrepancies Found
- Login form shows "Email" but code uses "email_address" field
- API returns 403 but UI shows generic error message
```

---

## Feature File Format

```gherkin
@business-rules @authentication @login
Feature: User Login
  The login page allows registered users to authenticate
  and access their personalized dashboard.

  Source: src/pages/Login.tsx, src/api/auth.ts
  URL: /login
  Last analyzed: 2026-01-30

  # === BUSINESS RULES ===

  @rule:AUTH-001 @validation
  Rule: Email must be in valid format
    - Required field
    - Must match email format (user@domain.tld)
    - Max 255 characters
    - Error: "Please enter a valid email"

  @rule:AUTH-002 @security
  Rule: Account locks after 5 failed attempts
    - Temporary lock for 15 minutes
    - Shows "Too many attempts. Try again later."
    - Applies per-email, not per-IP

  # === SCENARIOS ===

  Background:
    Given I am on the login page

  @happy-path
  Scenario: Successful login with valid credentials
    Given I am a registered user with email "user@example.com"
    When I enter my email and password
    And I click "Sign in"
    Then I am redirected to the dashboard
    And I see my personalized welcome message

  @error-handling
  Scenario: Login fails with incorrect password
    Given I am a registered user
    When I enter my email with an incorrect password
    And I click "Sign in"
    Then I see error "Invalid email or password"
    And I remain on the login page
    # Note: Error intentionally vague for security

  @security @rule:AUTH-002
  Scenario: Account locks after too many failed attempts
    Given I am a registered user
    When I fail to login 5 times in a row
    Then my account is temporarily locked
    And I see "Too many attempts. Try again later."
    And I cannot attempt login for 15 minutes

  @validation @data-driven @rule:AUTH-001
  Scenario Outline: Email validation
    When I enter email "<input>"
    And I try to submit
    Then validation result is "<result>"
    And I see message "<message>"

    Examples:
      | input              | result  | message                     |
      | user@example.com   | valid   |                             |
      |                    | invalid | Please enter a valid email  |
      | not-an-email       | invalid | Please enter a valid email  |
      | user@              | invalid | Please enter a valid email  |
```

---

## Validation Mode

When `--validate` flag is used:

### Validation Workflow

1. **Parse spec file:**
   - Extract all rules with IDs
   - Extract expected behaviors (scenarios)
   - Note expected error messages

2. **Analyze target code/URL:**
   - Run same analysis agents as capture mode
   - Extract current implementation state

3. **Compare and report:**

```markdown
# Validation Report: login.feature

## Summary
- Rules checked: 4
- Compliant: 3
- Deviations: 1
- Missing: 0

## Details

### ✅ AUTH-001: Email validation
Implemented as documented in src/components/LoginForm.tsx:23

### ✅ AUTH-002: Account lockout
Implemented in src/api/auth.ts:89

### ⚠️ AUTH-003: Password requirements
DEVIATION: Spec requires 8+ chars, code requires 6+ chars
- Spec: "Password must be at least 8 characters"
- Code: minLength: 6 (src/components/LoginForm.tsx:45)

### ✅ AUTH-004: Remember me
Implemented as documented
```

### With agent-browser validation:

```bash
# For each documented scenario with a URL:
agent-browser open <url>

# Test validation scenarios
agent-browser fill @email ""
agent-browser click @submit
agent-browser snapshot -i  # Check for expected error

# Compare actual vs expected
# Report any differences
```

---

## Best Practices

### 1. Business-Readable Language
Write for non-technical stakeholders.

| Technical (BAD) | Business (GOOD) |
|-----------------|-----------------|
| `POST /api/users returns 201` | `Account is created successfully` |
| `localStorage.setItem('token')` | `User stays logged in` |
| `useState triggers re-render` | `Form updates in real-time` |

### 2. One Rule Per Scenario
Each scenario tests exactly ONE business rule.

### 3. Tag Strategy

**Domain tags:** `@authentication`, `@payments`, `@users`
**Rule tags:** `@rule:AUTH-001`, `@rule:PAY-003`
**Type tags:** `@happy-path`, `@error-handling`, `@validation`, `@security`
**Execution tags:** `@smoke`, `@regression`, `@manual`

### 4. Source Traceability
Always include source file references so rules can be traced back to code.

---

## Example Execution

For input: `/gherkin ./src --url http://localhost:3000`

1. Check `agent-browser` installed (install if needed)
2. Discover project is Next.js with TypeScript
3. Launch 4 parallel Haiku agents:
   - Agent 1 finds 5 pages in `./src/app/`
   - Agent 2 finds 12 components with validation
   - Agent 3 finds 8 API endpoints
   - Agent 4 captures screenshots and UI elements
4. Opus synthesizes 23 business rules across 4 domains
5. Launch 4 Haiku agents to generate feature files
6. Write output to `.specs/` with index and visual assets

---

Now analyze the target and extract business rules as living Gherkin documentation.
