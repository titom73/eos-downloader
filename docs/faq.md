# Frequently Asked Questions

## Caching and Performance

### How does the cache work?

**eos-downloader** implements smart caching at two levels:

1. **File Caching**: Before downloading, the tool checks if the file already exists in the output directory. If found, it reuses the existing file instead of re-downloading.

2. **Docker Image Caching**: Before importing a cEOS image, the tool checks if the `image:tag` already exists in your local Docker registry. If found, it skips the import.

### How do I force re-download or re-import?

Use the `--force` flag:

```bash
# Force re-download even if file exists
ardl get eos --version 4.29.4M --force

# Force re-import Docker image even if it exists
ardl get eos --version 4.29.4M --format cEOS --import-docker --force
```

### Does cache checking work with Podman?

Yes! The Docker image cache checking automatically detects and works with both `docker` and `podman` commands.

### Where are cached files stored?

Cached files are stored in the directory specified by the `--output` option (default: current directory). The cache is **per-directory**, so using different output directories creates separate caches.

### How can I verify cached files are valid?

Currently, file caching uses simple existence checks. For production use, you can:

1. Use the built-in checksum validation after download:
```bash
ardl get eos --version 4.29.4M
# Tool automatically validates md5/sha512 if available
```

2. Use `--force` to ensure a fresh download when integrity is critical.

### Does dry-run mode respect the cache?

Yes! When using `--dry-run`, the tool will report whether it would use cached files or perform actual downloads:

```bash
ardl get eos --version 4.29.4M --dry-run
# Output: [DRY-RUN] Would use cached file: EOS-4.29.4M.swi
```

## Development and Contribution

### What is UV and why is it used?

**UV** is a fast Python package manager written in Rust by Astral (creators of Ruff). The project uses UV for:

- ⚡ **Speed**: 10-100x faster than pip for dependency resolution and installation
- 🔒 **Reproducibility**: Deterministic builds with `uv.lock` lockfile
- 🎯 **Simplicity**: Single tool replaces pip, pip-tools, virtualenv, and venv
- 🦀 **Reliability**: Built-in hash verification and integrity checks

### Do end users need UV to install eos-downloader?

**No!** End users can still install via pip:

```bash
pip install eos-downloader
```

UV is **only required for contributors** who want to develop, test, or contribute to the project.

### How do I switch from pip to UV for development?

If you previously used pip for development, migrating to UV is simple:

```bash
# 1. Install UV (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Remove old virtual environment
rm -rf .venv

# 3. Install dependencies with UV (creates new .venv)
uv sync --all-extras

# 4. Install pre-commit hooks
uv run pre-commit install

# Done! You're now using UV
```

See [docs/dev-notes/tox-to-uv-migration.md](./dev-notes/tox-to-uv-migration.md) for complete migration guide.

### Can I still use tox commands after UV migration?

**Yes!** The project maintains backward compatibility. Both work:

```bash
# Tox (backward compatible)
tox -e lint
tox -e type
tox -e test

# Makefile with UV (faster, direct)
make lint
make type
make test
```

Internally, tox commands delegate to UV + Makefile for better performance.

### What is uv.lock and why is it in the repository?

`uv.lock` is UV's lockfile that ensures:

- **Deterministic builds**: Everyone gets the exact same dependency versions
- **Security**: Contains cryptographic hashes of all packages
- **Reproducibility**: CI, Docker, and local environments use identical dependencies

**Always commit `uv.lock` changes** when you modify dependencies in `pyproject.toml`.

### How do I add or update dependencies?

```bash
# Add a new dependency (automatically updates uv.lock)
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update all dependencies to latest compatible versions
uv lock --upgrade

# Update specific package
uv lock --upgrade-package <package-name>
```

See [Contributing Guide](./contributing.md#uv-lockfile-management) for detailed instructions.

### CI fails with "lockfile out of sync" - what does this mean?

This means `uv.lock` is not in sync with `pyproject.toml`. Fix it:

```bash
# Regenerate lockfile
uv lock

# Commit the updated lockfile
git add uv.lock
git commit -m "chore: update lockfile"
```

CI uses `uv sync --frozen` to verify the lockfile matches `pyproject.toml` exactly.

### How do I troubleshoot UV issues?

```bash
# Clear UV cache
uv cache clean

# Verify environment
uv run python --version
uv pip list

# Recreate virtual environment from scratch
rm -rf .venv
uv sync --all-extras

# Check for dependency conflicts
uv lock --verbose
```

See [UV Documentation](https://docs.astral.sh/uv/) for more troubleshooting tips.

### Where can I learn more about UV?

- [UV Official Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- [Project's UV Migration Guide](./dev-notes/tox-to-uv-migration.md)
- [Contributing Guide](./contributing.md)

## EVE-NG with OpenSSL issue.

On EVE-NG, you may have to install/upgrade __pyOpenSSL__ in version `23.0.0`:

```bash
# Error when running ardl: AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'

$ pip install pyopenssl --upgrade
```
