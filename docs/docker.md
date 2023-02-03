# Docker Image

A [docker image](https://hub.docker.com/repository/docker/titom73/eos-downloader/tags?page=1&ordering=last_updated) is also available when Python cannot be used.

## Connect to your docker container

```bash
$ docker pull titom73/eos-downloader:edge
docker run -it --rm --entrypoint bash titom73/eos-downloader:dev
root@a9a8ceb533df:/local# ardl get eos --help
$ cd /download
$ ardl --token xxxx get eos --image-format cEOS --version 4.28.3M
```

## Use CLI with docker

```bash
docker run --rm titom73/eos-downloader:dev get eos --help
Usage: ardl get eos [OPTIONS]

  Download EOS image from Arista website

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
  --help                          Show this message and exit.
```

#### Available TAGS

- `edge`: Latest version built from the main branch
- `latest`: Latest stable Version
- `semver`: Version built from git tag
- `latest-dind`: Latest stable Version with docker CLI
- `semver-dind`: Version built from git tag with docker CLI
