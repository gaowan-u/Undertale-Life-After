# intro_animation.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
import pygame
import sys
import os
import time

# 窗口尺寸 / Window size
screen_width, screen_height = 1920, 1080

# 路径设置 / Path settings
base_folder = os.path.dirname(os.path.abspath(__file__))
image_folder = os.path.join(base_folder, "images")
audio_folder = os.path.join(base_folder, "audios")
audio_file = "begin.ogg"

# 背景图 / Background images
image_files = [
    "background_1.png",
    "background_2.png",
    "background_3.png",
    "background_4.png"
]

def load_resources():
    # 加载初始图片 / Load initial image
    first_image_path = os.path.join(image_folder, "background_0.jpg")
    if not os.path.exists(first_image_path):
        print(f"错误: 缺少初始图片: {first_image_path}")  # Error: missing initial image
        sys.exit(1)

    try:
        first_image = pygame.image.load(first_image_path)
        first_image = pygame.transform.scale(first_image, (screen_width, screen_height))
    except pygame.error:
        print(f"错误: 无法加载初始图片: {first_image_path}")  # Error: cannot load initial image
        sys.exit(1)

    # 加载其他图片 / Load other images
    images = []
    for img_file in image_files:
        path = os.path.join(image_folder, img_file)
        if not os.path.exists(path):
            print(f"错误: 图片文件不存在: {path}")  # Error: image file does not exist
            sys.exit(1)
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (screen_width, screen_height))
            images.append(img)
        except pygame.error:
            print(f"错误: 无法加载图片: {path}")  # Error: cannot load image
            sys.exit(1)

    # 加载音频 / Load audio
    audio_path = os.path.join(audio_folder, audio_file)
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")  # Error: audio file does not exist
        sys.exit(1)

    try:
        sound = pygame.mixer.Sound(audio_path)
    except pygame.error:
        print(f"错误: 无法加载音频: {audio_path}")  # Error: cannot load audio
        sys.exit(1)

    return first_image, images, sound


def play(screen):  # 添加screen参数
    first_image, images, audio = load_resources()
    current_image_index = 0
    last_change_time = time.time()

    # 图像切换间隔 / Image transition intervals
    image_intervals = {
        "img1_to_img2": 4.0,
        "img2_to_img3": 0.75,
        "img3_to_img4": 0.6
    }

    running = True
    all_images_shown = False
    end_time = 0
    resources_released = False

    try:
        # 显示初始图片 / Show initial image
        screen.blit(first_image, (0, 0))
        pygame.display.flip()
        first_image = None
        time.sleep(2)

        # 播放音频 / Play audio
        audio.play()
        start_time = time.time()

        while running:
            current_time = time.time()
            elapsed = current_time - start_time

            # 事件处理 / Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 图像切换逻辑 / Image switching logic
            if not all_images_shown:
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
                else:
                    all_images_shown = True
                    end_time = time.time()

            # 渲染 / Rendering
            screen.fill((0, 0, 0))
            
            if all_images_shown:
                if current_time - end_time > 5.0:
                    if not resources_released:
                        images = None
                        audio.stop()
                        resources_released = True
                        return True
                else:
                    for i in range(len(images)):
                        screen.blit(images[i], (0, 0))
            else:
                for i in range(current_image_index + 1):
                    screen.blit(images[i], (0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(60)

    except KeyboardInterrupt:
        print("程序结束。")  # Program ended
        sys.exit()
        pygame.quit()

    except Exception as e:
        print("程序错误：", e)  # Program error
        sys.exit()
        pygame.quit()
    finally:
        images = None
        audio.stop()
