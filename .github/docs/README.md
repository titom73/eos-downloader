# GitHub Documentation Index

This directory contains documentation related to GitHub workflows, CI/CD, and repository management.

## 📚 Available Documentation

### Workflows & Automation

- **[PR Labeling System](./PR_LABELING.md)** - Automatic labeling of Pull Requests based on Conventional Commits
- **[Release Process](./release.md)** - How to create and manage releases
- **[Coverage Badge Setup](./COVERAGE_BADGE_SETUP.md)** - Configuration for coverage badges

### Development Guidelines

- **[Python Versions Management](./PYTHON_VERSIONS.md)** - How Python versions are managed across the project
- **[Documentation Quick Reference](./DOCS_QUICK_REFERENCE.md)** - Quick reference for documentation

## 🔧 GitHub Workflows

The repository uses several GitHub Actions workflows located in `.github/workflows/`:

- `pr-triage.yml` - Automatic PR labeling and validation
- `pr-management.yml` - Code testing, linting, and coverage
- `pull-request-rn-labeler.yml` - Release notes labeling
- `coverage-badge.yml` - Coverage badge generation
- `documentation.yml` - Documentation deployment
- `release.yml` - Release automation

## 🏷️ Label System

The repository uses an automatic labeling system for PRs:

- **`kind:<type>`** - Type of change (feat, fix, doc, etc.)
- **`scope:<scope>`** - Affected component (eos_downloader, eos_downloader.cli)
- **`rn: <type>`** - Release notes categorization (added post-merge)

See [PR Labeling System](./PR_LABELING.md) for details.

## 🚀 Contributing

When creating a Pull Request:

1. Follow [Conventional Commits](https://www.conventionalcommits.org/) format
2. Ensure PR title matches the commit message format
3. Labels will be automatically assigned
4. All checks must pass before merge

## 📖 Additional Resources

- [Main Documentation](../../docs/) - User-facing documentation
- [Contributing Guide](../../docs/contributing.md) - How to contribute
- [GitHub Instructions](./../instructions/) - Copilot instructions for code generation
