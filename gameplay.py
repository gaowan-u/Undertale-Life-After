from typing import Dict, List, Optional, Tuple
import pygame
import math
import os
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT, IMAGE_FOLDER

# ==========================================
# 1. 资源安全加载器 (防止缺失图片导致崩溃)
# ==========================================
def safe_load_image(path: str, fallback_color: Tuple[int, int, int] = (100, 100, 100), size: Tuple[int, int] = (100, 100)) -> pygame.Surface:
    """安全加载图片，失败则返回纯色占位 Surface"""
    if os.path.exists(path):
        try:
            surface = pygame.image.load(path)
            try:
                return surface.convert_alpha()
            except pygame.error:
                return surface
        except pygame.error:
            print(f"[警告] 无法加载图片: {path}")

    # 创建占位符
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(fallback_color)
    return surface

# 预定义资源路径
IMG_DIR = IMAGE_FOLDER

# ==========================================
# 2. 硬编码常量提取
# ==========================================
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 25
PLAYER_INITIAL_X = 862
PLAYER_INITIAL_Y = 561
FRAME_DURATION = 80

JOYSTICK_X = 128
JOYSTICK_Y_FROM_BOTTOM = 240
JOYSTICK_RADIUS_RATIO = 0.9

BTN1_X = 1400
BTN2_X = 1544
BTN3_X = 1688
BTN_Y_FROM_BOTTOM = 240
BTN2_Y_FROM_BOTTOM = 320
BTN3_Y_FROM_BOTTOM = 400

BACK_BTN_LEFT = 50
BACK_BTN_TOP = 50
BACK_BTN_WIDTH = 120
BACK_BTN_HEIGHT = 50


def _build_assets() -> Dict[str, pygame.Surface]:
    return {
        'background': safe_load_image(os.path.join(IMG_DIR, "spawn.png"), (50, 50, 50), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        'joystick_base': safe_load_image(os.path.join(IMG_DIR, "cropped_joystick_base.png"), (80, 80, 80), (150, 150)),
        'joystick_top': safe_load_image(os.path.join(IMG_DIR, "cropped_joystick_top.png"), (150, 150, 150), (80, 80)),
        'btn_1': safe_load_image(os.path.join(IMG_DIR, "cropped_button_1.png"), (200, 50, 50), (80, 80)),
        'btn_2': safe_load_image(os.path.join(IMG_DIR, "cropped_button_2.png"), (50, 200, 50), (80, 80)),
        'btn_3': safe_load_image(os.path.join(IMG_DIR, "cropped_button_3.png"), (50, 50, 200), (80, 80)),
        'fb_btn_1': safe_load_image(os.path.join(IMG_DIR, "feedback_button_1.png"), (255, 100, 100), (80, 80)),
        'fb_btn_2': safe_load_image(os.path.join(IMG_DIR, "feedback_button_2.png"), (100, 255, 100), (80, 80)),
        'fb_btn_3': safe_load_image(os.path.join(IMG_DIR, "feedback_button_3.png"), (100, 100, 255), (80, 80)),
        'stand_down': safe_load_image(os.path.join(IMG_DIR, "frisk_stand.png"), (200, 50, 50), (40, 60)),
        'walk_down_r': safe_load_image(os.path.join(IMG_DIR, "frisk_foot_right_up.png"), (200, 50, 50), (40, 60)),
        'walk_down_l': safe_load_image(os.path.join(IMG_DIR, "frisk_foot_left_up.png"), (200, 50, 50), (40, 60)),
        'stand_up': safe_load_image(os.path.join(IMG_DIR, "frisk_back_stand.png"), (50, 50, 200), (40, 60)),
        'walk_up_r': safe_load_image(os.path.join(IMG_DIR, "frisk_back_foot_right_up.png"), (50, 50, 200), (40, 60)),
        'walk_up_l': safe_load_image(os.path.join(IMG_DIR, "frisk_back_foot_left_up.png"), (50, 50, 200), (40, 60)),
        'stand_left': safe_load_image(os.path.join(IMG_DIR, "frisk_stand_left.png"), (50, 200, 50), (40, 60)),
        'walk_left': safe_load_image(os.path.join(IMG_DIR, "frisk_walk_left.png"), (50, 200, 50), (40, 60)),
        'stand_right': safe_load_image(os.path.join(IMG_DIR, "frisk_stand_right.png"), (200, 200, 50), (40, 60)),
        'walk_right': safe_load_image(os.path.join(IMG_DIR, "frisk_walk_right.png"), (200, 200, 50), (40, 60)),
    }

ASSETS: Dict[str, pygame.Surface] = _build_assets()


def init_assets() -> None:
    """在 pygame 初始化后重新加载资源，确保 convert_alpha() 生效"""
    global ASSETS
    ASSETS = _build_assets()

# ==========================================
# 2. 核心类定义
# ==========================================
class Player:
    def __init__(self) -> None:
        self.width, self.height = PLAYER_WIDTH, PLAYER_HEIGHT
        self.rect = pygame.Rect(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, self.width, self.height)
        self.speed = PLAYER_SPEED
        self.direction: str = 'down'
        
        self.animation_timer: int = 0
        self.animation_index: int = 0
        self.frame_duration: int = FRAME_DURATION
        
        self.sequences: Dict[str, List[str]] = {
            'down':  ['stand_down', 'walk_down_r', 'stand_down', 'walk_down_l'],
            'up':    ['stand_up', 'walk_up_r', 'stand_up', 'walk_up_l'],
            'left':  ['stand_left', 'walk_left', 'stand_left', 'walk_left'],
            'right': ['stand_right', 'walk_right', 'stand_right', 'walk_right']
        }

    def update(self, dx: float, dy: float, current_time: int) -> None:
        is_moving = abs(dx) > 0.1 or abs(dy) > 0.1
        
        if is_moving:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
            if current_time - self.animation_timer > self.frame_duration:
                self.animation_timer = current_time
                self.animation_index = (self.animation_index + 1) % len(self.sequences[self.direction])
        else:
            self.animation_index = 0

    def draw(self, surface: pygame.Surface) -> None:
        seq = self.sequences[self.direction]
        img_key = seq[self.animation_index]
        img = ASSETS.get(img_key)
        if img:
            visual_rect = img.get_rect(midbottom=self.rect.midbottom)
            surface.blit(img, visual_rect)


class VirtualJoystick:
    def __init__(self) -> None:
        base_img = ASSETS['joystick_base']
        top_img = ASSETS['joystick_top']
        self.base_rect = base_img.get_rect(topleft=(JOYSTICK_X, SCREEN_HEIGHT - JOYSTICK_Y_FROM_BOTTOM))
        self.top_rect = top_img.get_rect(center=self.base_rect.center)
        self.radius = self.base_rect.width / 2 * JOYSTICK_RADIUS_RATIO
        self.dragging: bool = False
        self.direction: Tuple[float, float] = (0.0, 0.0)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.base_rect.collidepoint(event.pos) or self.top_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_position(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                self.reset()
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_position(event.pos)

    def _update_position(self, mouse_pos: Tuple[int, int]) -> None:
        dx = mouse_pos[0] - self.base_rect.centerx
        dy = mouse_pos[1] - self.base_rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > self.radius:
            ratio = self.radius / distance
            dx *= ratio
            dy *= ratio
            
        self.top_rect.centerx = self.base_rect.centerx + dx
        self.top_rect.centery = self.base_rect.centery + dy
        
        if distance > 10:
            self.direction = (dx / self.radius, dy / self.radius)
        else:
            self.direction = (0.0, 0.0)

    def reset(self) -> None:
        self.top_rect.center = self.base_rect.center
        self.direction = (0.0, 0.0)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(ASSETS['joystick_base'], self.base_rect)
        surface.blit(ASSETS['joystick_top'], self.top_rect)


class ActionButtons:
    def __init__(self) -> None:
        btn1 = ASSETS['btn_1']
        btn2 = ASSETS['btn_2']
        btn3 = ASSETS['btn_3']
        
        self.btn1_rect = btn1.get_rect(topleft=(BTN1_X, SCREEN_HEIGHT - BTN_Y_FROM_BOTTOM))
        self.btn2_rect = btn2.get_rect(topleft=(BTN2_X, SCREEN_HEIGHT - BTN2_Y_FROM_BOTTOM))
        self.btn3_rect = btn3.get_rect(topleft=(BTN3_X, SCREEN_HEIGHT - BTN3_Y_FROM_BOTTOM))
        self.back_rect = pygame.Rect(BACK_BTN_LEFT, BACK_BTN_TOP, BACK_BTN_WIDTH, BACK_BTN_HEIGHT)
        
        self.states: Dict[int, int] = {1: 0, 2: 0, 3: 0}
        self.pressed: Dict[int | str, bool] = {1: False, 2: False, 3: False, 'back': False}
        self._back_initialized = False

    def reset_states(self) -> None:
        for k in self.states:
            self.states[k] = 0
        for k in self.pressed:
            self.pressed[k] = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn1_rect.collidepoint(pos):
                self.states[1], self.pressed[1] = 1, True
            elif self.btn2_rect.collidepoint(pos):
                self.states[2], self.pressed[2] = 1, True
            elif self.btn3_rect.collidepoint(pos):
                self.states[3], self.pressed[3] = 1, True
            elif self.back_rect.collidepoint(pos):
                self.pressed['back'] = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.states[1], self.pressed[1] = 0, False
            self.states[2], self.pressed[2] = 0, False
            self.states[3], self.pressed[3] = 0, False
            self.pressed['back'] = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: self.states[1], self.pressed[1] = 1, True
            elif event.key == pygame.K_x: self.states[2], self.pressed[2] = 1, True
            elif event.key == pygame.K_c: self.states[3], self.pressed[3] = 1, True
            
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z: self.states[1], self.pressed[1] = 0, False
            elif event.key == pygame.K_x: self.states[2], self.pressed[2] = 0, False
            elif event.key == pygame.K_c: self.states[3], self.pressed[3] = 0, False

    def _init_back_surfaces(self) -> None:
        res = Resources()
        self._back_normal = pygame.Surface((BACK_BTN_WIDTH, BACK_BTN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self._back_normal, (50, 50, 50), (0, 0, BACK_BTN_WIDTH, BACK_BTN_HEIGHT), border_radius=8)
        pygame.draw.rect(self._back_normal, (100, 100, 100), (0, 0, BACK_BTN_WIDTH, BACK_BTN_HEIGHT), 2, border_radius=8)
        text = res.font_24.render("返回", True, res.COLOR_WHITE)
        tx = (BACK_BTN_WIDTH - text.get_width()) // 2
        ty = (BACK_BTN_HEIGHT - text.get_height()) // 2
        self._back_normal.blit(text, (tx, ty))

        self._back_hover = pygame.Surface((BACK_BTN_WIDTH, BACK_BTN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self._back_hover, (70, 70, 70), (0, 0, BACK_BTN_WIDTH, BACK_BTN_HEIGHT), border_radius=8)
        pygame.draw.rect(self._back_hover, res.COLOR_BLUE, (0, 0, BACK_BTN_WIDTH, BACK_BTN_HEIGHT), 2, border_radius=8)
        self._back_hover.blit(text, (tx, ty))
        self._back_initialized = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(ASSETS['fb_btn_1'] if self.states[1] else ASSETS['btn_1'], self.btn1_rect)
        surface.blit(ASSETS['fb_btn_2'] if self.states[2] else ASSETS['btn_2'], self.btn2_rect)
        surface.blit(ASSETS['fb_btn_3'] if self.states[3] else ASSETS['btn_3'], self.btn3_rect)
        if not self._back_initialized:
            self._init_back_surfaces()
        is_hover = self.back_rect.collidepoint(pygame.mouse.get_pos())
        surface.blit(self._back_hover if is_hover else self._back_normal, self.back_rect)


# ==========================================
# 3. 游戏会话管理器 (替代原全局逻辑)
# ==========================================
class GameplaySession:
    def __init__(self) -> None:
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player = Player()
        self.joystick = VirtualJoystick()
        self.buttons = ActionButtons()
        self.keyboard_dir: Tuple[float, float] = (0.0, 0.0)

    def _update_keyboard_input(self) -> None:
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
        
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
        self.keyboard_dir = (dx, dy)

    def load_from_save(self, save_data: dict) -> None:
        pos = save_data.get("position", {})
        self.player.rect.x = pos.get("x", PLAYER_INITIAL_X)
        self.player.rect.y = pos.get("y", PLAYER_INITIAL_Y)
        self.player.direction = pos.get("direction", "down")

    def process(self, events: List[pygame.event.Event]) -> Tuple[pygame.Surface, Optional[str]]:
        self.buttons.reset_states()

        for event in events:
            if _touch_ui_visible:
                self.joystick.handle_event(event)
                self.buttons.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.buttons.back_rect.collidepoint(event.pos):
                        return self.surface, "back"

        if _touch_ui_visible and self.buttons.pressed['back']:
            return self.surface, "back"

        self._update_keyboard_input()

        kx, ky = self.keyboard_dir
        jx, jy = self.joystick.direction if _touch_ui_visible else (0.0, 0.0)

        if abs(kx) > 0.1 or abs(ky) > 0.1:
            dx, dy = kx, ky
        else:
            dx, dy = jx, jy

        self.player.update(dx, dy, pygame.time.get_ticks())

        self.surface.fill((0, 0, 0))
        self.surface.blit(ASSETS['background'], (0, 0))
        self.player.draw(self.surface)
        if _touch_ui_visible:
            self.joystick.draw(self.surface)
            self.buttons.draw(self.surface)

        return self.surface, None


_session = GameplaySession()

def gameplay(events: List[pygame.event.Event]) -> Tuple[pygame.Surface, Optional[str]]:
    return _session.process(events)


def init_session_from_save(save_data: dict) -> None:
    _session.load_from_save(save_data)


_touch_ui_visible = True

def set_touch_ui_visible(visible: bool) -> None:
    global _touch_ui_visible
    _touch_ui_visible = visible

def get_touch_ui_visible() -> bool:
    return _touch_ui_visible