#!/usr/bin/env python3
"""把 Termux($PREFIX/lib) 里的非系统共享库收进 Nuitka 的 dist 目录。

Nuitka 在 Android 上无法自动修补 rpath，所以 pygame 依赖的 SDL2 / freetype /
图片音频解码库不会被捆绑。此脚本从 dist 里所有 ELF 的 DT_NEEDED 出发，
递归解析依赖，把 Termux 提供的库复制到 dist 根目录；libc/libm/libdl 等
由 Android 系统提供、或直接存在于 dist 的库会被跳过。

用法：python3 tools/bundle_termux_libs.py dist/main.dist
"""
import os
import re
import shutil
import subprocess
import sys

SYSTEM_DIRS = (
    "/system/lib64",
    "/system/lib",
    "/apex/com.android.runtime/lib64/bionic",
    "/apex/com.android.runtime/lib/bionic",
)
SYSTEM_LIBS = {
    "libc.so",
    "libm.so",
    "libdl.so",
    "liblog.so",
    "libandroid.so",
    "libstdc++.so",
    "libz.so",
    "libnativehelper.so",
    "libbinder.so",
    "libutils.so",
}


def is_elf(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def elf_needed(path: str) -> list[str]:
    out = subprocess.run(
        ["readelf", "-d", path], capture_output=True, text=True, check=False
    ).stdout
    return re.findall(r"Shared library: \[([^\]]+)\]", out)


def find_library(name: str, termux_lib: str) -> tuple[str | None, str | None]:
    """返回 (库真实路径, 来源)。来源为 'termux' / 'system' / None。"""
    if os.path.exists(os.path.join(termux_lib, name)):
        return os.path.realpath(os.path.join(termux_lib, name)), "termux"
    for d in SYSTEM_DIRS:
        candidate = os.path.join(d, name)
        if os.path.exists(candidate):
            return candidate, "system"
    return None, None


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: bundle_termux_libs.py <dist_dir>", file=sys.stderr)
        return 2

    dist = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dist):
        print(f"错误: dist 目录不存在: {dist}", file=sys.stderr)
        return 2

    termux_lib = os.path.join(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"), "lib")

    queue = []
    for dirpath, _, files in os.walk(dist):
        for f in files:
            p = os.path.join(dirpath, f)
            if is_elf(p):
                queue.append(p)

    if not queue:
        print("错误: dist 里没有找到 ELF 文件", file=sys.stderr)
        return 1

    seen: set[str] = set()
    copied: list[tuple[str, int]] = []
    missing: list[tuple[str, str]] = []

    while queue:
        path = queue.pop()
        for name in elf_needed(path):
            if name in seen:
                continue
            seen.add(name)

            if os.path.exists(os.path.join(dist, name)):
                continue  # dist 已有，无需处理

            real, source = find_library(name, termux_lib)
            if real is None:
                missing.append((name, os.path.relpath(path, dist)))
                continue
            if source == "system" or name in SYSTEM_LIBS:
                continue

            dest = os.path.join(dist, name)
            shutil.copy2(real, dest)
            copied.append((name, os.path.getsize(real)))
            queue.append(dest)

    for name, size in sorted(copied):
        print(f"  + {name:32s} {size / 1e6:6.2f} MB")

    total = sum(size for _, size in copied)
    print(f"[bundle] 新增 {len(copied)} 个库, {total / 1e6:.1f} MB")

    if missing:
        print("\n[bundle] 以下依赖未找到（可能导致启动失败）：", file=sys.stderr)
        for name, referrer in missing:
            print(f"  ! {name}  <- {referrer}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
