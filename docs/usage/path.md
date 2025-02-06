# Download any arista package

This command gives an option for advanced users to download any packages available on arista website and using the standard authentication mechanism.

!!! warning
    This command is for advanced user only

```bash
# Get a package from arista server
ardl get path -s "/support/path/to/docker/image/cEOS-lab-4.32.3M.tar.xz"

# Get a package from arista server and import into your docker engine
ardl get path -s "/support/path/to/docker/image/cEOS-lab-4.32.3M.tar.xz" --import-docker

# Get a package from arista server and import into your docker engine with specific image and version
ardl get path -s "/support/path/to/docker/image/cEOS-lab-4.32.3M.tar.xz" --import-docker --docker-image arista/myceos --docker-version 4.32.3M
```

## ardl get path options

```bash
$ ardl get path --help
Usage: ardl get path [OPTIONS]

  Download image from Arista server using direct path.

Options:
  -s, --source TEXT   Image path to download from Arista Website
  -o, --output PATH   Path to save downloaded package  [env var:
                      ARISTA_GET_PATH_OUTPUT; default: .]
  --import-docker     Import docker image to local docker  [env var:
                      ARISTA_GET_PATH_IMPORT_DOCKER]
  --docker-name TEXT  Docker image name  [env var:
                      ARISTA_GET_PATH_DOCKER_NAME; default: arista/ceos:raw]
  --docker-tag TEXT   Docker image tag  [env var: ARISTA_GET_PATH_DOCKER_TAG;
                      default: dev]
  --help              Show this message and exit.
```
