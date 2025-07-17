import pygame
import sys
import warnings
import math

# 忽略Pygame的社区警告
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')

# 导入其他模块
from intro_animation import play as play_intro, screen_width, screen_height
from main_menu import MainMenu

def main():
    # --- 初始化 ---
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("传说之下-劫后余生")
    clock = pygame.time.Clock()

    # --- 游戏状态和组件 ---
    game_state = 'intro'
    main_menu = MainMenu(screen)
    disclaimer_start_time = -1
    
    # 用于在暂停时保留游戏画面
    gameplay_surface = pygame.Surface((screen_width, screen_height))
    gameplay_surface.fill((20, 20, 30)) # 默认游戏背景

    # --- 版权声明内容 ---
    disclaimer_font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 24)
    disclaimer_text = [
        "本作品为粉丝创作，非官方授权产品",
        "Undertale™ 是Toby Fox的注册商标",
        "与Undertale开发团队无任何关联",
        "角色版权归原著作权方所有",
        "美术资源遵循CC BY-NC 4.0协议"
    ]

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
                    action = main_menu.handle_event(event)
                    if action == "start_game":
                        game_state = 'gameplay'
                    elif action == "open_settings":
                        print("设置功能尚未实现")
                    elif action == "exit":
                        running = False
                elif game_state == 'gameplay':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state = 'main_menu'

            # --- 状态逻辑更新 ---
            if game_state == 'intro':
                if play_intro(screen):
                    game_state = 'disclaimer'
                    disclaimer_start_time = pygame.time.get_ticks()
            
            # --- 渲染 ---
            # 1. 绘制基础背景
            if game_state == 'gameplay':
                # 绘制游戏场景
                gameplay_surface.fill((20, 20, 30)) # 深蓝色背景
                font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 36)
                text = font.render("游戏进行中... 按 ESC 暂停", True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_width/2, screen_height/2))
                gameplay_surface.blit(text, text_rect)
                screen.blit(gameplay_surface, (0,0))
            else:
                # 对于 intro, disclaimer, menu-before-game, 背景是纯黑
                screen.fill((0, 0, 0))

            # 2. 绘制顶层内容 (声明, 菜单)
            if game_state == 'disclaimer':
                elapsed = pygame.time.get_ticks() - disclaimer_start_time
                if elapsed >= 5000:
                    game_state = 'main_menu'
                else:
                    # 版权声明动画
                    if elapsed < 1000:
                        phase, progress = 'enter', elapsed / 1000
                    elif elapsed < 4000:
                        phase, progress = 'hold', (elapsed - 1000) / 3000
                    else:
                        phase, progress = 'exit', (elapsed - 4000) / 1000

                    base_y, target_y = screen_height + 80, screen_height - 160
                    
                    if phase == 'enter':
                        y_pos = base_y - (base_y - target_y) * (progress**0.7)
                        alpha = int(255 * progress)
                    elif phase == 'exit':
                        y_pos = target_y - 100 * progress
                        alpha = int(255 * (1 - progress))
                    else:
                        y_pos = target_y + 5 * math.sin(progress * 2 * math.pi)
                        alpha = 255

                    y_offset = int(y_pos)
                    for line in disclaimer_text:
                        text_surf = disclaimer_font.render(line, True, (230, 230, 230))
                        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
                        alpha_surf.blit(text_surf, (0, 0))
                        alpha_surf.set_alpha(alpha)
                        
                        shadow_surf = disclaimer_font.render(line, True, (0,0,0))
                        shadow_surf.set_alpha(alpha * 0.6)
                        screen.blit(shadow_surf, (22, y_offset + 2))
                        screen.blit(alpha_surf, (20, y_offset))
                        y_offset += 32

            elif game_state == 'main_menu':
                # 菜单会自己绘制半透明背景，所以它会叠加在当前画面上
                main_menu.draw()

            # --- 更新屏幕 ---
            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
