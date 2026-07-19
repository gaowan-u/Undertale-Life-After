from typing import NoReturn
from main_menu import MainMenu
from intro_animation import play as play_intro
from gameplay import gameplay, init_assets, init_session_from_save, set_touch_ui_visible, get_touch_ui_visible
from save_system import save_system
from save_menu import SaveMenu
from setting import Setting
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT, AUDIO_FOLDER
from screen_adapter import get_render_surface, render_to_screen, recreate as recreate_adapter, update as update_adapter
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

background_music = os.path.join(AUDIO_FOLDER, "menu_music.ogg")


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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    init_assets()
    pygame.display.set_caption("传说之下-劫后余生")
    recreate_adapter(screen)
    clock = pygame.time.Clock()
    # --- 游戏状态和组件 ---
    game_state = 'intro'
    render_surface = get_render_surface()
    main_menu = MainMenu(render_surface)
    save_menu = SaveMenu(render_surface)
    setting_menu = Setting(render_surface)
    disclaimer_start_time = -1

    DISCLAIMER_DURATION = 5000
    DISCLAIMER_FADE_IN = 1000
    DISCLAIMER_DISPLAY_END = 4000
    DISCLAIMER_FADE_OUT_START = 4000
    DISCLAIMER_FADE_OUT_DURATION = 1000
    DISCLAIMER_MID_DURATION = 3000
    DISCLAIMER_Y_BASE = SCREEN_HEIGHT - 160
    DISCLAIMER_Y_FADE_IN_OFFSET = 80
    DISCLAIMER_BOUNCE_AMPLITUDE = 5
    DISCLAIMER_FADE_OUT_SLIDE = 100
    DISCLAIMER_LINE_HEIGHT = 32
    DISCLAIMER_SHADOW_OFFSET = 2

    # 用于在暂停时保留游戏画面
    gameplay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
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

                if event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    update_adapter(screen.get_size())
                    continue

                # 状态机事件处理
                if game_state == 'main_menu':
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
                    action = save_menu.handle_event(event)
                    if action == "back":
                        game_state = 'main_menu'
                    elif action == "load_save":
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
                    elif action in ("volume", "quality"):
                        pass
                elif game_state == 'gameplay':
                    pass

            # --- 状态逻辑更新 ---
            if game_state == 'intro':
                intro_result = play_intro(screen)
                if intro_result:
                    game_state = 'disclaimer'
                    disclaimer_start_time = pygame.time.get_ticks()
                else:
                    running = False
            elif game_state == 'gameplay':
                try:
                    gameplay_surface, return_status = gameplay(events)
                    if return_status == "back":
                        game_state = 'main_menu'
                        background_music_playing = False
                    elif return_status == "exit":
                        # TODO: 切换到下一场景（素材尚未就绪）
                        print("[主循环] 收到出口信号 — 场景切换待实现")
                except Exception:
                    import traceback
                    traceback.print_exc()
                    print("游戏会话异常终止，返回主菜单")
                    game_state = 'main_menu'
                    background_music_playing = False

            # 菜单背景音乐自动播放（在事件循环外，确保无事件时也能启动）
            if game_state in ('main_menu', 'save_menu') and not background_music_playing and audio_available:
                try:
                    pygame.mixer.music.load(background_music)
                    pygame.mixer.music.play(-1)
                    background_music_playing = True
                except pygame.error:
                    print(f"警告：无法加载菜单音乐：{background_music}！")

            # --- 渲染到逻辑 surface (1920×1080) ---
            # 1. 绘制基础背景
            if game_state == 'gameplay':
                render_surface.blit(gameplay_surface, (0, 0))
            else:
                render_surface.fill((0, 0, 0))

            # 2. 绘制顶层内容 (声明, 菜单)
            if game_state == 'disclaimer':
                elapsed = pygame.time.get_ticks() - disclaimer_start_time
                if elapsed >= DISCLAIMER_DURATION:
                    game_state = 'main_menu'
                else:
                    if elapsed < DISCLAIMER_FADE_IN:
                        progress = elapsed / DISCLAIMER_FADE_IN
                        progress = 1 - (1 - progress) ** 3
                        y_pos = SCREEN_HEIGHT + DISCLAIMER_Y_FADE_IN_OFFSET - \
                            (SCREEN_HEIGHT + DISCLAIMER_Y_FADE_IN_OFFSET - DISCLAIMER_Y_BASE) * progress
                        alpha = int(255 * progress)
                    elif elapsed < DISCLAIMER_DISPLAY_END:
                        progress = (elapsed - DISCLAIMER_FADE_IN) / DISCLAIMER_MID_DURATION
                        y_pos = DISCLAIMER_Y_BASE + DISCLAIMER_BOUNCE_AMPLITUDE * \
                            math.sin(progress * 2 * math.pi)
                        alpha = 255
                    else:
                        progress = (elapsed - DISCLAIMER_FADE_OUT_START) / DISCLAIMER_FADE_OUT_DURATION
                        progress = progress ** 3
                        y_pos = DISCLAIMER_Y_BASE - DISCLAIMER_FADE_OUT_SLIDE * progress
                        alpha = int(255 * (1 - progress))

                    y_offset = int(y_pos)
                    for text_surf, shadow_surf in zip(disclaimer_text_surfaces, disclaimer_shadow_surfaces):
                        text_surf.set_alpha(alpha)
                        shadow_surf.set_alpha(int(alpha * 0.6))

                        render_surface.blit(shadow_surf, (20 + DISCLAIMER_SHADOW_OFFSET, y_offset + DISCLAIMER_SHADOW_OFFSET))
                        render_surface.blit(text_surf, (20, y_offset))
                        y_offset += DISCLAIMER_LINE_HEIGHT

            elif game_state == 'main_menu':
                main_menu.draw()
            elif game_state == 'save_menu':
                save_menu.draw()
            elif game_state == 'settings':
                setting_menu.draw()

            # --- 缩放 + 黑边适配到屏幕 ---
            render_to_screen(screen)
            pygame.display.flip()
            clock.tick(60) # 60帧

    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
