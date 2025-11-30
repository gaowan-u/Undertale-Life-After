import json
import os
import pygame
from intro_animation import screen_width, screen_height

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
            # 如果已有存档，更新存档中的名称
            save_data = self.load_save(self.current_save_slot)
            if save_data:
                save_data["player"]["name"] = name
                self.save_game({})  # 空游戏状态，只更新名称


class NameInputSystem:
    """名称输入系统"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 36)
        self.title_font = pygame.font.Font("fonts/NotoSansSC-Bold.ttf", 48)
        self.input_text = ""
        self.active = False
        self.max_length = 12
        
        # 输入框位置
        self.input_rect = pygame.Rect(screen_width//2 - 200, screen_height//2, 400, 50)
        self.title_rect = pygame.Rect(screen_width//2 - 200, screen_height//2 - 100, 400, 60)
        
        # 按钮
        self.confirm_rect = pygame.Rect(screen_width//2 - 100, screen_height//2 + 80, 200, 50)
        
        # 颜色
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (100, 100, 100)
        self.COLOR_BLUE = (0, 120, 255)
    
    def draw(self):
        """绘制名称输入界面"""
        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = self.title_font.render("请输入角色名称", True, self.COLOR_WHITE)
        title_pos = (self.title_rect.centerx - title_text.get_width()//2, self.title_rect.y)
        self.screen.blit(title_text, title_pos)
        
        # 输入框背景
        pygame.draw.rect(self.screen, self.COLOR_WHITE, self.input_rect, 2)
        if self.active:
            pygame.draw.rect(self.screen, self.COLOR_BLUE, self.input_rect, 3)
        
        # 输入文本
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.COLOR_WHITE)
        else:
            text_surface = self.font.render("点击此处输入...", True, self.COLOR_GRAY)
        
        text_pos = (self.input_rect.x + 10, self.input_rect.y + 10)
        self.screen.blit(text_surface, text_pos)
        
        # 确认按钮
        pygame.draw.rect(self.screen, self.COLOR_BLUE, self.confirm_rect)
        confirm_text = self.font.render("确认", True, self.COLOR_WHITE)
        confirm_pos = (self.confirm_rect.centerx - confirm_text.get_width()//2, 
                      self.confirm_rect.centery - confirm_text.get_height()//2)
        self.screen.blit(confirm_text, confirm_pos)
        
        # 提示文字
        hint_text = self.font.render(f"最大长度: {self.max_length} 字符", True, self.COLOR_GRAY)
        hint_pos = (screen_width//2 - hint_text.get_width()//2, screen_height//2 + 150)
        self.screen.blit(hint_text, hint_pos)
    
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
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    return self.input_text.strip()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                # 限制输入长度和字符类型
                if len(self.input_text) < self.max_length and event.unicode.isprintable():
                    self.input_text += event.unicode
        
        return None


# 全局存档系统实例
save_system = SaveSystem()
