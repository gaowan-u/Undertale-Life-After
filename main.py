import pygame
import sys
import os
import time

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 初始化音频系统

# 设置窗口尺寸
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("传说之下-劫后余生")

# 图片路径
image_folder = "/storage/emulated/0/传说之下-劫后余生/images"
image_files = [
    "background_1.png",
    "background_2.png",
    "background_3.png",
    "background_4.png"
]

# 音频路径 - 只加载一个8秒音频
audio_folder = "/storage/emulated/0/传说之下-劫后余生/audios"
audio_file = "begin.ogg"  # 8秒音频

# 加载资源函数
def load_resources():
    """加载所有图片和音频，检查是否存在"""
    # 加载图片
    images = []
    for img_file in image_files:
        path = os.path.join(image_folder, img_file)
        if not os.path.exists(path):
            print(f"错误: 图片文件不存在: {path}")
            sys.exit(1)
        
        try:
            img = pygame.image.load(path)
            if img.get_width() != screen_width or img.get_height() != screen_height:
                print(f"警告: 图片尺寸不匹配: {img_file} ({img.get_width()}x{img.get_height()})")
            images.append(img)
        except pygame.error:
            print(f"错误: 无法加载图片: {path}")
            sys.exit(1)
    
    if not images:
        print("错误: 没有找到可加载的图片")
        sys.exit(1)
    
    # 加载音频
    audio_path = os.path.join(audio_folder, audio_file)
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)
    
    try:
        sound = pygame.mixer.Sound(audio_path)
    except pygame.error:
        print(f"错误: 无法加载音频: {audio_path}")
        sys.exit(1)
    
    return images, sound

# 加载资源
images, audio = load_resources()
current_image_index = 0
last_change_time = time.time()

# 可调整的图片切换间隔（秒）
# 你可以根据需要调整这些值
image_intervals = {
    "img1_to_img2": 2.5,   # 第一张图片持续时间（2秒）
    "img2_to_img3": 0.3,   # 第二张图片持续时间（0.5秒）
    "img3_to_img4": 0.3  # 第三张图片持续时间（1秒）
}

# 主循环
running = True
try:
    # 初始播放音频
    audio.play()
    start_time = time.time()  # 记录开始时间
    
    while running:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 切换图片逻辑
        if current_image_index < len(images) - 1:
            # 根据当前图片索引确定切换间隔
            if current_image_index == 0:
                interval = image_intervals["img1_to_img2"]
            elif current_image_index == 1:
                interval = image_intervals["img2_to_img3"]
            elif current_image_index == 2:
                interval = image_intervals["img3_to_img4"]
            else:
                interval = 1.0  # 默认值
            
            # 检查是否需要切换到下一张图片
            if current_time - last_change_time > interval:
                # 切换到下一张图片
                current_image_index += 1
                last_change_time = current_time
        
        # 清屏
        screen.fill((0, 0, 0))
        
        # 叠加显示所有图片（从第一张到当前索引）
        for i in range(current_image_index + 1):
            screen.blit(images[i], (0, 0))
        
        # 更新显示
        pygame.display.flip()
        
        # 控制帧率
        pygame.time.Clock().tick(60)

except KeyboardInterrupt:
    print("\n程序结束 (Ctrl+C)")

finally:
    # 退出Pygame
    pygame.quit()
    sys.exit()