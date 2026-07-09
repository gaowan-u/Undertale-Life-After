import math
import pygame
from main_menu import MainMenu
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT
from gameplay import get_touch_ui_visible
from screen_adapter import get_logical_mouse_pos


class Setting(MainMenu):
    def __init__(self, screen):
        res = Resources()
        super().__init__(screen, res.setting_menu_items.copy(), "设置")

        self._last_touch_ui_state: bool | None = None
        self._touch_item_surf: pygame.Surface | None = None
        self._touch_item_sel_surf: pygame.Surface | None = None

    def handle_event(self, event):
        # 响应鼠标移动事件，更新选中项
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = get_logical_mouse_pos()
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
                    return "toggle_touch_ui"  # 切换触控UI可见性
                elif self.selected_index == 3:
                    return "back"        # 返回

        # 响应ESC键，返回主菜单
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        return None

    def draw(self):
        self.screen.blit(self.overlay, (0, 0))
        self.screen.blit(self._title_surface, self._title_rect)

        current_touch_ui = get_touch_ui_visible()
        if current_touch_ui != self._last_touch_ui_state:
            self._last_touch_ui_state = current_touch_ui
            state_text = "开" if current_touch_ui else "关"
            display_text = f"{self.menu_items[2]}: {state_text}"
            self._touch_item_surf = self.item_font.render(display_text, True, self.COLOR_WHITE)
            self._touch_item_sel_surf = self.item_font.render(display_text, True, self.COLOR_YELLOW)
            self.menu_rects[2] = self._touch_item_surf.get_rect(
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 2 * 80))

        for index in range(len(self.menu_items)):
            if index == 2:
                surf = self._touch_item_sel_surf if index == self.selected_index else self._touch_item_surf
            else:
                surf = self._item_selected_surfaces[index] if index == self.selected_index else self._item_surfaces[index]
            self.screen.blit(surf, self.menu_rects[index])

            if index == self.selected_index:
                breathing_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5
                heart_x = self.menu_rects[index].left - 60 + breathing_offset
                heart_y = self.menu_rects[index].centery - self.heart_selector.get_height() / 2
                self.screen.blit(self.heart_selector, (heart_x, heart_y))
