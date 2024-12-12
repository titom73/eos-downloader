CURRENT_DIR = $(shell pwd)

DOCKER_NAME ?= ghcr.io/titom73/eos-downloader
DOCKER_TAG ?= dev
DOCKER_FILE ?= Dockerfile
PYTHON_VER ?= 3

.PHONY: help
help: ## Display help message
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: base
base: ## Build a base image
	docker build -t $(DOCKER_NAME):$(DOCKER_TAG) --build-arg DOCKER_VERSION=$(DOCKER_VERSION) -f $(DOCKER_FILE) .

.PHONY: dnd
dnd:  ## Build a docker in docker image
	docker build -t $(DOCKER_NAME):dnd-$(DOCKER_TAG) --build-arg DOCKER_VERSION=$(DOCKER_VERSION) -f Dockerfile.docker .

.PHONY: build
build: base dnd  ## Build all dockers images (base and dnd)

.PHONY: push
push: ## Push the docker image to the registry
	docker push $(DOCKER_NAME):$(DOCKER_TAG)
