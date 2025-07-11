# main.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
import pygame
from intro_animation import play, screen_width, screen_height  # 只导入必要内容

def run_game(screen):  # 添加screen参数
    print("游戏开始......")  # Game started
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            # 事件处理 / Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 主渲染 / Main rendering
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)  # 60FPS
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")  # Ctrl+C detected


def main():
    pygame.init()  # 初始化 / Initialize
    pygame.mixer.init()
    
    # 在main.py中创建screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("传说之下-劫后余生")
    
    try:
        if play(screen):  # 将screen传入动画函数
            run_game(screen)  # 将screen传入主游戏循环
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")  # Ctrl+C detected
    finally:
        pygame.quit()  # 退出 / Quit

if __name__ == "__main__":
    main()  # 程序入口 / Entry point