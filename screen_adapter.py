"""
屏幕适配模块
将所有游戏内容渲染到 1920×1080 的逻辑 surface，
再按宽高比缩放到实际窗口，不足部分留黑边。
提供鼠标坐标转换功能，使碰撞箱始终基于逻辑坐标。
"""
import pygame
from resources import SCREEN_WIDTH, SCREEN_HEIGHT

_scale: float = 1.0
_offset_x: int = 0
_offset_y: int = 0

_render_surface: pygame.Surface | None = None


def get_render_surface() -> pygame.Surface:
    global _render_surface
    if _render_surface is None:
        _render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    return _render_surface


def recreate(display_surface: pygame.Surface) -> None:
    """在 display 初始化后调用，用匹配的像素格式重建 render surface"""
    global _render_surface
    _render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    update(display_surface.get_size())


def update(display_size: tuple[int, int]) -> None:
    """根据当前窗口大小更新缩放比例和偏移量"""
    global _scale, _offset_x, _offset_y
    w, h = display_size
    scale = min(w / SCREEN_WIDTH, h / SCREEN_HEIGHT)
    _scale = scale
    _offset_x = round((w - SCREEN_WIDTH * scale) / 2)
    _offset_y = round((h - SCREEN_HEIGHT * scale) / 2)


def to_logical(screen_pos: tuple[int, int]) -> tuple[float, float]:
    """将屏幕坐标转换为逻辑坐标 (1920×1080 空间)"""
    x = (screen_pos[0] - _offset_x) / _scale
    y = (screen_pos[1] - _offset_y) / _scale
    return (x, y)


def get_logical_mouse_pos() -> tuple[float, float]:
    """获取当前鼠标在逻辑坐标中的位置"""
    return to_logical(pygame.mouse.get_pos())


def render_to_screen(screen: pygame.Surface) -> None:
    """将逻辑 surface 按比例缩放到屏幕，不足补黑边"""
    w, h = screen.get_size()
    render_surf = get_render_surface()

    scaled_w = round(SCREEN_WIDTH * _scale)
    scaled_h = round(SCREEN_HEIGHT * _scale)

    screen.fill((0, 0, 0))

    if _scale == 1.0:
        screen.blit(render_surf, (_offset_x, _offset_y))
    else:
        scaled = pygame.transform.scale(render_surf, (scaled_w, scaled_h))
        screen.blit(scaled, (_offset_x, _offset_y))
