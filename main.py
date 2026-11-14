from typing import NoReturn
import os
import sys
import subprocess
import warnings

# 屏蔽两类启动噪音（必须先于 import pygame）：
# 1. pkg_resources 弃用警告——由 pygame.pkgdata 在导入时触发，过滤器需提前装好
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
# 2. Vulkan 加载器探测厂商驱动的 linker 警告——限定 ICD 扫描范围仅软件渲染器
#    （游戏走 SDL software/x11 渲染路径，不使用 Vulkan；setdefault 只影响本进程）
_LVP_ICD = os.path.join(os.environ.get('PREFIX', ''), 'share/vulkan/icd.d/lvp_icd.aarch64.json')
if os.path.exists(_LVP_ICD):
    os.environ.setdefault('VK_DRIVER_FILES', _LVP_ICD)
    os.environ.setdefault('VK_ICD_FILENAMES', _LVP_ICD)

import pygame

from resources import SCREEN_WIDTH, SCREEN_HEIGHT
from screen_adapter import render_to_screen, recreate as recreate_adapter, update as update_adapter
from scene_manager import SceneManager
from scenes.scenes_map import IntroScene


def _parse_args(argv: list[str]) -> bool:
    """解析启动参数。目前只有 --mute / -m：跳过音频初始化，静音启动。"""
    return '--mute' in argv or '-m' in argv


def _check_pulse_running() -> bool:
    """检测 pulseaudio 是否正在运行（带超时）。"""
    try:
        result = subprocess.run(
            ['pactl', 'info'],
            capture_output=True, text=True, timeout=3
        )
        return result.returncode == 0 and "Server Name: pulseaudio" in result.stdout
    except Exception:
        return False


def _init_audio(mute: bool = False) -> bool:
    """初始化音频。根据运行环境选择不同路径。mute=True 时直接跳过。"""
    if mute:
        return False

    # Termux 环境：检测 pulseaudio，必要时自动修复
    if 'PREFIX' in os.environ:
        if not _check_pulse_running():
            print("音频服务未运行，正在尝试自动修复...")
            try:
                from Fix_model.fix_pulse import fix_pulseaudio
                success, msg = fix_pulseaudio()
                print(msg)
                if not success:
                    return False
            except Exception as e:
                print(f"音频修复模块执行异常: {e}")
                return False
    # else: Windows / macOS / 桌面 Linux，跳过 pulseaudio 检测

    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)
        return True
    except pygame.error:
        pass

    return False


def main() -> NoReturn:
    # --- 初始化 ---
    mute = _parse_args(sys.argv[1:])
    pygame.init()
    audio_available = _init_audio(mute)
    if not audio_available and not mute:
        print("错误：无法初始化音频。")
        print("请确保音频服务已启动，例如：")
        print("  pulseaudio --start")
        print("提示：确实没有音频设备时，可用 --mute 静音启动。")
        pygame.quit()
        sys.exit(1)
    if mute:
        print("静音启动（--mute）")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("传说之下-劫后余生")
    recreate_adapter(screen)
    clock = pygame.time.Clock()

    from gameplay import init_assets
    init_assets()

    # --- 场景管理 ---
    manager = SceneManager()
    manager.start(IntroScene(manager, screen))

    # --- 游戏主循环 ---
    running = True
    try:
        while running:
            # --- 事件处理 ---
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    update_adapter(screen.get_size())

            if running:
                manager.handle_events(events)
                manager.update()

            # --- 渲染到逻辑 surface (1920×1080) + 缩放适配到屏幕 ---
            manager.draw()
            render_to_screen(screen)
            pygame.display.flip()
            clock.tick(60)  # 60帧

    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
    finally:
        manager.quit()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
