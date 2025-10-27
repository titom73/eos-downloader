# Automatic PR Labeling System

## Overview

The repository automatically assigns labels to Pull Requests based on the PR title using the Conventional Commits format.

## Label Types

### Kind Labels (`kind:<type>`)

These labels indicate the **type** of change in the PR:

| Label | Description | Example PR Title |
|-------|-------------|-----------------|
| `kind:feat` | New feature or functionality | `feat(eos_downloader): add cache support` |
| `kind:fix` | Bug fix | `fix(cli): correct error message display` |
| `kind:cut` | Remove code or files | `cut(eos_downloader): remove deprecated API` |
| `kind:doc` | Documentation changes | `doc: update installation guide` |
| `kind:ci` | CI/CD pipeline changes | `ci: add workflow for automated tests` |
| `kind:bump` | Dependency version updates | `bump: update requests to 2.31.0` |
| `kind:test` | Adding or updating tests | `test(eos_downloader): add unit tests` |
| `kind:refactor` | Code refactoring | `refactor(cli): improve code structure` |
| `kind:revert` | Revert a previous commit | `revert: undo feature X` |
| `kind:make` | Build system or tooling changes | `make: update build configuration` |
| `kind:chore` | Maintenance tasks | `chore: cleanup temporary files` |

### Scope Labels (`scope:<scope>`)

These labels indicate the **scope** or module affected:

| Label | Description | Example PR Title |
|-------|-------------|-----------------|
| `scope:eos_downloader` | Core package changes | `feat(eos_downloader): add new parser` |
| `scope:eos_downloader.cli` | CLI-specific changes | `fix(eos_downloader.cli): improve output` |

## How It Works

The workflow `.github/workflows/pr-triage.yml` automatically:

1. **Parses** the PR title when opened, edited, or synchronized
2. **Extracts** the type (e.g., `feat`, `fix`) and scope (e.g., `eos_downloader`)
3. **Creates** labels if they don't exist (with predefined colors)
4. **Assigns** the corresponding `kind:<type>` and `scope:<scope>` labels to the PR

## Label Colors

- **Kind labels**: Green (`#0E8A16`) - indicating the nature of the change
- **Scope labels**: Blue (`#1D76DB`) - indicating the affected component

## PR Title Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

Examples:
feat(eos_downloader): add cache support for downloads
fix(eos_downloader.cli): correct output formatting
doc: update README with new examples
```

## Benefits

1. **Automatic Organization**: PRs are automatically categorized
2. **Better Filtering**: Easy to find PRs by type or scope
3. **Release Notes**: Labels help generate accurate changelogs
4. **Visual Clarity**: Quick identification of PR purpose

## Validation

The PR title is validated by the `check_pr_semantic` job, which ensures:
- The type is one of the allowed types
- The scope (if provided) is valid
- The format follows Conventional Commits specification

If validation fails, the PR cannot be merged until the title is corrected.

## Workflow Summary Display

After processing, the workflow shows a summary in the GitHub Actions UI:

```
🏷️ PR Labeling Summary

- ✅ Added kind:feat label
- ✅ Added scope:eos_downloader label
```

Or if no scope is found:

```
🏷️ PR Labeling Summary

- ✅ Added kind:doc label
- ℹ️ No scope found in PR title
```
