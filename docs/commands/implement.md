<p align="center">
  <img src="../../assets/@implement.png" alt="Implement" width="120">
</p>

# /@implement

Process `@implement` comments in code files and convert them to documentation. This command finds implementation directives in your code, executes the requested changes, and transforms the comments into proper documentation.

## Usage

```bash
/@implement [file or directory to process]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| path | No | `.` | File or directory to process for @implement comments |

## How It Works

1. **Find** - Locate all `@implement` comments in the specified path
2. **Implement** - Execute the instructions in each comment
3. **Document** - Convert the @implement comment to proper documentation
4. **Format** - Add language-appropriate documentation (JSDoc, docstrings, etc.)

## Before and After

### Before

```typescript
// @implement: Add email validation function
```

### After

```typescript
/**
 * Validates email format using RFC 5322 standard regex
 * @param email - The email address to validate
 * @returns true if email format is valid
 */
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

## Examples

```bash
# Process a specific file
/@implement src/utils/validation.ts

# Process an entire directory
/@implement src/utils/

# Process current directory
/@implement
```

## Supported Comment Formats

```typescript
// @implement: Description of what to implement
```

```python
# @implement: Description of what to implement
```

```javascript
/* @implement: Description of what to implement */
```

## Documentation Formats

The command generates documentation appropriate to the language:

| Language | Format |
|----------|--------|
| TypeScript/JavaScript | JSDoc/TSDoc |
| Python | Docstrings (Google style) |
| Go | GoDoc comments |
| Rust | Rustdoc comments |
| Java | Javadoc |

## Best Practices

**Good @implement comments:**
```typescript
// @implement: Create a function that validates phone numbers
//             supporting US and international formats,
//             returning an object with isValid and formatted number

// @implement: Add error handling for the API call,
//             retry 3 times with exponential backoff
```

**Less effective:**
```typescript
// @implement: fix this
// @implement: add validation
```

## When to Use

- Marking TODO items for AI implementation
- Creating placeholders during design phase
- Delegating implementation details to AI
- Quick code scaffolding with documentation

## Workflow Integration

1. Write your code structure with `@implement` comments
2. Run `/@implement` to fill in implementations
3. Review the generated code and documentation
4. Commit the complete implementation

## See Also

- [/team](team.md) - Multi-agent implementation
- [codex-agent](../agents/codex.md) - Code generation
