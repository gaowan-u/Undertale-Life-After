#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== UndertaleAfterLife Android Shell Setup ==="

if ! command -v gradle &>/dev/null && ! command -v gradlew &>/dev/null; then
    echo "[1] Installing gradle..."
    pkg install gradle -y
fi

if ! command -v sdkmanager &>/dev/null; then
    echo "[2] Installing Android SDK command-line tools..."
    pkg install android-sdk -y
fi

echo "[3] Generating Gradle wrapper..."
gradle wrapper --gradle-version 8.9

echo "[4] Done! Build with:"
echo "    ANDROID_HOME=\$PREFIX/share/android-sdk ./gradlew assembleDebug"
echo ""
echo "    APK will be at: app/build/outputs/apk/debug/app-debug.apk"
