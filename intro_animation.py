# intro_animation.py
from typing import List, Optional
import pygame
import sys
import os
import time
from resources import SCREEN_WIDTH, SCREEN_HEIGHT, IMAGE_FOLDER, AUDIO_FOLDER

# 音频文件名
audio_file = "begin.ogg"

# 背景图 / Background images
image_files = [
    "background_1.png",
    "background_2.png",
    "background_3.png",
    "background_4.png"
]

# 模块级缓存，避免每帧重新读取文件
_cached_first_image: Optional[pygame.Surface] = None
_cached_images: Optional[List[pygame.Surface]] = None
_cached_sound: Optional[pygame.mixer.Sound] = None
_cached_audio_available: bool = False
_cached = False

def _load_resources() -> None:
    global _cached_first_image, _cached_images, _cached_sound, _cached_audio_available, _cached
    if _cached:
        return

    first_image_path = os.path.join(IMAGE_FOLDER, "background_0.jpg")
    if not os.path.exists(first_image_path):
        print(f"错误: 缺少初始图片: {first_image_path}")
        sys.exit(1)

    try:
        _cached_first_image = pygame.image.load(first_image_path)
        _cached_first_image = pygame.transform.scale(_cached_first_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        print(f"错误: 无法加载初始图片: {first_image_path}")
        sys.exit(1)

    _cached_images = []
    for img_file in image_files:
        path = os.path.join(IMAGE_FOLDER, img_file)
        if not os.path.exists(path):
            print(f"错误: 图片文件不存在: {path}")
            sys.exit(1)
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            _cached_images.append(img)
        except pygame.error:
            print(f"错误: 无法加载图片: {path}")
            sys.exit(1)

    audio_path = os.path.join(AUDIO_FOLDER, audio_file)
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)

    try:
        _cached_sound = pygame.mixer.Sound(audio_path)
        _cached_audio_available = True
    except pygame.error:
        print(f"警告: 无法加载音频: {audio_path}，将在静音模式下播放开场动画")
        _cached_sound = None
        _cached_audio_available = False

    _cached = True


def play(screen):
    _load_resources()
    first_image = _cached_first_image
    images = _cached_images
    audio = _cached_sound
    audio_available = _cached_audio_available

    current_image_index = 0
    last_change_time = time.time()

    image_intervals = {
        "img1_to_img2": 4.0,
        "img2_to_img3": 0.75,
        "img3_to_img4": 0.6
    }

    running = True
    all_images_shown = False
    end_time = 0
    skipped = False
    clock = pygame.time.Clock()

    try:
        screen.blit(first_image, (0, 0))
        pygame.display.flip()
        time.sleep(2)

        if audio_available and audio:
            audio.play()

        while running:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        skipped = True
                        break

            if skipped:
                break

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

            screen.fill((0, 0, 0))
            for i in range(current_image_index + 1):
                screen.blit(images[i], (0, 0))

            if all_images_shown and current_time - end_time > 5.0:
                if audio_available and audio:
                    audio.stop()
                return True

            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        print("程序结束。")
        pygame.quit()
        sys.exit()

    except Exception as e:
        print("程序错误：", e)
        pygame.quit()
        sys.exit()
    finally:
        if audio:
            audio.stop()

    if skipped:
        return True
    return False
