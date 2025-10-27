---
description: 'Prompt and workflow for generating conventional commit messages using a structured XML format. Guides users to create standardized, descriptive commit messages in line with the Conventional Commits specification, including instructions, examples, and validation.'
tools: ['run_in_terminal', 'get_terminal_output']
---

### Instructions

```xml
	<description>This file contains a prompt template for generating conventional commit messages. It provides instructions, examples, and formatting guidelines to help users write standardized, descriptive commit messages in accordance with the Conventional Commits specification.</description>
	<note>
```

### Workflow

**Follow these steps:**

1. Run `git status` to review changed files.
2. Run `git diff` or `git diff --cached` to inspect changes.
3. Stage your changes with `git add <file>`.
4. Construct your commit message using the following XML structure.
5. After generating your commit message, Copilot will automatically run the following command in your integrated terminal (no confirmation needed):

```bash
git commit -m "type(scope): description"
```

6. Just execute this prompt and Copilot will handle the commit for you in the terminal.

### Commit Message Structure

```xml
<commit-message>
	<type>feat|fix|cut|doc|ci|bump|test|refactor|revert|make|chore</type>
	<scope>eos_downloader|eos_downloader.cli|(optional)</scope>
	<description>A short, imperative summary of the change</description>
	<body>(optional: more detailed explanation)</body>
	<footer>(optional: e.g. BREAKING CHANGE: details, or issue references)</footer>
</commit-message>
```

### Commit Types (Synchronized with pr-triage.yml)

```xml
<commit-types>
	<type name="feat">New feature or functionality</type>
	<type name="fix">Bug fix</type>
	<type name="cut">Remove code or files (deprecated features)</type>
	<type name="doc">Documentation changes</type>
	<type name="ci">CI/CD pipeline changes</type>
	<type name="bump">Dependency version updates</type>
	<type name="test">Adding or updating tests</type>
	<type name="refactor">Code refactoring without changing functionality</type>
	<type name="revert">Revert a previous commit</type>
	<type name="make">Build system or tooling changes</type>
	<type name="chore">Maintenance tasks, no production code change</type>
</commit-types>
```

### Commit Scopes (Synchronized with pr-triage.yml)

```xml
<commit-scopes>
	<scope name="eos_downloader">Core package changes</scope>
	<scope name="eos_downloader.cli">CLI-specific changes</scope>
	<scope name="(none)">Scope is optional and can be omitted for broad changes</scope>
</commit-scopes>
```

### Examples

```xml
<examples>
	<example>feat(eos_downloader): add ability to parse arrays</example>
	<example>fix(eos_downloader.cli): correct button alignment in CLI output</example>
	<example>doc: update README with usage instructions</example>
	<example>refactor(eos_downloader): improve performance of data processing</example>
	<example>bump: update dependencies to latest versions</example>
	<example>ci: add new GitHub Actions workflow for testing</example>
	<example>test(eos_downloader): add unit tests for download manager</example>
	<example>cut(eos_downloader): remove deprecated legacy API endpoints</example>
	<example>feat!: send email on registration (BREAKING CHANGE: email service required)</example>
</examples>
```

### Validation

```xml
<validation>
	<type>Must be one of: feat, fix, cut, doc, ci, bump, test, refactor, revert, make, chore</type>
	<scope>Recommended scopes: eos_downloader, eos_downloader.cli (optional but encouraged)</scope>
	<description>Required. Use the imperative mood (e.g., "add", not "added")</description>
	<body>Optional. Use for additional context</body>
	<footer>Use for breaking changes or issue references</footer>
	<sync-note>Types and scopes are validated by pr-triage.yml workflow in pull requests</sync-note>
</validation>
```

### Pull Request Naming Convention

```xml
<pull-request-naming>
	<principle>Pull Request titles MUST follow Conventional Commits specification</principle>
	<principle>PR titles are validated by .github/workflows/pr-triage.yml</principle>
	<allowed-types>feat, fix, cut, doc, ci, bump, test, refactor, revert, make, chore</allowed-types>
	<allowed-scopes>eos_downloader, eos_downloader.cli (optional)</allowed-scopes>

	<single-commit-rule>
		<condition>When PR contains only ONE commit</condition>
		<requirement>PR title MUST match the commit message exactly</requirement>
		<validation>validateSingleCommitMatchesPrTitle: true in pr-triage.yml</validation>
		<example>
			<commit>feat(eos_downloader): add specific message when file is found in cache</commit>
			<pr-title>feat(eos_downloader): add specific message when file is found in cache</pr-title>
		</example>
	</single-commit-rule>

	<multi-commit-rule>
		<condition>When PR contains MULTIPLE commits</condition>
		<requirement>PR title should summarize the overall change using conventional commit format</requirement>
		<example>
			<commits>
				<commit>fix(eos_downloader): enhance error messages for missing versions</commit>
				<commit>feat(eos_downloader): add cache status messages</commit>
				<commit>test(eos_downloader): add tests for cache message display</commit>
			</commits>
			<pr-title>feat(eos_downloader): improve user feedback for downloads and cache</pr-title>
		</example>
	</multi-commit-rule>

	<rationale>
		<reason>Consistent PR titles improve changelog generation and release notes</reason>
		<reason>Makes PR history more searchable and understandable</reason>
		<reason>Facilitates automated semantic versioning</reason>
		<reason>PR titles are automatically validated by GitHub Actions workflow</reason>
	</rationale>

	<automatic-labeling>
		<principle>PRs are automatically labeled based on type and scope from the title</principle>
		<label-format>
			<kind>kind:&lt;type&gt; (e.g., kind:feat, kind:fix, kind:doc)</kind>
			<scope>scope:&lt;scope&gt; (e.g., scope:eos_downloader, scope:eos_downloader.cli)</scope>
		</label-format>
		<workflow>Implemented in .github/workflows/pr-triage.yml (label_kind_scope job)</workflow>
		<example>
			<pr-title>feat(eos_downloader): add cache support</pr-title>
			<labels>
				<label>kind:feat</label>
				<label>scope:eos_downloader</label>
			</labels>
		</example>
		<benefits>
			<benefit>Automatic PR categorization for better organization</benefit>
			<benefit>Easy filtering and searching of PRs by type or scope</benefit>
			<benefit>Visual clarity with color-coded labels (green for kind, blue for scope)</benefit>
			<benefit>Improved release notes generation</benefit>
		</benefits>
		<note>Labels are created automatically if they don't exist</note>
		<documentation>See .github/docs/PR_LABELING.md for complete documentation</documentation>
	</automatic-labeling>
</pull-request-naming>
```

### Final Step

```xml
<final-step>
	<cmd>git commit -m "type(scope): description"</cmd>
	<note>Replace with your constructed message. Include body and footer if needed.</note>
</final-step>
```
