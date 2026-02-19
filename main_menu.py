import pygame
import sys
import os
import math
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT

# 确保能从根目录导入，以便main.py调用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        
        # 使用 Resources 单例
        self.resources = Resources()
        
        # 从单例获取字体
        self.title_font = self.resources.title_font
        self.item_font = self.resources.item_font
        
        # 从单例获取菜单项
        self.menu_items = self.resources.main_menu_items.copy()
        self.selected_index = -1  # -1 表示没有选中任何项
        
        # 从单例获取颜色
        self.COLOR_WHITE = self.resources.COLOR_WHITE
        self.COLOR_YELLOW = self.resources.COLOR_YELLOW
        self.COLOR_RED = self.resources.COLOR_RED
        
        # 从单例获取遮罩层
        self.overlay = self.resources.overlay
        
        # 创建灵魂之心选择器
        self.heart_selector = self.resources.create_heart_surface(30, self.COLOR_RED)
        
        # 预先计算所有菜单项的矩形区域，用于后续的碰撞检测
        self.menu_rects = []
        for index, item in enumerate(self.menu_items):
            item_text = self.item_font.render(item, True, self.COLOR_WHITE)
            item_rect = item_text.get_rect(
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + index * 80))
            self.menu_rects.append(item_rect)

    def handle_event(self, event) -> str | None:
        # 响应鼠标移动事件，更新选中项
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.selected_index = -1
            for index, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = index
                    break
        
        # 响应鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.selected_index != -1:
                if self.selected_index == 0:
                    return "start_game"
                elif self.selected_index == 1:
                    return "load_game"
                elif self.selected_index == 2:
                    return "open_settings"
                elif self.selected_index == 3:
                    return "exit"
        
        # 响应ESC键，用于关闭菜单返回游戏
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
        
        return None  # 没有发生任何动作

    def draw(self, title="主菜单"):
        """绘制菜单。主循环需要先绘制好游戏背景，再调用此方法"""
        # 绘制半透明遮罩
        self.screen.blit(self.overlay, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render(title, True, self.COLOR_WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        self.screen.blit(title_text, title_rect)
        
        # 绘制菜单项
        for index, item in enumerate(self.menu_items):
            color = self.COLOR_YELLOW if index == self.selected_index else self.COLOR_WHITE
            item_text = self.item_font.render(item, True, color)
            self.screen.blit(item_text, self.menu_rects[index])
            
            # 如果当前项被选中，绘制灵魂之心
            if index == self.selected_index:
                breathing_offset = math.sin(
                    pygame.time.get_ticks() * 0.005) * 5
                heart_x = self.menu_rects[index].left - 60 + breathing_offset
                heart_y = self.menu_rects[index].centery - \
                    self.heart_selector.get_height() / 2
                self.screen.blit(self.heart_selector, (heart_x, heart_y))