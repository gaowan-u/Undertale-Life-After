from typing import List
import pygame
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT
from screen_adapter import get_logical_mouse_pos, to_logical


class MainMenu:
    _ACTIONS = ("start_game", "load_game", "open_settings", "exit")

    def __init__(self, screen, items=None, title="主菜单"):
        self.screen = screen

        self.resources = Resources()

        self.title_font = self.resources.title_font
        self.item_font = self.resources.title_font_medium

        self.menu_items = items if items is not None else self.resources.main_menu_items.copy()
        self.selected_index = -1

        self.COLOR_WHITE = self.resources.COLOR_WHITE
        self.COLOR_YELLOW = self.resources.COLOR_YELLOW
        self.COLOR_RED = self.resources.COLOR_RED

        self.overlay = self.resources.overlay

        self.heart_selector = self.resources.create_heart_surface(30, self.COLOR_RED)

        self._build_items(title)

    def _build_items(self, title: str) -> None:
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

        self._title_surface = self.title_font.render(title, True, self.COLOR_WHITE)
        self._title_rect = self._title_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))

    def _index_at(self, pos: tuple[float, float]) -> int:
        """逻辑坐标命中的菜单项索引，未命中返回 -1。"""
        for index, rect in enumerate(self.menu_rects):
            if rect.collidepoint(pos):
                return index
        return -1

    def _activate(self, index: int) -> str | None:
        """菜单项被点击/确认时返回的动作，子类可覆写。"""
        if 0 <= index < len(self._ACTIONS):
            return self._ACTIONS[index]
        return None

    def _navigate_keyboard(self, event) -> str | None:
        n = len(self.menu_items)
        if event.key in (pygame.K_UP, pygame.K_w):
            if self.selected_index == -1:
                self.selected_index = n - 1
            else:
                self.selected_index = (self.selected_index - 1) % n
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if self.selected_index == -1:
                self.selected_index = 0
            else:
                self.selected_index = (self.selected_index + 1) % n
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            return self._activate(self.selected_index)
        return None

    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            return self._navigate_keyboard(event)

        if event.type == pygame.MOUSEMOTION:
            self.selected_index = self._index_at(get_logical_mouse_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 以点击坐标为准，不依赖 hover 状态（快速移动/触屏 tap 时 hover 可能过期）
            index = self._index_at(to_logical(event.pos))
            if index != -1:
                self.selected_index = index
                return self._activate(index)

        return None

    def draw(self):
        self.screen.blit(self.overlay, (0, 0))
        self.screen.blit(self._title_surface, self._title_rect)

        for index in range(len(self.menu_items)):
            if index == self.selected_index:
                self.screen.blit(self._item_selected_surfaces[index], self.menu_rects[index])
                breathing_offset = Resources.breathing_offset()
                heart_x = self.menu_rects[index].left - 60 + breathing_offset
                heart_y = self.menu_rects[index].centery - self.heart_selector.get_height() / 2
                self.screen.blit(self.heart_selector, (heart_x, heart_y))
            else:
                self.screen.blit(self._item_surfaces[index], self.menu_rects[index])
