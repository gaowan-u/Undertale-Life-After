from typing import Any, Dict, Optional, List
import json
import os
import pygame
from resources import SCREEN_WIDTH, SCREEN_HEIGHT
from screen_adapter import get_logical_mouse_pos, to_logical


class SaveSystem:
    def __init__(self) -> None:
        self.save_dir: str = "saves"
        self.current_save_slot: Optional[int] = None
        self.player_name: str = "Frisk"
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_save_file_path(self, slot_id: int) -> str:
        return os.path.join(self.save_dir, f"save_{slot_id}.json")
    
    def create_default_save_data(self) -> Dict[str, Any]:
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
                "current_scene": "falling_ruins",
                "completed_chapters": [],
                "unlocked_areas": ["falling_ruins"],
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
                "controls": "keyboard"
            }
        }
    
    def create_new_save(self, slot_id: int, player_name: Optional[str] = None) -> bool:
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
    
    def load_save(self, slot_id: int) -> Optional[Dict[str, Any]]:
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
    
    def save_game(self, game_state: Dict[str, Any]) -> bool:
        if not self.current_save_slot:
            return False
        
        save_path = self.get_save_file_path(self.current_save_slot)
        try:
            save_data = self.load_save(self.current_save_slot)
            if not save_data:
                return False
            
            save_data["metadata"]["last_played"] = self.get_current_timestamp()
            save_data["metadata"]["play_time"] += game_state.get("play_time", 0)
            
            if "player_position" in game_state:
                save_data["position"] = game_state["player_position"]
            
            if "player_stats" in game_state:
                save_data["player"].update(game_state["player_stats"])
            
            if "progress" in game_state:
                save_data["progress"].update(game_state["progress"])
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def delete_save(self, slot_id: int) -> bool:
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
    
    def get_save_info(self, slot_id: int) -> Optional[Dict[str, Any]]:
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
    
    def list_saves(self) -> List[Dict[str, Any]]:
        saves: List[Dict[str, Any]] = []
        for i in range(1, 4):
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
    
    def get_current_timestamp(self) -> str:
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def set_player_name(self, name: str) -> None:
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
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font("fonts/NotoSansSC-Regular.ttf", 36)
        self.title_font = pygame.font.Font("fonts/NotoSansSC-Bold.ttf", 48)
        self.input_text: str = ""
        self.active: bool = True
        self.max_length: int = 12
        
        self.input_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2, 400, 50)
        self.title_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 60)
        self.confirm_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 80, 200, 50)
        self.back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150, 200, 50)
        
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (100, 100, 100)
        self.COLOR_BLUE = (0, 120, 255)
        self.COLOR_RED = (255, 80, 80)
        
        self.cursor_visible: bool = True
        self.cursor_blink_time: int = 0
        self.cursor_blink_interval: int = 500
        
        self._title_text = self.title_font.render("请输入角色名称", True, self.COLOR_WHITE)
        self._title_shadow = self.title_font.render("请输入角色名称", True, (0, 0, 0))
        self._hint_text = self.font.render(f"最大长度: {self.max_length} 字符", True, self.COLOR_GRAY)
        self._extra_hint = self.font.render("支持中英文输入", True, (100, 100, 100))
        
        self._gradient_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            alpha = int(180 * (y / SCREEN_HEIGHT))
            pygame.draw.line(self._gradient_overlay, (20, 20, 30, alpha), (0, y), (SCREEN_WIDTH, y))
    
    def draw(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = current_time
        
        self.screen.blit(self._gradient_overlay, (0, 0))
        
        title_pos = (self.title_rect.centerx - self._title_text.get_width()//2, self.title_rect.y)
        self.screen.blit(self._title_shadow, (title_pos[0] + 2, title_pos[1] + 2))
        self.screen.blit(self._title_text, title_pos)
        
        pygame.draw.rect(self.screen, (30, 30, 40), self.input_rect, border_radius=8)
        
        if self.active:
            pygame.draw.rect(self.screen, self.COLOR_BLUE, self.input_rect, 3, border_radius=8)
        else:
            pygame.draw.rect(self.screen, (80, 80, 90), self.input_rect, 2, border_radius=8)
        
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.COLOR_WHITE)
        else:
            text_surface = self.font.render("点击此处输入...", True, self.COLOR_GRAY)
        
        text_y = self.input_rect.y + (self.input_rect.height - text_surface.get_height()) // 2
        text_pos = (self.input_rect.x + 15, text_y)
        self.screen.blit(text_surface, text_pos)
        
        if self.active and self.cursor_visible:
            cursor_x = text_pos[0] + text_surface.get_width() + 2
            cursor_y = text_pos[1]
            cursor_height = text_surface.get_height()
            cursor_width = 3
            
            pygame.draw.rect(self.screen, self.COLOR_BLUE,
                           (cursor_x, cursor_y, cursor_width, cursor_height))
        
        mouse_pos = get_logical_mouse_pos()
        is_confirm_hover = self.confirm_rect.collidepoint(mouse_pos)
        
        if is_confirm_hover:
            confirm_color = (30, 140, 255)
        else:
            confirm_color = self.COLOR_BLUE
        
        pygame.draw.rect(self.screen, confirm_color, self.confirm_rect, border_radius=8)
        
        if is_confirm_hover:
            pygame.draw.rect(self.screen, (100, 180, 255), self.confirm_rect, 2, border_radius=8)
        
        confirm_text = self.font.render("确认", True, self.COLOR_WHITE)
        confirm_pos = (self.confirm_rect.centerx - confirm_text.get_width()//2,
                      self.confirm_rect.centery - confirm_text.get_height()//2)
        self.screen.blit(confirm_text, confirm_pos)
        
        is_back_hover = self.back_rect.collidepoint(mouse_pos)
        
        if is_back_hover:
            back_color = (255, 120, 120)
        else:
            back_color = self.COLOR_RED
        
        pygame.draw.rect(self.screen, back_color, self.back_rect, border_radius=8)
        
        if is_back_hover:
            pygame.draw.rect(self.screen, (255, 180, 180), self.back_rect, 2, border_radius=8)
        
        back_text = self.font.render("返回", True, self.COLOR_WHITE)
        back_pos = (self.back_rect.centerx - back_text.get_width()//2,
                   self.back_rect.centery - back_text.get_height()//2)
        self.screen.blit(back_text, back_pos)
        
        hint_pos = (SCREEN_WIDTH//2 - self._hint_text.get_width()//2, SCREEN_HEIGHT//2 + 220)
        self.screen.blit(self._hint_text, hint_pos)
        
        extra_hint_pos = (SCREEN_WIDTH//2 - self._extra_hint.get_width()//2, SCREEN_HEIGHT//2 + 260)
        self.screen.blit(self._extra_hint, extra_hint_pos)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            logical_pos = to_logical(event.pos)
            if self.input_rect.collidepoint(logical_pos):
                self.active = True
            else:
                self.active = False
            
            if self.confirm_rect.collidepoint(logical_pos):
                if self.input_text.strip():
                    return self.input_text.strip()
                else:
                    return "Frisk"
            
            if self.back_rect.collidepoint(logical_pos):
                return "cancel"
        
        elif self.active:
            if event.type == pygame.TEXTINPUT:
                text = event.text
                if len(self.input_text) + len(text) <= self.max_length:
                    self.input_text += text
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        return self.input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
        
        return None


# 全局存档系统实例
save_system = SaveSystem()
