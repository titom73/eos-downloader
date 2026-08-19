#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Building EosDownloaderApp..."
/usr/bin/swift build 2>&1
BUILD_EXIT=$?
if [[ $BUILD_EXIT -ne 0 ]]; then
    echo "ERROR: swift build failed with exit code $BUILD_EXIT"
    exit $BUILD_EXIT
fi

# Detect arch-specific build dir
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    BUILD_DIR=".build/arm64-apple-macosx/debug"
else
    BUILD_DIR=".build/x86_64-apple-macosx/debug"
fi

# Verify the binary was actually built
if [[ ! -f "$BUILD_DIR/EosDownloaderApp" ]]; then
    echo "ERROR: Binary not found at $BUILD_DIR/EosDownloaderApp"
    find .build -name "EosDownloaderApp" -type f 2>/dev/null || echo "(none found)"
    exit 1
fi

APP="$BUILD_DIR/EosDownloaderApp.app"

echo "==> Creating .app bundle at $APP..."
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
mkdir -p "$APP/Contents/Resources"

cp "$BUILD_DIR/EosDownloaderApp" "$APP/Contents/MacOS/"
cp "Sources/EosDownloaderApp/Info.plist" "$APP/Contents/"

# PkgInfo marks this as a proper macOS application bundle
echo -n "APPL????" > "$APP/Contents/PkgInfo"

# Generate AppIcon.icns from docs/imgs/logo.jpg
SOURCE_LOGO="$SCRIPT_DIR/../docs/imgs/logo.jpg"
if [[ -f "$SOURCE_LOGO" ]]; then
    echo "==> Generating AppIcon.icns..."
    ICONSET_PARENT="$(mktemp -d)"
    ICONSET_TMP="$ICONSET_PARENT/AppIcon.iconset"
    mkdir -p "$ICONSET_TMP"
    for SIZE in 16 32 128 256 512; do
        sips -z $SIZE $SIZE "$SOURCE_LOGO" --setProperty format png \
            --out "$ICONSET_TMP/icon_${SIZE}x${SIZE}.png" > /dev/null
        DOUBLE=$((SIZE * 2))
        sips -z $DOUBLE $DOUBLE "$SOURCE_LOGO" --setProperty format png \
            --out "$ICONSET_TMP/icon_${SIZE}x${SIZE}@2x.png" > /dev/null
    done
    iconutil -c icns "$ICONSET_TMP" -o "$APP/Contents/Resources/AppIcon.icns" 2>/dev/null \
        && echo "    -> AppIcon.icns generated" \
        || echo "    -> iconutil failed, running without custom icon"
    rm -rf "$ICONSET_PARENT"
else
    echo "==> Skipping icon: $SOURCE_LOGO not found"
fi

echo "==> Launching app..."
open -n "$APP"
echo "Done."
