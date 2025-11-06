ARG PYTHON_VER=3
ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM ghcr.io/astral-sh/uv:latest AS uv

FROM --platform=$BUILDPLATFORM python:${PYTHON_VER}-slim

# Copy UV from official image
COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /local

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

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
        "org.opencontainers.image.version"="dev"

# Copy application code
COPY . /local

# Install dependencies and application using UV with frozen lockfile for reproducibility
RUN uv sync --frozen --no-dev --no-editable

ENV PATH="/local/.venv/bin:$PATH"

ENTRYPOINT [ "ardl" ]
