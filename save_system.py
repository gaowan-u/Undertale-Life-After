import json
import os
import pygame
from resources import SCREEN_WIDTH, SCREEN_HEIGHT

class SaveSystem:
    def __init__(self):
        self.save_dir = "saves"
        self.current_save_slot = None
        self.player_name = "Frisk"  # 默认名称
        
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_save_file_path(self, slot_id):
        """获取存档文件路径"""
        return os.path.join(self.save_dir, f"save_{slot_id}.json")
    
    def create_default_save_data(self):
        """创建默认的存档数据结构"""
        return {
            "metadata": {
                "version": "0.0.1",
                "created_at": None,
                "last_played": None,
                "play_time": 0
            },
            "player": {
                "name": self.player_name,
                "level": 1,
                "health": 20,
                "max_health": 20,
                "attack": 10,
                "defense": 10,
                "gold": 0,
                "items": [],
                "equipment": {}
            },
            "progress": {
                "current_chapter": 1,
                "current_scene": "坠落遗迹",
                "completed_chapters": [],
                "unlocked_areas": ["坠落遗迹"],
                "story_flags": {},
                "choices": {}
            },
            "position": {
                "x": 862,
                "y": 561,
                "direction": "down"
            },
            "settings": {
                "music_volume": 0.7,
                "sfx_volume": 0.8,
                "language": "zh-CN",
                "controls": "keyboard"  # keyboard, touch, or auto
            }
        }
    
    def create_new_save(self, slot_id, player_name=None):
        """创建新存档"""
        if player_name:
            self.player_name = player_name
        
        save_data = self.create_default_save_data()
        save_data["player"]["name"] = self.player_name
        save_data["metadata"]["created_at"] = self.get_current_timestamp()
        save_data["metadata"]["last_played"] = self.get_current_timestamp()
        
        save_path = self.get_save_file_path(slot_id)
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            self.current_save_slot = slot_id
            return True
        except Exception as e:
            print(f"创建存档失败: {e}")
            return False
    
    def load_save(self, slot_id):
        """加载存档"""
        save_path = self.get_save_file_path(slot_id)
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.current_save_slot = slot_id
            self.player_name = save_data["player"]["name"]
            return save_data
        except Exception as e:
            print(f"加载存档失败: {e}")
            return None
    
    def save_game(self, game_state):
        """保存当前游戏状态"""
        if not self.current_save_slot:
            return False
        
        save_path = self.get_save_file_path(self.current_save_slot)
        try:
            # 更新存档数据
            save_data = self.load_save(self.current_save_slot)
            if not save_data:
                return False
            
            # 更新游戏状态
            save_data["metadata"]["last_played"] = self.get_current_timestamp()
            save_data["metadata"]["play_time"] += game_state.get("play_time", 0)
            
            # 更新玩家位置和状态
            if "player_position" in game_state:
                save_data["position"] = game_state["player_position"]
            
            if "player_stats" in game_state:
                save_data["player"].update(game_state["player_stats"])
            
            if "progress" in game_state:
                save_data["progress"].update(game_state["progress"])
            
            # 保存到文件
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def delete_save(self, slot_id):
        """删除存档"""
        save_path = self.get_save_file_path(slot_id)
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
                if self.current_save_slot == slot_id:
                    self.current_save_slot = None
                return True
            return False
        except Exception as e:
            print(f"删除存档失败: {e}")
            return False
    
    def get_save_info(self, slot_id):
        """获取存档信息"""
        save_data = self.load_save(slot_id)
        if not save_data:
            return None
        
        return {
            "slot_id": slot_id,
            "player_name": save_data["player"]["name"],
            "level": save_data["player"]["level"],
            "chapter": save_data["progress"]["current_chapter"],
            "play_time": save_data["metadata"]["play_time"],
            "last_played": save_data["metadata"]["last_played"]
        }
    
    def list_saves(self):
        """列出所有存档"""
        saves = []
        for i in range(1, 4):  # 假设有3个存档位
            save_info = self.get_save_info(i)
            if save_info:
                saves.append(save_info)
            else:
                saves.append({
                    "slot_id": i,
                    "player_name": "空存档位",
                    "level": 0,
                    "chapter": 0,
                    "play_time": 0,
                    "last_played": None,
                    "is_empty": True
                })
        return saves
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def set_player_name(self, name):
        """设置玩家名称"""
        self.player_name = name
        if self.current_save_slot:
            save_path = self.get_save_file_path(self.current_save_slot)
            if os.path.exists(save_path):
                try:
                    with open(save_path, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    save_data["player"]["name"] = name
                    with open(save_path, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"更新存档名称失败: {e}")


class NameInputSystem:
    """名称输入系统"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 36)
        self.title_font = pygame.font.Font("fonts/NotoSansSC-Bold.ttf", 48)
        self.input_text = ""
        self.active = True  # 默认激活输入框
        self.max_length = 12
        
        # 输入框位置
        self.input_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2, 400, 50)
        self.title_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 60)
        
        # 按钮
        self.confirm_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 80, 200, 50)
        self.back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150, 200, 50)
        
        # 颜色
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (100, 100, 100)
        self.COLOR_BLUE = (0, 120, 255)
        self.COLOR_RED = (255, 80, 80)
        
        # 光标闪烁控制
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 500  # 毫秒
    
    def draw(self):
        """绘制名称输入界面"""
        # 更新光标闪烁状态
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = current_time
        
        # 半透明渐变背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            alpha = int(180 * (y / SCREEN_HEIGHT))
            pygame.draw.line(overlay, (20, 20, 30, alpha), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(overlay, (0, 0))
        
        # 标题 - 添加发光效果
        title_text = self.title_font.render("请输入角色名称", True, self.COLOR_WHITE)
        title_pos = (self.title_rect.centerx - title_text.get_width()//2, self.title_rect.y)
        
        # 标题阴影
        title_shadow = self.title_font.render("请输入角色名称", True, (0, 0, 0, 100))
        self.screen.blit(title_shadow, (title_pos[0] + 2, title_pos[1] + 2))
        self.screen.blit(title_text, title_pos)
        
        # 输入框背景 - 圆角矩形
        pygame.draw.rect(self.screen, (30, 30, 40), self.input_rect, border_radius=8)
        
        # 输入框边框
        if self.active:
            pygame.draw.rect(self.screen, self.COLOR_BLUE, self.input_rect, 3, border_radius=8)
        else:
            pygame.draw.rect(self.screen, (80, 80, 90), self.input_rect, 2, border_radius=8)
        
        # 输入文本
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.COLOR_WHITE)
        else:
            text_surface = self.font.render("点击此处输入...", True, self.COLOR_GRAY)
        
        # 修正文本位置，使其垂直居中
        text_y = self.input_rect.y + (self.input_rect.height - text_surface.get_height()) // 2
        text_pos = (self.input_rect.x + 15, text_y)
        self.screen.blit(text_surface, text_pos)
        
        # 绘制光标（仅在激活状态且光标可见时）
        if self.active and self.cursor_visible:
            cursor_x = text_pos[0] + text_surface.get_width() + 2
            cursor_y = text_pos[1]
            cursor_height = text_surface.get_height()
            cursor_width = 3
            
            # 光标颜色
            cursor_color = self.COLOR_BLUE
            
            # 绘制光标
            pygame.draw.rect(self.screen, cursor_color, 
                           (cursor_x, cursor_y, cursor_width, cursor_height))
        
        # 确认按钮 - 圆角和悬停效果
        mouse_pos = pygame.mouse.get_pos()
        is_confirm_hover = self.confirm_rect.collidepoint(mouse_pos)
        
        if is_confirm_hover:
            confirm_color = (30, 140, 255)
        else:
            confirm_color = self.COLOR_BLUE
        
        pygame.draw.rect(self.screen, confirm_color, self.confirm_rect, border_radius=8)
        
        # 确认按钮边框
        if is_confirm_hover:
            pygame.draw.rect(self.screen, (100, 180, 255), self.confirm_rect, 2, border_radius=8)
        
        confirm_text = self.font.render("确认", True, self.COLOR_WHITE)
        confirm_pos = (self.confirm_rect.centerx - confirm_text.get_width()//2, 
                      self.confirm_rect.centery - confirm_text.get_height()//2)
        self.screen.blit(confirm_text, confirm_pos)
        
        # 返回按钮 - 圆角和悬停效果
        is_back_hover = self.back_rect.collidepoint(mouse_pos)
        
        if is_back_hover:
            back_color = (255, 120, 120)
        else:
            back_color = self.COLOR_RED
        
        pygame.draw.rect(self.screen, back_color, self.back_rect, border_radius=8)
        
        # 返回按钮边框
        if is_back_hover:
            pygame.draw.rect(self.screen, (255, 180, 180), self.back_rect, 2, border_radius=8)
        
        back_text = self.font.render("返回", True, self.COLOR_WHITE)
        back_pos = (self.back_rect.centerx - back_text.get_width()//2, 
                   self.back_rect.centery - back_text.get_height()//2)
        self.screen.blit(back_text, back_pos)
        
        # 提示文字
        hint_text = self.font.render(f"最大长度: {self.max_length} 字符", True, self.COLOR_GRAY)
        hint_pos = (SCREEN_WIDTH//2 - hint_text.get_width()//2, SCREEN_HEIGHT//2 + 220)
        self.screen.blit(hint_text, hint_pos)
        
        # 额外提示
        extra_hint_text = self.font.render("支持中英文输入", True, (100, 100, 100))
        extra_hint_pos = (SCREEN_WIDTH//2 - extra_hint_text.get_width()//2, SCREEN_HEIGHT//2 + 260)
        self.screen.blit(extra_hint_text, extra_hint_pos)
    
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 点击输入框激活
            if self.input_rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            
            # 点击确认按钮
            if self.confirm_rect.collidepoint(event.pos):
                if self.input_text.strip():
                    return self.input_text.strip()
                else:
                    # 如果输入为空，使用默认名称
                    return "Frisk"
            
            # 点击返回按钮
            if self.back_rect.collidepoint(event.pos):
                return "cancel"
        
        elif self.active:
            # 处理中文输入法提交的文本
            if event.type == pygame.TEXTINPUT:
                text = event.text
                # 限制输入长度
                if len(self.input_text) + len(text) <= self.max_length:
                    self.input_text += text
            
            # 处理键盘输入（用于退格、回车等）
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        return self.input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                # 对于普通键盘输入，也使用 unicode（兼容非输入法输入）
                elif event.unicode and event.unicode.isprintable():
                    if len(self.input_text) < self.max_length:
                        self.input_text += event.unicode
        
        return None


# 全局存档系统实例
save_system = SaveSystem()
