#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEST="$SCRIPT_DIR/../Sources/EosDownloaderApp/Resources/ardl_bundle"

cd "$PROJECT_ROOT"

echo "Building ardl binary from project root: $PROJECT_ROOT"

uv sync --all-extras

uv run pyinstaller \
  --onedir \
  --name ardl \
  --hidden-import eos_downloader \
  --target-architecture universal2 \
  --osx-bundle-identifier com.arista.eos-downloader.cli \
  --noconfirm \
  eos_downloader/cli/__main__.py

rm -rf "$DEST"
cp -r dist/ardl "$DEST"

echo "✅ ardl bundle ready at $DEST"
echo "   -> Verify: $DEST/ardl info versions --help"
