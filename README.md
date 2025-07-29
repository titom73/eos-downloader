[![tests](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml/badge.svg?event=push)](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eos-downloader)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)
![GitHub release](https://img.shields.io/github/v/release/titom73/arista-downloader)
![PyPI - Downloads/month](https://img.shields.io/pypi/dm/eos-downloader)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

# Arista Software Downloader

## Overview

A project to download Arista softwares to local folder, Cloudvision or EVE-NG. It comes in 2 way: a framework with object to automate Arista software download and a CLI for human activities.

<img src='docs/imgs/logo.jpg' class="center" width="800px" />

> [!CAUTION]
> This script should not be deployed on EOS device. If you do that, there is no support to expect from Arista TAC team.

```bash
# install eos-downloader from pypi
pip install eos-downloader

# download EOS swi for EOS 64bits
ardl --token <your-token> get eos --format 64 --latest --release-type M
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
```

## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](https://github.com/titom73/eos-downloader/blob/main/LICENSE) License
