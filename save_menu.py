import pygame
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT
from save_system import save_system, NameInputSystem
from screen_adapter import get_logical_mouse_pos, to_logical


class SaveMenu:
    def __init__(self, screen):
        self.screen = screen

        self.resources = Resources()

        self.font = self.resources.font_32
        self.title_font = self.resources.title_font_medium
        self.small_font = self.resources.font_24

        self.COLOR_WHITE = self.resources.COLOR_WHITE
        self.COLOR_GRAY = self.resources.COLOR_GRAY
        self.COLOR_BLUE = self.resources.COLOR_BLUE
        self.COLOR_GREEN = self.resources.COLOR_GREEN
        self.COLOR_RED = self.resources.COLOR_RED

        self._title_text = self.title_font.render("选择存档", True, self.COLOR_WHITE)
        self._title_shadow = self.title_font.render("选择存档", True, (0, 0, 0))
        self._back_text = self.font.render("返回", True, self.COLOR_WHITE)
        self._empty_slot_text = self.font.render("空存档位", True, (150, 150, 150))
        self._new_game_text = self.small_font.render("点击创建新游戏", True, (120, 120, 120))
        self._delete_text = self.small_font.render("删除", True, self.COLOR_WHITE)

        self._underline_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,
            70 + self._title_text.get_height() + 5,
            200, 3
        )

        self.save_slots = []
        slot_width, slot_height = 600, 120
        for i in range(3):
            slot_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - slot_width // 2,
                200 + i * (slot_height + 20),
                slot_width,
                slot_height
            )
            self.save_slots.append(slot_rect)
        self._delete_rects = [
            pygame.Rect(slot_rect.right - 90, slot_rect.y + 40, 70, 35)
            for slot_rect in self.save_slots
        ]

        self.back_rect = pygame.Rect(50, 50, 120, 50)

        self.selected_slot = None
        self._hovered_slot = -1
        self.name_input_system = None
        self.showing_name_input = False
        self._cached_saves = None
        self._slot_render_cache: dict[int, dict] = {}

        self._show_delete_confirm = False
        self._delete_confirm_slot = -1
        self._delete_confirm_selected = "no"
        self._init_delete_confirm_dialog()

    def _init_delete_confirm_dialog(self) -> None:
        res = self.resources
        font = res.font_24
        dialog_w, dialog_h = 480, 200
        dialog_x = (SCREEN_WIDTH - dialog_w) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_h) // 2
        self._dc_dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        self._dc_dialog_bg = pygame.Surface((dialog_w, dialog_h), pygame.SRCALPHA)
        pygame.draw.rect(self._dc_dialog_bg, (30, 30, 30), (0, 0, dialog_w, dialog_h), border_radius=12)
        pygame.draw.rect(self._dc_dialog_bg, (100, 100, 100), (0, 0, dialog_w, dialog_h), 2, border_radius=12)

        self._dc_title = font.render("确认删除", True, res.COLOR_YELLOW)
        self._dc_msg = font.render("确定要删除此存档吗？此操作不可撤销。", True, res.COLOR_WHITE)

        btn_w, btn_h = 120, 40
        gap = 40
        total_w = btn_w * 2 + gap
        btn_start_x = dialog_x + (dialog_w - total_w) // 2
        btn_y = dialog_y + dialog_h - btn_h - 25
        self._dc_yes_rect = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
        self._dc_no_rect = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)

        self._dc_yes_normal = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._dc_yes_normal, (60, 20, 20), (0, 0, btn_w, btn_h), border_radius=8)
        yes_text = font.render("确定删除", True, res.COLOR_WHITE)
        self._dc_yes_normal.blit(yes_text, ((btn_w - yes_text.get_width()) // 2, (btn_h - yes_text.get_height()) // 2))

        self._dc_yes_hover = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._dc_yes_hover, (200, 40, 40), (0, 0, btn_w, btn_h), border_radius=8)
        self._dc_yes_hover.blit(yes_text, ((btn_w - yes_text.get_width()) // 2, (btn_h - yes_text.get_height()) // 2))

        self._dc_no_normal = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._dc_no_normal, (50, 50, 50), (0, 0, btn_w, btn_h), border_radius=8)
        no_text = font.render("取消", True, res.COLOR_WHITE)
        self._dc_no_normal.blit(no_text, ((btn_w - no_text.get_width()) // 2, (btn_h - no_text.get_height()) // 2))

        self._dc_no_hover = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(self._dc_no_hover, (70, 70, 70), (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(self._dc_no_hover, (100, 100, 100), (0, 0, btn_w, btn_h), 2, border_radius=8)
        self._dc_no_hover.blit(no_text, ((btn_w - no_text.get_width()) // 2, (btn_h - no_text.get_height()) // 2))

    def refresh_saves(self):
        self._cached_saves = save_system.list_saves()
        self._slot_render_cache.clear()

    def _get_saves(self):
        if self._cached_saves is None:
            self.refresh_saves()
        return self._cached_saves

    def draw(self):
        self.screen.blit(self.resources.gradient_overlay, (0, 0))

        title_pos = (SCREEN_WIDTH // 2 - self._title_text.get_width() // 2, 70)
        self.screen.blit(self._title_shadow, (title_pos[0] + 2, title_pos[1] + 2))
        self.screen.blit(self._title_text, title_pos)

        pygame.draw.rect(self.screen, self.COLOR_BLUE, self._underline_rect)

        mouse_pos = get_logical_mouse_pos()
        is_back_hover = self.back_rect.collidepoint(mouse_pos)

        back_color = (70, 70, 70) if is_back_hover else (50, 50, 50)
        pygame.draw.rect(self.screen, back_color, self.back_rect, border_radius=8)
        if is_back_hover:
            pygame.draw.rect(self.screen, self.COLOR_BLUE, self.back_rect, 2, border_radius=8)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), self.back_rect, 2, border_radius=8)

        back_pos = (self.back_rect.centerx - self._back_text.get_width() // 2,
                    self.back_rect.centery - self._back_text.get_height() // 2)
        self.screen.blit(self._back_text, back_pos)

        saves = self._get_saves()

        for i, slot_rect in enumerate(self.save_slots):
            save_info = saves[i]
            is_hover = slot_rect.collidepoint(mouse_pos)
            is_selected = (self._hovered_slot == i)

            if is_selected:
                bg_color = self.resources.COLOR_BG_HOVER
                border_color = self.COLOR_GREEN
                border_width = 3
            elif is_hover:
                bg_color = self.resources.COLOR_BG_HOVER
                border_color = self.COLOR_BLUE
                border_width = 3
            else:
                bg_color = self.resources.COLOR_BG_DARK
                border_color = self.resources.COLOR_BORDER
                border_width = 2

            pygame.draw.rect(self.screen, bg_color, slot_rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, slot_rect, border_width, border_radius=12)

            if save_info.get("is_empty"):
                self.screen.blit(self._empty_slot_text, (slot_rect.x + 25, slot_rect.y + 20))

                plus_color = self.COLOR_GREEN if (is_hover or is_selected) else (100, 100, 100)
                plus_size = 30
                plus_cx = slot_rect.x + 500
                plus_cy = slot_rect.centery
                pygame.draw.line(self.screen, plus_color,
                                 (plus_cx - plus_size // 2, plus_cy),
                                 (plus_cx + plus_size // 2, plus_cy), 4)
                pygame.draw.line(self.screen, plus_color,
                                 (plus_cx, plus_cy - plus_size // 2),
                                 (plus_cx, plus_cy + plus_size // 2), 4)

                self.screen.blit(self._new_game_text, (slot_rect.x + 25, slot_rect.y + 60))
            else:
                if i not in self._slot_render_cache:
                    cache = {}
                    cache['name'] = self.font.render(f"玩家: {save_info['player_name']}", True, self.COLOR_WHITE)
                    cache['chapter'] = self.small_font.render(f"章节: {save_info['chapter']}", True, (180, 180, 180))
                    cache['level'] = self.small_font.render(f"等级: {save_info['level']}", True, (180, 180, 180))
                    if save_info.get('last_played'):
                        cache['time'] = self.small_font.render(f"时间: {save_info['last_played']}", True, (150, 150, 150))
                    self._slot_render_cache[i] = cache
                cache = self._slot_render_cache[i]

                self.screen.blit(cache['name'], (slot_rect.x + 25, slot_rect.y + 5))

                pygame.draw.rect(self.screen, (60, 60, 70),
                                 (slot_rect.x + 25, slot_rect.y + 45, slot_rect.width - 50, 1))

                self.screen.blit(cache['chapter'], (slot_rect.x + 25, slot_rect.y + 58))
                self.screen.blit(cache['level'], (slot_rect.x + 200, slot_rect.y + 58))

                if save_info['last_played'] and 'time' in cache:
                    self.screen.blit(cache['time'], (slot_rect.x + 25, slot_rect.y + 88))

                delete_rect = self._delete_rects[i]
                is_delete_hover = delete_rect.collidepoint(mouse_pos)
                delete_color = (220, 50, 50) if is_delete_hover else (180, 40, 40)

                pygame.draw.rect(self.screen, delete_color, delete_rect, border_radius=6)
                delete_pos = (delete_rect.centerx - self._delete_text.get_width() // 2,
                              delete_rect.centery - self._delete_text.get_height() // 2)
                self.screen.blit(self._delete_text, delete_pos)

        if self._show_delete_confirm:
            self._draw_delete_confirm(mouse_pos)

        if self.showing_name_input and self.name_input_system:
            self.name_input_system.draw()

    def _draw_delete_confirm(self, mouse_pos) -> None:
        self.screen.blit(self._dc_dialog_bg, self._dc_dialog_rect.topleft)

        tx = self._dc_dialog_rect.centerx - self._dc_title.get_width() // 2
        ty = self._dc_dialog_rect.top + 25
        self.screen.blit(self._dc_title, (tx, ty))

        mx = self._dc_dialog_rect.centerx - self._dc_msg.get_width() // 2
        my = ty + 40
        self.screen.blit(self._dc_msg, (mx, my))

        yes_hover = self._dc_yes_rect.collidepoint(mouse_pos) or self._delete_confirm_selected == "yes"
        no_hover = self._dc_no_rect.collidepoint(mouse_pos) or self._delete_confirm_selected == "no"
        self.screen.blit(self._dc_yes_hover if yes_hover else self._dc_yes_normal, self._dc_yes_rect)
        self.screen.blit(self._dc_no_hover if no_hover else self._dc_no_normal, self._dc_no_rect)

    def handle_event(self, event):
        if self._show_delete_confirm:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._show_delete_confirm = False
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                    self._delete_confirm_selected = "no" if self._delete_confirm_selected == "yes" else "yes"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self._delete_confirm_selected == "yes":
                        self._show_delete_confirm = False
                        if save_system.delete_save(self._delete_confirm_slot):
                            self.refresh_saves()
                            self._hovered_slot = -1
                            return "save_deleted"
                    else:
                        self._show_delete_confirm = False
                return None
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = get_logical_mouse_pos()
                if self._dc_yes_rect.collidepoint(mouse_pos):
                    self._delete_confirm_selected = "yes"
                elif self._dc_no_rect.collidepoint(mouse_pos):
                    self._delete_confirm_selected = "no"
                else:
                    self._delete_confirm_selected = "no"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._delete_confirm_selected == "yes":
                    self._show_delete_confirm = False
                    if save_system.delete_save(self._delete_confirm_slot):
                        self.refresh_saves()
                        self._hovered_slot = -1
                        return "save_deleted"
                elif self._delete_confirm_selected == "no":
                    self._show_delete_confirm = False
            return None

        if self.showing_name_input and self.name_input_system:
            result = self.name_input_system.handle_event(event)
            if result and result != "cancel":
                if save_system.create_new_save(self.selected_slot, result):
                    self.showing_name_input = False
                    self.name_input_system = None
                    self.refresh_saves()
                    self._hovered_slot = -1
                    return "load_save"
                else:
                    self.showing_name_input = False
                    self.name_input_system = None
                    return "save_error"
            elif result == "cancel" or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.showing_name_input = False
                self.name_input_system = None
                return None
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return None
                return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            saves = self._get_saves()
            n = len(self.save_slots)
            if event.key in (pygame.K_UP, pygame.K_w):
                if self._hovered_slot == -1:
                    self._hovered_slot = n - 1
                else:
                    self._hovered_slot = (self._hovered_slot - 1) % n
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self._hovered_slot == -1:
                    self._hovered_slot = 0
                else:
                    self._hovered_slot = (self._hovered_slot + 1) % n
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self._hovered_slot != -1:
                    save_info = saves[self._hovered_slot]
                    if save_info.get("is_empty"):
                        self.selected_slot = self._hovered_slot + 1
                        self.name_input_system = NameInputSystem(self.screen)
                        self.showing_name_input = True
                    else:
                        self.selected_slot = self._hovered_slot + 1
                        return "load_save"
            elif event.key == pygame.K_DELETE:
                if self._hovered_slot != -1 and not saves[self._hovered_slot].get("is_empty"):
                    self._delete_confirm_slot = self._hovered_slot + 1
                    self._delete_confirm_selected = "no"
                    self._show_delete_confirm = True
            return None

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = get_logical_mouse_pos()
            self._hovered_slot = -1
            for i, slot_rect in enumerate(self.save_slots):
                if slot_rect.collidepoint(mouse_pos):
                    self._hovered_slot = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN:
            logical_pos = to_logical(event.pos)
            if self.back_rect.collidepoint(logical_pos):
                return "back"

            saves = self._get_saves()
            for i, slot_rect in enumerate(self.save_slots):
                save_info = saves[i]

                if not save_info.get("is_empty"):
                    delete_rect = self._delete_rects[i]
                    if delete_rect.collidepoint(logical_pos):
                        self._delete_confirm_slot = i + 1
                        self._delete_confirm_selected = "no"
                        self._show_delete_confirm = True
                        return None

                if slot_rect.collidepoint(logical_pos):
                    if save_info.get("is_empty"):
                        self.selected_slot = i + 1
                        self.name_input_system = NameInputSystem(self.screen)
                        self.showing_name_input = True
                        return None
                    else:
                        self.selected_slot = i + 1
                        return "load_save"

        return None
