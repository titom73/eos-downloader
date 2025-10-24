# Python Version Management System

## 📋 Overview

This system allows you to **centralize and automatically synchronize** Python versions used across:

- ✅ GitHub Actions workflows (test matrices)
- ✅ `pyproject.toml` (classifiers and requires-python)
- ✅ Documentation
- ✅ Scripts and tools

## 🎯 Single Source of Truth

All Python versions are defined in a single file:

```text
.github/python-versions.json
```

### File Format

```json
{
  "versions": ["3.9", "3.10", "3.11", "3.12"],
  "min_version": "3.9",
  "max_version": "3.12",
  "default_version": "3.11"
}
```

**Fields**:

- `versions`: Complete list of versions to test
- `min_version`: Minimum required Python version
- `max_version`: Maximum supported Python version
- `default_version`: Default version for operations

## 🔄 Synchronization Workflow

### 1. Modify Versions

```bash
# Edit the JSON file
vim .github/python-versions.json

# Example: add Python 3.13
{
  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],
  "min_version": "3.9",
  "max_version": "3.13",
  "default_version": "3.11"
}
```

### 2. Synchronize Automatically

```bash
# Run the synchronization script
python .github/scripts/sync-python-versions.py
```

**This script automatically updates**:

- ✅ Classifiers in `pyproject.toml`
- ✅ `requires-python` in `pyproject.toml`

### 3. Verify Synchronization

```bash
# Check that everything is synchronized
python .github/scripts/check-python-versions.py
```

### 4. Use in Workflows

GitHub Actions workflows can automatically read versions from JSON:

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      python-versions: ${{ steps.set-versions.outputs.versions }}
    steps:
      - uses: actions/checkout@v5

      - name: Load Python versions
        id: set-versions
        run: |
          VERSIONS=$(cat .github/python-versions.json | jq -c '.versions')
          echo "versions=$VERSIONS" >> $GITHUB_OUTPUT

  test:
    needs: setup
    strategy:
      matrix:
        python-version: ${{ fromJson(needs.setup.outputs.python-versions) }}
    # ... rest of the job
```

## 🛠️ Available Scripts

### `.github/scripts/sync-python-versions.py`

**Purpose**: Synchronizes versions from JSON to pyproject.toml

**Usage**:

```bash
python .github/scripts/sync-python-versions.py
```

**Actions performed**:

1. Reads `.github/python-versions.json`
2. Updates Python classifiers in `pyproject.toml`
3. Updates `requires-python` in `pyproject.toml`
4. Displays a summary of changes

**Example output**:

```text
📋 Loading Python versions from JSON...
✅ Found versions: ['3.9', '3.10', '3.11', '3.12']
   Min version: 3.9
   Max version: 3.12

📝 Updating pyproject.toml...
✅ Updated Python version classifiers
✅ Updated requires-python

🎉 Synchronization complete!

💡 Next steps:
   1. Review changes: git diff pyproject.toml
   2. Run tests to ensure compatibility
   3. Commit changes: git add pyproject.toml && git commit -m 'chore: sync Python versions'
```

### `.github/scripts/check-python-versions.py`

**Purpose**: Verifies that versions are synchronized

**Usage**:

```bash
python .github/scripts/check-python-versions.py
```

**Return codes**:

- `0`: Everything is synchronized ✅
- `1`: Desynchronization detected ❌

**Example output (synchronized)**:

```text
✅ Python versions are synchronized
```

**Example output (out of sync)**:

```text
❌ Python versions are out of sync!

📋 Versions in .github/python-versions.json: ['3.9', '3.10', '3.11', '3.12']
📄 Versions in pyproject.toml: ['3.9', '3.10', '3.11']

💡 To fix this, run:
   python .github/scripts/sync-python-versions.py
```

## 🔍 Automatic CI Verification

The workflow `.github/workflows/check-python-versions.yml` automatically checks synchronization on:

- ✅ Every Pull Request modifying `python-versions.json` or `pyproject.toml`
- ✅ Every push to `main`

**If desynchronized**:

- ❌ The workflow fails
- 💡 Error message with instructions to fix

## 📝 Add Pre-commit Hook (Optional)

To check locally before each commit:

```yaml
# Add to .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-python-versions
        name: Check Python versions sync
        entry: python .github/scripts/check-python-versions.py
        language: system
        pass_filenames: false
        files: ^(\.github/python-versions\.json|pyproject\.toml)$
```

Then:

```bash
pre-commit install
```

## 🎯 Use Cases

### Add a New Python Version

1. **Update JSON**:

```json
{
  "versions": ["3.9", "3.10", "3.11", "3.12", "3.13"],
  "max_version": "3.13"
}
```

2. **Synchronize**:

```bash
python .github/scripts/sync-python-versions.py
```

3. **Verify**:

```bash
git diff pyproject.toml
```

4. **Commit**:

```bash
git add .github/python-versions.json pyproject.toml
git commit -m "feat: add Python 3.13 support"
```

### Remove an Old Version

1. **Update JSON**:

```json
{
  "versions": ["3.10", "3.11", "3.12"],
  "min_version": "3.10"
}
```

2. **Synchronize**:

```bash
python .github/scripts/sync-python-versions.py
```

3. **Test**:

```bash
tox
```

4. **Commit**:

```bash
git add .github/python-versions.json pyproject.toml
git commit -m "chore: drop Python 3.9 support"
```

## 🔄 Affected Workflows

The following workflows use this system:

| Workflow | Usage |
|----------|-------|
| `pr-management.yml` | Tests all versions in pre-commit, compiling, linting, typing, pytest jobs |
| `documentation.yml` | Uses `default_version` to build documentation |
| `release.yml` | Uses `default_version` for release |
| `check-python-versions.yml` | Verifies synchronization |

## ✅ Benefits

1. **Single source of truth**: One modification to update everything
2. **Automation**: Scripts to synchronize and verify
3. **CI/CD integration**: Automatic verification in workflows
4. **Fewer errors**: Avoids synchronization oversights
5. **Simplified maintenance**: Only one file to edit
6. **Clear documentation**: Readable and commented JSON format

## 🚨 Important Notes

1. **Test before committing**: Always run tests after modification
2. **Check CI**: Ensure all jobs pass
3. **Documentation**: Update docs if necessary
4. **Dependencies**: Verify dependency compatibility

## 📚 References

- **Sync script**: `.github/scripts/sync-python-versions.py`
- **Check script**: `.github/scripts/check-python-versions.py`
- **Verification workflow**: `.github/workflows/check-python-versions.yml`
- **Source of truth**: `.github/python-versions.json`

---

**Maintained by**: @titom73
**Last updated**: 2025-10-24
