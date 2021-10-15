# Arista Software Downloader

Script to download Arista softwares to local folder, Cloudvision or EVE-NG.

Supported Version & platform (`--ver`):

- EOS using version schema only (`4.x.y`)
- Cloudvision using `cvp-x.y.z`
- TerminAttr using `TerminAtt-x.y.z`

Supported images (`--img`):

- `INT`: International version
- `64`: 64 bits version
- `2GB` for 2GB flash platform
- `2GB-INT`: for 2GB running International
- `vEOS`: Virtual EOS image
- `vEOS-lab`: Virtual Lab EOS
- `vEOS64-lab`: Virtual Lab EOS running 64B
- `cEOS`: Docker version of EOS
- `cEOS64`: Docker version of EOS running in 64 bits
- `RN`: To download Release Notes only
- `kvm` / `ova` / `rpm` / `upgrade`: For Cloudvision platform

## Requirements

Repository requires Python `>=3.6` with following requirements:

```requirements
cryptography
paramiko
requests
requests-toolbelt
scp
tqdm
```

## Installation

```bash
$ pip install git+https://github.com/titom73/arista-downloader
```

## Usage

- Download EOS locally

```bash
$ arista-download --api <Your Arista.com Token> --ver 4.26.2F
[...]
SHA512 checksum correct
```

- Download vEOS-lab on EVE-NG + image Installation

```bash
# Raw image with ZTP
$ arista-download --api <Your Arista.com Token> --ver 4.27.0F --img vEOS-lab --eve

# Disabling ZTP
$ arista-download --api <Your Arista.com Token> --ver 4.27.0F --img vEOS-lab --eve --disable_ztp
```

## Author

From an original idea of [@Mark Rayson](https://github.com/Sparky-python) in [arista-netdevops-community/eos-scripts](https://github.com/arista-netdevops-community/eos-scripts)

## License

Code is under [Apache2](LICENSE) License
