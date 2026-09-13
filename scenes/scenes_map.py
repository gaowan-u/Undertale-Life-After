"""玩法类场景。

IntroScene：包装现有 intro_animation 播放器（保留其内部循环，特殊处理）。
DisclaimerScene：版权声明，从 main.py 平移而来。
MapScene：数据驱动的地图场景——背景/边界/出生点/出口/交互全部读 data/scenes/*.json。

对 scenes_menu 的引用使用方法内懒导入，避免循环依赖。
"""
import json
import math
import os
import pygame
from typing import Dict, Optional

from scene_manager import Scene, SceneManager
from resources import Resources, SCREEN_WIDTH, SCREEN_HEIGHT, AUDIO_FOLDER, SCENES_FOLDER
from gameplay import Player, VirtualJoystick, ActionButtons, load_background, get_touch_ui_visible
from map_boundary import load_boundary
import music

DEFAULT_SCENE = "falling_ruins"

_scene_data_cache: Dict[str, dict] = {}


def load_scene_data(scene_id: str) -> Optional[dict]:
    """加载场景 JSON 定义，带缓存；文件不存在返回 None。"""
    if scene_id in _scene_data_cache:
        return _scene_data_cache[scene_id]
    path = os.path.join(SCENES_FOLDER, f"{scene_id}.json")
    if not os.path.exists(path):
        print(f"[场景] 文件不存在: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _scene_data_cache[scene_id] = data
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[场景] 无法解析 {path}: {e}")
        return None


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
# 地图场景（数据驱动）
# ==========================================
class MapScene(Scene):
    """通用地图场景：一切行为由 data/scenes/{id}.json 描述。

    JSON 字段：
        background   背景图文件名（images/ 下）
        boundary     行走边界文件名（data/ 下，MapBoundaryDetector 生成）
        bgm          背景音乐文件名（audios/ 下，可省略）
        spawn        默认出生点 {x, y, direction}（rect 左上角坐标）
        exits        出口列表 [{rect, dir, target, target_spawn}]
                     rect: [x, y, w, h]；dir: 触发所需移动方向
    """

    def __init__(self, manager: SceneManager, scene_id: str = DEFAULT_SCENE,
                 spawn_override: Optional[dict] = None) -> None:
        super().__init__(manager)

        data = load_scene_data(scene_id)
        if data is None:
            print(f"[场景] 回退到默认场景 {DEFAULT_SCENE}")
            data = load_scene_data(DEFAULT_SCENE)
        if data is None:
            raise RuntimeError("默认场景数据缺失，无法进入游戏")
        self._data = data
        self.scene_id = data.get("id", scene_id)

        self._background = load_background(data["background"])
        self._boundary = load_boundary(data["boundary"])

        spawn = spawn_override or data["spawn"]
        self.player = Player(spawn["x"], spawn["y"], spawn.get("direction", "down"))
        self.joystick = VirtualJoystick()
        self.buttons = ActionButtons()
        self.keyboard_dir = (0.0, 0.0)
        self._events: list[pygame.event.Event] = []

    # --- 工厂方法 ---
    @classmethod
    def new_game(cls, manager: SceneManager) -> "MapScene":
        return cls(manager)

    @classmethod
    def from_save(cls, manager: SceneManager, save_data: dict) -> "MapScene":
        scene_id = save_data.get("progress", {}).get("current_scene") or DEFAULT_SCENE
        pos = save_data.get("position")
        spawn = None
        if pos:
            spawn = {
                "x": pos.get("x", 862),
                "y": pos.get("y", 561),
                "direction": pos.get("direction", "down"),
            }
        return cls(manager, scene_id, spawn_override=spawn)

    # --- 生命周期 ---
    def on_enter(self) -> None:
        bgm = self._data.get("bgm")
        if bgm:
            music.play(os.path.join(AUDIO_FOLDER, bgm))

    # --- 每帧 ---
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self.buttons.reset_states()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
                self._back_to_menu()
                return
            if get_touch_ui_visible():
                self.joystick.handle_event(event)
                self.buttons.handle_event(event)
            else:
                self.buttons.handle_back_event(event)

    def update(self, dt: float) -> None:
        if self.buttons.pressed['back']:
            self._back_to_menu()
            return

        keys = pygame.key.get_pressed()
        self.buttons.update_hold(keys)
        self._update_keyboard_input(keys)

        kx, ky = self.keyboard_dir
        jx, jy = self.joystick.direction if get_touch_ui_visible() else (0.0, 0.0)
        if abs(kx) > 0.1 or abs(ky) > 0.1:
            dx, dy = kx, ky
        else:
            dx, dy = jx, jy

        self.player.update(dx, dy, pygame.time.get_ticks(), self._boundary)
        self._check_exits(dx, dy)

    def draw(self) -> None:
        self.surface.blit(self._background, (0, 0))
        self.player.draw(self.surface)
        if get_touch_ui_visible():
            self.joystick.draw(self.surface)
            self.buttons.draw(self.surface)
        else:
            self.buttons._draw_back_button(self.surface)

    # --- 内部逻辑 ---
    def _update_keyboard_input(self, keys) -> None:
        dx, dy = 0.0, 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1

        if dx == 0 and dy == 0:
            self.keyboard_dir = (0.0, 0.0)
            return

        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
        self.keyboard_dir = (dx, dy)

    def _check_exits(self, dx: float, dy: float) -> None:
        if self.manager.busy:
            return
        for exit_def in self._data.get("exits", []):
            rect = pygame.Rect(exit_def["rect"])
            if not self.player.rect.colliderect(rect):
                continue

            direction = exit_def.get("dir", "right")
            moving_out = (
                (direction == "right" and dx > 0.1) or
                (direction == "left" and dx < -0.1) or
                (direction == "down" and dy > 0.1) or
                (direction == "up" and dy < -0.1)
            )
            if not moving_out:
                continue

            target = exit_def["target"]
            spawn = exit_def.get("target_spawn")
            print(f"[场景] 切换: {self.scene_id} → {target}")
            self.manager.replace(MapScene(self.manager, target, spawn_override=spawn))
            return

    def _back_to_menu(self) -> None:
        from scenes.scenes_menu import MainMenuScene
        self.manager.reset(MainMenuScene(self.manager))
