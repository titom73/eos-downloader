# Download CloudVision package from arista website

This command gives you option to download EOS images localy. Some options are available based on image type like importing your cEOS container in your local registry

```bash
# Get latest version of CVP in Vvmware format
ardl get cvp --latest --format ova

# Get latest version of CVP in upgrade format
ardl get eos --branch 4.29 --format upgrade
```

## Interactive mode

Use `--interactive` (`-i`) to open a guided wizard that lets you pick the format,
branch and version with the arrow keys (CVP has no release type), choose the
output directory and a force-re-download toggle, then confirms with the
equivalent command before downloading.

```bash
ardl get cvp --interactive
```

`--interactive` requires an interactive terminal and a token, and cannot be
combined with `--version`, `--latest` or `--branch`.

## ardl get eos options

Below are all the options available to get EOS package:

```bash
$ ardl get cvp --help
Usage: ardl get cvp [OPTIONS]

  Download CVP image from Arista server.

Options:
  --format TEXT   Image format  [env var: ARISTA_GET_CVP_FORMAT; default: ova]
  --output PATH   Path to save image  [env var: ARISTA_GET_CVP_OUTPUT;
                  default: .]
  --latest        Get latest version. If --branch is not use, get the latest
                  branch with specific release type  [env var:
                  ARISTA_GET_CVP_LATEST]
  --version TEXT      EOS version to download  [env var: ARISTA_GET_CVP_VERSION]
  --branch TEXT       Branch to download  [env var: ARISTA_GET_CVP_BRANCH]
  --dry-run           Enable dry-run mode: only run code without system changes
  --force             Force download even if cached files exist  [env var:
                      ARISTA_GET_CVP_FORCE]
  --no-progress       Disable the download progress display (useful for
                      CI/non-TTY)
  --interactive, -i   Open a guided wizard to pick format, version and options
  --help
```

!!! info
    You can get information about available version using the [`ardl info version` cli](./info.md)