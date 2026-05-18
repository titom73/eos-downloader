---
name: bump-release
description: Bump the project version using bumpver, update pyproject.toml, and prepare a release PR
disable-model-invocation: true
---

Bump the eos-downloader version following the project's bumpver workflow.

Usage: /bump-release [patch|minor|major]
Default level: patch

Steps:
1. Show current version: `uv run bumpver show`
2. Dry-run the bump and display the diff: `uv run bumpver update --<level> --dry`
3. Ask the user to confirm before applying
4. Apply the bump: `uv run bumpver update --<level>`
   - This updates `pyproject.toml` fields: `current_version` and `version = "v{version}"`
   - Creates a commit automatically (bumpver is configured with `commit = true`)
5. Remind the user that `tag = false` and `push = false` in bumpver config — they must push manually
6. Suggest: `git push origin main` then let GitHub Actions handle the release via `.github/workflows/release.yml` (OIDC Trusted Publishing to PyPI)

Version pattern: MAJOR.MINOR.PATCH (e.g. 0.15.0 → 0.15.1 for patch)
