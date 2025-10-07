import pygame
from intro_animation import screen_height, screen_width
import math
gameplay_surface = pygame.Surface((screen_width, screen_height))


def resource():
    paths = {
        'background': "./images/出生点.png",
        'attention': "./images/Frisk_立正.png",
        'right_up': "./images/Frisk_右脚抬.png",
        'left_up': "./images/Frisk_左脚抬.png",
        'turn_left': "./images/Frisk_左转立正.png",
        'left_walk': "./images/Frisk_左脚走路.png",
        'turn_right': "./images/Frisk_右转立正.png",
        'right_walk': "./images/Frisk_右脚走路.png",
        'cropped_joystick_base': "./images/cropped_joystick_base.png",
        'cropped_joystick_top': "./images/cropped_joystick_top.png",
        'cropped_button_1': "./images/cropped_button_1.png",
        'cropped_button_2': "./images/cropped_button_2.png",
        'cropped_button_3': "./images/cropped_button_3.png"
    }
    return {key: pygame.image.load(path) for key, path in paths.items()}

# 使用时通过键名访问，如：images['background']

def gameplay(events):
    images = resource()
    gameplay_surface.blits([
        (images['background'], (0, 0)),
        (images['attention'], (832, 492)),
        (images['cropped_joystick_base'], (128, 720)),
        (images['cropped_joystick_top'], (208, 800)),
        (images['cropped_button_1'], (1400, 840)),
        (images['cropped_button_2'], (1544, 760)),
        (images['cropped_button_3'], (1688, 680))
    ])
    return gameplay_surface

