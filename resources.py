"""
资源管理单例模块
集中管理游戏中所有共享资源：字体、颜色、路径、遮罩层等
"""
import math
import os
import pygame

# 窗口尺寸
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# 路径设置
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
FONT_FOLDER = os.path.join(BASE_FOLDER, "fonts")
IMAGE_FOLDER = os.path.join(BASE_FOLDER, "images")
AUDIO_FOLDER = os.path.join(BASE_FOLDER, "audios")
VIDEO_FOLDER = os.path.join(BASE_FOLDER, "videos")


class Resources:
    """
    资源管理单例类
    集中加载和管理游戏中所有共享资源，避免重复加载
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_resources()
        return cls._instance

    def _init_resources(self):
        """初始化所有资源"""
        self._init_fonts()
        self._init_colors()
        self._init_overlays()
        self._init_menu_items()

    def _init_fonts(self):
        """初始化字体"""
        font_path = os.path.join(FONT_FOLDER, "NotoSansSC-Bold.ttf")
        regular_font_path = os.path.join(FONT_FOLDER, "NotoSansSC-Regular.ttf")

        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.title_font_medium = pygame.font.Font(font_path, 48)
        except (FileNotFoundError, pygame.error):
            print("警告: 无法加载粗体字体，使用系统默认")
            self.title_font = pygame.font.Font(None, 72)
            self.title_font_medium = pygame.font.Font(None, 48)

        try:
            self.font_32 = pygame.font.Font(regular_font_path, 32)
            self.font_36 = pygame.font.Font(regular_font_path, 36)
            self.font_24 = pygame.font.Font(regular_font_path, 24)
        except (FileNotFoundError, pygame.error):
            print("警告: 无法加载常规字体，使用系统默认")
            self.font_32 = pygame.font.Font(None, 32)
            self.font_36 = pygame.font.Font(None, 36)
            self.font_24 = pygame.font.Font(None, 24)

    def _init_colors(self):
        """初始化颜色常量"""
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (100, 100, 100)

        self.COLOR_YELLOW = (255, 255, 0)
        self.COLOR_RED = (255, 0, 0)
        self.COLOR_BLUE = (0, 120, 255)
        self.COLOR_GREEN = (0, 200, 0)

        self.COLOR_BG_DARK = (35, 35, 45)
        self.COLOR_BG_HOVER = (45, 45, 55)
        self.COLOR_BORDER = (80, 80, 90)

    def _init_overlays(self):
        """初始化遮罩层"""
        # 半透明黑色遮罩（用于菜单背景）
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

        # 渐变遮罩（用于存档菜单）
        self.gradient_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            alpha = int(180 * (y / SCREEN_HEIGHT))
            pygame.draw.line(self.gradient_overlay, (20, 20, 30, alpha), (0, y), (SCREEN_WIDTH, y))

    def _init_menu_items(self):
        """初始化菜单项"""
        # 主菜单项
        self.main_menu_items = ["开始游戏", "加载游戏", "设置", "退出"]
        # 设置菜单项
        self.setting_menu_items = ["音量", "画质", "触控UI", "返回"]

    # ========== 便捷方法 ==========

    def create_heart_surface(self, size=30, color=None):
        """创建灵魂之心 Surface"""
        if color is None:
            color = self.COLOR_RED
        heart_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        points = [
            (size // 2, size), (0, size // 4), (size // 4, 0),
            (size // 2, size // 4), (size * 3 // 4, 0), (size, size // 4)
        ]
        pygame.draw.polygon(heart_surface, color, points)
        return heart_surface

    @staticmethod
    def breathing_offset(speed=0.005, amplitude=5):
        return math.sin(pygame.time.get_ticks() * speed) * amplitude


# 模块级便捷访问
def get_resources():
    """获取 Resources 单例"""
    return Resources()
