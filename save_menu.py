import pygame
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT
from save_system import save_system, NameInputSystem


class SaveMenu:
    def __init__(self, screen):
        self.screen = screen
        
        # 使用 Resources 单例
        self.resources = Resources()
        
        # 从单例获取字体
        self.font = self.resources.font_32
        self.title_font = self.resources.title_font_medium
        self.small_font = self.resources.font_24
        
        # 从单例获取颜色
        self.COLOR_WHITE = self.resources.COLOR_WHITE
        self.COLOR_BLACK = self.resources.COLOR_BLACK
        self.COLOR_GRAY = self.resources.COLOR_GRAY
        self.COLOR_BLUE = self.resources.COLOR_BLUE
        self.COLOR_GREEN = self.resources.COLOR_GREEN
        self.COLOR_RED = self.resources.COLOR_RED
        
        # 存档槽位置
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
        
        # 按钮
        self.back_rect = pygame.Rect(50, 50, 120, 50)
        
        # 状态
        self.selected_slot = None
        self.name_input_system = None
        self.showing_name_input = False

    def draw_rounded_rect(self, surface, color, rect, radius=10, width=0):
        """绘制圆角矩形"""
        pygame.draw.rect(surface, color, rect, width, border_radius=radius)

    def draw(self):
        """绘制存档菜单"""
        # 使用单例中的渐变遮罩
        self.screen.blit(self.resources.gradient_overlay, (0, 0))
        
        # 标题 - 添加发光效果
        title_text = self.title_font.render("选择存档", True, self.COLOR_WHITE)
        title_pos = (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 70)
        
        # 标题阴影
        title_shadow = self.title_font.render("选择存档", True, (0, 0, 0, 100))
        self.screen.blit(title_shadow, (title_pos[0] + 2, title_pos[1] + 2))
        self.screen.blit(title_text, title_pos)
        
        # 标题下划线
        underline_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,
            title_pos[1] + title_text.get_height() + 5,
            200,
            3
        )
        pygame.draw.rect(self.screen, self.COLOR_BLUE, underline_rect)
        
        # 返回按钮 - 圆角和渐变
        mouse_pos = pygame.mouse.get_pos()
        is_back_hover = self.back_rect.collidepoint(mouse_pos)
        
        if is_back_hover:
            back_color = (70, 70, 70)
        else:
            back_color = (50, 50, 50)
        
        self.draw_rounded_rect(self.screen, back_color, self.back_rect, 8)
        if is_back_hover:
            self.draw_rounded_rect(self.screen, self.COLOR_BLUE, self.back_rect, 8, 2)
        else:
            self.draw_rounded_rect(self.screen, (100, 100, 100), self.back_rect, 8, 2)
        
        back_text = self.font.render("返回", True, self.COLOR_WHITE)
        back_pos = (self.back_rect.centerx - back_text.get_width() // 2,
                    self.back_rect.centery - back_text.get_height() // 2)
        self.screen.blit(back_text, back_pos)
        
        # 获取存档列表
        saves = save_system.list_saves()
        
        # 绘制存档槽
        for i, slot_rect in enumerate(self.save_slots):
            save_info = saves[i]
            
            # 槽背景 - 悬停效果
            is_hover = slot_rect.collidepoint(mouse_pos)
            
            if is_hover:
                bg_color = self.resources.COLOR_BG_HOVER
                border_color = self.COLOR_BLUE
                border_width = 3
            else:
                bg_color = self.resources.COLOR_BG_DARK
                border_color = self.resources.COLOR_BORDER
                border_width = 2
            
            # 绘制圆角矩形背景
            self.draw_rounded_rect(self.screen, bg_color, slot_rect, 12)
            self.draw_rounded_rect(self.screen, border_color, slot_rect, 12, border_width)
            
            # 存档信息
            if save_info.get("is_empty"):
                # 空存档位 - 添加图标提示
                empty_text = self.font.render("空存档位", True, (150, 150, 150))
                empty_pos = (slot_rect.x + 25, slot_rect.y + 20)
                self.screen.blit(empty_text, empty_pos)
                
                # 添加加号图标
                plus_color = self.COLOR_GREEN if is_hover else (100, 100, 100)
                plus_size = 30
                plus_center_x = slot_rect.x + 500
                plus_center_y = slot_rect.centery
                pygame.draw.line(self.screen, plus_color,
                                 (plus_center_x - plus_size // 2, plus_center_y),
                                 (plus_center_x + plus_size // 2, plus_center_y), 4)
                pygame.draw.line(self.screen, plus_color,
                                 (plus_center_x, plus_center_y - plus_size // 2),
                                 (plus_center_x, plus_center_y + plus_size // 2), 4)
                
                new_game_text = self.small_font.render("点击创建新游戏", True, (120, 120, 120))
                new_game_pos = (slot_rect.x + 25, slot_rect.y + 60)
                self.screen.blit(new_game_text, new_game_pos)
            else:
                # 有存档 - 更精美的信息展示
                # 玩家名称 - 使用更大字体和颜色
                name_text = self.font.render(f"玩家: {save_info['player_name']}", True, self.COLOR_WHITE)
                name_pos = (slot_rect.x + 25, slot_rect.y + 5)
                self.screen.blit(name_text, name_pos)
                
                # 分隔线
                separator_rect = pygame.Rect(slot_rect.x + 25, slot_rect.y + 45, slot_rect.width - 50, 1)
                pygame.draw.rect(self.screen, (60, 60, 70), separator_rect)
                
                # 章节信息
                chapter_text = self.small_font.render(f"章节: {save_info['chapter']}", True, (180, 180, 180))
                chapter_pos = (slot_rect.x + 25, slot_rect.y + 58)
                self.screen.blit(chapter_text, chapter_pos)
                
                # 等级
                level_text = self.small_font.render(f"等级: {save_info['level']}", True, (180, 180, 180))
                level_pos = (slot_rect.x + 200, slot_rect.y + 58)
                self.screen.blit(level_text, level_pos)
                
                # 最后游玩时间
                if save_info['last_played']:
                    time_text = self.small_font.render(f"时间: {save_info['last_played']}", True, (150, 150, 150))
                    time_pos = (slot_rect.x + 25, slot_rect.y + 88)
                    self.screen.blit(time_text, time_pos)
                
                # 删除按钮 - 圆角和更好的样式
                delete_rect = pygame.Rect(slot_rect.right - 90, slot_rect.y + 40, 70, 35)
                is_delete_hover = delete_rect.collidepoint(mouse_pos)
                
                if is_delete_hover:
                    delete_color = (220, 50, 50)
                else:
                    delete_color = (180, 40, 40)
                
                self.draw_rounded_rect(self.screen, delete_color, delete_rect, 6)
                delete_text = self.small_font.render("删除", True, self.COLOR_WHITE)
                delete_pos = (delete_rect.centerx - delete_text.get_width() // 2,
                              delete_rect.centery - delete_text.get_height() // 2)
                self.screen.blit(delete_text, delete_pos)
        
        # 如果正在显示名称输入界面
        if self.showing_name_input and self.name_input_system:
            self.name_input_system.draw()

    def handle_event(self, event):
        """处理存档菜单事件"""
        # 如果正在显示名称输入界面，只处理名称输入事件和ESC取消，完全阻止其他点击
        if self.showing_name_input and self.name_input_system:
            result = self.name_input_system.handle_event(event)
            if result and result != "cancel":
                # 名称输入完成，创建新存档
                if save_system.create_new_save(self.selected_slot, result):
                    self.showing_name_input = False
                    self.name_input_system = None
                    return "load_save"
                else:
                    # 创建存档失败
                    self.showing_name_input = False
                    self.name_input_system = None
                    return "save_error"
            elif result == "cancel" or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # 取消名称输入
                self.showing_name_input = False
                self.name_input_system = None
                return None
            else:
                # 其他事件已经被名称输入系统处理，返回None表示继续等待输入
                # 阻止鼠标点击事件传递到存档槽
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return None
                return None
        
        # 存档菜单事件处理
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 返回按钮
            if self.back_rect.collidepoint(event.pos):
                return "back"
            
            # 存档槽点击
            saves = save_system.list_saves()
            for i, slot_rect in enumerate(self.save_slots):
                save_info = saves[i]
                
                # 检查是否点击了删除按钮（只在非空存档时）
                if not save_info.get("is_empty"):
                    delete_rect = pygame.Rect(slot_rect.right - 80, slot_rect.y + 40, 60, 30)
                    if delete_rect.collidepoint(event.pos):
                        # 确认删除存档
                        if save_system.delete_save(i + 1):
                            return "save_deleted"
                        else:
                            return "delete_error"
                
                # 检查是否点击了存档槽
                if slot_rect.collidepoint(event.pos):
                    if save_info.get("is_empty"):
                        # 空存档位，开始名称输入
                        self.selected_slot = i + 1  # 存档位从1开始
                        self.name_input_system = NameInputSystem(self.screen)
                        self.showing_name_input = True
                        return None
                    else:
                        # 已有存档，加载游戏
                        self.selected_slot = i + 1
                        return "load_save"
        
        return None

    def update(self):
        """更新存档菜单状态"""
        # 这里可以添加一些动画效果
        pass