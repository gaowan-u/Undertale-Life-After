import pygame
from intro_animation import screen_width, screen_height
from save_system import save_system, NameInputSystem

class SaveMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 32)
        self.title_font = pygame.font.Font("fonts/NotoSansSC-Bold.ttf", 48)
        self.small_font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 24)
        
        # 存档槽位置
        self.save_slots = []
        slot_width, slot_height = 600, 120
        for i in range(3):
            slot_rect = pygame.Rect(
                screen_width//2 - slot_width//2,
                200 + i * (slot_height + 20),
                slot_width,
                slot_height
            )
            self.save_slots.append(slot_rect)
        
        # 按钮
        self.back_rect = pygame.Rect(50, 50, 120, 50)
        
        # 颜色
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (100, 100, 100)
        self.COLOR_BLUE = (0, 120, 255)
        self.COLOR_GREEN = (0, 200, 0)
        self.COLOR_RED = (255, 0, 0)
        
        # 状态
        self.selected_slot = None
        self.name_input_system = None
        self.showing_name_input = False
        
    def draw(self):
        """绘制存档菜单"""
        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = self.title_font.render("选择存档", True, self.COLOR_WHITE)
        title_pos = (screen_width//2 - title_text.get_width()//2, 80)
        self.screen.blit(title_text, title_pos)
        
        # 返回按钮
        pygame.draw.rect(self.screen, self.COLOR_GRAY, self.back_rect)
        back_text = self.font.render("返回", True, self.COLOR_WHITE)
        back_pos = (self.back_rect.centerx - back_text.get_width()//2, 
                   self.back_rect.centery - back_text.get_height()//2)
        self.screen.blit(back_text, back_pos)
        
        # 获取存档列表
        saves = save_system.list_saves()
        
        # 绘制存档槽
        for i, slot_rect in enumerate(self.save_slots):
            save_info = saves[i]
            
            # 槽背景
            if slot_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (50, 50, 50), slot_rect)
            else:
                pygame.draw.rect(self.screen, (30, 30, 30), slot_rect)
            
            pygame.draw.rect(self.screen, self.COLOR_WHITE, slot_rect, 2)
            
            # 存档信息
            if save_info.get("is_empty"):
                # 空存档位
                empty_text = self.font.render("空存档位", True, self.COLOR_GRAY)
                empty_pos = (slot_rect.x + 20, slot_rect.y + 20)
                self.screen.blit(empty_text, empty_pos)
                
                new_game_text = self.small_font.render("点击创建新游戏", True, self.COLOR_GRAY)
                new_game_pos = (slot_rect.x + 20, slot_rect.y + 60)
                self.screen.blit(new_game_text, new_game_pos)
            else:
                # 有存档
                # 玩家名称
                name_text = self.font.render(f"玩家: {save_info['player_name']}", True, self.COLOR_WHITE)
                name_pos = (slot_rect.x + 20, slot_rect.y + 20)
                self.screen.blit(name_text, name_pos)
                
                # 章节信息
                chapter_text = self.small_font.render(f"章节: {save_info['chapter']}", True, self.COLOR_GRAY)
                chapter_pos = (slot_rect.x + 20, slot_rect.y + 60)
                self.screen.blit(chapter_text, chapter_pos)
                
                # 等级和游戏时间
                level_text = self.small_font.render(f"等级: {save_info['level']}", True, self.COLOR_GRAY)
                level_pos = (slot_rect.x + 200, slot_rect.y + 60)
                self.screen.blit(level_text, level_pos)
                
                # 最后游玩时间
                if save_info['last_played']:
                    time_text = self.small_font.render(f"最后游玩: {save_info['last_played']}", True, self.COLOR_GRAY)
                    time_pos = (slot_rect.x + 350, slot_rect.y + 60)
                    self.screen.blit(time_text, time_pos)
                
                # 删除按钮
                delete_rect = pygame.Rect(slot_rect.right - 80, slot_rect.y + 40, 60, 30)
                pygame.draw.rect(self.screen, self.COLOR_RED, delete_rect)
                delete_text = self.small_font.render("删除", True, self.COLOR_WHITE)
                delete_pos = (delete_rect.centerx - delete_text.get_width()//2, 
                             delete_rect.centery - delete_text.get_height()//2)
                self.screen.blit(delete_text, delete_pos)
        
        # 如果正在显示名称输入界面
        if self.showing_name_input and self.name_input_system:
            self.name_input_system.draw()
    
    def handle_event(self, event):
        """处理存档菜单事件"""
        # 如果正在显示名称输入界面，优先处理名称输入事件
        if self.showing_name_input and self.name_input_system:
            result = self.name_input_system.handle_event(event)
            if result:
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # 取消名称输入
                self.showing_name_input = False
                self.name_input_system = None
                return None
            else:
                # 其他事件已经被名称输入系统处理，返回None表示继续等待输入
                return None
        
        # 存档菜单事件处理
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 返回按钮
            if self.back_rect.collidepoint(event.pos):
                return "back"
            
            # 存档槽点击
            for i, slot_rect in enumerate(self.save_slots):
                if slot_rect.collidepoint(event.pos):
                    saves = save_system.list_saves()
                    save_info = saves[i]
                    
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
            
            # 删除按钮点击
            for i, slot_rect in enumerate(self.save_slots):
                delete_rect = pygame.Rect(slot_rect.right - 80, slot_rect.y + 40, 60, 30)
                if delete_rect.collidepoint(event.pos):
                    saves = save_system.list_saves()
                    save_info = saves[i]
                    if not save_info.get("is_empty"):
                        # 确认删除存档
                        if save_system.delete_save(i + 1):
                            return "save_deleted"
                        else:
                            return "delete_error"
        
        return None
    
    def update(self):
        """更新存档菜单状态"""
        # 这里可以添加一些动画效果
        pass
