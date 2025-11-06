# Notes

Notes regarding how to release eos-downloader package

## Package requirements

- UV package manager (with dev dependencies installed: `uv sync --extra dev`)
- `bumpver` (installed via UV dev dependencies)
- `build` (installed via UV dev dependencies)
- `twine` (installed via UV dev dependencies)

Also, [Github CLI](https://cli.github.com/) can be helpful and is recommended

## Bumping version

In a branch specific for this, use the `bumpver` tool.
It is configured to update:
* pyproject.toml

For instance to bump a patch version:

```bash
uv run bumpver update --patch --tag final
```

and for a minor version

```bash
uv run bumpver update --minor --tag final
```

Tip: It is possible to check what the changes would be using `--dry`

```bash
uv run bumpver update --minor  --tag final --dry
```

For a development version, you can use the following:

```bash
uv run bumpver update --minor  --tag dev --tagnum --dry
```

The following tag should be used:

- `dev`: for internal testing
- `rc`: for release candidate testing

> ![INFORMATION]
> This tags are not released to pypi and are only available via git installation.

## Creating release on Github

Create the release on Github with the appropriate tag `vx.x.x`

## Release version `x.x.x`

> [!IMPORTANT]
> TODO - make this a github workflow

`x.x.x` is the version to be released

This is to be executed at the top of the repo

1. Checkout the latest version of `main` with the correct tag for the release
2. Create a new branch for release

   ```bash
   git switch -c rel/vx.x.x
   ```
3. [Optional] Clean dist if required

4. Build the package locally

   ```bash
   uv build
   ```
5. Check the package with `twine` (replace with your vesion)

    ```bash
    uv run twine check dist/*
    ```
6. Upload the package to test.pypi

    ```bash
    uv run twine upload -r testpypi dist/eos-downloader-x.x.x.*
    ```
7. Verify the package by installing it in a local venv and checking it installs
   and run correctly (run the tests)

   ```bash
   # In a brand new UV environment
   uv venv test-release
   source test-release/bin/activate  # On Windows: test-release\Scripts\activate
   uv pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple --no-cache eos-downloader
   ```
8. Push to eos-downloader repository and create a Pull Request

    ```bash
    git push origin HEAD
    gh pr create --title 'bump: eos-downloader vx.x.x'
    ```
9.  Merge PR after review and wait for [workflow](https://github.com/titom73/eos-downloader/blob/main/.github/workflows/release.yml) to be executed.

   ```bash
   gh pr merge --squash
   ```

10. Like 7 but for normal pypi

    ```bash
    # In a brand new UV environment
    uv venv test-prod-release
    source test-prod-release/bin/activate  # On Windows: test-prod-release\Scripts\activate
    uv pip install eos-downloader
    ```

11. Test installed version

    ```bash
    eos-downloader --version
    ```