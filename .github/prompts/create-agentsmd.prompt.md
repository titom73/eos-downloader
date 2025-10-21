[Move this file to .github/prompts/create-agentsmd.prompt.md. No changes to file content required.]
- How to start development server
- Build commands
- Watch/hot-reload setup
- Package manager specifics (npm, pnpm, yarn, etc.)

#### Testing Instructions

- How to run tests (unit, integration, e2e)
- Test file locations and naming conventions
- Coverage requirements
- Specific test patterns or frameworks used
- How to run subset of tests or focus on specific areas

#### Code Style Guidelines

- Language-specific conventions
- Linting and formatting rules
- File organization patterns
- Naming conventions
- Import/export patterns

#### Build and Deployment

- Build commands and outputs
- Environment configurations
- Deployment steps and requirements
- CI/CD pipeline information

### 3. Optional but Recommended Sections

#### Security Considerations

- Security testing requirements
- Secrets management
- Authentication patterns
- Permission models

#### Monorepo Instructions (if applicable)

- How to work with multiple packages
- Cross-package dependencies
- Selective building/testing
- Package-specific commands

#### Pull Request Guidelines

- Title format requirements
- Required checks before submission
- Review process
- Commit message conventions

#### Debugging and Troubleshooting

- Common issues and solutions
- Logging patterns
- Debug configuration
- Performance considerations

## Example Template

Use this as a starting template and customize based on the specific project:

```markdown
# AGENTS.md

## Project Overview

[Brief description of the project, its purpose, and key technologies]

## Setup Commands

- Install dependencies: `[package manager] install`
- Start development server: `[command]`
- Build for production: `[command]`

## Development Workflow

- [Development server startup instructions]
- [Hot reload/watch mode information]
- [Environment variable setup]

## Testing Instructions

- Run all tests: `[command]`
- Run unit tests: `[command]`
- Run integration tests: `[command]`
- Test coverage: `[command]`
- [Specific testing patterns or requirements]

## Code Style

- [Language and framework conventions]
- [Linting rules and commands]
- [Formatting requirements]
- [File organization patterns]

## Build and Deployment

- [Build process details]
- [Output directories]
- [Environment-specific builds]
- [Deployment commands]

## Pull Request Guidelines

- Title format: [component] Brief description
- Required checks: `[lint command]`, `[test command]`
- [Review requirements]

## Additional Notes

- [Any project-specific context]
- [Common gotchas or troubleshooting tips]
- [Performance considerations]
```

## Working Example from agents.md

Here's a real example from the agents.md website:

```markdown
# Sample AGENTS.md file

## Dev environment tips

- Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
- Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
- Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
- Check the name field inside each package's package.json to confirm the right name—skip the top-level one.

## Testing instructions

- Find the CI plan in the .github/workflows folder.
- Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
- From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
- To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
- Fix any test or type errors until the whole suite is green.
- After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
- Add or update tests for the code you change, even if nobody asked.

## PR instructions

- Title format: [<project_name>] <Title>
- Always run `pnpm lint` and `pnpm test` before committing.
```

## Implementation Steps

1. **Analyze the project structure** to understand:

   - Programming languages and frameworks used
   - Package managers and build tools
   - Testing frameworks
   - Project architecture (monorepo, single package, etc.)

2. **Identify key workflows** by examining:

   - package.json scripts
   - Makefile or other build files
   - CI/CD configuration files
   - Documentation files

3. **Create comprehensive sections** covering:

   - All essential setup and development commands
   - Testing strategies and commands
   - Code style and conventions
   - Build and deployment processes

4. **Include specific, actionable commands** that agents can execute directly

5. **Test the instructions** by ensuring all commands work as documented

6. **Keep it focused** on what agents need to know, not general project information

## Best Practices

- **Be specific**: Include exact commands, not vague descriptions
- **Use code blocks**: Wrap commands in backticks for clarity
- **Include context**: Explain why certain steps are needed
- **Stay current**: Update as the project evolves
- **Test commands**: Ensure all listed commands actually work
- **Consider nested files**: For monorepos, create AGENTS.md files in subprojects as needed

## Monorepo Considerations

For large monorepos:

- Place a main AGENTS.md at the repository root
- Create additional AGENTS.md files in subproject directories
- The closest AGENTS.md file takes precedence for any given location
- Include navigation tips between packages/projects

## Final Notes

- AGENTS.md works with 20+ AI coding tools including Cursor, Aider, Gemini CLI, and many others
- The format is intentionally flexible - adapt it to your project's needs
- Focus on actionable instructions that help agents understand and work with your codebase
- This is living documentation - update it as your project evolves

When creating the AGENTS.md file, prioritize clarity, completeness, and actionability. The goal is to give any coding agent enough context to effectively contribute to the project without requiring additional human guidance.
