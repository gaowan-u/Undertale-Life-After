import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
import pygame
import sys
import os
import time

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 设置窗口尺寸
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("传说之下-劫后余生")

# 路径设置
base_folder = "/storage/emulated/0/传说之下-劫后余生"
image_folder = os.path.join(base_folder, "images")
audio_folder = os.path.join(base_folder, "audios")
audio_file = "begin.ogg"

# 所有背景图（1~4）
image_files = [
    "background_1.png",
    "background_2.png",
    "background_3.png",
    "background_4.png"
]

# 加载资源
def load_resources():
    # 加载第0张图片（单独显示）
    first_image_path = os.path.join(image_folder, "background_0.jpg")
    if not os.path.exists(first_image_path):
        print(f"错误: 缺少初始图片: {first_image_path}")
        sys.exit(1)

    try:
        first_image = pygame.image.load(first_image_path)
        first_image = pygame.transform.scale(first_image, (screen_width, screen_height))
    except pygame.error:
        print(f"错误: 无法加载初始图片: {first_image_path}")
        sys.exit(1)

    # 加载其余图片
    images = []
    for img_file in image_files:
        path = os.path.join(image_folder, img_file)
        if not os.path.exists(path):
            print(f"错误: 图片文件不存在: {path}")
            sys.exit(1)
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (screen_width, screen_height))
            images.append(img)
        except pygame.error:
            print(f"错误: 无法加载图片: {path}")
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

    return first_image, images, sound

# 资源加载
first_image, images, audio = load_resources()
current_image_index = 0
last_change_time = time.time()

# 每张图片显示的时长（单位：秒）
image_intervals = {
    "img1_to_img2": 4.0,
    "img2_to_img3": 0.75,
    "img3_to_img4": 0.65
}

# 主循环开始
running = True
try:
    # step 1：先显示第0张图片（1秒）
    screen.blit(first_image, (0, 0))
    pygame.display.flip()
    time.sleep(2)  # 停留2秒

    # step 2：播放音频并开始切图逻辑
    audio.play()
    start_time = time.time()

    while running:
        current_time = time.time()
        elapsed = current_time - start_time

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 图像切换逻辑
        if current_image_index < len(images) - 1:
            if current_image_index == 0:
                interval = image_intervals["img1_to_img2"]
            elif current_image_index == 1:
                interval = image_intervals["img2_to_img3"]
            elif current_image_index == 2:
                interval = image_intervals["img3_to_img4"]
            else:
                interval = 1.0

            if current_time - last_change_time > interval:
                current_image_index += 1
                last_change_time = current_time

        # 渲染所有已切换的图片
        screen.fill((0, 0, 0))
        for i in range(current_image_index + 1):
            screen.blit(images[i], (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

except KeyboardInterrupt:
    print("\n程序终止（Ctrl+C）")
finally:
    pygame.quit()
    sys.exit()
