## 传说之下-劫后余生 v0.1.3

本版本使用 **Nuitka** 编译为原生二进制，无需安装 Python。

### 下载

| 平台 | 文件 |
|------|------|
| Windows (x64) | `Undertale-AfterLife-windows.zip` |
| Linux (x86_64) | `Undertale-AfterLife-linux-x86_64.zip` |
| macOS | `Undertale-AfterLife-macos.zip` |
| Linux / Termux (ARM64) | `Undertale-AfterLife-linux-arm64.zip` |

### 使用方法

**Windows / Linux (x86_64) / macOS：**
解压后直接运行 `Undertale-AfterLife`（Windows 上为 `Undertale-AfterLife.exe`）。所有依赖已打包在内，开箱即用。

**Termux / Linux ARM64：**
解压后运行 `./run.sh` 启动。

### Termux 用户必读

**为什么需要 `run.sh`？**
ARM64 版本使用 `run.sh` 启动，原因如下：

Nuitka 将 Python 代码编译为了原生二进制，程序本身的 Python 层已经无需解释器。但 `pygame` 底层依赖一系列 **C 动态库**（System-Level 库），包括：

- `libSDL2-2.0.so` — 图形/音频/输入
- `libfreetype.so` — 字体渲染
- `libpng16.so` — 图片解码
- `libogg.so` / `libvorbis.so` — 音频编解码
- `libandroid-support.so` — Termux 兼容层

在桌面 Linux / Windows / macOS 上，这些库由 Nuitka 自动打包进 dist 目录并修正路径，无需额外操作。但在 **Termux（Android）** 环境下，Android ELF 二进制格式不支持标准的 rpath 修正机制，导致 Nuitka 无法自动捆绑它们。

`run.sh` 的作用是将 Termux 系统库目录添加到 `LD_LIBRARY_PATH`，让动态链接器能找到这些库。**只要你的 Termux 安装过 `pygame`，这些依赖就已经存在，不需要额外安装。**

**前置依赖（Termux）：**
```bash
pkg install x11-repo
pkg install python-pygame
```
安装 `python-pygame` 时会自动拉入 `SDL2`、`freetype`、`libpng` 等所有底层依赖。

**启动报 segfault 怎么办？**
如果你启动时遇到以下错误：

```
pygame 2.6.1 (SDL 2.32.10, Python 3.14.6)
Hello from the pygame community.
[1] 7304 segmentation fault ./run.sh
```

**这不是软件本身的 bug。** 这是 Termux + Termux-X11 进程状态异常导致的。解决方法：

1. 将 Termux 和 Termux-X11 从后台划掉（彻底关闭，不只是切到后台）
2. 重新打开 Termux-X11，再打开 Termux
3. 重新运行 `./run.sh`

通常重启后即可正常启动。

### 编译说明

| 平台 | 编译环境 |
|------|---------|
| Windows | GitHub Actions (`windows-latest`) |
| Linux x86_64 | GitHub Actions (`ubuntu-latest`) |
| macOS | GitHub Actions (`macos-latest`) |
| ARM64 | Termux aarch64（本地 Nuitka 编译） |
