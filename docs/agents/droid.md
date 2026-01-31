<p align="center">
  <img src="../../assets/droid.png" alt="Droid" width="120">
</p>

# Droid Agent

A specialized agent that interfaces with Factory's Droid CLI to provide enterprise-grade code generation, analysis, and collaborative development capabilities. Excels at understanding codebases contextually and making thoughtful, reviewable changes.

## When to Use

- Codebase analysis and architecture understanding
- Code modifications requiring transparent review workflows
- Security audits and vulnerability assessments
- Enterprise tool integration (Jira, Notion, Slack)
- Git operations with conversational intelligence
- Following team conventions and organizational knowledge
- Complex features requiring specification-driven development

## Capabilities

- **Codebase Analysis** - Understanding architecture, technologies, entry points
- **Contextual Code Changes** - Modifications with transparent review workflows
- **Security Auditing** - Identifying vulnerabilities and creating remediation plans
- **Enterprise Integration** - Working with Jira, Notion, Slack, and other tools
- **Git Operations** - Intelligent version control with conversational commands
- **Organizational Knowledge** - Following team conventions and coding standards
- **Specification-Driven Development** - Planning before implementation

## Invocation

```bash
/toolkit:droid-agent Analyze this project and explain the architecture
```

## Examples

**Codebase Analysis:**
```
Prompt: "Analyze this codebase and explain the overall architecture"
```

**Enterprise Integration:**
```
Prompt: "Implement the feature described in this Jira ticket: https://company.atlassian.net/browse/PROJ-123"
```

**Security Audit:**
```
Prompt: "Audit this codebase for security vulnerabilities and create a remediation plan"
```

## Command Patterns

### Codebase Analysis
```
> analyze this codebase and explain the overall architecture
> what technologies and frameworks does this project use?
> where are the main entry points and how is testing set up?
```

### Code Modifications
```
> add comprehensive logging to the main application startup
> refactor the authentication module to use JWT tokens
```

### Security Auditing
```
> audit this codebase for security vulnerabilities
> check for SQL injection vulnerabilities in the database layer
```

### Enterprise Tool Integration
```
> implement the feature described in this Jira ticket: [URL]
> check the Notion doc for requirements
```

### Git Operations
```
> review my uncommitted changes and suggest improvements
> create a well-structured commit following team conventions
```

## Transparent Review Process

When making changes, Droid will:

1. **Analyze** - Review your current setup
2. **Propose** - Show specific changes with a clear plan
3. **Display** - Show exactly what will be modified
4. **Wait** - Require your approval before applying

## Specification Mode

For larger features, use Specification Mode which:
- Automatically provides planning before implementation
- Breaks down complex tasks into manageable steps
- Ensures alignment with requirements before coding

## Best Practices

1. **Be specific with context** - Include details about the issue or feature
2. **Use specification mode** - For complex features needing automatic planning
3. **Leverage organizational knowledge** - Reference team standards
4. **Always review proposed changes** - Use the transparent diff view
5. **Integrate enterprise tools** - Connect Jira, Notion, Slack for context
6. **Follow the review workflow** - Never skip the approval step

## Requirements

- **Droid CLI** - Auto-installed: `curl -fsSL https://app.factory.ai/cli | sh`
- **Network Access** - Required for API calls
- **Factory Account** - For authentication

## Security Considerations

1. Review all proposed changes before approval
2. Ensure enterprise integrations use proper authentication
3. Be cautious with code that handles sensitive data
4. Follow compliance requirements for your organization
5. Use MCP integrations for additional security tooling

## When NOT to Use

- Quick one-off scripts without review needs
- Tasks that don't benefit from organizational context
- Simple file operations that don't need AI assistance
- Offline work (requires internet)
- Tasks where review workflow would be overhead

## See Also

- [gemini-agent](gemini.md) - Large codebase analysis
- [cursor-agent](cursor.md) - Code review with sessions
- [/review](../commands/review.md) - Code review workflow
