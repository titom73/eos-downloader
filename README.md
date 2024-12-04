[![tests](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml/badge.svg?event=push)](https://github.com/titom73/eos-downloader/actions/workflows/pr-management.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eos-downloader)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)
![GitHub release](https://img.shields.io/github/v/release/titom73/arista-downloader)
![PyPI - Downloads/month](https://img.shields.io/pypi/dm/eos-downloader)

<!--
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
!-->

# Arista Software Downloader

Script to download Arista softwares to local folder, Cloudvision or EVE-NG.

Current version of this software supports EOS and CVP package only.

> [!CAUTION]
> This script should not be deployed on EOS device. If you do that, there is no support to expect from Arista TAC team.


```bash
pip install eos-downloader
```

## CLI commands

A new CLI is available to execute commands. This CLI is going to replace [`eos-download`](./bin/README.md) script which is now marked as __deprecated__

```bash
 ardl
Usage: ardl [OPTIONS] COMMAND [ARGS]...

  Arista Network Download CLI

Options:
  --version     Show the version and exit.
  --token TEXT  Arista Token from your customer account  [env var:
                ARISTA_TOKEN]
  --help        Show this message and exit.

Commands:
  debug  Debug commands to work with ardl
  get    Download Arista from Arista website
  info   List information from Arista website
```

> **Warning**
> To use this CLI you need to get a valid token from your [Arista Account page](https://www.arista.com/en/users/profile).
> For technical reason, it is only available for customers with active maintenance contracts and not for personnal accounts

### Get information about softwares versions

`ardl` comes witth a tool to get version information from Arista website.

#### Get information about available versions

```bash
ardl info versions --help
Usage: ardl info versions [OPTIONS]

  List available versions of Arista packages (eos or CVP) packages

Options:
  --format [json|text]            Output format
  --package [eos|cvp]
  -b, --branch TEXT
  --release-type TEXT
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --help                          Show this message and exit.
```

With this CLI, you can specify either a branch or a release type when applicable to filter information:

```bash
# Get F version in branch 4.29
❯ ardl info versions --branch 4.29 --release-type F
Listing versions
  - version: 4.29.2F
  - version: 4.29.1F
  - version: 4.29.0.2F
  - version: 4.29.2F
  - version: 4.29.1F
  - version: 4.29.0.2F

# Get M version in branch 4.29
❯ ardl info versions --branch 4.29 --release-type M
Listing versions
  - version: 4.29.10M
  - version: 4.29.9.1M
  - version: 4.29.9M
  - version: 4.29.8M
  - version: 4.29.7.1M
  ...
```

You can also specify JSON as output format:

```bash
ardl info versions --branch 4.29 --release-type F --format json
[
  {
    "version": "4.29.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.1F",
    "branch": "4.29"
  },
  {
    "version": "4.29.0.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.1F",
    "branch": "4.29"
  },
  {
    "version": "4.29.0.2F",
    "branch": "4.29"
  }
]
```

##### Get information about latest version available

CLI has option to get latest version available. Like `ardl info versions`, you can filter by `branch` and/or `release-type` when applicable.

```bash
ardl info latest --help
Usage: ardl info latest [OPTIONS]

  List available versions of Arista packages (eos or CVP) packages

Options:
  --format [json|text]            Output format
  --package [eos|cvp]
  -b, --branch TEXT
  --release-type TEXT
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --help                          Show this message and exit.
```

### Download EOS Package

> **Note**
> Supported packages are: EOS, cEOS, vEOS-lab, cEOS64

TBD

## Requirements

Repository requires Python `>=3.6` with following requirements:

```requirements
cvprac
cryptography
paramiko
requests
requests-toolbelt
scp
tqdm
```

On EVE-NG, you may have to install/upgrade __pyOpenSSL__ in version `23.0.0`:

```bash
# Error when running ardl: AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'

$ pip install pyopenssl --upgrade
```

## Docker

Please refer to [docker documentation](docs/docker.md)

## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](LICENSE) License
