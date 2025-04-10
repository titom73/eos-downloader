# Download CloudVision package from arista website

This command gives you option to download EOS images localy. Some options are available based on image type like importing your cEOS container in your local registry

```bash
# Get latest version of CVP in Vvmware format
ardl get cvp --latest --format ova

# Get latest version of CVP in upgrade format
ardl get eos --branch 4.29 --format upgrade
```

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
  --version TEXT  EOS version to download  [env var: ARISTA_GET_CVP_VERSION]
  --branch TEXT   Branch to download  [env var: ARISTA_GET_CVP_BRANCH]
  --dry-run       Enable dry-run mode: only run code without system changes
  --help
```

!!! info
    You can get information about available version using the [`ardl info version` cli](./info.md)