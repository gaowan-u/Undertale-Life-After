"""
场景管理器
提供 Scene 基类 + 场景栈（push/pop/replace）+ 黑屏过渡效果。
所有场景（主菜单、地图、对话、战斗）继承 Scene，由 SceneManager 统一调度。

设计要点：
- 场景栈：对话/战斗可 push 覆盖在地图上，pop 后回到地图，地图无需感知覆盖层的存在
- 过渡：replace/push 时黑屏淡出→切换→淡入，资源加载藏在黑屏后面
- 事件传播：事件只发给栈顶场景；栈顶可完全吞掉（对话打开时地图收不到键盘）
"""
from typing import List, Optional
import pygame

from screen_adapter import get_render_surface

SCREEN_W_FALLBACK = 1920
SCREEN_H_FALLBACK = 1080


class Scene:
    """场景基类。子类按需覆写钩子。"""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager
        # 逻辑 surface（1920×1080），所有绘制都画到这里
        self.surface = get_render_surface()

    # --- 生命周期 ---
    def on_enter(self) -> None:
        """进入场景时调用（过渡黑屏期间，可安全做资源加载）。"""

    def on_exit(self) -> None:
        """离开场景时调用。"""

    # --- 每帧 ---
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理单个事件。"""

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """批量事件入口。默认逐个转发 handle_event；
        需要完整事件列表的场景（如 gameplay）覆写此方法。"""
        for event in events:
            self.handle_event(event)

    def update(self, dt: float) -> None:
        """逻辑更新。dt 为距上帧秒数。"""

    def draw(self) -> None:
        """绘制到 self.surface。"""


class SceneManager:
    """场景栈管理器 + 过渡状态机。

    过渡分三阶段：fade_out（黑屏渐浓）→ 切换场景 → fade_in（黑屏渐淡）。
    过渡期间旧场景已停止接收事件/更新，但最后一帧画面保留在底层。
    """

    FADE_MS = 300  # 单向淡入/淡出时长

    def __init__(self) -> None:
        self._stack: List[Scene] = []
        self._pending: Optional[tuple] = None  # (op, scene_factory)
        self._fade_start: int = 0
        self._phase: str = "idle"  # idle / fade_out / fade_in
        self._switching_base: bool = False  # replace 时是否弹出旧场景

    # --- 栈操作 ---

    @property
    def current(self) -> Optional[Scene]:
        return self._stack[-1] if self._stack else None

    def start(self, scene: Scene) -> None:
        """启动第一个场景（无过渡）。"""
        self._stack = [scene]
        scene.on_enter()

    def push(self, scene: Scene, fade: bool = False) -> None:
        """叠加场景（对话/战斗覆盖层）。fade=True 时带黑屏过渡。"""
        self._begin_transition("push", scene, fade)

    def pop(self, fade: bool = False) -> None:
        """移除栈顶场景。"""
        self._begin_transition("pop", None, fade)

    def replace(self, scene: Scene, fade: bool = True) -> None:
        """替换栈顶场景（关卡切换）。默认带黑屏过渡。"""
        self._begin_transition("replace", scene, fade)

    def reset(self, scene: Scene, fade: bool = False) -> None:
        """清空场景栈并进入新场景（回主菜单 / 开始游戏）。"""
        self._begin_transition("reset", scene, fade)

    def _begin_transition(self, op: str, scene, fade: bool) -> None:
        if self._phase != "idle":
            # 已在过渡中：忽略重复请求（防止出口区反复触发）
            return
        if not fade:
            self._do_switch(op, scene)
            return
        self._pending = (op, scene)
        self._fade_start = pygame.time.get_ticks()
        self._phase = "fade_out"

    def _do_switch(self, op: str, scene) -> None:
        if op == "pop":
            popped = self._stack.pop()
            popped.on_exit()
        elif op == "push":
            scene.on_enter()
            self._stack.append(scene)
        elif op == "replace":
            popped = self._stack.pop()
            popped.on_exit()
            scene.on_enter()
            self._stack.append(scene)
        elif op == "reset":
            while self._stack:
                self._stack.pop().on_exit()
            scene.on_enter()
            self._stack.append(scene)

    # --- 每帧调度 ---

    @property
    def busy(self) -> bool:
        """过渡进行中（此时不应接受场景切换请求）。"""
        return self._phase != "idle"

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """把事件交给栈顶场景。过渡期间冻结输入。"""
        if self._phase != "idle" or not self._stack:
            return
        self._stack[-1].handle_events(events)

    def update(self) -> None:
        """推进过渡状态机和栈顶场景逻辑。"""
        now = pygame.time.get_ticks()
        if self._phase == "fade_out":
            if now - self._fade_start >= self.FADE_MS:
                op, scene = self._pending
                self._pending = None
                self._do_switch(op, scene)
                self._fade_start = now
                self._phase = "fade_in"
            return  # 过渡期间栈顶场景不更新
        elif self._phase == "fade_in":
            if now - self._fade_start >= self.FADE_MS:
                self._phase = "idle"

        if self._stack:
            self._stack[-1].update(_frame_dt())

    def draw(self) -> None:
        """绘制场景栈 + 过渡黑罩。"""
        if not self._stack:
            return
        top = self._stack[-1]
        # 栈底到栈顶依次绘制（覆盖层叠在下面场景之上）
        for scene in self._stack:
            scene.draw()

        # 过渡黑罩（画到栈顶场景的 surface 上）
        if self._phase != "idle":
            elapsed = pygame.time.get_ticks() - self._fade_start
            if self._phase == "fade_out":
                alpha = int(255 * min(elapsed / self.FADE_MS, 1.0))
            else:
                alpha = int(255 * max(1.0 - elapsed / self.FADE_MS, 0.0))
            overlay = pygame.Surface(top.surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            top.surface.blit(overlay, (0, 0))

    def quit(self) -> None:
        """依次退出所有场景。"""
        while self._stack:
            self._stack.pop().on_exit()


# --- 帧时间 ---

_last_ticks: int = 0


def _frame_dt() -> float:
    """距上帧秒数（上限 0.1s 防卡顿跳变）。"""
    global _last_ticks
    now = pygame.time.get_ticks()
    if _last_ticks == 0:
        _last_ticks = now
        return 0.0
    dt = (now - _last_ticks) / 1000.0
    _last_ticks = now
    return min(dt, 0.1)
