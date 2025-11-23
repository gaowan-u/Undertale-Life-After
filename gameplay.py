import pygame
from intro_animation import screen_height, screen_width
import math

# --- 1. 资源加载  ---
try:
    IMAGE_ASSETS = {
        'background': pygame.image.load("./images/出生点.png"),
        'cropped_joystick_base': pygame.image.load("./images/cropped_joystick_base.png"),
        'cropped_joystick_top': pygame.image.load("./images/cropped_joystick_top.png"),
        'cropped_button_1': pygame.image.load("./images/cropped_button_1.png"),
        'cropped_button_2': pygame.image.load("./images/cropped_button_2.png"),
        'cropped_button_3': pygame.image.load("./images/cropped_button_3.png"),
        'feedback_button_1': pygame.image.load("./images/feedback_button_1.png"),
        'feedback_button_2': pygame.image.load("./images/feedback_button_2.png"),
        'feedback_button_3': pygame.image.load("./images/feedback_button_3.png"),
        'frisk_stand_down': pygame.image.load("./images/Frisk_立正.png"),
        'frisk_walk_down_r': pygame.image.load("./images/Frisk_右脚抬.png"),
        'frisk_walk_down_l': pygame.image.load("./images/Frisk_左脚抬.png"),
        'frisk_stand_up': pygame.image.load("./images/Frisk_背着立正.png"),
        'frisk_walk_up_r': pygame.image.load("./images/Frisk_背部右脚抬.png"),
        'frisk_walk_up_l': pygame.image.load("./images/Frisk_背部左脚抬.png"),
        'frisk_stand_left': pygame.image.load("./images/Frisk_左转立正.png"),
        'frisk_walk_left': pygame.image.load("./images/Frisk_左脚走路.png"),
        'frisk_stand_right': pygame.image.load("./images/Frisk_右转立正.png"),
        'frisk_walk_right': pygame.image.load("./images/Frisk_右脚走路.png"),
    }
except pygame.error as e:
    print(f"致命错误: 加载图片资源失败: {e}")
    IMAGE_ASSETS = {}

# --- 2. 摇杆初始化 ---
gameplay_surface = pygame.Surface((screen_width, screen_height))
joystick_base_img = IMAGE_ASSETS.get('cropped_joystick_base')
joystick_top_img = IMAGE_ASSETS.get('cropped_joystick_top')
if joystick_base_img and joystick_top_img:
    joystick_base_rect = joystick_base_img.get_rect(topleft=(128, screen_height - 240))
    joystick_top_rect = joystick_top_img.get_rect(center=joystick_base_rect.center)
else:
    joystick_base_rect, joystick_top_rect = pygame.Rect(0,0,1,1), pygame.Rect(0,0,1,1)
joystick_dragging = False
joystick_radius = joystick_base_rect.width / 2 * 0.9
joystick_direction = (0, 0)

# --- 3. 玩家状态初始化 ---
player_start_topleft = (862, 561) 
PLAYER_LOGICAL_WIDTH, PLAYER_LOGICAL_HEIGHT = 40, 60 
player_logical_rect = pygame.Rect(0, 0, PLAYER_LOGICAL_WIDTH, PLAYER_LOGICAL_HEIGHT)
player_logical_rect.topleft = player_start_topleft
player_direction = 'down'
player_speed = 25
ANIMATION_FRAME_DURATION = 80

# --- 4. 动画系统初始化 ---
animation_timer, animation_index = 0, 0
ANIMATION_SEQUENCES = {
    'down':  ['frisk_stand_down', 'frisk_walk_down_r', 'frisk_stand_down', 'frisk_walk_down_l'],
    'up':    ['frisk_stand_up', 'frisk_walk_up_r', 'frisk_stand_up', 'frisk_walk_up_l'],
    'left':  ['frisk_stand_left', 'frisk_walk_left', 'frisk_stand_left', 'frisk_walk_left'],
    'right': ['frisk_stand_right', 'frisk_walk_right', 'frisk_stand_right', 'frisk_walk_right']
}

# --- 5. 按钮系统初始化 ---
# 按钮位置和状态
button_1_rect = pygame.Rect(1400, screen_height - 240, IMAGE_ASSETS['cropped_button_1'].get_width(), IMAGE_ASSETS['cropped_button_1'].get_height())
button_2_rect = pygame.Rect(1544, screen_height - 320, IMAGE_ASSETS['cropped_button_2'].get_width(), IMAGE_ASSETS['cropped_button_2'].get_height())
button_3_rect = pygame.Rect(1688, screen_height - 400, IMAGE_ASSETS['cropped_button_3'].get_width(), IMAGE_ASSETS['cropped_button_3'].get_height())

# 按钮状态：0=正常，1=按下
button_1_state = 0
button_2_state = 0  
button_3_state = 0

# 记录按钮是否正在被按下
button_1_pressed = False
button_2_pressed = False  
button_3_pressed = False

# --- 6. 函数定义  ---
def update_joystick_position(mouse_pos):
    global joystick_direction
    dx = mouse_pos[0] - joystick_base_rect.centerx
    dy = mouse_pos[1] - joystick_base_rect.centery
    distance = math.hypot(dx, dy)
    if distance > joystick_radius:
        ratio = joystick_radius / distance
        dx *= ratio
        dy *= ratio
    joystick_top_rect.centerx = joystick_base_rect.centerx + dx
    joystick_top_rect.centery = joystick_base_rect.centery + dy
    joystick_direction = (dx / joystick_radius, dy / joystick_radius) if distance > 10 else (0, 0)

def reset_joystick():
    global joystick_direction
    joystick_top_rect.center = joystick_base_rect.center
    joystick_direction = (0, 0)

def handle_joystick_events(events):
    global joystick_dragging
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if joystick_top_rect.collidepoint(event.pos):
                joystick_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if joystick_dragging:
                joystick_dragging = False
                reset_joystick()

def handle_button_events(events):
    global button_1_state, button_2_state, button_3_state
    global button_1_pressed, button_2_pressed, button_3_pressed
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查哪个按钮被按下
            if button_1_rect.collidepoint(event.pos):
                button_1_state = 1
                button_1_pressed = True
                print("按钮1被按下")  # 调试信息
                
            elif button_2_rect.collidepoint(event.pos):
                button_2_state = 1
                button_2_pressed = True
                print("按钮2被按下")  # 调试信息
                
            elif button_3_rect.collidepoint(event.pos):
                button_3_state = 1
                button_3_pressed = True
                print("按钮3被按下")  # 调试信息

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # 检查哪个按钮被松开
            if button_1_pressed:
                button_1_state = 0
                button_1_pressed = False
                print("按钮1被松开")  # 调试信息
                
            if button_2_pressed:
                button_2_state = 0
                button_2_pressed = False
                print("按钮2被松开")  # 调试信息
                
            if button_3_pressed:
                button_3_state = 0
                button_3_pressed = False
                print("按钮3被松开")  # 调试信息

def update_button_states():
    # 这个函数现在不需要做任何事情，因为状态已经在事件处理中即时更新
    pass

def draw_buttons():
    # 绘制按钮1
    if button_1_state == 0:  # 正常状态
        gameplay_surface.blit(IMAGE_ASSETS['cropped_button_1'], button_1_rect.topleft)
    else:  # 按下状态
        gameplay_surface.blit(IMAGE_ASSETS['feedback_button_1'], button_1_rect.topleft)
    
    # 绘制按钮2
    if button_2_state == 0:  # 正常状态
        gameplay_surface.blit(IMAGE_ASSETS['cropped_button_2'], button_2_rect.topleft)
    else:  # 按下状态
        gameplay_surface.blit(IMAGE_ASSETS['feedback_button_2'], button_2_rect.topleft)
    
    # 绘制按钮3
    if button_3_state == 0:  # 正常状态
        gameplay_surface.blit(IMAGE_ASSETS['cropped_button_3'], button_3_rect.topleft)
    else:  # 按下状态
        gameplay_surface.blit(IMAGE_ASSETS['feedback_button_3'], button_3_rect.topleft)

# --- 7. 主循环逻辑 ---
def gameplay(events):
    global player_direction, animation_timer, animation_index
    
    # 处理输入事件
    handle_joystick_events(events)
    handle_button_events(events)
    
    # 更新状态
    if joystick_dragging:
        update_joystick_position(pygame.mouse.get_pos())
    
    update_button_states()

    # --- 玩家逻辑更新  ---
    dx, dy = joystick_direction
    is_joystick_pushed = abs(dx) > 0.1 or abs(dy) > 0.1

    # <<< 更新朝向（Turn）>>>
    # 只要摇杆被推动（有输入意图），就立刻更新角色朝向。
    if is_joystick_pushed:
        if abs(dx) > abs(dy):
            player_direction = 'right' if dx > 0 else 'left'
        else:
            player_direction = 'down' if dy > 0 else 'up'

    # <<< 更新位移和动画（Move）>>>
    # 只有当摇杆被推动时，才发生位置移动，并播放行走动画。
    if is_joystick_pushed:
        # 移动逻辑盒子
        player_logical_rect.x += dx * player_speed
        player_logical_rect.y += dy * player_speed
        
        # 更新动画计时
        current_time = pygame.time.get_ticks()
        if current_time - animation_timer > ANIMATION_FRAME_DURATION:
            animation_timer = current_time
            animation_index = (animation_index + 1) % len(ANIMATION_SEQUENCES[player_direction])
    else:
        # 如果摇杆没有被推动，则动画重置为站立姿势（第0帧）
        animation_index = 0

    # --- 绘制  ---
    gameplay_surface.blit(IMAGE_ASSETS['background'], (0, 0))
    
    current_sprite_key = ANIMATION_SEQUENCES[player_direction][animation_index]
    current_player_image = IMAGE_ASSETS.get(current_sprite_key)
    if current_player_image:
        visual_rect = current_player_image.get_rect(midbottom=player_logical_rect.midbottom)
        gameplay_surface.blit(current_player_image, visual_rect)
    
    # 绘制UI元素
    gameplay_surface.blit(joystick_base_img, joystick_base_rect)
    draw_buttons()  # 使用新的按钮绘制函数
    gameplay_surface.blit(joystick_top_img, joystick_top_rect)
    
    return gameplay_surface