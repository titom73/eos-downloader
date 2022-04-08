CURRENT_DIR = $(shell pwd)
TESTS ?= tests/unit/ tests/system
TAG ?= eos_download and not slow
TEST_OPT = -rA --cov-report term:skip-covered
REPORT = -v --html=tests/report.html --html=report.html --self-contained-html --cov-report=html --color yes
# COVERAGE = --cov=eos_downloader

DOCKER_NAME ?= titom73/eos-downloader
DOCKER_TAG ?= dev
DOCKER_FILE ?= Dockerfile
PYTHON_VER ?= 3.8

.PHONY: test
test:
	pytest $(TEST_OPT) $(REPORT) $(COVERAGE) -m '$(TAG)' $(TESTS)

.PHONY: build
build:
	docker build -t $(DOCKER_NAME):$(DOCKER_TAG) --build-arg DOCKER_VERSION=$(DOCKER_VERSION) -f $(DOCKER_FILE) .