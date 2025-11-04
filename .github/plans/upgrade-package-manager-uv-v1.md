---
goal: Migrate eos-downloader project from pip/setuptools to UV package manager
version: 1.1
date_created: 2025-11-04
last_updated: 2025-11-04
owner: Thomas Grimonet
status: In progress
tags: ['upgrade', 'infrastructure', 'tooling', 'uv', 'package-manager', 'devops']
---

# Implementation Plan: Migration to UV Package Manager

![Status: In progress](https://img.shields.io/badge/status-In%20progress-yellow)

## Introduction

This implementation plan describes the migration of the eos-downloader project from traditional pip/setuptools-based dependency management to UV (https://github.com/astral-sh/uv), a fast Python package installer and resolver written in Rust by Astral (creators of Ruff). UV provides significant performance improvements (10-100x faster than pip), better dependency resolution, and modern features while maintaining full compatibility with the existing Python ecosystem.

**Key Benefits of UV:**

- ⚡ **Performance**: 10-100x faster than pip for dependency resolution and installation
- 🔒 **Reliability**: Deterministic builds with lockfile (uv.lock)
- 🔐 **Security**: Built-in hash verification and integrity checks
- 🎯 **Simplicity**: Single tool replaces pip, pip-tools, virtualenv, and more
- 🐍 **Compatibility**: Full PyPI compatibility, works with existing pyproject.toml
- 🦀 **Modern**: Written in Rust, actively maintained by Astral

This migration will modernize the development workflow while maintaining backward compatibility for end users who install via pip.

## 1. Requirements & Constraints

### Requirements

- **REQ-001**: Maintain full compatibility with existing project dependencies (cryptography, paramiko, requests, tqdm, loguru, rich, cvprac, click, pydantic)
- **REQ-002**: Preserve all existing tox test environments and commands functionality
- **REQ-003**: Update all user-facing and developer documentation to reflect UV usage
- **REQ-004**: Adapt all GitHub Actions workflows to use UV instead of pip
- **REQ-005**: Ensure bumpver continues to work correctly with new project structure
- **REQ-006**: Maintain support for Python 3.9, 3.10, 3.11, and 3.12
- **REQ-007**: Keep pyproject.toml as the single source of truth for project metadata
- **REQ-008**: Preserve all optional dependency groups (dev, doc) with same packages
- **REQ-009**: Maintain CLI entrypoints functionality (ardl, lard commands)
- **REQ-010**: Ensure backward compatibility for end users installing from PyPI via pip
- **REQ-011**: Preserve existing project structure (eos_downloader/ directory, tests/ structure)
- **REQ-012**: Maintain Docker image functionality and build process
- **REQ-013**: Support partial installations with UV (equivalent to `pip install -e .` and `pip install -e ".[doc]"`)
- **REQ-014**: Preserve complete project definition from pyproject.toml without modifications (metadata, dependencies, build-system, scripts, optional-dependencies)

### Security Requirements

- **SEC-001**: Use UV's lockfile mechanism (uv.lock) for reproducible builds across all environments
- **SEC-002**: Pin all dependencies with exact versions in lockfile including transitive dependencies
- **SEC-003**: Validate package hashes for security using UV's built-in verification
- **SEC-004**: Ensure GitHub Actions workflows use verified UV installation methods
- **SEC-005**: Maintain or improve current security scanning practices (dependency-review, etc.)

### Constraints

- **CON-001**: Must not break existing CI/CD pipelines during migration (phased rollout acceptable)
- **CON-002**: Migration should be completed in a single PR to avoid partial/inconsistent states
- **CON-003**: Must maintain compatibility with Docker builds (Dockerfile, Dockerfile.docker)
- **CON-004**: Cannot introduce breaking changes to end users installing via pip from PyPI
- **CON-005**: Must work with existing GitHub Actions matrix strategy (Python 3.9-3.12)
- **CON-006**: Script compatibility: .github/scripts/*.py must continue to function

### Guidelines

- **GUD-001**: Follow UV best practices as documented in official documentation (https://github.com/astral-sh/uv)
- **GUD-002**: Use uv.lock file for deterministic dependency resolution (commit to repository)
- **GUD-003**: Leverage UV's built-in virtual environment management instead of manual venv
- **GUD-004**: Maintain existing project structure where possible (minimize disruption)
- **GUD-005**: Document all UV commands with pip equivalents for easy transition
- **GUD-006**: Use UV's workspace features if beneficial for future monorepo considerations

### Patterns to Follow

- **PAT-001**: Use `uv sync` for installing dependencies (replaces `pip install -r requirements.txt`)
- **PAT-002**: Use `uv sync --all-extras` for installing with all optional dependencies (replaces `pip install -e .[dev]`)
- **PAT-003**: Use `uv run <command>` for executing commands in UV-managed environment (replaces `python -m` or direct execution)
- **PAT-004**: Use `uv add <package>` for adding new dependencies (replaces `pip install` + manual pyproject.toml edit)
- **PAT-005**: Use `uv remove <package>` for removing dependencies (replaces manual pyproject.toml edit + pip uninstall)
- **PAT-006**: Use `uv lock` to update lockfile after dependency changes (replaces pip-compile)
- **PAT-007**: Use `uv build` for building distributions (replaces `python -m build`)
- **PAT-008**: Use `uv pip compile` for generating requirements.txt if needed for legacy compatibility
- **PAT-009**: Use `uv sync` for editable install without extras (replaces `pip install -e .`)
- **PAT-010**: Use `uv sync --extra doc` for editable install with specific extra (replaces `pip install -e ".[doc]"`)
- **PAT-011**: Use `uv sync --all-extras` for editable install with all extras (replaces `pip install -e ".[dev,doc]"`)

## 2. Implementation Steps

### Implementation Phase 1: UV Configuration & Setup

- GOAL-001: Initialize UV configuration and verify compatibility with existing project structure

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Install UV locally for testing: `curl -LsSf https://astral.sh/uv/install.sh \| sh` or `brew install uv` | ✅ | 2025-11-04 |
| TASK-002 | Verify UV installation: `uv --version` (should be >= 0.4.0) | ✅ | 2025-11-04 |
| TASK-003 | Review current pyproject.toml structure: sections [build-system], [project], [project.optional-dependencies], [project.scripts], [tool.*] | ✅ | 2025-11-04 |
| TASK-004 | Run `uv sync` in project root to test initial dependency resolution | ✅ | 2025-11-04 |
| TASK-005 | Verify lockfile creation: `uv.lock` should be generated with all dependencies (main + dev + doc) pinned | ✅ | 2025-11-04 |
| TASK-006 | Test installation with UV: `uv sync --all-extras` should install all dependencies without errors | ✅ | 2025-11-04 |
| TASK-007 | Verify CLI commands work: `uv run ardl --version` and `uv run lard --version` should execute correctly | ✅ | 2025-11-04 |
| TASK-008 | Add `uv.lock` to git tracking: `git add uv.lock` and commit with message "chore: add UV lockfile for deterministic builds" | ✅ | 2025-11-04 |
| TASK-009 | Update .gitignore to include UV cache directories: `.uv/` and `.venv/` (if not already present) | ✅ | 2025-11-04 |
| TASK-009a | Fix `.python-version`: replace invalid project name with actual Python version (e.g., `3.13`) to eliminate UV warnings | ✅ | 2025-11-04 |
| TASK-009b | Fix VIRTUAL_ENV conflict: add `unset VIRTUAL_ENV` to `.envrc` to prevent pyenv/UV conflict warnings | ✅ | 2025-11-04 |
| TASK-009c | Create example config files: `.python-version.example` and `.envrc.example` for documentation | ✅ | 2025-11-04 |

### Implementation Phase 2: Tox Command Migration & Makefile

- GOAL-002: Replace tox commands with UV equivalents while maintaining exact same functionality and test coverage

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Document all existing tox commands from pyproject.toml [tool.tox] section: envlist = clean, lint, type, py{39,310,311,312} | | |
| TASK-011 | Create Makefile with UV-based commands for developer convenience | | |
| TASK-012 | Add Makefile target `make install`: runs `uv sync --all-extras` (replaces `pip install -e .[dev]`) | | |
| TASK-012a | Add Makefile target `make install-base`: runs `uv sync` (replaces `pip install -e .`) | | |
| TASK-012b | Add Makefile target `make install-doc`: runs `uv sync --extra doc` (replaces `pip install -e ".[doc]"`) | | |
| TASK-013 | Add Makefile target `make test`: runs `uv run pytest --cov=eos_downloader --cov-report=term-missing --cov-report=html` (replaces `tox -e py39`) | | |
| TASK-014 | Add Makefile target `make lint`: runs `uv run flake8 eos_downloader tests && uv run pylint eos_downloader` (replaces `tox -e lint`) | | |
| TASK-015 | Add Makefile target `make type`: runs `uv run mypy eos_downloader` (replaces `tox -e type`) | | |
| TASK-016 | Add Makefile target `make clean`: runs cleanup commands for test artifacts, cache, etc. (replaces `tox -e clean`) | | |
| TASK-017 | Add Makefile target `make format`: runs `uv run black eos_downloader tests && uv run isort eos_downloader tests` for code formatting | | |
| TASK-018 | Add Makefile target `make docs`: runs `uv run mkdocs build` for documentation building | | |
| TASK-019 | Test all Makefile targets locally to ensure parity with tox functionality and same test coverage | | |
| TASK-020 | Document command mapping in README.md: create comparison table (pip/tox commands -> UV/Makefile equivalents, including partial installs) | | |

### Implementation Phase 3: Script Adaptation

- GOAL-003: Update .github/scripts/*.py to ensure compatibility with UV environment and continue functioning correctly

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | Analyze check-python-versions.py: extracts Python version classifiers from pyproject.toml using regex | | |
| TASK-022 | Test check-python-versions.py with UV environment: `uv run python .github/scripts/check-python-versions.py` | | |
| TASK-023 | Update check-python-versions.py if needed: ensure it works with uv.lock present and UV venv structure | | |
| TASK-024 | Analyze sync-python-versions.py: updates pyproject.toml classifiers and requires-python field | | |
| TASK-025 | Test sync-python-versions.py with UV environment: `uv run python .github/scripts/sync-python-versions.py` | | |
| TASK-026 | Update sync-python-versions.py if needed: ensure it correctly modifies pyproject.toml without breaking UV compatibility | | |
| TASK-027 | Verify python-versions.json synchronization still works correctly after UV migration | | |
| TASK-028 | Update .github/scripts/README.md with UV usage examples: `uv run python .github/scripts/<script>.py` | | |
| TASK-029 | Test all scripts end-to-end in UV environment to ensure full compatibility | | |

### Implementation Phase 4: Bumpver Configuration

- GOAL-004: Update bumpver configuration to work correctly with UV and ensure version bumping targets all necessary files

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-030 | Review current bumpver configuration in pyproject.toml [tool.bumpver] section | | |
| TASK-031 | Identify all files containing version strings: pyproject.toml (project.version), eos_downloader/__init__.py (__version__) | | |
| TASK-032 | Verify [tool.bumpver.file_patterns] includes all version-bearing files correctly | | |
| TASK-033 | Test bumpver with UV environment: `uv run bumpver update --dry --patch` (dry run) | | |
| TASK-034 | Verify version bumping updates: pyproject.toml, __init__.py, and any other version references | | |
| TASK-035 | Test that UV automatically updates uv.lock when pyproject.toml version changes: `uv lock` after bumpver | | |
| TASK-036 | Add post-bumpver hook if needed: automatically run `uv lock` after version bump | | |
| TASK-037 | Document bumpver workflow in CONTRIBUTING.md: include UV lock update step | | |

### Implementation Phase 5: GitHub Actions Migration

- GOAL-005: Update all GitHub Actions workflows to use UV instead of pip, maintaining all existing functionality and test coverage

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-038 | Identify all workflows using pip/venv: pr-management.yml, release.yml, documentation.yml, on_demand.yml, coverage-badge.yml | | |
| TASK-039 | Add UV installation step using official action: `astral-sh/setup-uv@v3` (https://github.com/astral-sh/setup-uv) | | |
| TASK-040 | Update pr-management.yml: replace `pip install` with `uv sync --all-extras` in all test jobs | | |
| TASK-041 | Update pr-management.yml: replace test execution `pytest` with `uv run pytest` | | |
| TASK-042 | Update pr-management.yml: replace lint commands with `uv run flake8` and `uv run pylint` | | |
| TASK-043 | Update pr-management.yml: replace type checking with `uv run mypy` | | |
| TASK-044 | Update release.yml: replace pip build commands with `uv build` for PyPI publishing | | |
| TASK-045 | Update release.yml: ensure uv.lock is included in source distribution for reproducibility | | |
| TASK-046 | Update documentation.yml: replace pip install with `uv sync` and mkdocs build with `uv run mkdocs build` | | |
| TASK-047 | Update on_demand.yml: replace pip commands with UV equivalents if workflow exists | | |
| TASK-048 | Update coverage-badge.yml: use UV for pytest-cov execution: `uv run pytest --cov` | | |
| TASK-049 | Add caching for UV in all workflows: cache `~/.cache/uv` and `uv.lock` for faster subsequent runs | | |
| TASK-050 | Test all workflows in feature branch: create test PR to verify all jobs pass successfully | | |

### Implementation Phase 6: Docker Configuration

- GOAL-006: Update Dockerfile and Dockerfile.docker to use UV for dependency installation, maintaining image functionality and optimizing build times

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-051 | Update Dockerfile: add UV installation in builder stage `COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv` | | |
| TASK-052 | Update Dockerfile: replace `pip install` commands with `uv sync --frozen` for reproducible builds | | |
| TASK-053 | Update Dockerfile: copy pyproject.toml and uv.lock into Docker image before dependency installation | | |
| TASK-054 | Update Dockerfile: ensure .venv is properly created and activated in final stage | | |
| TASK-055 | Update Dockerfile.docker: apply same UV changes as Dockerfile (includes Docker-in-Docker support) | | |
| TASK-056 | Update .dockerignore: ensure uv.lock is NOT ignored (needed for frozen installs) | | |
| TASK-057 | Update .dockerignore: add `.uv/` cache directory to ignore list | | |
| TASK-058 | Test Docker builds locally: `docker build -t eos-downloader:uv-test .` should succeed | | |
| TASK-059 | Test Docker image functionality: `docker run eos-downloader:uv-test ardl --version` should work | | |
| TASK-060 | Verify Docker image size: compare with previous pip-based image (UV should be similar or smaller) | | |
| TASK-061 | Benchmark Docker build time: compare with previous pip-based build (UV should be faster) | | |

### Implementation Phase 7: Documentation Updates

- GOAL-007: Update all user-facing and developer documentation to reflect UV usage and provide clear migration guidance

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-062 | Update README.md: replace pip installation instructions with UV: `uv sync` for development, keep `pip install eos-downloader` for users | | |
| TASK-063 | Update README.md: add "For Contributors" section explaining UV setup: `curl -LsSf https://astral.sh/uv/install.sh \| sh` | | |
| TASK-064 | Update README.md: add command comparison table (pip vs UV commands) | | |
| TASK-065 | Update CONTRIBUTING.md: replace all pip commands with UV equivalents throughout the document | | |
| TASK-066 | Update CONTRIBUTING.md: add section on UV lockfile management: when to run `uv lock`, how to add dependencies | | |
| TASK-067 | Update docs/contributing.md: mirror changes from CONTRIBUTING.md for consistency | | |
| TASK-068 | Create new doc: docs/migration-guide-uv.md explaining migration for existing contributors | | |
| TASK-069 | Update docs/migration-guide-uv.md: include troubleshooting section for common UV issues | | |
| TASK-070 | Update docs/faq.md: add UV-related FAQs (what is UV, why migrate, how to install, common issues) | | |
| TASK-071 | Create UV command cheatsheet in docs: table of common operations (install, add, remove, update, build, test) | | |
| TASK-072 | Update all code examples in docs/ that show pip commands to use UV instead | | |
| TASK-073 | Add UV prerequisites to documentation: system requirements, installation methods (curl, brew, cargo) | | |

### Implementation Phase 8: Cleanup & Validation

- GOAL-008: Remove deprecated configuration, validate the migration, and ensure all functionality works correctly

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-074 | Review [tool.tox] section in pyproject.toml: decide whether to keep for reference or remove | | |
| TASK-075 | Remove requirements.txt files if they exist (UV uses uv.lock, but check if any legacy files present) | | |
| TASK-076 | Remove tox.ini if it exists as separate file (currently config is embedded in pyproject.toml) | | |
| TASK-077 | Run full test suite with UV: `uv run pytest --cov=eos_downloader --cov-report=term-missing` should achieve same coverage as before | | |
| TASK-078 | Run linting with UV: `uv run flake8 eos_downloader tests` should pass without new errors | | |
| TASK-079 | Run linting with UV: `uv run pylint eos_downloader` should pass without new errors | | |
| TASK-080 | Run type checking with UV: `uv run mypy eos_downloader` should pass without new type errors | | |
| TASK-081 | Build documentation with UV: `uv run mkdocs build` should succeed without errors | | |
| TASK-082 | Build package with UV: `uv build` should create wheel and sdist in dist/ directory | | |
| TASK-083 | Test package installation from built artifact: `pip install dist/*.whl` in fresh venv should work | | |
| TASK-084 | Verify CLI commands work from installed package: `ardl --help` and `lard --help` | | |
| TASK-085 | Test all CLI subcommands: `ardl get eos --help`, `ardl info eos --help`, etc. | | |
| TASK-086 | Verify lockfile freshness: `uv lock --check` should confirm uv.lock is up to date with pyproject.toml | | |
| TASK-087 | Run complete Docker build: `docker build -t eos-downloader:uv-final .` and test image functionality | | |
| TASK-088 | Create comprehensive PR with all changes: include detailed testing checklist in PR description | | |
| TASK-089 | Update PR with testing results: verify all GitHub Actions workflows pass successfully | | |
| TASK-090 | Obtain code review approval and merge to main branch | | |

## 3. Alternatives

### Alternative Approaches Considered

- **ALT-001**: Poetry (https://python-poetry.org/) - Popular modern Python package manager
  - **Pros**: Mature ecosystem, large community, good documentation, proven track record
  - **Cons**: Slower than UV (Python-based vs Rust-based), adds abstraction layer over setuptools, migration would require poetry.lock format
  - **Reason not chosen**: UV provides significantly better performance (10-100x faster) and is more aligned with standard Python tooling without additional abstraction layers
  
- **ALT-002**: PDM (https://pdm.fming.dev/) - Modern Python package manager with PEP 582 support
  - **Pros**: Modern, supports PEP 582 (__pypackages__), good performance
  - **Cons**: Smaller community than Poetry, less established, performance not as good as UV
  - **Reason not chosen**: UV has better performance benchmarks, stronger momentum, and backing from Astral (Ruff creators)
  
- **ALT-003**: Stay with pip + pip-tools (https://pip-tools.readthedocs.io/)
  - **Pros**: Industry standard, universally supported, minimal learning curve, no migration needed
  - **Cons**: Slower dependency resolution, manual lockfile management with pip-compile, multiple tools needed (pip, pip-tools, virtualenv)
  - **Reason not chosen**: Does not provide the performance benefits, modern features (single tool), and improved developer experience of UV
  
- **ALT-004**: Pipenv (https://pipenv.pypa.io/) - Official PyPA virtual environment and dependency manager
  - **Pros**: Official PyPA tool, integrated Pipfile/Pipfile.lock, built-in virtualenv management
  - **Cons**: Significantly slower than UV, has had maintenance concerns historically, less active development
  - **Reason not chosen**: Performance issues, slower release cycle, UV provides better modern alternative

- **ALT-005**: Gradual migration (partial UV adoption, keep pip for some workflows)
  - **Pros**: Lower risk, can test UV incrementally, easier rollback if issues found
  - **Cons**: Confusing mixed tooling state, harder to maintain, extends migration timeline, requires managing two tool chains
  - **Reason not chosen**: Clean cutover is better for long-term maintainability; testing in feature branch mitigates risk; mixed state creates confusion for contributors

- **ALT-006**: Rye (https://rye-up.com/) - Also from Astral, precursor to UV
  - **Pros**: Same creators as UV, similar goals
  - **Cons**: Rye is being deprecated in favor of UV, migration to UV would still be needed later
  - **Reason not chosen**: UV is the future direction from Astral; migrating to deprecated tool makes no sense

### Partial Installation Support

UV fully supports partial installations equivalent to pip's `-e .` and `-e ".[extra]"` patterns through its `--extra` flag system:

- **Base install** (`pip install -e .`): `uv sync` - Installs only core dependencies
- **Single extra** (`pip install -e ".[doc]"`): `uv sync --extra doc` - Installs core + doc dependencies
- **Multiple extras** (`pip install -e ".[dev,doc]"`): `uv sync --extra dev --extra doc` - Installs core + specified extras
- **All extras** (`pip install -e ".[dev]"` where dev includes all): `uv sync --all-extras` - Installs all dependency groups

This maintains the same flexibility as pip while providing UV's performance benefits and deterministic resolution via uv.lock.

## 4. Dependencies

### External Dependencies

- **DEP-001**: UV package manager (https://github.com/astral-sh/uv) - minimum version 0.4.0, recommended latest stable
- **DEP-002**: GitHub Actions astral-sh/setup-uv action (https://github.com/astral-sh/setup-uv) for CI/CD integration
- **DEP-003**: Docker base images must support UV installation (Python 3.9+ images, any Linux distro with curl)
- **DEP-004**: All existing Python dependencies must remain compatible with UV resolver (verified in Phase 1)
- **DEP-005**: Bumpver compatibility with UV environment for automated version management

### Internal Dependencies

- **DEP-006**: Completion of Phase 1 (UV setup) required before any other phase can begin - validates UV compatibility
- **DEP-007**: Phase 2 (Tox migration) depends on Phase 1 completion - need working UV environment first
- **DEP-008**: Phase 3 (Script adaptation) depends on Phase 1 completion - scripts run in UV environment
- **DEP-009**: Phase 4 (Bumpver) depends on Phase 1 completion - needs UV lockfile mechanism
- **DEP-010**: Phase 5 (GitHub Actions) depends on Phases 1-4 completion - all local changes must work first
- **DEP-011**: Phase 6 (Docker) depends on Phase 1 completion - needs uv.lock file
- **DEP-012**: Phase 7 (Documentation) should document all changes from Phases 1-6 - updates after technical implementation
- **DEP-013**: Phase 8 (Cleanup) depends on all previous phases - final validation of complete migration

### Dependency Graph

```
Phase 1 (UV Setup)
    ├── Phase 2 (Tox Migration)
    ├── Phase 3 (Script Adaptation)
    ├── Phase 4 (Bumpver)
    ├── Phase 6 (Docker)
    └── Phase 5 (GitHub Actions)
            └── Phase 7 (Documentation)
                    └── Phase 8 (Cleanup & Validation)
```

## 5. Files

### Files to Create

- **FILE-001**: `uv.lock` - UV lockfile with pinned dependencies (generated by `uv sync`, ~2769+ lines)
- **FILE-002**: `Makefile` - Command aliases for UV operations (clean, install, install-base, install-doc, test, lint, type, format, docs, build)
- **FILE-003**: `docs/migration-guide-uv.md` - Migration guide for existing contributors, including partial installation examples
- **FILE-004**: `docs/uv-commands-cheatsheet.md` - UV command reference and comparison table with pip equivalents including partial installs
- **FILE-005**: `.python-version.example` - Example Python version file (contains actual Python version like `3.13`)
- **FILE-006**: `.envrc.example` - Example direnv configuration with `unset VIRTUAL_ENV` to prevent UV warnings

### Files to Modify

- **FILE-005**: `pyproject.toml` - Ensure UV compatibility (build-system stays setuptools, verify all sections work with UV)
- **FILE-006**: `README.md` - Update installation instructions, add UV setup section for contributors
- **FILE-007**: `CONTRIBUTING.md` - Replace all pip commands with UV equivalents throughout document
- **FILE-008**: `docs/contributing.md` - Mirror CONTRIBUTING.md changes for consistency
- **FILE-009**: `docs/faq.md` - Add UV-related FAQs (installation, troubleshooting, benefits)
- **FILE-010**: `.github/workflows/pr-management.yml` - Replace pip with UV, add UV caching
- **FILE-011**: `.github/workflows/release.yml` - Replace pip with UV, use `uv build` for packaging
- **FILE-012**: `.github/workflows/documentation.yml` - Replace pip with UV for docs build
- **FILE-013**: `.github/workflows/on_demand.yml` - Replace pip with UV if workflow exists
- **FILE-014**: `.github/workflows/coverage-badge.yml` - Replace pip with UV for test execution
- **FILE-015**: `Dockerfile` - Add UV installation, use `uv sync --frozen`, copy uv.lock
- **FILE-016**: `Dockerfile.docker` - Same UV changes as Dockerfile for Docker-in-Docker variant
- **FILE-017**: `.github/scripts/check-python-versions.py` - Test and update if needed for UV compatibility
- **FILE-018**: `.github/scripts/sync-python-versions.py` - Test and update if needed for UV compatibility
- **FILE-019**: `.github/scripts/README.md` - Update with UV usage examples
- **FILE-020**: `.dockerignore` - Ensure uv.lock is NOT ignored, add `.uv/` cache
- **FILE-021**: `.gitignore` - Add UV-specific patterns: `.uv/`, `.venv/` (if not present)

### Files to Potentially Remove/Deprecate

- **FILE-022**: `requirements.txt` - Check if exists; replace with uv.lock (project currently uses pyproject.toml, not requirements.txt)
- **FILE-023**: `requirements-dev.txt` - Check if exists; replace with uv.lock (project uses optional-dependencies in pyproject.toml)
- **FILE-024**: `tox.ini` - Currently embedded in pyproject.toml [tool.tox]; decide whether to keep for reference or remove after Makefile creation
- **FILE-025**: `[tool.tox]` section in pyproject.toml - May deprecate after successful Makefile migration, or keep for reference

### Files Not Modified (End User Compatibility)

- **FILE-026**: PyPI distribution (wheel/sdist) - End users can still `pip install eos-downloader` (UV only affects development)
- **FILE-027**: `eos_downloader/__init__.py` - No changes needed for UV migration
- **FILE-028**: `eos_downloader/**/*.py` - No application code changes needed (UV is development tool only)

## 6. Testing

### Test Cases

- **TEST-001**: Fresh UV installation: `curl -LsSf https://astral.sh/uv/install.sh | sh && uv --version`
  - **Expected**: UV installs successfully, version >= 0.4.0 displayed
  
- **TEST-002**: Initial dependency installation: `uv sync --all-extras` from clean checkout
  - **Expected**: All dependencies (main + dev + doc) install without errors, .venv created, uv.lock generated
  
- **TEST-003**: Full test suite execution: `uv run pytest --cov=eos_downloader --cov-report=term-missing`
  - **Expected**: All tests pass (100+ tests), coverage >= 80% (same or better than current)
  
- **TEST-004**: Linting with flake8: `uv run flake8 eos_downloader tests`
  - **Expected**: No new linting errors introduced (existing count maintained)
  
- **TEST-005**: Linting with pylint: `uv run pylint eos_downloader`
  - **Expected**: No new pylint errors introduced (existing score maintained)
  
- **TEST-006**: Type checking: `uv run mypy eos_downloader`
  - **Expected**: No new type errors introduced (existing type coverage maintained)
  
- **TEST-007**: Package building: `uv build`
  - **Expected**: Wheel and sdist created in dist/ directory, both installable
  
- **TEST-008**: Documentation building: `uv run mkdocs build`
  - **Expected**: Documentation builds without errors, site/ directory created
  
- **TEST-009**: CLI functionality: `uv run ardl --version && uv run ardl --help`
  - **Expected**: CLI commands work correctly, version and help displayed
  
- **TEST-010**: CLI subcommands: `uv run ardl get eos --help && uv run ardl info eos --help`
  - **Expected**: All subcommands accessible and functional
  
- **TEST-011**: Docker build: `docker build -t eos-downloader:uv-test -f Dockerfile .`
  - **Expected**: Image builds successfully in <5 minutes (faster than pip)
  
- **TEST-012**: Docker functionality: `docker run eos-downloader:uv-test ardl --version`
  - **Expected**: CLI works in container, correct version displayed
  
- **TEST-013**: Docker size comparison: `docker images | grep eos-downloader`
  - **Expected**: Image size similar or smaller than current pip-based image
  
- **TEST-014**: Version bumping: `uv run bumpver update --dry --patch`
  - **Expected**: Dry run shows correct version updates in pyproject.toml, __init__.py
  
- **TEST-015**: Lockfile update after version bump: `uv lock` after bumpver
  - **Expected**: uv.lock updates with new version, no dependency changes
  
- **TEST-016**: Script execution: `uv run python .github/scripts/check-python-versions.py`
  - **Expected**: Script runs successfully, validates Python versions
  
- **TEST-017**: Lockfile freshness check: `uv lock --check`
  - **Expected**: Confirms uv.lock is up to date with pyproject.toml
  
- **TEST-018**: GitHub Actions pr-management workflow: Push to feature branch, create PR
  - **Expected**: All jobs pass (test matrix for Python 3.9-3.12, lint, type check)
  
- **TEST-019**: GitHub Actions caching: Run workflow twice, check cache hit
  - **Expected**: Second run uses cache, significantly faster dependency installation
  
- **TEST-020**: Package installation from PyPI (post-release validation): `pip install eos-downloader`
  - **Expected**: End users can still install via pip (backward compatibility maintained)
  
- **TEST-021**: Makefile targets: `make clean && make install && make test && make lint && make type`
  - **Expected**: All Makefile targets execute successfully
  
- **TEST-022**: Fresh contributor setup: Clone repo, follow README UV setup, run tests
  - **Expected**: New contributor can set up environment and run tests in <5 minutes
  
- **TEST-023**: Dependency addition: `uv add requests-mock` as dev dependency
  - **Expected**: Dependency added to pyproject.toml [project.optional-dependencies.dev], uv.lock updated
  
- **TEST-024**: Dependency removal: `uv remove requests-mock`
  - **Expected**: Dependency removed from pyproject.toml, uv.lock updated
  
- **TEST-025a**: Partial installation (base): `uv sync` in fresh clone
  - **Expected**: Only core dependencies installed, package available in editable mode, CLI commands work
  
- **TEST-025b**: Partial installation (doc extra): `uv sync --extra doc` in fresh clone
  - **Expected**: Core + doc dependencies installed (mkdocs, mkdocstrings, etc.), documentation buildable
  
- **TEST-025c**: Partial installation (dev extra): `uv sync --extra dev` in fresh clone
  - **Expected**: Core + dev dependencies installed (pytest, flake8, mypy, etc.), tests runnable
  
- **TEST-025d**: Full installation: `uv sync --all-extras` in fresh clone
  - **Expected**: All dependencies installed (core + dev + doc), all commands work
  
- **TEST-026**: Cross-platform test: Run `uv sync` on Linux, macOS, Windows
  - **Expected**: UV works identically on all platforms, same uv.lock behavior
  
- **TEST-027**: pyproject.toml preservation: Verify [project], [project.scripts], [project.optional-dependencies], [build-system] sections unchanged
  - **Expected**: All project metadata preserved exactly, no UV-specific modifications needed

## 7. Risks & Assumptions

### Risks

- **RISK-001**: UV may have undiscovered bugs or edge cases with complex dependency graphs
  - **Likelihood**: Low (UV is well-tested, used in production by many projects)
  - **Impact**: Medium (could block migration, require workarounds)
  - **Mitigation**: Thorough testing in feature branch before merge; keep rollback plan ready; report issues to UV project with detailed reproduction
  
- **RISK-002**: GitHub Actions UV setup may fail on certain runner versions or OS combinations
  - **Likelihood**: Low (astral-sh/setup-uv action is well-maintained)
  - **Impact**: Medium (CI/CD pipeline failures)
  - **Mitigation**: Test on all runner versions in matrix (ubuntu-latest, windows-latest if applicable); have fallback to pip installation if UV setup fails
  
- **RISK-003**: Docker build time or final image size may increase unexpectedly
  - **Likelihood**: Very Low (UV should be faster and similar/smaller size)
  - **Impact**: Low (minor performance degradation)
  - **Mitigation**: Benchmark before/after migration; optimize Dockerfile layers; use multi-stage builds effectively; consider UV caching in build
  
- **RISK-004**: Some dependencies may have issues with UV's resolver (rare edge cases)
  - **Likelihood**: Very Low (UV uses same PyPI index as pip, compatible resolver)
  - **Impact**: High if it occurs (migration blocked)
  - **Mitigation**: Test dependency resolution early in Phase 1; if issues found, report to UV project; worst case, document workarounds or stay with pip for specific dependencies
  
- **RISK-005**: Contributors may resist changing from familiar pip workflow
  - **Likelihood**: Medium (change management challenge)
  - **Impact**: Low (training/documentation can address)
  - **Mitigation**: Provide clear documentation with command comparison table; emphasize performance benefits (10-100x faster); create migration guide for contributors; offer help/support during transition period
  
- **RISK-006**: bumpver may not work correctly with UV-managed project or lockfile updates
  - **Likelihood**: Low (bumpver is tool-agnostic, works with pyproject.toml)
  - **Impact**: Medium (version management disrupted)
  - **Mitigation**: Test thoroughly in Phase 4; add post-bumpver hook to run `uv lock`; document manual lockfile update if needed; consider alternative version bumping tools if bumpver incompatible
  
- **RISK-007**: Lockfile merge conflicts in collaborative development
  - **Likelihood**: Medium (multiple contributors updating dependencies)
  - **Impact**: Low (can be resolved with `uv lock`)
  - **Mitigation**: Document conflict resolution in CONTRIBUTING.md: always run `uv lock` after resolving pyproject.toml conflicts; consider using `uv lock --check` in pre-commit hooks

### Assumptions

- **ASSUMPTION-001**: UV will remain actively maintained and supported by Astral
  - **Validation**: Astral is well-funded, UV is strategic product for them (part of Ruff ecosystem)
  - **Risk if false**: Would need to migrate to another tool (Poetry, PDM)
  
- **ASSUMPTION-002**: UV's lockfile format (uv.lock) will remain stable and backward compatible
  - **Validation**: UV follows semantic versioning, major version changes would be announced
  - **Risk if false**: May need lockfile regeneration on UV updates
  
- **ASSUMPTION-003**: All current dependencies (cryptography, paramiko, requests, tqdm, loguru, rich, cvprac, click, pydantic) are compatible with UV resolver
  - **Validation**: UV uses standard PyPI resolution, compatible with pip
  - **Risk if false**: Would need to find workarounds or alternative dependencies (unlikely)
  
- **ASSUMPTION-004**: GitHub Actions runners will continue to support UV installation via astral-sh/setup-uv action
  - **Validation**: Official action maintained by Astral, widely used
  - **Risk if false**: Can fall back to manual UV installation via curl or cargo
  
- **ASSUMPTION-005**: UV's performance benefits (10-100x faster) will be realized in this project's CI/CD pipelines
  - **Validation**: Benchmarks from UV project show consistent speedups
  - **Risk if false**: Still get other benefits (deterministic builds, better tooling), performance neutral worst case
  
- **ASSUMPTION-006**: End users installing from PyPI via pip will not be affected (backward compatibility)
  - **Validation**: UV only affects development; published packages work with pip
  - **Risk if false**: Critical issue, would need to fix packaging (unlikely scenario)
  
- **ASSUMPTION-007**: Docker base images (Python 3.9+ official images) support UV installation without issues
  - **Validation**: UV installs via curl or binary copy, minimal requirements
  - **Risk if false**: Can use alternative installation methods (cargo, manual binary)
  
- **ASSUMPTION-008**: The project's current test suite (pytest, coverage, flake8, pylint, mypy) is comprehensive enough to validate UV migration
  - **Validation**: Current coverage >= 80%, tests passing consistently
  - **Risk if false**: May miss edge cases; mitigated by thorough manual testing in Phase 8

## 8. Related Specifications / Further Reading

### Official UV Documentation

- [UV GitHub Repository](https://github.com/astral-sh/uv) - Main repository with README and documentation
- [UV Documentation](https://docs.astral.sh/uv/) - Official documentation site
- [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/) - Installation methods for all platforms
- [UV User Guide](https://docs.astral.sh/uv/guides/) - Comprehensive guides for common tasks
- [UV Configuration](https://docs.astral.sh/uv/configuration/) - Configuration options and settings
- [UV FAQ](https://docs.astral.sh/uv/faq/) - Frequently asked questions

### UV Concepts & Features

- [UV Lockfile (uv.lock)](https://docs.astral.sh/uv/concepts/lockfile/) - Understanding UV's lockfile format
- [UV Resolution](https://docs.astral.sh/uv/concepts/resolution/) - How UV resolves dependencies
- [UV Workspaces](https://docs.astral.sh/uv/concepts/workspaces/) - Monorepo support (future consideration)
- [UV Python Version Management](https://docs.astral.sh/uv/guides/python-versions/) - Managing Python versions with UV
- [UV Performance Benchmarks](https://github.com/astral-sh/uv#benchmarks) - Performance comparison with other tools

### GitHub Actions Integration

- [astral-sh/setup-uv Action](https://github.com/astral-sh/setup-uv) - Official GitHub Action for UV setup
- [UV in CI/CD Guide](https://docs.astral.sh/uv/guides/ci-cd/) - Best practices for using UV in CI/CD pipelines
- [Caching UV in GitHub Actions](https://github.com/astral-sh/setup-uv#caching) - How to cache UV installations and dependencies

### Project Documentation (Internal)

- [Python Instructions](.github/instructions/python.instructions.md) - Project Python coding standards
- [Testing Instructions](.github/instructions/testing.instructions.md) - Testing guidelines and best practices
- [DevOps Core Principles](.github/instructions/devops-core-principles.instructions.md) - DevOps culture and practices
- [GitHub Actions CI/CD Best Practices](.github/instructions/github-actions-ci-cd-best-practices.instructions.md) - CI/CD workflow guidelines
- [Copilot Instructions](.github/copilot-instructions.md) - GitHub Copilot configuration for this project
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute to eos-downloader

### Related GitHub Discussions & Issues

- [UV vs Poetry comparison](https://github.com/astral-sh/uv/discussions/categories/q-a) - Community discussions
- [UV Roadmap](https://github.com/astral-sh/uv/milestones) - Upcoming features and improvements
- [UV Changelog](https://github.com/astral-sh/uv/releases) - Release notes and version history

### Python Packaging Standards

- [Python Packaging User Guide](https://packaging.python.org/) - Official Python packaging documentation
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/) - Specifying build systems
- [PEP 518 - Build System Requirements](https://peps.python.org/pep-0518/) - pyproject.toml specification
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/) - Storing project metadata in pyproject.toml
- [PEP 660 - Editable Installs](https://peps.python.org/pep-0660/) - Editable installation specification

### Community Resources & Comparisons

- [Astral Blog](https://astral.sh/blog) - Announcements and technical deep-dives from UV creators
- [UV Reddit Community](https://www.reddit.com/r/Python/search/?q=uv%20package%20manager) - Community discussions
- [Python Packaging Tools Comparison](https://packaging.python.org/en/latest/guides/tool-recommendations/) - Official recommendations
- [Modern Python Packaging](https://py-pkgs.org/) - Free online book about Python packaging

### Migration Guides from Other Tools

- [Migrating from Poetry to UV](https://docs.astral.sh/uv/guides/migration/#migrating-from-poetry) - If applicable for reference
- [Migrating from PDM to UV](https://docs.astral.sh/uv/guides/migration/#migrating-from-pdm) - If applicable for reference
- [Using UV with existing pip workflow](https://docs.astral.sh/uv/guides/integration/pip/) - Compatibility guide

---

**Note**: This plan is a living document. Update status badges, completion dates, and add learnings as implementation progresses. After completion, document actual results (performance improvements, any deviations from plan) for future reference.
