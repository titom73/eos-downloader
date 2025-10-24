# Quick Reference Guide - Documentation Deployment

## 🚀 Quick Start

### Local Development
```bash
# Option 1: Using Makefile
make docs-serve

# Option 2: Using helper script
./scripts/docs-helper.sh serve

# Option 3: Direct command
mkdocs serve
```

### Build and Validate
```bash
# Option 1: Using Makefile
make docs-build

# Option 2: Using helper script
./scripts/docs-helper.sh build

# Option 3: Direct command
mkdocs build --strict --verbose --clean
```

## 📋 Common Operations

### For Developers

#### Test Changes Locally
```bash
# 1. Start development server
make docs-serve
# → Access at http://127.0.0.1:8000

# 2. Make your changes in docs/

# 3. View changes in browser (auto-reload)

# 4. When satisfied, build to validate
make docs-build
```

#### Test Mike Deployment (No Push)
```bash
# Using Makefile
make docs-test

# Using helper script
./scripts/docs-helper.sh test

# Direct command
mike deploy test-build test
mike list
# Note: This creates a local commit. To undo: git reset --soft HEAD~1
```

### For Maintainers

#### Create a Release
```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "chore: bump version to v0.14.0"

# 3. Create and push tag
git tag v0.14.0
git push origin v0.14.0

# 4. Workflows automatically:
#    - Build and publish to PyPI
#    - Build and push Docker images
#    - Deploy documentation as v0.14.0 with alias 'stable'
#    - Set v0.14.0 as default version
```

#### Deploy Development Docs
```bash
# Automatic on push to main
git push origin main
# → Deploys as 'main' with alias 'development'

# Manual deployment
make docs-deploy-dev

# Using helper script
./scripts/docs-helper.sh deploy main development
```

#### Deploy Specific Version
```bash
# Using Makefile
make docs-deploy-stable VERSION=v0.13.0

# Using helper script
./scripts/docs-helper.sh deploy v0.13.0 stable

# Direct command
mike deploy --push v0.13.0 stable
```

#### List Deployed Versions
```bash
# Using Makefile
make docs-list

# Using helper script
./scripts/docs-helper.sh list

# Direct command
mike list
```

#### Delete Old Version
```bash
# Using Makefile
make docs-delete VERSION=v0.10.0

# Using helper script (with confirmation)
./scripts/docs-helper.sh delete v0.10.0

# Direct command
mike delete --push v0.10.0
```

#### Set Default Version
```bash
# Using helper script
./scripts/docs-helper.sh set-default stable

# Direct command
mike set-default --push stable
```

## 🔧 Troubleshooting

### Documentation Won't Build
```bash
# Check syntax errors
mkdocs build --strict

# Check specific file
cat docs/path/to/file.md

# Clear cache and rebuild
make docs-clean
make docs-build
```

### Mike Issues
```bash
# Verify mike is installed
pip show mike

# Reconfigure git (mike requirement)
git config --global user.name 'Your Name'
git config --global user.email 'your.email@example.com'

# Test locally (creates local commit, no push)
mike deploy test-build test
mike list
# To undo: git reset --soft HEAD~1
```

### Workflow Not Triggering
```bash
# Check workflow file syntax
cat .github/workflows/deploy-docs.yml

# View workflow runs
gh run list --workflow=deploy-docs.yml

# View specific run logs
gh run view <run-id>
```

### GitHub Pages Not Updating
```bash
# 1. Check gh-pages branch
git fetch origin gh-pages
git checkout gh-pages
git log -1
# Should show recent commit from GitHub Actions

# 2. Check versions.json
cat versions.json
# Should list all deployed versions

# 3. Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# 4. Check GitHub Pages settings
# Repository → Settings → Pages
# Source should be: gh-pages branch, / (root)
```

## 📚 Documentation Structure

```
docs/
├── README.md                           # Home page
├── contributing/
│   ├── documentation-deployment.md     # This guide
│   ├── docs-deployment-summary.md     # Executive summary
│   └── ...
├── usage/                              # Usage guides
└── api/                                # API documentation
```

## 🎯 Version Strategy

| Event | Version | Alias | Default |
|-------|---------|-------|---------|
| Tag `v0.13.0` push | `v0.13.0` | `stable` | ✅ Yes |
| Push to `main` | `main` | `development` | ❌ No |
| Manual dispatch | Custom | Custom/None | Optional |

## 🔗 Important URLs

- **Documentation Site**: https://titom73.github.io/eos-downloader/
- **Version Selector**: Dropdown in top navigation
- **All Versions**: https://titom73.github.io/eos-downloader/versions/
- **GitHub Repository**: https://github.com/titom73/eos-downloader
- **GitHub Actions**: https://github.com/titom73/eos-downloader/actions

## 📖 Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/contributing/documentation-deployment.md` | Complete deployment guide |
| `.github/workflows/README.md` | Workflow reference |
| `DOCS_DEPLOYMENT_CHANGELOG.md` | Change log |
| `scripts/README.md` | Scripts documentation |

## 🆘 Getting Help

1. **Check Documentation**: Review guides in `docs/contributing/`
2. **Helper Script**: Run `./scripts/docs-helper.sh help`
3. **Makefile**: Run `make help` for available targets
4. **GitHub Issues**: Open issue for bugs or questions
5. **Workflow Logs**: Check Actions tab for deployment issues

## 💡 Tips

### Speed Up Local Development
```bash
# Use incremental builds (default in serve mode)
mkdocs serve

# Skip strict mode for faster iteration
mkdocs build --clean
```

### Preview Before Deploying
```bash
# Build and serve from site/ directory
mkdocs build
cd site && python -m http.server 8001
```

### Verify Links
```bash
# Check for broken links (requires linkchecker)
mkdocs build
linkchecker site/
```

### Check File Changes
```bash
# See what will be deployed
git diff origin/gh-pages..HEAD -- docs/ mkdocs.yml
```

## 🎓 Learn More

- **MkDocs**: https://www.mkdocs.org/
- **MkDocs Material**: https://squidfunk.github.io/mkdocs-material/
- **Mike**: https://github.com/jimporter/mike
- **GitHub Actions**: https://docs.github.com/en/actions
- **GitHub Pages**: https://docs.github.com/en/pages

---

**Last Updated**: 2025-10-24  
**Maintainers**: @titom73
