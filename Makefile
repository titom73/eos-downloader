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

################################################################################
# Documentation targets
################################################################################

.PHONY: docs-serve
docs-serve: ## Serve documentation locally (with live reload)
	@echo "Starting MkDocs server..."
	@echo "Access at: http://127.0.0.1:8000"
	mkdocs serve

.PHONY: docs-build
docs-build: ## Build documentation (with strict mode)
	@echo "Building documentation..."
	mkdocs build --strict --verbose --clean
	@echo "✓ Documentation built successfully in ./site/"

.PHONY: docs-test
docs-test: ## Test mike deployment locally (no push)
	@echo "Testing mike deployment..."
	@mike deploy test-build test
	@echo "✓ Mike test successful (commit not pushed)"
	@mike list
	@echo ""
	@echo "⚠️  To undo the local commit: git reset --soft HEAD~1"

.PHONY: docs-list
docs-list: ## List all deployed documentation versions
	@echo "Deployed documentation versions:"
	@mike list

.PHONY: docs-deploy-dev
docs-deploy-dev: ## Deploy development documentation (main)
	@echo "Deploying development documentation..."
	mike deploy --push main development
	@echo "✓ Development documentation deployed"

.PHONY: docs-deploy-stable
docs-deploy-stable: ## Deploy stable documentation (requires VERSION var)
ifndef VERSION
	@echo "Error: VERSION variable is required"
	@echo "Usage: make docs-deploy-stable VERSION=v0.13.0"
	@exit 1
endif
	@echo "Deploying stable documentation for $(VERSION)..."
	mike deploy --push $(VERSION) stable
	mike set-default --push stable
	@echo "✓ Stable documentation deployed for $(VERSION)"

.PHONY: docs-delete
docs-delete: ## Delete a documentation version (requires VERSION var)
ifndef VERSION
	@echo "Error: VERSION variable is required"
	@echo "Usage: make docs-delete VERSION=v0.10.0"
	@exit 1
endif
	@echo "Deleting documentation version $(VERSION)..."
	@read -p "Are you sure? [y/N]: " confirm && [ "$$confirm" = "y" ]
	mike delete --push $(VERSION)
	@echo "✓ Documentation version $(VERSION) deleted"

.PHONY: docs-clean
docs-clean: ## Clean built documentation
	@echo "Cleaning documentation build..."
	rm -rf site/
	@echo "✓ Documentation build cleaned"

.PHONY: docs-help
docs-help: ## Show documentation helper commands
	@./scripts/docs-helper.sh help
