[![Testing & Docker Build for edge](https://github.com/titom73/eos-downloader/actions/workflows/push-to-main.yml/badge.svg)](https://github.com/titom73/eos-downloader/actions/workflows/push-to-main.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eos-downloader) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/titom73/arista-downloader) ![PyPI - Downloads](https://img.shields.io/pypi/dm/eos-downloader) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/titom73/eos-downloader/edge)

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
  --token TEXT  Arista Token from your customer account  [env var:
                ARISTA_TOKEN]
  --help        Show this message and exit.

Commands:
  debug    Debug commands to work with ardl
  get      Download Arista from Arista website
  version  Display version of ardl
```

### Download EOS Package


> Supported packages are: EOS, cEOS, vEOS-lab, cEOS64

You can download EOS packages with following commands:

```bash
# Example for a cEOS package
$ ardl get eos --version 4.28.3M --image-type cEOS
```

Available options are :

```bash
Options:
  --image-type [64|INT|2GB-INT|cEOS|cEOS64|vEOS|vEOS-lab|EOS-2GB|default]
                                  EOS Image type  [required]
  --version TEXT                  EOS version  [required]
  --docker-name TEXT              Docker image name (default: arista/ceos)
                                  [default: arista/ceos]
  --output PATH                   Path to save image  [default: .]
  --log-level, --log [debug|info|warning|error|critical]
                                  Logging level of the command
  --eve-ng / --no-eve-ng          Run EVE-NG vEOS provisioning (only if CLI
                                  runs on an EVE-NG server)
  --disable-ztp / --no-disable-ztp
                                  Disable ZTP process in vEOS image (only
                                  available with --eve-ng)
  --import-docker / --no-import-docker
                                  Import docker image (only available with
                                  --image_type cEOSlab)
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

## Docker

Please refer to [docker documentation](docs/docker.md)

## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](LICENSE) License
