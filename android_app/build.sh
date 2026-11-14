#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")"

ANDROID_HOME="${ANDROID_HOME:-/data/data/com.termux/files/home/android-sdk}"
export ANDROID_HOME

# ---- helpers ----
find_aapt2_jar() {
    find "$HOME/.gradle/caches/modules-2/files-2.1/com.android.tools.build/aapt2" \
        -name 'aapt2-*-linux.jar' -type f 2>/dev/null | head -1
}

aapt2_jar_has_arm() {
    local jar="$1"
    local tmpdir="$ANDROID_HOME/tmp"
    mkdir -p "$tmpdir"
    local out
    out=$(cd "$tmpdir" && jar xf "$jar" aapt2 && file aapt2 2>/dev/null)
    rm -f "$tmpdir/aapt2"
    echo "$out" | grep -q 'ARM aarch64'
}

# ---- step 1: ensure Termux packages ----
echo "[1/4] Checking Termux packages..."
for pkg in aapt aapt2 d8; do
    if ! pkg list-installed 2>/dev/null | grep -q "^$pkg/"; then
        echo "  Installing $pkg..."
        pkg install "$pkg" -y >/dev/null 2>&1
    fi
done
echo "  OK"

# ---- step 2: patch aapt2 JAR (ARM replacement) ----
AAPT2_JAR=$(find_aapt2_jar)
if [ -z "$AAPT2_JAR" ]; then
    echo "[2/4] aapt2 JAR not found in cache — will be downloaded on first build."
else
    echo "[2/4] aapt2 JAR: $AAPT2_JAR"
    if [ -f "${AAPT2_JAR}.orig" ]; then
        echo "  Already patched. Skipping."
    elif aapt2_jar_has_arm "$AAPT2_JAR"; then
        echo "  Already ARM. Skipping."
    else
        echo "  Patching x86_64 → ARM..."
        cp "$AAPT2_JAR" "${AAPT2_JAR}.orig"
        TMPDIR="$ANDROID_HOME/tmp"
        mkdir -p "$TMPDIR"
        (
            cd "$TMPDIR"
            jar xf "$AAPT2_JAR" aapt2
            cp /data/data/com.termux/files/usr/bin/aapt2 ./aapt2
            jar uf "$AAPT2_JAR" aapt2
            rm -f aapt2
        )
        echo "  Patched."
        # Clear ALL Gradle transform caches so it re-extracts the ARM binary
        TRANSFORM_CACHE="$HOME/.gradle/caches"
        if [ -d "$TRANSFORM_CACHE" ]; then
            for dir in "$TRANSFORM_CACHE"/*/transforms/*/transformed/aapt2-*; do
                if [ -d "$dir" ]; then
                    rm -rf "$dir" 2>/dev/null || true
                fi
            done
            echo "  Transform caches cleared."
        fi
    fi
fi

# ---- step 3: ensure local.properties ----
echo "[3/4] Checking local.properties..."
if ! grep -q "sdk.dir" local.properties 2>/dev/null; then
    echo "sdk.dir=$ANDROID_HOME" > local.properties
    echo "  Written."
else
    echo "  OK"
fi

# ---- step 4: build ----
echo "[4/4] Building APK..."
./gradlew assembleDebug --no-daemon

echo ""
echo "=== BUILD COMPLETE ==="
echo "APK: $(realpath app/build/outputs/apk/debug/app-debug.apk 2>/dev/null || echo 'app/build/outputs/apk/debug/app-debug.apk')"
