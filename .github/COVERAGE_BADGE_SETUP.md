# Coverage Badge Setup Guide

## Overview

This project uses GitHub Actions to automatically generate and update a coverage badge that displays the current test coverage percentage.

## Setup Instructions

### Step 1: Create a Gist for the Badge

1. Go to https://gist.github.com/
2. Create a **public** gist with any filename (e.g., `eos-downloader-coverage.json`)
3. Add some placeholder content: `{"schemaVersion": 1}`
4. Click "Create public gist"
5. Copy the Gist ID from the URL (e.g., `https://gist.github.com/username/abc123def456` → Gist ID is `abc123def456`)

### Step 2: Add Gist ID to Repository Secrets

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GIST_ID`
4. Value: Paste your Gist ID from Step 1
5. Click "Add secret"

### Step 3: Add Coverage Badge to README

Add this line to your `README.md` (replace `YOUR_GITHUB_USERNAME` and `YOUR_GIST_ID`):

```markdown
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_GIST_ID/raw/eos-downloader-coverage.json)](https://github.com/titom73/eos-downloader/actions/workflows/coverage-badge.yml)
```

**Example** (replace with your actual values):
```markdown
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/titom73/abc123def456/raw/eos-downloader-coverage.json)](https://github.com/titom73/eos-downloader/actions/workflows/coverage-badge.yml)
```

### Step 4: Trigger the Workflow

The coverage badge workflow runs automatically on every push to `main`. To trigger it manually:

1. Go to Actions → Coverage Badge
2. Click "Run workflow" → "Run workflow"
3. Wait for the workflow to complete
4. The badge in your README will update automatically

## How It Works

### Workflow: `coverage-badge.yml`

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Install Python dependencies
3. Run pytest with coverage (`--cov=eos_downloader --cov-branch`)
4. Extract coverage percentage from `coverage.json`
5. Update the Gist with the new badge data
6. Upload coverage report as artifact

### Workflow: `pr-management.yml` (Enhanced)

**New Feature: Coverage Comments on PRs**

When a PR is created or updated, the workflow will:
1. Run all tests with coverage
2. Extract coverage metrics
3. Post a comment on the PR with:
   - Overall coverage percentage
   - Total/covered/missing statements
   - Branch coverage
   - Status emoji (✅ ≥80%, ⚠️ 60-79%, ❌ <60%)

## Badge Color Ranges

The badge color automatically adjusts based on coverage:

- **🟢 Green**: 80-100% coverage (excellent)
- **🟡 Yellow**: 60-79% coverage (acceptable)
- **🟠 Orange**: 40-59% coverage (needs improvement)
- **🔴 Red**: 0-39% coverage (critical)

## Coverage Reports

Coverage reports are available in two places:

1. **Workflow Artifacts**: Each workflow run uploads `coverage.json` and `.coverage` files
   - Navigate to: Actions → Coverage Badge → Latest run → Artifacts
   - Download: `coverage-report.zip`
   - Retention: 30 days

2. **Local Generation**:
   ```bash
   # Run tests with coverage
   pytest --cov=eos_downloader --cov-report=html

   # Open HTML report
   open htmlcov/index.html
   ```

## Troubleshooting

### Badge Not Updating

1. Check that the workflow completed successfully
2. Verify the Gist ID secret is correct
3. Ensure the Gist is public (not secret)
4. Clear your browser cache (badges are cached by shields.io)

### Workflow Permission Errors

If you see permission errors:
1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"
4. Click "Save"

### Badge Shows "Invalid"

- The Gist URL might be incorrect
- Wait a few minutes for shields.io cache to refresh
- Verify the Gist contains valid JSON

## Manual Badge Alternative

If you prefer a simpler approach without Gists, you can use a static badge:

```markdown
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml)
```

Update the percentage manually after running coverage locally.

## Resources

- [Dynamic Badges Action](https://github.com/schneegans/dynamic-badges-action)
- [Shields.io Documentation](https://shields.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
