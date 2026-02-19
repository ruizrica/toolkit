# /design

Interactive design system generator that gathers brand preferences through Q&A, scaffolds semantic design tokens, and creates both standalone token files and Tailwind-integrated outputs. Finishes by invoking `/frontend-design` to produce a visual showcase of the generated tokens.

## Usage

```bash
/design [project name or path]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| project name or path | No | Where to output the design system (defaults to current directory) |

## Workflow Phases

The design pipeline runs through 5 phases:

### Phase 0: Context Detection

Scans the project for existing configuration:
- Existing `tokens.json` or `design-tokens.*` files (used as defaults)
- `tailwind.config.*` (auto-patched to import generated theme)
- `package.json` framework hints (React, Vue, Svelte, Sass)
- iOS/Android project files

### Phase 1: Interactive Q&A (7 Questions)

Questions are asked one at a time via interactive prompts:

| # | Topic | Options |
|---|-------|---------|
| 1 | Project context | Output path selection |
| 2 | Colors | Hex values, extract from project, or starter palette |
| 3 | Typography | System fonts, Google Fonts, or custom |
| 4 | Spacing | 4px base (Tailwind), 8px base (Material), or custom |
| 5 | Border radius | Rounded, sharp, pill, or custom |
| 6 | Shadows | Subtle, elevated, none, or custom |
| 7 | Output formats | Multi-select: CSS, SCSS, iOS Swift, Android XML, Style Dictionary |

Colors use **semantic naming**: `brand-green`, `content-primary`, `surface-muted` — not generic names like `primary-500`.

### Phase 2: Token Generation

Creates `design-system/tokens.json` as the canonical source of truth:
- **brand-\*** — Brand identity colors with full shade scales (50–950)
- **content-\*** — Text colors (primary, secondary, muted, inverse)
- **surface-\*** — Background colors (default, muted, elevated, inverse)
- **border-\*** — Border colors (default, muted)
- Typography, spacing, border radius, and shadow tokens

Shade scales are generated via HSL interpolation from the user-provided base color.

### Phase 3: Output Scaffolding

**Always generated (dual output):**

| File | Description |
|------|-------------|
| `design-system/tokens.json` | Canonical token source of truth |
| `design-system/tailwind/theme.js` | Tailwind theme extension with semantic classes |
| `design-system/README.md` | Usage guide with examples |

**Tailwind integration:**
- Existing `tailwind.config.*` is auto-patched to import the theme
- If no config exists, a fresh one is generated
- Enables classes like `text-brand-green`, `bg-surface-muted`, `text-content-primary`

**Additional formats (based on Q7 selection):**

| File | Description |
|------|-------------|
| `design-system/css/variables.css` | CSS custom properties (`:root` variables) |
| `design-system/scss/_variables.scss` | SCSS variables and maps |
| `design-system/ios/DesignTokens.swift` | Swift enums with Color extensions |
| `design-system/android/design_tokens.xml` | Android color/dimen resources |
| `design-system/tokens/style-dictionary.json` | CTI format for build pipelines |

### Phase 4: Sample Showcase

Invokes the `/frontend-design` skill to create production-grade sample components:
- Card component with surface colors, borders, shadows
- Button set (primary, secondary, ghost) using brand colors
- Form input with border and focus states
- Hero section showcasing typography and spacing

Output goes to `design-system/showcase/`.

### Phase 5: Summary

Reports generated files, Tailwind class examples, import instructions, and regeneration guidance.

## Output Structure

```
design-system/
├── tokens.json                    # Canonical source of truth
├── tailwind/
│   └── theme.js                   # Tailwind theme extension
├── css/
│   └── variables.css              # CSS custom properties (if selected)
├── scss/
│   └── _variables.scss            # SCSS variables (if selected)
├── ios/
│   └── DesignTokens.swift         # iOS tokens (if selected)
├── android/
│   └── design_tokens.xml          # Android tokens (if selected)
├── tokens/
│   └── style-dictionary.json      # Style Dictionary (if selected)
├── showcase/
│   └── index.html                 # Visual showcase (from /frontend-design)
└── README.md                      # Usage guide
```

## Tailwind Classes

After generation, these utility classes become available:

```
# Brand colors (with shade scales)
text-brand-green       bg-brand-green       border-brand-green
text-brand-green-50    bg-brand-green-50    border-brand-green-50
text-brand-green-500   bg-brand-green-500   border-brand-green-500

# Content colors
text-content-primary   text-content-secondary   text-content-muted

# Surface colors
bg-surface-default     bg-surface-muted     bg-surface-elevated

# Border colors
border-border-default  border-border-muted

# Typography
font-heading           font-body            font-mono

# Spacing, radius, shadows
p-4  m-8  gap-6       rounded-sm  rounded-lg    shadow-sm  shadow-md
```

## Examples

### Basic Usage

```bash
/design
```

Runs the full interactive pipeline in the current directory.

### With Project Path

```bash
/design my-app
```

Outputs to `my-app/design-system/`.

### Iterating on Existing Tokens

```bash
/design
```

If `design-system/tokens.json` already exists, the pipeline detects it and pre-populates Q&A with current values — making it easy to iterate.

## Key Design Decisions

- **Opus model** — High-quality aesthetic decisions for token generation
- **Semantic naming** — `brand-*`, `content-*`, `surface-*` instead of generic `primary-500`
- **Dual output** — Standalone token files + Tailwind integration, always
- **tokens.json is source of truth** — All formats derive from it
- **Auto-patches Tailwind** — Detects and extends existing config
- **No build dependencies** — Pure Claude generation, no npm packages needed
- **`/frontend-design` integration** — Visual proof that tokens work, not just config files

## See Also

- [/kiro](kiro.md) — Spec-driven development with interactive Q&A
- [/handbook](handbook.md) — Project documentation generation
- [/team](team.md) — Multi-agent coordination
