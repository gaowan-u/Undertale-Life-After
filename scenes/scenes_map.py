"""玩法类场景。

IntroScene：包装现有 intro_animation 播放器（保留其内部循环，特殊处理）。
DisclaimerScene：版权声明，从 main.py 平移而来。
MapScene：地图场景——阶段一只做薄包装，把 gameplay 模块的会话挂进框架。

对 scenes_menu 的引用使用方法内懒导入，避免循环依赖。
"""
import math
import pygame

from scene_manager import Scene, SceneManager
from resources import Resources, SCREEN_HEIGHT


# ==========================================
# 开场动画
# ==========================================
class IntroScene(Scene):
    """开场动画。intro_animation.play() 有自己的事件循环和 display.flip()，
    按项目经验必须传实际屏幕 surface 而非逻辑 render surface。"""

    def __init__(self, manager: SceneManager, screen: pygame.Surface) -> None:
        super().__init__(manager)
        self._screen = screen
        self._started = False

    def update(self, dt: float) -> None:
        if self._started:
            return
        self._started = True  # play() 内部阻塞直到动画结束，确保只调用一次
        from intro_animation import play
        play(self._screen)
        from scenes.scenes_menu import MainMenuScene
        self.manager.reset(DisclaimerScene(self.manager))


# ==========================================
# 版权声明（自 main.py 平移，逻辑不变）
# ==========================================
_DISCLAIMER_DURATION = 5000
_FADE_IN = 1000
_DISPLAY_END = 4000
_FADE_OUT_START = 4000
_FADE_OUT_DURATION = 1000
_MID_DURATION = 3000
_Y_BASE = SCREEN_HEIGHT - 160
_Y_FADE_IN_OFFSET = 80
_BOUNCE_AMPLITUDE = 5
_FADE_OUT_SLIDE = 100
_LINE_HEIGHT = 32
_SHADOW_OFFSET = 2

_DISCLAIMER_TEXT = [
    "本作品为粉丝创作，非官方授权产品",
    "Undertale™ 是Toby Fox的注册商标",
    "与Undertale开发团队无任何关联",
    "角色版权归原著作权方所有",
    "美术资源遵循CC BY-NC 4.0协议",
]


class DisclaimerScene(Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._start_time = pygame.time.get_ticks()

        font = Resources().font_24
        self._lines = []
        self._shadows = []
        for line in _DISCLAIMER_TEXT:
            text_surf = font.render(line, True, (230, 230, 230))
            shadow_surf = font.render(line, True, (0, 0, 0))
            for surf_list, src in ((self._lines, text_surf), (self._shadows, shadow_surf)):
                alpha_surf = pygame.Surface(src.get_size(), pygame.SRCALPHA)
                alpha_surf.blit(src, (0, 0))
                surf_list.append(alpha_surf)

    def update(self, dt: float) -> None:
        if pygame.time.get_ticks() - self._start_time >= _DISCLAIMER_DURATION:
            from scenes.scenes_menu import MainMenuScene
            self.manager.reset(MainMenuScene(self.manager))

    def draw(self) -> None:
        self.surface.fill((0, 0, 0))
        elapsed = pygame.time.get_ticks() - self._start_time

        if elapsed < _FADE_IN:
            progress = 1 - (1 - elapsed / _FADE_IN) ** 3
            y_pos = SCREEN_HEIGHT + _Y_FADE_IN_OFFSET - \
                (SCREEN_HEIGHT + _Y_FADE_IN_OFFSET - _Y_BASE) * progress
            alpha = int(255 * progress)
        elif elapsed < _DISPLAY_END:
            progress = (elapsed - _FADE_IN) / _MID_DURATION
            y_pos = _Y_BASE + _BOUNCE_AMPLITUDE * math.sin(progress * 2 * math.pi)
            alpha = 255
        else:
            progress = ((elapsed - _FADE_OUT_START) / _FADE_OUT_DURATION) ** 3
            y_pos = _Y_BASE - _FADE_OUT_SLIDE * progress
            alpha = int(255 * (1 - progress))

        y_offset = int(y_pos)
        for text_surf, shadow_surf in zip(self._lines, self._shadows):
            text_surf.set_alpha(alpha)
            shadow_surf.set_alpha(int(alpha * 0.6))
            self.surface.blit(shadow_surf, (20 + _SHADOW_OFFSET, y_offset + _SHADOW_OFFSET))
            self.surface.blit(text_surf, (20, y_offset))
            y_offset += _LINE_HEIGHT


# ==========================================
# 地图场景（阶段一：薄包装）
# ==========================================
class MapScene(Scene):
    """把 gameplay 模块的 GameplaySession 挂进场景框架。

    gameplay() 每帧返回 (surface, status)，阶段一直接 blit 其结果；
    阶段二会把 GameplaySession 泛化为数据驱动的通用地图并取代本包装。
    """

    def __init__(self, manager: SceneManager, save_data: dict | None) -> None:
        super().__init__(manager)
        self._events: list[pygame.event.Event] = []
        self._map_surface = self.surface.copy()
        self._map_surface.fill((0, 0, 0))
        if save_data is not None:
            from gameplay import init_session_from_save
            init_session_from_save(save_data)

    @classmethod
    def new_game(cls, manager: SceneManager) -> "MapScene":
        return cls(manager, None)

    @classmethod
    def from_save(cls, manager: SceneManager, save_data: dict) -> "MapScene":
        return cls(manager, save_data)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        # gameplay() 需要整帧事件列表做输入处理，这里只收集；
        # ESC 返回主菜单在旧版是主循环直接处理的，此处保留该行为
        self._events.extend(events)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
                self._back_to_menu()

    def update(self, dt: float) -> None:
        from gameplay import gameplay
        self._map_surface, status = gameplay(self._events)
        self._events.clear()
        if status == "back":
            self._back_to_menu()
        elif status == "exit":
            # 阶段三实现场景切换；当前先打印占位（与旧行为一致）
            print("[主循环] 收到出口信号 — 场景切换待实现")

    def _back_to_menu(self) -> None:
        from scenes.scenes_menu import MainMenuScene
        self.manager.reset(MainMenuScene(self.manager))

    def draw(self) -> None:
        self.surface.blit(self._map_surface, (0, 0))
