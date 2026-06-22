from typing import NoReturn
from main_menu import MainMenu
from intro_animation import play as play_intro
from gameplay import gameplay, init_assets, init_session_from_save, set_touch_ui_visible, get_touch_ui_visible
from save_system import save_system
from save_menu import SaveMenu
from setting import Setting
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT
import pygame
import sys
import warnings
import math
import os
import subprocess

# 忽略Pygame的社区警告
warnings.filterwarnings("ignore", category=UserWarning,
                        module='pygame.pkgdata')

# 导入其他模块

background_music = "./audios/menu_music.ogg" # 菜单背景音乐


def _play_menu_bgm(audio_available: bool, bgm_playing: bool) -> bool:
    """播放菜单背景音乐，返回新的播放状态"""
    if not bgm_playing and audio_available:
        try:
            pygame.mixer.music.load(background_music)
            pygame.mixer.music.play(-1)
            return True
        except pygame.error:
            print(f"警告：无法加载菜单音乐：{background_music}！")
    return bgm_playing


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


def _init_audio() -> bool:
    """初始化音频。根据运行环境选择不同路径。"""
    if 'ANDROID_ARGUMENT' in os.environ:
        # p4a APK 环境，直接初始化
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.5)
            return True
        except pygame.error:
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
    pygame.init()
    audio_available = _init_audio()
    if not audio_available:
        print("错误：无法初始化音频。")
        print("请确保音频服务已启动，例如：")
        print("  pulseaudio --start")
        pygame.quit()
        sys.exit()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    init_assets()
    pygame.display.set_caption("传说之下-劫后余生")
    clock = pygame.time.Clock()
    # --- 游戏状态和组件 ---
    game_state = 'intro'
    main_menu = MainMenu(screen)
    save_menu = SaveMenu(screen)
    setting_menu = Setting(screen)
    disclaimer_start_time = -1

    # 用于在暂停时保留游戏画面
    gameplay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    gameplay_surface.fill((0, 0, 0))  # 默认游戏背景

    # --- 版权声明内容 ---
    disclaimer_font = Resources().font_24
    disclaimer_text = [
        "本作品为粉丝创作，非官方授权产品",
        "Undertale™ 是Toby Fox的注册商标",
        "与Undertale开发团队无任何关联",
        "角色版权归原著作权方所有",
        "美术资源遵循CC BY-NC 4.0协议"
    ]

    # 预渲染文本表面（性能优化）
    disclaimer_text_surfaces = []
    disclaimer_shadow_surfaces = []
    for line in disclaimer_text:
        text_surf = disclaimer_font.render(line, True, (230, 230, 230))
        shadow_surf = disclaimer_font.render(line, True, (0, 0, 0))

        # 预转换为带透明度的surface
        text_alpha = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        text_alpha.blit(text_surf, (0, 0))

        shadow_alpha = pygame.Surface(shadow_surf.get_size(), pygame.SRCALPHA)
        shadow_alpha.blit(shadow_surf, (0, 0))

        disclaimer_text_surfaces.append(text_alpha)
        disclaimer_shadow_surfaces.append(shadow_alpha)

    background_music_playing = False # 当这玩意为False的时候就会播放菜单音乐
    # 游戏主循环
    running = True
    try:
        while running:
            # --- 事件处理 ---
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                # 状态机事件处理
                if game_state == 'main_menu':
                    background_music_playing = _play_menu_bgm(audio_available, background_music_playing)
                    action = main_menu.handle_event(event)
                    if action == "start_game":
                        game_state = 'gameplay'
                        if background_music_playing:
                            pygame.mixer.music.stop()
                            background_music_playing = False
                    elif action == "load_game":
                        game_state = 'save_menu'
                    elif action == "open_settings":
                        game_state = 'settings'
                    elif action == "exit":
                        running = False
                elif game_state == 'save_menu':
                    background_music_playing = _play_menu_bgm(audio_available, background_music_playing)
                    action = save_menu.handle_event(event)
                    if action == "back":
                        game_state = 'main_menu'
                    elif action == "load_save":
                        # 加载存档并开始游戏
                        loaded_data = save_system.load_save(save_menu.selected_slot)
                        if loaded_data:
                            print(f"加载存档 {save_menu.selected_slot}: {loaded_data['player']['name']}")
                            init_session_from_save(loaded_data)
                            game_state = 'gameplay'
                            if background_music_playing:
                                pygame.mixer.music.stop()
                                background_music_playing = False
                        else:
                            print("存档加载失败")
                elif game_state == 'settings':
                    action = setting_menu.handle_event(event)
                    if action == "toggle_touch_ui":
                        set_touch_ui_visible(not get_touch_ui_visible())
                    elif action == "back":
                        game_state = 'main_menu'
                elif game_state == 'gameplay':
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
                        game_state = 'main_menu'
                        background_music_playing = _play_menu_bgm(audio_available, background_music_playing)

            # --- 状态逻辑更新 ---
            if game_state == 'intro':
                if play_intro(screen):
                    game_state = 'disclaimer'
                    disclaimer_start_time = pygame.time.get_ticks()
            elif game_state == 'gameplay':
                gameplay_surface, return_status = gameplay(events)
                if return_status == "back":
                    game_state = 'main_menu'
                    background_music_playing = _play_menu_bgm(audio_available, background_music_playing)

            # --- 渲染 ---
            # 1. 绘制基础背景
            if game_state == 'gameplay':
                # 绘制游戏场景
                screen.blit(gameplay_surface, (0, 0))
            else:
                # 对于 intro, disclaimer, menu-before-game, 背景是纯黑
                screen.fill((0, 0, 0))

            # 2. 绘制顶层内容 (声明, 菜单)
            if game_state == 'disclaimer':
                elapsed = pygame.time.get_ticks() - disclaimer_start_time
                if elapsed >= 5000:
                    game_state = 'main_menu'
                else:
                    # 版权声明动画（优化版）
                    if elapsed < 1000:
                        progress = elapsed / 1000
                        # 缓动函数：easeOutCubic
                        progress = 1 - (1 - progress) ** 3
                        y_pos = SCREEN_HEIGHT + 80 - \
                            (SCREEN_HEIGHT + 80 - (SCREEN_HEIGHT - 160)) * progress
                        alpha = int(255 * progress)
                    elif elapsed < 4000:
                        progress = (elapsed - 1000) / 3000
                        y_pos = SCREEN_HEIGHT - 160 + 5 * \
                            math.sin(progress * 2 * math.pi)
                        alpha = 255
                    else:
                        progress = (elapsed - 4000) / 1000
                        # 缓动函数：easeInCubic
                        progress = progress ** 3
                        y_pos = (SCREEN_HEIGHT - 160) - 100 * progress
                        alpha = int(255 * (1 - progress))

                    # 批量设置透明度并绘制（性能优化）
                    y_offset = int(y_pos)
                    for i in range(len(disclaimer_text)):
                        text_surf = disclaimer_text_surfaces[i]
                        shadow_surf = disclaimer_shadow_surfaces[i]

                        text_surf.set_alpha(alpha)
                        shadow_surf.set_alpha(int(alpha * 0.6))

                        screen.blit(shadow_surf, (22, y_offset + 2))
                        screen.blit(text_surf, (20, y_offset))
                        y_offset += 32

            elif game_state == 'main_menu':
                # 菜单会自己绘制半透明背景，所以它会叠加在当前画面上
                main_menu.draw()
            elif game_state == 'save_menu':
                # 存档菜单会自己绘制半透明背景
                save_menu.draw()
            elif game_state == 'settings':
                # 设置菜单
                setting_menu.draw()

            # --- 更新屏幕 ---
            pygame.display.flip()
            clock.tick(60) # 60帧

    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
