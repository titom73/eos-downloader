# Download cEOS images from a containerlab topology

The `--containerlab-topology` (or `--clab`) option parses a [containerlab](https://containerlab.dev/) topology YAML file, extracts all cEOS versions referenced by nodes, and batch-downloads + imports them to Docker in a single command.

## Prerequisites

- A valid containerlab topology file with `kind: ceos` nodes
- Each cEOS node must have a resolvable Docker image with an EOS version tag (e.g., `arista/ceos:4.33.1F`)

## Examples

```bash
# Download all cEOS images from a containerlab topology
ardl get eos --clab topology.clab.yml --format cEOS

# Use ARM-based cEOS images
ardl get eos --clab topology.clab.yml --format cEOSarm

# Preview what would be downloaded without making changes
ardl get eos --clab topology.clab.yml --format cEOS --dry-run

# Use a custom Docker image name
ardl get eos --clab topology.clab.yml --format cEOS --docker-name myregistry/ceos

# Force re-download and re-import even if images are cached
ardl get eos --clab topology.clab.yml --format cEOS --force
```

## How it works

1. **Parses** the containerlab YAML topology file
2. **Identifies** all nodes with `kind: ceos`
3. **Resolves images** from node-level `image` fields, falling back to kind-level defaults (`topology.kinds.ceos.image`)
4. **Supports environment variables** in image strings using `${VAR:=default}` syntax
5. **Deduplicates** versions — each unique EOS version is downloaded only once
6. **Downloads** each version from the Arista server
7. **Imports** each image to Docker with the appropriate name and tag

## Topology file example

A minimal containerlab topology that uses a kind-level default image with a node-level override:

```yaml
name: my-lab

topology:
  kinds:
    ceos:
      image: arista/ceos:4.33.1F

  nodes:
    spine1:
      kind: ceos
    spine2:
      kind: ceos
    leaf1:
      kind: ceos
      image: arista/ceos:4.34.2.1F  # override the default
    leaf2:
      kind: ceos
```

In this example, `ardl` would download two versions: `4.33.1F` and `4.34.2.1F`.

### Using environment variables

Containerlab supports environment variable substitution in image strings. This is useful for CI/CD pipelines or shared topology files:

```yaml
topology:
  kinds:
    ceos:
      image: ${EOS_IMAGE:=arista/ceos}:${EOS_VERSION:=4.34.2.1F}
```

If `EOS_VERSION` is not set in the environment, the default value `4.34.2.1F` will be used.

!!! warning "Mutual exclusivity"
    The `--containerlab-topology` / `--clab` option is mutually exclusive with `--version`, `--latest`, and `--branch`. You cannot specify both a topology file and a specific version selector.

!!! tip "Dry-run mode"
    Use `--dry-run` to preview which versions would be downloaded and imported without actually downloading files or modifying Docker images. This is useful for validating your topology file.

## ardl get eos options

Below are all the options available to get EOS package:

```bash
$ ardl get eos --help
Usage: ardl get eos [OPTIONS]

  Download EOS image from Arista server.

Options:
  --format TEXT                   Image format  [default: vmdk]
  --output PATH                   Path to save image  [env var:
                                  ARISTA_GET_EOS_OUTPUT; default: .]
  --latest                        Get latest version. If --branch is not use,
                                  get the latest branch with specific release
                                  type  [env var: ARISTA_GET_EOS_LATEST]
  --eve-ng                        Run EVE-NG vEOS provisioning (only if CLI
                                  runs on an EVE-NG server)  [env var:
                                  ARISTA_GET_EOS_EVE_NG]
  --import-docker                 Import docker image to local docker  [env
                                  var: ARISTA_GET_EOS_IMPORT_DOCKER]
  --skip-download                 Skip download process - for debug only
  --docker-name TEXT              Docker image name  [env var:
                                  ARISTA_GET_EOS_DOCKER_NAME; default:
                                  arista/ceos]
  --docker-tag TEXT               Docker image tag  [env var:
                                  ARISTA_GET_EOS_DOCKER_TAG]
  --version TEXT                  EOS version to download  [env var:
                                  ARISTA_GET_EOS_VERSION]
  --release-type TEXT             Release type (M for Maintenance, F for
                                  Feature)  [env var:
                                  ARISTA_GET_EOS_RELEASE_TYPE; default: F]
  --branch TEXT                   Branch to download  [env var:
                                  ARISTA_GET_EOS_BRANCH]
  --dry-run                       Enable dry-run mode: only run code without
                                  system changes
  --force                         Force download/import even if cached files
                                  or Docker images exist  [env var:
                                  ARISTA_GET_EOS_FORCE]
  --containerlab-topology, --clab FILE
                                  Path to containerlab topology file to
                                  download all cEOS images.
  --help                          Show this message and exit.
```

!!! info
    You can get information about available version using the [`ardl info version` cli](./info.md)
