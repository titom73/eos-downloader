# Scripts Directory

This directory contains helper scripts for various development and deployment tasks.

## Available Scripts

### 📚 Documentation Helper (`docs-helper.sh`)

Interactive helper script for managing documentation with MkDocs and mike.

**Usage:**
```bash
./scripts/docs-helper.sh <command> [options]
```

**Commands:**
- `serve` - Start local documentation server with live reload
- `build` - Build documentation with strict validation
- `test` - Test mike deployment locally (no push)
- `list` - List all deployed documentation versions
- `deploy <version> [alias]` - Deploy specific version
- `delete <version>` - Delete deployed version
- `set-default <version>` - Set default version
- `help` - Show help message

**Examples:**
```bash
# Development workflow
./scripts/docs-helper.sh serve

# Validate documentation
./scripts/docs-helper.sh build

# Deploy version
./scripts/docs-helper.sh deploy v0.13.0 stable

# List versions
./scripts/docs-helper.sh list
```

**Features:**
- ✅ Colored output for better readability
- ✅ Dependency checking
- ✅ Interactive prompts for destructive operations
- ✅ Comprehensive error handling
- ✅ Git configuration automation

## Quick Start

All scripts are executable and can be run directly:

```bash
# Make script executable (already done in repo)
chmod +x scripts/docs-helper.sh

# Run script
./scripts/docs-helper.sh help
```

## Alternative: Makefile Targets

You can also use Makefile targets which wrap these scripts:

```bash
make docs-serve     # Same as: ./scripts/docs-helper.sh serve
make docs-build     # Same as: ./scripts/docs-helper.sh build
make docs-test      # Same as: ./scripts/docs-helper.sh test
make docs-list      # Same as: ./scripts/docs-helper.sh list
```

See `Makefile` for all available targets.

## Documentation

For detailed documentation on the deployment process:
- **Deployment Guide**: `docs/contributing/documentation-deployment.md`
- **Workflow Reference**: `.github/workflows/README.md`
- **Summary**: `docs/contributing/docs-deployment-summary.md`

## Requirements

### For Documentation Scripts
- Python 3.9+
- MkDocs and dependencies (install with `pip install -e ".[doc]"`)
- Git
- mike (included in doc dependencies)

### System Dependencies
- bash or zsh shell
- Standard Unix utilities (grep, awk, sed)

## Adding New Scripts

When adding new scripts to this directory:

1. **Make it executable**: `chmod +x scripts/your-script.sh`
2. **Add shebang**: Start with `#!/usr/bin/env bash`
3. **Add help**: Implement `--help` flag
4. **Document**: Update this README
5. **Add to Makefile**: Create corresponding make target if appropriate

### Script Template

```bash
#!/usr/bin/env bash

# Script Description
# Brief explanation of what this script does

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Show help
show_help() {
    cat << EOF
Usage: $0 [options]

Description of what the script does.

Options:
    -h, --help    Show this help message
    -v, --verbose Enable verbose output

Examples:
    $0
    $0 --verbose
EOF
}

# Main function
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Script logic here
    print_info "Starting..."
    # Do work
    print_success "Done!"
}

# Run main function
main "$@"
```

## Troubleshooting

### Script Permission Denied
```bash
# Fix: Make script executable
chmod +x scripts/your-script.sh
```

### Command Not Found
```bash
# Fix: Run from project root or use absolute path
cd /path/to/eos-downloader
./scripts/docs-helper.sh help
```

### Missing Dependencies
```bash
# Fix: Install project dependencies
pip install -e ".[dev,doc]"
```

## Support

For issues with scripts:
1. Check script has execute permissions: `ls -l scripts/`
2. Verify dependencies are installed
3. Run with `bash -x` for debugging: `bash -x scripts/docs-helper.sh command`
4. Check script documentation: `./scripts/script-name.sh --help`

## Contributing

When contributing scripts:
- Follow the template above
- Add comprehensive error handling
- Include helpful error messages
- Test on both macOS and Linux
- Update this README

---

**Last Updated**: 2025-10-24
