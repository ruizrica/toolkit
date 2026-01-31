<p align="center">
  <img src="../../assets/gemini.png" alt="Gemini" width="120">
</p>

# Gemini Agent

A specialized agent that interfaces with Google Gemini CLI for advanced codebase analysis. Leverages Gemini's massive context window (up to 1 million tokens), Google Search integration, and native coding capabilities.

## When to Use

- Analyzing large codebases that exceed standard context limits (>100KB)
- Performing comprehensive multi-directory code reviews
- Generating architecture documentation
- Leveraging Google Search for real-time information and best practices
- Conducting security audits across entire repositories
- Verifying feature implementations project-wide

## Capabilities

- **Large Codebase Analysis** - Process entire repositories using 1M token context
- **Google Search Integration** - Built-in web search for current documentation
- **Native Coding Assistance** - Bug fixes, feature creation, test coverage
- **Architecture Documentation** - Generate comprehensive architectural overviews
- **Security Auditing** - Identify vulnerabilities with real-time advisory lookups
- **High Request Limits** - Generous API limits for personal and professional use

## Invocation

```bash
/toolkit:gemini-agent Analyze the authentication module for security issues
```

## Examples

**Large Codebase Analysis:**
```
Prompt: "Analyze our entire microservices architecture and identify potential bottlenecks"
```

**Security Audit with Current Standards:**
```
Prompt: "Review our authentication implementation against the latest 2025 security standards"
```

**Multi-File Refactoring:**
```
Prompt: "Convert all our API calls from callbacks to async/await pattern"
```

## Command Patterns

### Basic Analysis (Most Common)
```bash
gemini -p "Your analysis prompt here"
```

### Multiple Directory Inclusion
```bash
gemini --include-directories src,lib,tests -p "Your analysis prompt"
```

### Web-Grounded Responses
```bash
gemini -p "Search for [current topic] and provide analysis"
```

## Model Selection

**Default**: Gemini 2.5 Flash Lite - Works best for 99% of tasks. Do not specify the `-m` flag unless necessary.

**Pro Mode**: Only use Gemini 2.5 Pro when:
- Codebase exceeds 100k tokens
- User explicitly requests comprehensive analysis of massive repositories

## Best Practices

1. **Verify availability** - Check Gemini CLI is installed before use
2. **Use --include-directories** - Explicitly control what's analyzed
3. **Default to Flash Lite** - Unless context demands otherwise
4. **Leverage Google Search** - For current information and best practices
5. **Save important analyses** - Store in `.claude/analysis/` for reference

## Requirements

- **Gemini CLI** - Auto-installed if missing: `npm install -g @google/gemini-cli`
- **Google Account** - For authentication
- **Network Access** - Required for API calls

## Limitations

- Cannot directly modify files (use Edit/Write tools after analysis)
- Token limits still apply even with 1M context
- Cost considerations for large-scale usage
- Requires network connection

## See Also

- [cursor-agent](cursor.md) - Code review with sessions
- [droid-agent](droid.md) - Enterprise codebase analysis
- [/handbook](../commands/handbook.md) - Project documentation
