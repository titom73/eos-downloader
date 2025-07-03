ARG PYTHON_VER=3
ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM python:${PYTHON_VER}-slim

RUN pip install --upgrade pip

WORKDIR /local
COPY . /local

LABEL maintainer="Thomas Grimonet <tom@inetsix.net>"
LABEL   "org.opencontainers.image.title"="eos-downloader" \
        "org.opencontainers.image.description"="eos-downloader container" \
        "org.opencontainers.artifact.description"="A CLI to manage Arista EOS version download" \
        "org.opencontainers.image.source"="https://github.com/titom73/eos-downloader" \
        "org.opencontainers.image.url"="https://github.com/titom73/eos-downloader" \
        "org.opencontainers.image.documentation"="https://github.com/titom73/eos-downloader" \
        "org.opencontainers.image.licenses"="Apache-2.0" \
        "org.opencontainers.image.vendor"="N/A" \
        "org.opencontainers.image.authors"="Thomas Grimonet <tom@inetsix.net>" \
        "org.opencontainers.image.base.name"="python" \
        "org.opencontainers.image.revision"="dev" \
        "org.opencontainers.image.version"="dev" \
        "annotation": {"org.opencontainers.image.description"="eos-downloader container"}

ENV PYTHONPATH=/local
RUN pip --no-cache-dir install .

ENTRYPOINT [ "/usr/local/bin/ardl" ]
