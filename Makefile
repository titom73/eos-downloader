CURRENT_DIR = $(shell pwd)

DOCKER_NAME ?= titom73/eos-downloader
DOCKER_TAG ?= dev
DOCKER_FILE ?= Dockerfile
PYTHON_VER ?= 3.9

.PHONY: build
build:
	docker build -t $(DOCKER_NAME):$(DOCKER_TAG) --build-arg DOCKER_VERSION=$(DOCKER_VERSION) -f $(DOCKER_FILE) .
