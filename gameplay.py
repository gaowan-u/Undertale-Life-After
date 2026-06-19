import pygame
import math
import os
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT, IMAGE_FOLDER

# ==========================================
# 1. 资源安全加载器 (防止缺失图片导致崩溃)
# ==========================================
def safe_load_image(path, fallback_color=(100, 100, 100), size=(100, 100)):
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
ASSETS = {
    'background': safe_load_image(os.path.join(IMG_DIR, "出生点.png"), (50, 50, 50), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    'joystick_base': safe_load_image(os.path.join(IMG_DIR, "cropped_joystick_base.png"), (80, 80, 80), (150, 150)),
    'joystick_top': safe_load_image(os.path.join(IMG_DIR, "cropped_joystick_top.png"), (150, 150, 150), (80, 80)),
    'btn_1': safe_load_image(os.path.join(IMG_DIR, "cropped_button_1.png"), (200, 50, 50), (80, 80)),
    'btn_2': safe_load_image(os.path.join(IMG_DIR, "cropped_button_2.png"), (50, 200, 50), (80, 80)),
    'btn_3': safe_load_image(os.path.join(IMG_DIR, "cropped_button_3.png"), (50, 50, 200), (80, 80)),
    'fb_btn_1': safe_load_image(os.path.join(IMG_DIR, "feedback_button_1.png"), (255, 100, 100), (80, 80)),
    'fb_btn_2': safe_load_image(os.path.join(IMG_DIR, "feedback_button_2.png"), (100, 255, 100), (80, 80)),
    'fb_btn_3': safe_load_image(os.path.join(IMG_DIR, "feedback_button_3.png"), (100, 100, 255), (80, 80)),
    # 玩家动画序列
    'stand_down': safe_load_image(os.path.join(IMG_DIR, "Frisk_立正.png"), (200, 50, 50), (40, 60)),
    'walk_down_r': safe_load_image(os.path.join(IMG_DIR, "Frisk_右脚抬.png"), (200, 50, 50), (40, 60)),
    'walk_down_l': safe_load_image(os.path.join(IMG_DIR, "Frisk_左脚抬.png"), (200, 50, 50), (40, 60)),
    'stand_up': safe_load_image(os.path.join(IMG_DIR, "Frisk_背着立正.png"), (50, 50, 200), (40, 60)),
    'walk_up_r': safe_load_image(os.path.join(IMG_DIR, "Frisk_背部右脚抬.png"), (50, 50, 200), (40, 60)),
    'walk_up_l': safe_load_image(os.path.join(IMG_DIR, "Frisk_背部左脚抬.png"), (50, 50, 200), (40, 60)),
    'stand_left': safe_load_image(os.path.join(IMG_DIR, "Frisk_左转立正.png"), (50, 200, 50), (40, 60)),
    'walk_left': safe_load_image(os.path.join(IMG_DIR, "Frisk_左脚走路.png"), (50, 200, 50), (40, 60)),
    'stand_right': safe_load_image(os.path.join(IMG_DIR, "Frisk_右转立正.png"), (200, 200, 50), (40, 60)),
    'walk_right': safe_load_image(os.path.join(IMG_DIR, "Frisk_右脚走路.png"), (200, 200, 50), (40, 60)),
}

# ==========================================
# 2. 核心类定义
# ==========================================
class Player:
    def __init__(self):
        self.width, self.height = 40, 60
        self.rect = pygame.Rect(862, 561, self.width, self.height)
        self.speed = 25
        self.direction = 'down'
        
        self.animation_timer = 0
        self.animation_index = 0
        self.frame_duration = 80
        
        self.sequences = {
            'down':  ['stand_down', 'walk_down_r', 'stand_down', 'walk_down_l'],
            'up':    ['stand_up', 'walk_up_r', 'stand_up', 'walk_up_l'],
            'left':  ['stand_left', 'walk_left', 'stand_left', 'walk_left'],
            'right': ['stand_right', 'walk_right', 'stand_right', 'walk_right']
        }

    def update(self, dx, dy, current_time):
        is_moving = abs(dx) > 0.1 or abs(dy) > 0.1
        
        # 更新朝向
        if is_moving:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            
            # 移动位置
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
            # 更新动画帧
            if current_time - self.animation_timer > self.frame_duration:
                self.animation_timer = current_time
                self.animation_index = (self.animation_index + 1) % len(self.sequences[self.direction])
        else:
            # 静止时重置为站立姿态 (第0帧)
            self.animation_index = 0

    def draw(self, surface):
        seq = self.sequences[self.direction]
        img_key = seq[self.animation_index]
        img = ASSETS.get(img_key)
        if img:
            # 保持脚部对齐
            visual_rect = img.get_rect(midbottom=self.rect.midbottom)
            surface.blit(img, visual_rect)


class VirtualJoystick:
    def __init__(self):
        base_img = ASSETS['joystick_base']
        self.base_rect = base_img.get_rect(topleft=(128, SCREEN_HEIGHT - 240))
        self.top_rect = base_img.get_rect(center=self.base_rect.center) # 初始居中
        self.radius = self.base_rect.width / 2 * 0.9
        self.dragging = False
        self.direction = (0.0, 0.0)

    def handle_event(self, event):
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

    def _update_position(self, mouse_pos):
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

    def reset(self):
        self.top_rect.center = self.base_rect.center
        self.direction = (0.0, 0.0)

    def draw(self, surface):
        surface.blit(ASSETS['joystick_base'], self.base_rect)
        surface.blit(ASSETS['joystick_top'], self.top_rect)


class ActionButtons:
    def __init__(self):
        btn1 = ASSETS['btn_1']
        btn2 = ASSETS['btn_2']
        btn3 = ASSETS['btn_3']
        
        self.btn1_rect = btn1.get_rect(topleft=(1400, SCREEN_HEIGHT - 240))
        self.btn2_rect = btn2.get_rect(topleft=(1544, SCREEN_HEIGHT - 320))
        self.btn3_rect = btn3.get_rect(topleft=(1688, SCREEN_HEIGHT - 400))
        self.back_rect = pygame.Rect(50, 50, 120, 50)
        
        self.states = {1: 0, 2: 0, 3: 0} # 0: 正常, 1: 按下
        self.pressed = {1: False, 2: False, 3: False, 'back': False}

    def reset_states(self):
        for k in self.states:
            self.states[k] = 0
        for k in self.pressed:
            self.pressed[k] = False

    def handle_event(self, event):
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

    def draw(self, surface):
        # 绘制动作按钮
        surface.blit(ASSETS['fb_btn_1'] if self.states[1] else ASSETS['btn_1'], self.btn1_rect)
        surface.blit(ASSETS['fb_btn_2'] if self.states[2] else ASSETS['btn_2'], self.btn2_rect)
        surface.blit(ASSETS['fb_btn_3'] if self.states[3] else ASSETS['btn_3'], self.btn3_rect)
        
        # 绘制返回按钮
        try:
            res = Resources()
            font = res.font_24
            is_hover = self.back_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (70, 70, 70) if is_hover else (50, 50, 50)
            border_color = res.COLOR_BLUE if is_hover else (100, 100, 100)
            
            pygame.draw.rect(surface, bg_color, self.back_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, self.back_rect, 2, border_radius=8)
            
            text = font.render("返回", True, res.COLOR_WHITE)
            surface.blit(text, (self.back_rect.centerx - text.get_width()//2, 
                                self.back_rect.centery - text.get_height()//2))
        except Exception:
            pass


# ==========================================
# 3. 游戏会话管理器 (替代原全局逻辑)
# ==========================================
class GameplaySession:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player = Player()
        self.joystick = VirtualJoystick()
        self.buttons = ActionButtons()
        self.keyboard_dir = (0.0, 0.0)

    def _update_keyboard_input(self):
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

    def process(self, events):
        # 0. 清除上一帧残留的按钮状态（防止退出再进入时误触发）
        self.buttons.reset_states()

        # 1. 处理输入
        for event in events:
            self.joystick.handle_event(event)
            self.buttons.handle_event(event)
            
            # 检查返回按钮点击 (鼠标)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttons.back_rect.collidepoint(event.pos):
                    return self.surface, "back"
                    
        # 检查返回按钮点击 (键盘状态)
        if self.buttons.pressed['back']:
            return self.surface, "back"

        # 2. 更新逻辑
        self._update_keyboard_input()
        
        # 优先键盘，其次摇杆
        kx, ky = self.keyboard_dir
        jx, jy = self.joystick.direction
        
        if abs(kx) > 0.1 or abs(ky) > 0.1:
            dx, dy = kx, ky
        else:
            dx, dy = jx, jy
            
        self.player.update(dx, dy, pygame.time.get_ticks())

        # 3. 绘制
        self.surface.fill((0, 0, 0))
        self.surface.blit(ASSETS['background'], (0, 0))
        self.player.draw(self.surface)
        self.joystick.draw(self.surface)
        self.buttons.draw(self.surface)

        return self.surface, None


# ==========================================
# 4. 兼容 main.py 的导出接口
# ==========================================
_session = GameplaySession()

def gameplay(events):
    """保持与原 main.py 完全兼容的接口"""
    return _session.process(events)