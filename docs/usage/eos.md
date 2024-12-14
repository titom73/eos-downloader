# Download EOS package from arista website

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

## ardl get eos options

Below are all the options available to get EOS package:

```bash
$ ardl get eos --help
Usage: ardl get eos [OPTIONS]

  Download EOS image from Arista server.

Options:
  --format TEXT        Image format  [default: vmdk]
  --output PATH        Path to save image  [default: .]
  --latest             Get latest version. If --branch is not use, get the
                       latest branch with specific release type
  --eve-ng             Run EVE-NG vEOS provisioning (only if CLI runs on an
                       EVE-NG server)
  --import-docker      Import docker image to local docker
  --skip-download      Skip download process - for debug only
  --docker-name TEXT   Docker image name  [default: arista/ceos]
  --docker-tag TEXT    Docker image tag
  --version TEXT       EOS version to download
  --release-type TEXT  Release type (M for Maintenance, F for Feature)
                       [default: F]
  --branch TEXT        Branch to download
  --dry-run            Enable dry-run mode: only run code without system
                       changes
  --help               Show this message and exit.
```

!!! info
    You can get information about available version using the [`ardl info version` cli](./info.md)