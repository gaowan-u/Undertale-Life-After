#!/bin/bash
set -eu

# Undertale: AfterLife — Nuitka 构建脚本
# 用法: ./build.sh                    # 自动检测当前平台编译
#       ./build.sh windows             # GitHub Actions: windows-latest
#       ./build.sh linux               # GitHub Actions: ubuntu-latest
#       ./build.sh macos               # GitHub Actions: macos-latest

PLATFORM="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"

case "$PLATFORM" in
    linux|windows|macos|darwin)
        ;;
    *)
        echo "Unsupported platform: $PLATFORM (use: linux, windows, macos)"
        exit 1
        ;;
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

DIST_DIR="dist/Undertale-AfterLife.dist"

# ── Termux: bundle libpython (Nuitka auto-detect fails on Android) ──
if [ "$PLATFORM" = "linux" ] && [ -n "${PREFIX:-}" ]; then
    LIBPYTHON="/data/data/com.termux/files/usr/lib/libpython3.14.so"
    if [ -f "$LIBPYTHON" ] && [ ! -f "${DIST_DIR}/libpython3.14.so" ]; then
        echo "[Termux] Bundling libpython..."
        cp "$LIBPYTHON" "$DIST_DIR/"
    fi
fi

# ── Determine binary path ──────────────────────────────────────────
case "$PLATFORM" in
    windows)
        BIN="${DIST_DIR}/Undertale-AfterLife.exe"
        ARCHIVE_NAME="Undertale-AfterLife-windows"
        ;;
    linux)
        BIN="${DIST_DIR}/Undertale-AfterLife.bin"
        case "$(uname -m)" in
            aarch64|armv8l|arm64)
                ARCHIVE_NAME="Undertale-AfterLife-linux-arm64"
                ;;
            *)
                ARCHIVE_NAME="Undertale-AfterLife-linux-x86_64"
                ;;
        esac
        ;;
    macos|darwin)
        BIN="${DIST_DIR}/Undertale-AfterLife.bin"
        ARCHIVE_NAME="Undertale-AfterLife-macos"
        ;;
esac

# ── Verify ─────────────────────────────────────────────────────────
if [ -f "$BIN" ]; then
    chmod +x "$BIN" 2>/dev/null || true
    echo ""
    echo "=== Build OK ==="
    echo "Binary:  $BIN"
    echo "Dist:    $DIST_DIR"
else
    echo ""
    echo "=== WARNING: binary not found ==="
    echo "Expected: $BIN"
    find dist/ -type f -perm -111 2>/dev/null || find dist/ -type f 2>/dev/null | head -20
    exit 1
fi

# ── Create archive ─────────────────────────────────────────────────
echo ""
echo "Packaging: ${ARCHIVE_NAME}.zip"
(cd "$DIST_DIR" && zip -r "../${ARCHIVE_NAME}.zip" .)
echo "Archive: dist/${ARCHIVE_NAME}.zip"
