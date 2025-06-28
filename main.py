# main.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
import pygame
from intro_animation import play
from intro_animation import screen


def run_game():
    print("游戏开始......")  # 游戏主循环开始，后续会在这里处理所有核心玩法和界面
    # Start the main game loop. All core gameplay and UI logic will go here.
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # 用户点击关闭窗口，安全退出
                    # User clicked the window close button, exit safely.
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False  # 按下ESC键，退出游戏
                        # Press ESC to exit the game.

            # 主游戏渲染逻辑，每帧刷新画面
            # Main game rendering logic, refresh the screen every frame
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)  # 控制帧率为60FPS / Limit to 60 FPS
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")  # 支持命令行强制退出
        # Support for Ctrl+C exit in terminal
        running = False


def main():
    pygame.init()  # 初始化Pygame库 / Initialize Pygame
    pygame.mixer.init()  # 初始化音频模块 / Initialize audio
    
    try:
        if play():
            run_game()  # 运行主游戏 / Start the main game
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")  # 支持命令行强制退出
    finally:
        pygame.quit()  # 退出Pygame，释放所有资源 / Quit Pygame and release resources

if __name__ == "__main__":
    main()  # 程序入口 / Program entry point