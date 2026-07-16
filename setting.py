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

        self._show_confirm = False
        self._confirm_selected: str | None = None
        self._build_confirm_dialog(res)

    def _build_confirm_dialog(self, res: Resources) -> None:
        font = res.font_24
        color_white = res.COLOR_WHITE
        color_yellow = res.COLOR_YELLOW

        self._confirm_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._confirm_overlay.fill((0, 0, 0, 180))

        dialog_w, dialog_h = 560, 240
        dialog_x = (SCREEN_WIDTH - dialog_w) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_h) // 2
        self._confirm_dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        self._confirm_dialog_bg = pygame.Surface((dialog_w, dialog_h), pygame.SRCALPHA)
        pygame.draw.rect(self._confirm_dialog_bg, (30, 30, 30), (0, 0, dialog_w, dialog_h), border_radius=12)
        pygame.draw.rect(self._confirm_dialog_bg, (100, 100, 100), (0, 0, dialog_w, dialog_h), 2, border_radius=12)

        self._confirm_title = font.render("提示", True, color_yellow)

        msg_lines = ["关闭触控UI后，屏幕按钮将消失，", "只能使用键盘操作。确定要继续吗？"]
        self._confirm_msg_lines = [font.render(line, True, color_white) for line in msg_lines]

        btn_w, btn_h = 140, 45
        gap = 60
        total_btn_w = btn_w * 2 + gap
        btn_start_x = dialog_x + (dialog_w - total_btn_w) // 2
        btn_y = dialog_y + dialog_h - btn_h - 30

        self._confirm_yes_rect = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
        self._confirm_no_rect = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)

        self._btn_yes_normal = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._btn_yes_normal, (50, 50, 50), (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(self._btn_yes_normal, (100, 100, 100), (0, 0, btn_w, btn_h), 2, border_radius=8)
        yes_text = font.render("确定", True, color_white)
        self._btn_yes_normal.blit(yes_text, ((btn_w - yes_text.get_width()) // 2, (btn_h - yes_text.get_height()) // 2))

        self._btn_yes_hover = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._btn_yes_hover, (70, 70, 70), (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(self._btn_yes_hover, color_yellow, (0, 0, btn_w, btn_h), 2, border_radius=8)
        self._btn_yes_hover.blit(yes_text, ((btn_w - yes_text.get_width()) // 2, (btn_h - yes_text.get_height()) // 2))

        self._btn_no_normal = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._btn_no_normal, (50, 50, 50), (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(self._btn_no_normal, (100, 100, 100), (0, 0, btn_w, btn_h), 2, border_radius=8)
        no_text = font.render("取消", True, color_white)
        self._btn_no_normal.blit(no_text, ((btn_w - no_text.get_width()) // 2, (btn_h - no_text.get_height()) // 2))

        self._btn_no_hover = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._btn_no_hover, (70, 70, 70), (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(self._btn_no_hover, color_yellow, (0, 0, btn_w, btn_h), 2, border_radius=8)
        self._btn_no_hover.blit(no_text, ((btn_w - no_text.get_width()) // 2, (btn_h - no_text.get_height()) // 2))

    def handle_event(self, event):
        if self._show_confirm:
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = get_logical_mouse_pos()
                if self._confirm_yes_rect.collidepoint(mouse_pos):
                    self._confirm_selected = "yes"
                elif self._confirm_no_rect.collidepoint(mouse_pos):
                    self._confirm_selected = "no"
                else:
                    self._confirm_selected = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._confirm_selected == "yes":
                    self._show_confirm = False
                    self._confirm_selected = None
                    return "toggle_touch_ui"
                elif self._confirm_selected == "no":
                    self._show_confirm = False
                    self._confirm_selected = None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._show_confirm = False
                self._confirm_selected = None
            return None

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = get_logical_mouse_pos()
            self.selected_index = -1
            for index, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = index
                    break

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.selected_index != -1:
                if self.selected_index == 0:
                    return "volume"
                elif self.selected_index == 1:
                    return "quality"
                elif self.selected_index == 2:
                    if get_touch_ui_visible():
                        self._show_confirm = True
                        return None
                    else:
                        return "toggle_touch_ui"
                elif self.selected_index == 3:
                    return "back"

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
                breathing_offset = Resources.breathing_offset()
                heart_x = self.menu_rects[index].left - 60 + breathing_offset
                heart_y = self.menu_rects[index].centery - self.heart_selector.get_height() / 2
                self.screen.blit(self.heart_selector, (heart_x, heart_y))

        if self._show_confirm:
            self.screen.blit(self._confirm_overlay, (0, 0))
            self.screen.blit(self._confirm_dialog_bg, self._confirm_dialog_rect.topleft)
            title_x = self._confirm_dialog_rect.centerx - self._confirm_title.get_width() // 2
            title_y = self._confirm_dialog_rect.top + 25
            self.screen.blit(self._confirm_title, (title_x, title_y))
            for i, line_surf in enumerate(self._confirm_msg_lines):
                line_x = self._confirm_dialog_rect.centerx - line_surf.get_width() // 2
                line_y = title_y + 40 + i * 30
                self.screen.blit(line_surf, (line_x, line_y))

            mouse_pos = get_logical_mouse_pos()
            yes_hover = self._confirm_yes_rect.collidepoint(mouse_pos)
            no_hover = self._confirm_no_rect.collidepoint(mouse_pos)
            self.screen.blit(self._btn_yes_hover if yes_hover else self._btn_yes_normal, self._confirm_yes_rect)
            self.screen.blit(self._btn_no_hover if no_hover else self._btn_no_normal, self._confirm_no_rect)
