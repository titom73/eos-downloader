#!/usr/bin/env bash

# Documentation Deployment Helper Script
# This script helps with local documentation testing and deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}\n"
}

# Check if dependencies are installed
check_dependencies() {
    print_header "Checking Dependencies"

    if ! command -v uv &> /dev/null; then
        print_error "UV is not installed"
        print_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "UV found: $(uv --version)"

    if ! uv run python -c "import mkdocs" &> /dev/null; then
        print_warning "MkDocs not found. Installing dependencies..."
        uv sync --extra doc
    fi
    print_success "MkDocs is installed"

    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git found: $(git --version | head -n1)"
}

# Serve documentation locally
serve_docs() {
    print_header "Serving Documentation Locally"
    print_info "Starting MkDocs server..."
    print_info "Access at: http://127.0.0.1:8000"
    print_info "Press Ctrl+C to stop"
    echo ""
    uv run mkdocs serve
}

# Build documentation
build_docs() {
    print_header "Building Documentation"
    print_info "Building with strict mode..."
    uv run mkdocs build --strict --verbose --clean
    print_success "Documentation built successfully!"
    print_info "Output directory: ./site/"
}

# Test mike deployment
test_mike() {
    print_header "Testing Mike Deployment"

    # Configure git if not configured
    if ! git config user.name &> /dev/null; then
        print_info "Configuring git user..."
        git config --global user.name "Test User"
        git config --global user.email "test@example.com"
    fi

    print_info "Testing local deployment (creates local commit, no push)..."
    uv run mike deploy test-build test

    print_success "Mike test deployment successful!"
    print_info "Listing all versions:"
    uv run mike list

    print_warning "Note: This created a local commit. To undo: git reset --soft HEAD~1"
}

# List deployed versions
list_versions() {
    print_header "Deployed Documentation Versions"

    if git show-ref --quiet refs/remotes/origin/gh-pages; then
        print_info "Fetching gh-pages branch..."
        git fetch origin gh-pages

        print_info "Checking out gh-pages..."
        git checkout gh-pages

        if [ -f versions.json ]; then
            print_success "Versions found in gh-pages branch:"
            if ! python3 -m json.tool < versions.json; then
                print_error "Malformed JSON in versions.json. Please check the file contents."
            fi
        else
            print_warning "No versions.json found in gh-pages branch"
        fi

        git checkout -
    else
        print_warning "No gh-pages branch found"
        print_info "Documentation has not been deployed yet"
    fi
}

# Deploy specific version
deploy_version() {
    local version=$1
    local alias=$2

    if [ -z "$version" ]; then
        print_error "Version argument required"
        echo "Usage: $0 deploy <version> [alias]"
        exit 1
    fi

    print_header "Deploying Version: $version"

    if [ -n "$alias" ]; then
        print_info "Deploying $version with alias: $alias"
        uv run mike deploy --push "$version" "$alias"
    else
        print_info "Deploying $version without alias"
        uv run mike deploy --push "$version"
    fi

    print_success "Deployment complete!"
    # Extract repo owner and name for URL construction
    local REPO_OWNER=$(git config --get remote.origin.url | sed 's/.*github.com[:\/]\(.*\)\.git/\1/' | cut -d'/' -f1)
    local REPO_NAME=$(basename $(git rev-parse --show-toplevel))
    print_info "View at: https://${REPO_OWNER}.github.io/${REPO_NAME}/"
}

# Delete version
delete_version() {
    local version=$1

    if [ -z "$version" ]; then
        print_error "Version argument required"
        echo "Usage: $0 delete <version>"
        exit 1
    fi

    print_header "Deleting Version: $version"
    print_warning "This will permanently delete the version from gh-pages"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        uv run mike delete --push "$version"
        print_success "Version $version deleted"
    else
        print_info "Deletion cancelled"
    fi
}

# Set default version
set_default() {
    local version=$1

    if [ -z "$version" ]; then
        print_error "Version argument required"
        echo "Usage: $0 set-default <version>"
        exit 1
    fi

    print_header "Setting Default Version: $version"
    uv run mike set-default --push "$version"
    print_success "Default version set to: $version"
}

# Show help
show_help() {
    cat << EOF
Documentation Deployment Helper

Usage: $0 <command> [options]

Commands:
    serve           Serve documentation locally for development
    build           Build documentation (with strict mode)
    test            Test mike deployment locally (no push)
    list            List all deployed versions from gh-pages
    deploy          Deploy a specific version
                    Usage: $0 deploy <version> [alias]
                    Example: $0 deploy v0.13.0 stable
    delete          Delete a deployed version
                    Usage: $0 delete <version>
    set-default     Set default version for the documentation
                    Usage: $0 set-default <version>
    help            Show this help message

Examples:
    # Serve docs locally
    $0 serve

    # Build and validate docs
    $0 build

    # Test mike deployment
    $0 test

    # List deployed versions
    $0 list

    # Deploy development version
    $0 deploy main development

    # Deploy release version
    $0 deploy v0.13.0 stable

    # Set default version
    $0 set-default stable

    # Delete old version
    $0 delete v0.10.0

Documentation:
    See docs/contributing/documentation-deployment.md for more information
    See .github/workflows/README.md for workflow documentation

EOF
}

# Main script
main() {
    check_dependencies

    case "${1:-}" in
        serve)
            serve_docs
            ;;
        build)
            build_docs
            ;;
        test)
            test_mike
            ;;
        list)
            list_versions
            ;;
        deploy)
            deploy_version "$2" "$3"
            ;;
        delete)
            delete_version "$2"
            ;;
        set-default)
            set_default "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -z "${1:-}" ]; then
                print_error "No command specified"
            else
                print_error "Unknown command: $1"
            fi
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
