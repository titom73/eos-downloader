# Docker Image

A [docker image](https://hub.docker.com/repository/docker/titom73/eos-downloader/tags?page=1&ordering=last_updated) is also available when Python cannot be used.

```bash
$ docker pull titom73/eos-downloader:edge
$ docker run -it -rm -v ${PWD}:/download titom73/eos-downloader:edge bash
$ cd /download
$ eos-download --image cEOS --version 4.27.1F
```
#### Available TAGS

- `edge`: Latest version built from the main branch
- `latest`: Latest stable Version
- `semver`: Version built from git tag
- `latest-dind`: Latest stable Version with docker CLI
- `semver-dind`: Version built from git tag with docker CLI
