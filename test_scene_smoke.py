"""无头冒烟测试：验证场景框架的核心流转。

模拟主循环帧（不真开窗口，SDL dummy 驱动）：
开场→声明→主菜单→设置→存档菜单→玩法→回主菜单
"""
import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
# dummy 驱动下 display 未开也可能无法 convert，开个最小窗口
screen = pygame.display.set_mode((1920, 1080))

from scene_manager import SceneManager
from scenes.scenes_map import DisclaimerScene, MapScene
from scenes.scenes_menu import MainMenuScene, SettingScene, SaveMenuScene
from gameplay import init_assets

passed = []
failed = []


def check(name, cond):
    (passed if cond else failed).append(name)
    print(("PASS" if cond else "FAIL"), name)


init_assets()

manager = SceneManager()

# 1. 启动主菜单（跳过开场动画，intro 需要真实循环）
manager.start(MainMenuScene(manager))
check("启动进入主菜单", isinstance(manager.current, MainMenuScene))

# 2. 模拟跑几帧（无事件）
for _ in range(5):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("主菜单跑5帧无异常", True)

# 3. 打开设置（push）→ 返回（pop）
manager.push(SettingScene(manager))
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("push 设置场景", isinstance(manager.current, SettingScene))
manager.pop()
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("pop 回主菜单", isinstance(manager.current, MainMenuScene))

# 4. 存档菜单 push/pop
manager.push(SaveMenuScene(manager))
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("push 存档菜单", isinstance(manager.current, SaveMenuScene))
manager.pop()
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("pop 回主菜单", isinstance(manager.current, MainMenuScene))

# 5. 开始游戏 → 地图场景
from scenes.scenes_map import MapScene
manager.reset(MapScene.new_game(manager))
for _ in range(5):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("进入地图场景", isinstance(manager.current, MapScene))

# 6. 地图场景返回主菜单（模拟 gameplay 返回 "back" 不易构造，用 ESC 事件）
manager.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("ESC 回主菜单", isinstance(manager.current, MainMenuScene))

# 7. 免责声明场景计时结束自动切换
manager.reset(DisclaimerScene(manager))
# 等过 5 秒时长
pygame.time.wait(0)
d = manager.current
d._start_time -= 6000  # 直接改起始时间模拟超时
manager.update()
for _ in range(3):
    manager.handle_events([])
    manager.update()
    manager.draw()
check("声明结束回主菜单", isinstance(manager.current, MainMenuScene))

# 8. 过渡期间输入冻结
from scene_manager import Scene

class DummyScene(Scene):
    def __init__(self, m):
        super().__init__(m)
        self.got = False
    def handle_event(self, e):
        self.got = True

manager.reset(DummyScene(manager))
old_scene = manager.current
manager._begin_transition("push", DummyScene(manager), True)
manager.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)])
check("过渡期间事件冻结", not old_scene.got)
# 跑完过渡（FADE_MS=300，需真实时间流逝）
for _ in range(100):
    pygame.time.wait(10)
    manager.handle_events([])
    manager.update()
    manager.draw()
check("过渡结束恢复 idle", not manager.busy)
check("过渡后到达新场景", isinstance(manager.current, DummyScene))

# 9. quit 清栈
manager.quit()
check("quit 后栈空", manager.current is None)

print()
print(f"=== {len(passed)} passed, {len(failed)} failed ===")
sys.exit(1 if failed else 0)
