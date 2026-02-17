import math
import pygame
from main_menu import MainMenu
from resources import SCREEN_WIDTH, SCREEN_HEIGHT


class Setting(MainMenu):
    def __init__(self, screen):
        super().__init__(screen)
        # 覆盖菜单项为设置菜单项
        self.menu_items = self.resources.setting_menu_items.copy()
        
        # 重新计算菜单项位置
        self.menu_rects = []
        for index, item in enumerate(self.menu_items):
            item_text = self.item_font.render(item, True, self.COLOR_WHITE)
            item_rect = item_text.get_rect(
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + index * 80))
            self.menu_rects.append(item_rect)
    
    def handle_event(self, event):
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
                    return "volume"      # 音量设置
                elif self.selected_index == 1:
                    return "quality"     # 画质设置
                elif self.selected_index == 2:
                    return "control"     # 控制设置
                elif self.selected_index == 3:
                    return "back"        # 返回
        
        # 响应ESC键，返回主菜单
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
        
        return None

    def draw(self, title="设置"):
        """绘制设置菜单"""
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