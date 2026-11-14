#!/usr/bin/env bash
set -eu

# Undertale: AfterLife — Nuitka 构建脚本

PLATFORM="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
case "$PLATFORM" in
    linux|windows|macos|darwin) ;;
    *) echo "Unsupported platform: $PLATFORM (use: linux, windows, macos)"; exit 1 ;;
esac

echo "=== Undertale: AfterLife — Nuitka Build ==="
echo "Platform: $PLATFORM"
echo "Arch:     $(uname -m)"

# ── Build ──────────────────────────────────────────────────────────
python3 -m nuitka \
    --standalone \
    --include-data-dir=images=images \
    --include-data-dir=audios=audios \
    --include-data-dir=fonts=fonts \
    --include-data-dir=data=data \
    --output-dir=dist \
    --output-filename=Undertale-AfterLife \
    --assume-yes-for-downloads \
    main.py

DIST_DIR="dist/main.dist"

# ── Termux patches ─────────────────────────────────────────────────
if [ "$PLATFORM" = "linux" ] && [ -n "${PREFIX:-}" ]; then
    echo "[Termux] Bundling libpython..."
    cp "${PREFIX}/lib/libpython3.14.so" "$DIST_DIR/" 2>/dev/null || true
    echo "[Termux] Creating launch wrapper..."
    cat > "$DIST_DIR/run.sh" << 'WRAPPER'
#!/data/data/com.termux/files/usr/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export LD_LIBRARY_PATH="/data/data/com.termux/files/usr/lib:${SCRIPT_DIR}"
chmod +x ./Undertale-AfterLife
exec "${SCRIPT_DIR}/Undertale-AfterLife"
WRAPPER
    chmod +x "$DIST_DIR/run.sh"
    echo "[Termux] Usage: cd dist/main.dist && ./run.sh"
fi

# ── Binary path ────────────────────────────────────────────────────
case "$PLATFORM" in
    windows) BIN="${DIST_DIR}/Undertale-AfterLife.exe" ; ARCHIVE_NAME="Undertale-AfterLife-windows" ;;
    linux)
        BIN="${DIST_DIR}/Undertale-AfterLife"
        case "$(uname -m)" in
            aarch64|armv8l|arm64) ARCHIVE_NAME="Undertale-AfterLife-linux-arm64" ;;
            *) ARCHIVE_NAME="Undertale-AfterLife-linux-x86_64" ;;
        esac
        ;;
    macos|darwin) BIN="${DIST_DIR}/Undertale-AfterLife" ; ARCHIVE_NAME="Undertale-AfterLife-macos" ;;
esac

# ── Verify ─────────────────────────────────────────────────────────
if [ -f "$BIN" ]; then
    chmod +x "$BIN" 2>/dev/null || true
    echo ""
    echo "=== Build OK ==="
    echo "Binary:  $BIN"
    echo "Dist:    $DIST_DIR"
else
    echo "=== FAIL: binary not found at $BIN ==="
    find dist/ -type f -executable 2>/dev/null || find dist/ -type f 2>/dev/null | head -20
    exit 1
fi

# ── Create archive ─────────────────────────────────────────────────
echo ""
echo "Packaging: ${ARCHIVE_NAME}.zip"
(cd "$DIST_DIR" && zip -r "../${ARCHIVE_NAME}.zip" .)
echo "Archive: dist/${ARCHIVE_NAME}.zip"
