[![Pytest Validation](https://github.com/titom73/arista-downloader/actions/workflows/pytest.yml/badge.svg)](https://github.com/titom73/arista-downloader/actions/workflows/pytest.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eos-downloader) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/titom73/arista-downloader) ![PyPI - Format](https://img.shields.io/pypi/format/eos-downloader) ![PyPI - Downloads](https://img.shields.io/pypi/dm/eos-downloader) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/titom73/eos-downloader/edge)

# Arista Software Downloader

Script to download Arista softwares to local folder, Cloudvision or EVE-NG.

```bash
pip install eos-downloader
```

## scripts

### eos-download

```bash
usage: eos-download [-h]
  --version VERSION
  [--token TOKEN]
  [--image IMAGE]
  [--destination DESTINATION]
  [--eve]
  [--noztp]
  [--import_docker]
  [--docker_name DOCKER_NAME]
  [--verbose VERBOSE]
  [--log]

EOS downloader script.

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         arista.com user API key - can use ENV:ARISTA_TOKEN
  --image IMAGE         Type of EOS image required
  --version VERSION     EOS version to download from website
  --destination DESTINATION
                        Path where to save EOS package downloaded
  --eve                 Option to install EOS package to EVE-NG
  --noztp               Option to deactivate ZTP when used with EVE-NG
  --import_docker       Option to import cEOS image to docker
  --docker_name DOCKER_NAME
                        Docker image name to use
  --verbose VERBOSE     Script verbosity
  --log                 Option to activate logging to eos-downloader.log file
```

- Token are read from `ENV:ARISTA_TOKEN` unless you specify a specific token with CLI.

- Supported platforms:

  - `INT`: International version
  - `64`: 64 bits version
  - `2GB` for 2GB flash platform
  - `2GB-INT`: for 2GB running International
  - `vEOS`: Virtual EOS image
  - `vEOS-lab`: Virtual Lab EOS
  - `vEOS64-lab`: Virtual Lab EOS running 64B
  - `cEOS`: Docker version of EOS
  - `cEOS64`: Docker version of EOS running in 64 bits

#### Examples

- Download vEOS-lab image and install in EVE-NG

```bash
$ eos-download --image vEOS-lab --version 4.25.7M --eve --noztp
```

- Download Docker image

```bash
$ eos-download --image cEOS --version 4.27.1F
🪐 eos-downloader is starting...
    - Image Type: cEOS
    - Version: 4.27.2F
✅ Authenticated on arista.com
🔎  Searching file cEOS-lab-4.27.2F.tar.xz
    -> Found file at /support/download/EOS-USA/Active Releases/4.27/EOS-4.27.2F/cEOS-lab/cEOS-lab-4.27.2F.tar.xz
💾  Downloading cEOS-lab-4.27.2F.tar.xz ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 17.1 MB/s • 451.6/451.6 MB • 0:00:19 •
🚀  Running checksum validation
🔎  Searching file cEOS-lab-4.27.2F.tar.xz.sha512sum
    -> Found file at /support/download/EOS-USA/Active
Releases/4.27/EOS-4.27.2F/cEOS-lab/cEOS-lab-4.27.2F.tar.xz.sha512sum
💾  Downloading cEOS-lab-4.27.2F.tar.xz.sha512sum ━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • ? • 154/154 bytes • 0:00:00 •
✅  Downloaded file is correct.
```

__Note:__ `ARISTA_TOKEN` should be set in your .profile and not set for each command. If not set, you can use `--token` knob.

```bash
# Export Token
export ARISTA_TOKEN="xxxxxxx"
```

### Cloudvision Image uploader

Create an image bundle on Cloudvision.

```bash
cvp-upload -h
usage: cvp-upload [-h]
    [--token TOKEN]
    [--image IMAGE]
    --cloudvision CLOUDVISION
    [--create_bundle]
    [--timeout TIMEOUT]
    [--verbose VERBOSE]

Cloudvision Image uploader script.

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         CVP Authentication token - can use ENV:ARISTA_AVD_CV_TOKEN
  --image IMAGE         Type of EOS image required
  --cloudvision CLOUDVISION
                        Cloudvision instance where to upload image
  --create_bundle       Option to create image bundle with new uploaded image
  --timeout TIMEOUT     Timeout connection. Default is set to 1200sec
  --verbose VERBOSE     Script verbosity
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

## Installation

### Python PIP

```bash
# Development version from github
$ pip install git+https://github.com/titom73/eos-downloader

# Stable versions
pip install eos-downloader
```

<!-- ### Poetry

Deactivated since pyproject.toml is first source for pip and do not cover script section of setup.py

```bash
# Install dependencies
poetry install

# Run script
poetry run python <script>
``` -->

A docker image is also available when Python cannot be used.

```bash
$ docker pull titom73/eos-downloader:edge
$ docker run -it -rm -v ${PWD}:/download titom73/eos-downloader:edge bash
$ cd /download
$ eos-download --image cEOS --version 4.27.1F
```
## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](LICENSE) License
