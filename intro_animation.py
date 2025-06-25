# intro_animation.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')
import pygame
import sys
import os
import time

# 设置窗口尺寸
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("传说之下-劫后余生")

# 路径设置
base_folder = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
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


def play():
    # 资源加载
    first_image, images, audio = load_resources()
    current_image_index = 0
    last_change_time = time.time()

    image_intervals = {
        "img1_to_img2": 4.0,
        "img2_to_img3": 0.75,
        "img3_to_img4": 0.65
    }

    running = True
    all_images_shown = False
    end_time = None  # 记录所有图片显示完成的时间
    resources_released = False  # 记录资源是否已释放

    try:
        # 显示初始图片
        screen.blit(first_image, (0, 0))
        pygame.display.flip()
        first_image = None  # 释放初始图片资源
        time.sleep(2)

        # 播放音频
        audio.play()
        start_time = time.time()

        while running:
            current_time = time.time()
            elapsed = current_time - start_time

            # 事件处理 - 用户退出检测
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 图像切换逻辑
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
                    # 所有图片已显示完毕
                    all_images_shown = True
                    end_time = time.time()  # 记录所有图片显示完成的时间

            # 渲染逻辑
            screen.fill((0, 0, 0))  # 先填充黑色背景
            
            if all_images_shown:
                # 检查是否已经过了5秒
                if current_time - end_time > 5.0:
                    # 释放资源（只执行一次）
                    if not resources_released:
                        images = None  # 释放图片资源
                        audio.stop()  # 停止音频
                        resources_released = True
                        return True
                else:
                    # 显示所有图片（叠加效果）
                    for i in range(len(images)):
                        screen.blit(images[i], (0, 0))
            else:
                for i in range(current_image_index + 1):
                    screen.blit(images[i], (0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(60)

    except KeyboardInterrupt:
        print("程序结束。")
        sys.exit()
        pygame.quit()

    except Exception as e:
        print("你的程序貌似出现了一点问题，程序终止！这是错误问题："+e)
        sys.exit()
        pygame.quit()
    finally:
        images = None
        audio.stop()
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    data = play()
    print(data)
    # sys.exit()
    # pygame.quit()