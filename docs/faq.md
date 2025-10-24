# Frequently Asked Questions

## Caching and Performance

### How does the cache work?

**eos-downloader** implements smart caching at two levels:

1. **File Caching**: Before downloading, the tool checks if the file already exists in the output directory. If found, it reuses the existing file instead of re-downloading.

2. **Docker Image Caching**: Before importing a cEOS image, the tool checks if the `image:tag` already exists in your local Docker registry. If found, it skips the import.

### How do I force re-download or re-import?

Use the `--force` flag:

```bash
# Force re-download even if file exists
ardl get eos --version 4.29.4M --force

# Force re-import Docker image even if it exists
ardl get eos --version 4.29.4M --format cEOS --import-docker --force
```

### Does cache checking work with Podman?

Yes! The Docker image cache checking automatically detects and works with both `docker` and `podman` commands.

### Where are cached files stored?

Cached files are stored in the directory specified by the `--output` option (default: current directory). The cache is **per-directory**, so using different output directories creates separate caches.

### How can I verify cached files are valid?

Currently, file caching uses simple existence checks. For production use, you can:

1. Use the built-in checksum validation after download:
```bash
ardl get eos --version 4.29.4M
# Tool automatically validates md5/sha512 if available
```

2. Use `--force` to ensure a fresh download when integrity is critical.

### Does dry-run mode respect the cache?

Yes! When using `--dry-run`, the tool will report whether it would use cached files or perform actual downloads:

```bash
ardl get eos --version 4.29.4M --dry-run
# Output: [DRY-RUN] Would use cached file: EOS-4.29.4M.swi
```

## EVE-NG with OpenSSL issue.

On EVE-NG, you may have to install/upgrade __pyOpenSSL__ in version `23.0.0`:

```bash
# Error when running ardl: AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'

$ pip install pyopenssl --upgrade
```
