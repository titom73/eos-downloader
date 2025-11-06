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
	uv run mkdocs serve

.PHONY: docs-build
docs-build: ## Build documentation (with strict mode)
	@echo "Building documentation..."
	uv run mkdocs build --strict --verbose --clean
	@echo "✓ Documentation built successfully in ./site/"

.PHONY: docs-test
docs-test: ## Test mike deployment locally (no push)
	@echo "Testing mike deployment..."
	uv run mike deploy test-build test
	@echo "✓ Mike test successful (commit not pushed)"
	uv run mike list
	@echo ""
	@echo "⚠️  To undo the local commit: git reset --soft HEAD~1"

.PHONY: docs-list
docs-list: ## List all deployed documentation versions
	@echo "Deployed documentation versions:"
	uv run mike list

.PHONY: docs-deploy-dev
docs-deploy-dev: ## Deploy development documentation (main)
	@echo "Deploying development documentation..."
	uv run mike deploy --push main development
	@echo "✓ Development documentation deployed"

.PHONY: docs-deploy-stable
docs-deploy-stable: ## Deploy stable documentation (requires VERSION var)
ifndef VERSION
	@echo "Error: VERSION variable is required"
	@echo "Usage: make docs-deploy-stable VERSION=v0.13.0"
	@exit 1
endif
	@echo "Deploying stable documentation for $(VERSION)..."
	uv run mike deploy --push $(VERSION) stable
	uv run mike set-default --push stable
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
	uv run mike delete --push $(VERSION)
	@echo "✓ Documentation version $(VERSION) deleted"

.PHONY: docs-clean
docs-clean: ## Clean built documentation
	@echo "Cleaning documentation build..."
	rm -rf site/
	@echo "✓ Documentation build cleaned"

.PHONY: docs-help
docs-help: ## Show documentation helper commands
	@uv run bash .github/scripts/docs-helper.sh help

################################################################################
# Development & Testing targets (UV-based)
################################################################################

.PHONY: install
install: ## Install dependencies with UV (all extras)
	@echo "Installing all dependencies with UV..."
	uv sync --all-extras
	@echo "✓ Installation complete"

.PHONY: install-base
install-base: ## Install base dependencies only (production)
	@echo "Installing base dependencies..."
	uv sync
	@echo "✓ Base installation complete"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	uv sync --extra dev
	@echo "✓ Development installation complete"

.PHONY: install-doc
install-doc: ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	uv sync --extra doc
	@echo "✓ Documentation installation complete"

.PHONY: lint
lint: ## Run linting (flake8 + pylint)
	@echo "Running flake8..."
	uv run flake8 --max-line-length=165 --config=/dev/null eos_downloader
	@echo "✓ flake8 passed"
	@echo ""
	@echo "Running pylint..."
	uv run pylint --rcfile=pylintrc eos_downloader
	@echo "✓ pylint passed"

.PHONY: type
type: ## Run type checking with mypy
	@echo "Running mypy type checking..."
	uv run mypy --config-file=pyproject.toml eos_downloader
	@echo "✓ Type checking passed"

.PHONY: test
test: ## Run tests with pytest
	@echo "Running pytest..."
	uv run pytest -rA -q --color yes --cov=eos_downloader tests/
	@echo "✓ Tests passed"

.PHONY: coverage
coverage: ## Run tests with coverage report
	@echo "Running pytest with coverage..."
	uv run pytest -rA -q \
		--cov=eos_downloader \
		--cov-report term-missing \
		--cov-report html \
		--cov-report xml \
		--color yes \
		tests/
	@echo "✓ Coverage report generated"
	@echo "HTML report: htmlcov/index.html"
	@echo "XML report: coverage.xml"

.PHONY: format
format: ## Format code with black
	@echo "Formatting code with black..."
	uv run black eos_downloader tests
	@echo "✓ Code formatted"

.PHONY: format-check
format-check: ## Check code formatting without modifying
	@echo "Checking code formatting..."
	uv run black --check eos_downloader tests
	@echo "✓ Code formatting is correct"

################################################################################
# CI/CD targets (optimized for GitHub Actions)
################################################################################

.PHONY: ci-install
ci-install: ## CI: Install dependencies (dev extras only)
	@echo "CI: Installing dependencies..."
	uv sync --frozen --extra dev
	@echo "✓ CI installation complete"

.PHONY: ci-lint
ci-lint: ## CI: Run linting checks
	@echo "CI: Running lint checks..."
	uv run flake8 --max-line-length=165 --config=/dev/null eos_downloader
	uv run pylint --rcfile=pylintrc eos_downloader
	@echo "✓ CI lint passed"

.PHONY: ci-type
ci-type: ## CI: Run type checking
	@echo "CI: Running type checks..."
	uv run mypy --config-file=pyproject.toml eos_downloader
	@echo "✓ CI type checking passed"

.PHONY: ci-test
ci-test: ## CI: Run tests
	@echo "CI: Running tests..."
	uv run pytest -rA -q --color yes --cov=eos_downloader tests/
	@echo "✓ CI tests passed"

.PHONY: ci-coverage
ci-coverage: ## CI: Run tests with coverage and generate reports
	@echo "CI: Running coverage..."
	uv run pytest -rA -q \
		--cov=eos_downloader \
		--cov-report term-missing \
		--cov-report html \
		--cov-report xml \
		--color yes \
		tests/
	@echo "✓ CI coverage complete"

.PHONY: ci-all
ci-all: ci-lint ci-type ci-test ## CI: Run all checks (lint, type, test)
	@echo "✓ All CI checks passed"

################################################################################
# Utility targets
################################################################################

.PHONY: sync-python-versions
sync-python-versions: ## Sync Python versions from JSON to pyproject.toml
	@echo "Synchronizing Python versions..."
	uv run python .github/scripts/sync-python-versions.py
	@echo "✓ Python versions synchronized"
	@echo ""
	@echo "Review changes:"
	@echo "  git diff pyproject.toml"

.PHONY: clean
clean: docs-clean ## Clean all generated files
	@echo "Cleaning Python cache and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml .coverage 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "✓ Clean complete"

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	@echo "Removing .venv..."
	rm -rf .venv
	@echo "✓ Virtual environment removed"

.PHONY: reset
reset: clean clean-venv ## Full reset (clean + remove venv)
	@echo "Full reset complete. Run 'make install' to reinstall."

.PHONY: check
check: lint type test ## Run all local checks (lint, type, test)
	@echo "✓ All checks passed"

.PHONY: dev-setup
dev-setup: install ## Complete development setup
	@echo "Setting up development environment..."
	uv run pre-commit install
	@echo "✓ Development environment ready"
	@echo ""
	@echo "Available commands:"
	@echo "  make lint      - Run linting"
	@echo "  make type      - Run type checking"
	@echo "  make test      - Run tests"
	@echo "  make coverage  - Run tests with coverage"
	@echo "  make check     - Run all checks"
	@echo "  make format    - Format code"
