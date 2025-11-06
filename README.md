[![tests](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml/badge.svg?event=push)](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/titom73/17c473b44b23f1a4c92d3d100644368c/raw/eos-downloader-coverage.json)](https://github.com/titom73/eos-downloader/actions/workflows/coverage-badge.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eos-downloader)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)
![PyPI - Downloads/month](https://img.shields.io/pypi/dm/eos-downloader)

# Arista Software Downloader

## Overview

A project to download Arista softwares to local folder, Cloudvision or EVE-NG. It comes in 2 way: a framework with object to automate Arista software download and a CLI for human activities.

**Key Features:**
- 🚀 **Smart Caching**: Automatically caches downloaded files and Docker images to save bandwidth and time
- 📦 **Multiple Formats**: Support for EOS (64-bit, vEOS, cEOS) and CloudVision Portal
- 🐳 **Docker Integration**: Direct import to Docker/Podman registries
- 🔧 **EVE-NG Support**: Automated provisioning for network simulation
- ⚡ **Fast Iterations**: Subsequent runs complete instantly using cached resources

<img src='docs/imgs/logo.jpg' class="center" width="800px" />

> [!CAUTION]
> This script should not be deployed on EOS device. If you do that, there is no support to expect from Arista TAC team.

```bash
# install eos-downloader from pypi
pip install eos-downloader

# download EOS swi for EOS 64bits (uses cache on subsequent runs)
ardl --token <your-token> get eos --format 64 --latest --release-type M

# force re-download even if cached
ardl --token <your-token> get eos --format 64 --latest --release-type M --force
```

Full documentation is available on [our website](https://titom73.github.io/eos-downloader/).

## Download EOS package from arista website

This command gives you option to download EOS images localy. Some options are available based on image type like importing your cEOS container in your local registry

```bash
# Get latest version of EOS using docker format.
ardl get eos --latest --format cEOS

# Get latest version of maintenance type in specific branch 4.29
ardl get eos --branch 4.29 --format cEOS --release-type M

# Get a specific version
ardl get eos --version 4.29.4M

# Get a specific version and import to docker using default arista/ceos:{version}{release_type}
ardl get eos --version 4.29.4M --import-docker

# Get a specific version and import to EVE-NG
ardl get eos --version 4.33.0F --eve-ng

# Force re-download/re-import (bypass cache)
ardl get eos --version 4.29.4M --import-docker --force
```

### Smart Caching

**eos-downloader** automatically caches downloads and Docker images:

- **Files**: If a file exists in the output directory, it's reused (no re-download)
- **Docker Images**: If an image:tag exists locally, import is skipped
- **Force Mode**: Use `--force` to bypass cache and force fresh download/import

This makes repeated runs **instant** and saves bandwidth! 🚀

## Contributing

A contributing guide is available in [docs folder](./docs/contributing.md)

**Quick Start:**

```bash
# 1. Install UV (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on macOS: brew install uv

# 2. Clone the repository
git clone https://github.com/titom73/eos-downloader.git
cd eos-downloader

# 3. Install development dependencies (creates .venv automatically)
uv sync --all-extras

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Run tests
uv run pytest

# 6. Start developing!
uv run ardl --help
```

## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](https://github.com/titom73/eos-downloader/blob/main/LICENSE) License
