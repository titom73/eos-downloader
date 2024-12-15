# Environment Variables in eos-downloader

## Overview

`ardl` is able to read environment variables to replace cli option to make it easier to work with in workflow. Even if all cli options can be replaced by environment variables, here are the most useful ones:

Standard rule for these variables is:

```bash
# root command
ARISTA_<OPTION_NAME>

# First Level command
ARISTA_<COMMAND_NAME>_<OPTION_NAME>

# Second level command
ARISTA_<COMMAND_NAME>_<COMMAND_NAME>_<OPTION_NAME>
```

!!! TIP "How to get variable names"
    Standard _ENV_ variables are exposed in cli help and are visible with `[env var: ARISTA_GET_EOS_DOCKER_TAG]`

## Standard Variables

__Generic Options__:

- __ARISTA_TOKEN__ (`ardl --token`): Load your token and avoid to print your token in clear text during a workflow.

__EOS Options__:

- __ARISTA_GET_EOS_FORMAT__ (`ardl get eos --format`): Image format
- __ARISTA_GET_EOS_OUTPUT__ (`ardl get eos --output`): Path to save EOS image.
- __ARISTA_GET_EOS_VERSION__ (`ardl get eos --version`): Version to download from Arista server
- __ARISTA_GET_EOS_BRANCH__ (`ardl get eos --latest`): Flag to retrieve latest version available from arista server.
- __ARISTA_GET_EOS_BRANCH__ (`ardl get eos --branch`): Branch to download
- __ARISTA_GET_EOS_EVE_NG__ (`ardl get eos --eve-ng`): Run EVE-NG vEOS provisioning (only if CLI runs on an EVE-NG server).
- __ARISTA_GET_EOS_DOCKER_NAME__ (`ardl get eos --docker-name`): Docker image name when importing cEOS.
- __ARISTA_GET_EOS_DOCKER_TAG__ (`ardl get eos --docker-tag`): Docker tag to use when cEOS image is imported in Docker.
- __ARISTA_GET_EOS_RELEASE_TYPE__ (`ardl get eos --release-type`): Release type (M for Maintenance, F for Feature)

__CVP options__:

- __ARISTA_GET_CVP_FORMAT__ (`ardl get cvp --format`): Image format
- __ARISTA_GET_CVP_OUTPUT__ (`ardl get cvp --output`): Path to save CVP image.
- __ARISTA_GET_CVP_LATEST__ (`ardl get cvp --latest`): Flag to retrieve latest version available from arista server.
- __ARISTA_GET_CVP_VERSION__ (`ardl get cvp --version`): Version to download from Arista server
- __ARISTA_GET_CVP_BRANCH__ (`ardl get cvp --branch`): Branch to download


## Usage examples

- Basic usage with `export`

```bash
# Use token from env variables
export ARISTA_TOKEN=1234567890
ardl info versions --branch 4.29
```

- Usage with direnv

```bash
cat .envrc
export ARISTA_TOKEN=1234567890

direnv allow
direnv: loading .envrc
direnv: export +ARISTA_TOKEN

ardl info versions --branch 4.29
```