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
  debug    Debug commands to work with ardl
  get      Download Arista from Arista website
```

> **Warning**
> To use this CLI you need to get a valid token from your [Arista Account page](https://www.arista.com/en/users/profile).
> For technical reason, it is only available for customers with active maintenance contracts and not for personnal accounts

### Download EOS Package

> **Note**
> Supported packages are: EOS, cEOS, vEOS-lab, cEOS64

CLI gives an option to get latest version available. By default it takes latest `F` release

```bash
ardl get eos --image-type cEOS --latest
```

If you want to get latest M release, you can use `--release-type`:

```bash
ardl get eos --image-type cEOS --release-type M --latest
```

You can download a specific EOS packages with following commands:

```bash
# Example for a cEOS package
$ ardl get eos --version 4.28.3M --image-type cEOS
```

Available options are :

```bash
Usage: ardl get eos [OPTIONS]

  Download EOS image from Arista website

Options:
  --image-type [64|INT|2GB-INT|cEOS|cEOS64|vEOS|vEOS-lab|EOS-2GB|default]
                                  EOS Image type  [required]
  --version TEXT                  EOS version
  -l, --latest                    Get latest version in given branch. If
                                  --branch is not use, get the latest branch
                                  with specific release type
  -rtype, --release-type [F|M]    EOS release type to search
  -b, --branch TEXT               EOS Branch to list releases
  --docker-name TEXT              Docker image name (default: arista/ceos)
                                  [default: arista/ceos]
  --output PATH                   Path to save image  [default: .]
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --eve-ng                        Run EVE-NG vEOS provisioning (only if CLI
                                  runs on an EVE-NG server)
  --disable-ztp                   Disable ZTP process in vEOS image (only
                                  available with --eve-ng)
  --import-docker                 Import docker image (only available with
                                  --image_type cEOSlab)
  --help                          Show this message and exit.
```

You can use `--latest` and `--release-type` option to get latest EOS version matching a specific release type

```bash
# Get latest M release
❯ ardl get eos --latest -rtype m
🪐 eos-downloader is starting...
    - Image Type: default
    - Version: None
🔎  Searching file EOS-4.29.3M.swi
    -> Found file at /support/download/EOS-USA/Active Releases/4.29/EOS-4.29.3M/EOS-4.29.3M.swi
...
✅  Downloaded file is correct.
✅  processing done !
```

### List available EOS versions from Arista website

You can easily get list of available version using CLI as shown below:

```bash
❯ ardl info eos-versions
Usage: ardl info eos-versions [OPTIONS]

  List Available EOS version on Arista.com website.

  Comes with some filters to get latest release (F or M) as well as branch
  filtering

    - To get latest M release available (without any branch): ardl info eos-
    versions --latest -rtype m

    - To get latest F release available: ardl info eos-versions --latest
    -rtype F

Options:
  -l, --latest                    Get latest version in given branch. If
                                  --branch is not use, get the latest branch
                                  with specific release type
  -rtype, --release-type [F|M]    EOS release type to search
  -b, --branch TEXT               EOS Branch to list releases
  -v, --verbose                   Human readable output. Default is none to
                                  use output in script)
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --help                          Show this message and exit.
```

__Example__

```bash
❯ ardl info eos-versions -rtype m --branch 4.28
['4.28.6.1M', '4.28.6M', '4.28.5.1M', '4.28.5M', '4.28.4M', '4.28.3M']
```

### Download CVP package

> Supported packages are: OVA, KVM, RPM, Upgrade

```bash
$ ardl get cvp --format upgrade --version 2022.2.1 --log-level debug --output ~/Downloads
```

Available options are :

```bash
  --format [ova|rpm|kvm|upgrade]  CVP Image type  [required]
  --version TEXT                  CVP version  [required]
  --output PATH                   Path to save image  [default: .]
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --help                          Show this message and exit.
```

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
