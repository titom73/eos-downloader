# Download EOS package from arista website

This command gives you option to download EOS images localy. Some options are available based on image type like importing your cEOS container in your local registry

```bash
# Get latest version of EOS using docker format.
ardl get eos --latest --format cEOS

# Get latest version of maintenance type in specific branch 4.29
ardl get eos --branch 4.29 --format cEOS --release-type M

# Get a specific version
ardl get eos --version 4.29.4M

# Get a specific version and import to docker
# using default arista/ceos:{version}{release_type}
ardl get eos --version 4.29.4M --import-docker

# Get a specific version and import to EVE-NG
ardl get eos --version 4.33.0F --eve-ng

# Get 64-bit vEOS lab image (vmdk format for VMware)
ardl get eos --version 4.35.1F --format vEOS64-lab

# Get 64-bit vEOS lab image (qcow2 format for KVM/QEMU)
ardl get eos --version 4.35.1F --format vEOS64-lab-qcow2

# Force re-download even if file is cached
ardl get eos --version 4.29.4M --force

# Force re-import of Docker image even if it exists
ardl get eos --version 4.29.4M --import-docker --force
```

## Smart Caching

**eos-downloader** includes intelligent caching to avoid redundant downloads and Docker imports:

### File Caching

- By default, if a file already exists in the output directory, it will be **reused** instead of re-downloaded
- Saves bandwidth and time when running the same command multiple times
- Use `--force` to bypass the cache and force re-download

```bash
# First run: downloads the file
ardl get eos --version 4.29.4M --output /downloads

# Second run: uses cached file (no download)
ardl get eos --version 4.29.4M --output /downloads

# Force re-download
ardl get eos --version 4.29.4M --output /downloads --force
```

### Docker Image Caching

- Before importing a cEOS image, **eos-downloader** checks if the image:tag already exists locally
- Skips the import if the image is already present
- Use `--force` to re-import even if the image exists

```bash
# First run: downloads and imports to Docker
ardl get eos --version 4.29.4M --format cEOS --import-docker

# Second run: file is cached, Docker image exists (no import)
ardl get eos --version 4.29.4M --format cEOS --import-docker

# Force re-import
ardl get eos --version 4.29.4M --format cEOS --import-docker --force
```

### Benefits

- **Faster iterations**: Subsequent runs complete almost instantly
- **Bandwidth savings**: No redundant downloads
- **Disk space optimization**: Reuse existing files
- **CI/CD friendly**: Safe to run repeatedly without overhead

!!! tip "Podman Support"
    The Docker cache checking works with both `docker` and `podman` commands automatically.

!!! warning "Cache Validation"
    File caching currently uses simple existence checks. For production use, consider using checksums to verify file integrity after download.

## ardl get eos options

Below are all the options available to get EOS package:

```bash
$ ardl get eos --help
Usage: ardl get eos [OPTIONS]

  Download EOS image from Arista server.

Options:
  --format TEXT        Image format  [default: vmdk]
  --output PATH        Path to save image  [env var: ARISTA_GET_EOS_OUTPUT;
                       default: .]
  --latest             Get latest version. If --branch is not use, get the
                       latest branch with specific release type  [env var:
                       ARISTA_GET_EOS_LATEST]
  --eve-ng             Run EVE-NG vEOS provisioning (only if CLI runs on an
                       EVE-NG server)  [env var: ARISTA_GET_EOS_EVE_NG]
  --import-docker      Import docker image to local docker  [env var:
                       ARISTA_GET_EOS_IMPORT_DOCKER]
  --skip-download      Skip download process - for debug only
  --docker-name TEXT   Docker image name  [env var:
                       ARISTA_GET_EOS_DOCKER_NAME; default: arista/ceos]
  --docker-tag TEXT    Docker image tag  [env var: ARISTA_GET_EOS_DOCKER_TAG]
  --version TEXT       EOS version to download  [env var:
                       ARISTA_GET_EOS_VERSION]
  --release-type TEXT  Release type (M for Maintenance, F for Feature)  [env
                       var: ARISTA_GET_EOS_RELEASE_TYPE; default: F]
  --branch TEXT        Branch to download  [env var: ARISTA_GET_EOS_BRANCH]
  --dry-run            Enable dry-run mode: only run code without system
                       changes
  --force              Force download/import even if cached files or Docker
                       images exist  [env var: ARISTA_GET_EOS_FORCE]
  --help               Show this message and exit.
```

!!! info
    You can get information about available version using the [`ardl info version` cli](./info.md)
