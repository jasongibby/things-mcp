#!/bin/bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v uv >/dev/null
command -v dxt >/dev/null

BUILD_PYTHON=$(uv python find '>=3.12')
BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/things-mcp.XXXXXX")
trap 'rm -rf "$BUILD_DIR"' EXIT
PACKAGE_DIR="$BUILD_DIR/package"
mkdir -p "$PACKAGE_DIR/server" dist

cp manifest.json "$PACKAGE_DIR/"
cp things_server.py "$PACKAGE_DIR/server/main.py"
cp url_scheme.py formatters.py "$PACKAGE_DIR/server/"

# Bundle the same runtime dependency versions used by the source installation.
uv export --locked --no-dev --no-emit-project \
    --output-file "$BUILD_DIR/requirements.txt" > /dev/null
uv pip install --python "$BUILD_PYTHON" --target "$PACKAGE_DIR/server/lib" \
    --require-hashes --requirements "$BUILD_DIR/requirements.txt"

VERSION=$("$BUILD_PYTHON" -c 'import json; print(json.load(open("manifest.json"))["version"])')
dxt pack "$PACKAGE_DIR" "dist/things-mcp-${VERSION}.dxt"
echo "Created dist/things-mcp-${VERSION}.dxt"
