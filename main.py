# main.py
import pygame
from intro_animation import *

def run_game():
    print("游戏开始......")
    # 添加主游戏循环
    clock = pygame.time.Clock()
    running = True
    
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

def main():
    pygame.init()
    pygame.mixer.init()
    
    if play():
        run_game()  # 运行主游戏
    
    pygame.quit()

if __name__ == "__main__":
    main()