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
        zpix_path = os.path.join(FONT_FOLDER, "zpix.ttf")
        dtm_path = os.path.join(FONT_FOLDER, "DTM-Mono.otf")
        bit8_path = os.path.join(FONT_FOLDER, "8bitoperator_jve.ttf")
        determination_path = os.path.join(FONT_FOLDER, "greater-determination-sans.ttf")

        def _load_font(path, size, fallback_name=None):
            try:
                return pygame.font.Font(path, size)
            except (FileNotFoundError, pygame.error) as e:
                print(f"警告: 无法加载字体 {os.path.basename(path)} ({e})，使用系统默认")
                return pygame.font.Font(None, size)

        # 中文像素字体 (Zpix) — 标题 / 菜单 / 通用
        self.title_font = _load_font(zpix_path, 72)
        self.title_font_medium = _load_font(zpix_path, 48)
        self.font_32 = _load_font(zpix_path, 32)
        self.font_36 = _load_font(zpix_path, 36)
        self.font_24 = _load_font(zpix_path, 24)

        # Undertale 风格英文字体 (DTM-Mono) — 对话 / 叙述
        self.dialog_font = _load_font(dtm_path, 48)
        self.dialog_font_small = _load_font(dtm_path, 36)

        # 8bit Operator — 战斗数字 (伤害 / HP)
        self.battle_number_font = _load_font(bit8_path, 48)
        self.battle_number_font_small = _load_font(bit8_path, 36)

        # Determination Sans — 备选 UI 字体
        self.ui_font = _load_font(determination_path, 48)
        self.ui_font_small = _load_font(determination_path, 36)

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
