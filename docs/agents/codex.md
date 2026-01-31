<p align="center">
  <img src="../../assets/codex.png" alt="Codex" width="120">
</p>

# Codex Agent

A specialized agent that interfaces with OpenAI Codex CLI to provide advanced code generation and analysis capabilities. Excels at understanding natural language descriptions and converting them into working code.

## When to Use

- Natural language to code conversion
- Complex algorithm implementation
- Code explanation or documentation
- Multi-language code translation
- Intelligent code completion beyond basic IDE features
- Bug fixing with AI assistance
- Code review and analysis tasks
- Prototype development from descriptions

## Capabilities

- **Natural Language to Code** - Converting descriptions into working code
- **Code Explanation** - Breaking down complex algorithms and logic
- **Code Completion** - Intelligent autocompletion and suggestions
- **Bug Detection** - Identifying and fixing code issues
- **Code Translation** - Converting between programming languages
- **Documentation Generation** - Creating clear code documentation
- **Algorithm Implementation** - Building efficient solutions to problems

## Invocation

```bash
/toolkit:codex-agent Create a function that validates email addresses using regex
```

## Examples

**Code Generation:**
```
Prompt: "Create a Python function that validates email addresses using proper regex patterns"
```

**Code Explanation:**
```
Prompt: "Explain what this recursive algorithm does step by step"
```

**Code Translation:**
```
Prompt: "Convert this Python function to JavaScript while maintaining functionality"
```

## Command Patterns

### Basic Code Generation
```bash
codex "Create a Python function that [description]"
```

### Code Explanation
```bash
codex explain --code="[code snippet]" --language="python"
```

### Bug Fixing
```bash
codex fix --file="buggy_code.py" --error="[error description]"
```

### Code Translation
```bash
codex translate --from="python" --to="javascript" --code="[code]"
```

### Documentation Generation
```bash
codex document --file="functions.py" --style="google"
```

### Test Generation
```bash
codex generate-tests --file="module.py" --framework="pytest"
```

## Model Selection

| Model | Use Case |
|-------|----------|
| code-davinci-002 | Complex code generation and analysis |
| code-cushman-001 | Simple completions (faster/cheaper) |

## Best Practices

1. **Choose appropriate models** - code-davinci-002 for complex, code-cushman-001 for simple
2. **Provide clear context** - Include imports, function signatures, comments
3. **Structure prompts effectively** - Be specific about requirements
4. **Validate outputs** - Always review generated code for correctness and security
5. **Use temperature settings** - Lower for deterministic, higher for creative
6. **Handle rate limits** - Monitor usage and implement delays

## Requirements

- **Codex CLI** - Auto-installed if missing: `npm i -g @openai/codex`
- **OpenAI API Key** - Required for authentication
- **Network Access** - Required for API calls

## Security Considerations

1. Never send sensitive data (API keys, passwords) to Codex
2. Review generated code for security vulnerabilities
3. Be cautious with code that handles user input
4. Validate all external dependencies and imports
5. Consider privacy implications when sending code to OpenAI

## When NOT to Use

- Simple file operations (use basic file tools)
- Text search and replace (use sed/grep)
- Offline work (requires internet)
- Tasks requiring guaranteed deterministic output

## See Also

- [cursor-agent](cursor.md) - Code review with sessions
- [opencode-agent](opencode.md) - Multi-model access
- [/@implement](../commands/implement.md) - Process @implement comments
