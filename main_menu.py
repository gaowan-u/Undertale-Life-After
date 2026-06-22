import pygame
import math
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        
        self.resources = Resources()
        
        self.title_font = self.resources.title_font
        self.item_font = self.resources.item_font
        
        self.menu_items = self.resources.main_menu_items.copy()
        self.selected_index = -1
        
        self.COLOR_WHITE = self.resources.COLOR_WHITE
        self.COLOR_YELLOW = self.resources.COLOR_YELLOW
        self.COLOR_RED = self.resources.COLOR_RED
        
        self.overlay = self.resources.overlay
        
        self.heart_selector = self.resources.create_heart_surface(30, self.COLOR_RED)
        
        # 预渲染所有菜单项文字（避免每帧 font.render）
        self.menu_rects = []
        self._item_surfaces: List[pygame.Surface] = []
        self._item_selected_surfaces: List[pygame.Surface] = []
        for index, item in enumerate(self.menu_items):
            surf = self.item_font.render(item, True, self.COLOR_WHITE)
            sel_surf = self.item_font.render(item, True, self.COLOR_YELLOW)
            rect = surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + index * 80))
            self._item_surfaces.append(surf)
            self._item_selected_surfaces.append(sel_surf)
            self.menu_rects.append(rect)

        # 预渲染标题
        self._title_surface = self.title_font.render("主菜单", True, self.COLOR_WHITE)
        self._title_rect = self._title_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.selected_index = -1
            for index, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = index
                    break
        
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
        
        return None

    def draw(self, title="主菜单"):
        self.screen.blit(self.overlay, (0, 0))
        self.screen.blit(self._title_surface, self._title_rect)
        
        for index in range(len(self.menu_items)):
            if index == self.selected_index:
                self.screen.blit(self._item_selected_surfaces[index], self.menu_rects[index])
                breathing_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5
                heart_x = self.menu_rects[index].left - 60 + breathing_offset
                heart_y = self.menu_rects[index].centery - self.heart_selector.get_height() / 2
                self.screen.blit(self.heart_selector, (heart_x, heart_y))
            else:
                self.screen.blit(self._item_surfaces[index], self.menu_rects[index])