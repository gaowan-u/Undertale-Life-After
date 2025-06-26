# main.py
import pygame
from intro_animation import play
from intro_animation import screen

def run_game():
    print("游戏开始......")
    # 添加主游戏循环
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 主游戏渲染逻辑
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
        running = False

def main():
    pygame.init()
    pygame.mixer.init()
    
    try:
        if play():
            run_game()  # 运行主游戏
    except KeyboardInterrupt:
        print("\n检测到Ctrl+C中断，退出游戏...")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()