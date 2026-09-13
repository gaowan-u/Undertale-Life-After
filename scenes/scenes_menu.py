"""主菜单类场景：主菜单 / 存档菜单 / 设置。

对 scenes_map 的引用使用方法内懒导入，避免循环依赖。
"""
import os
import pygame

from scene_manager import Scene, SceneManager
from main_menu import MainMenu
from save_menu import SaveMenu
from setting import Setting
from save_system import save_system
from resources import AUDIO_FOLDER
import music


MENU_MUSIC = os.path.join(AUDIO_FOLDER, "menu_music.ogg")


class MenuMusicMixin:
    """菜单类场景共用的 BGM 控制：进入播放，退出停止。
    场景退出时必定 stop，因此进入时直接重新加载播放即可。"""

    def on_enter(self) -> None:
        music.play(MENU_MUSIC)

    def on_exit(self) -> None:
        music.stop()


class MainMenuScene(MenuMusicMixin, Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.menu = MainMenu(self.surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.menu.handle_event(event)
        if action == "start_game":
            from scenes.scenes_map import MapScene
            self.manager.reset(MapScene.new_game(self.manager))
        elif action == "load_game":
            self.manager.push(SaveMenuScene(self.manager))
        elif action == "open_settings":
            self.manager.push(SettingScene(self.manager))
        elif action == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def draw(self) -> None:
        self.surface.fill((0, 0, 0))
        self.menu.draw()


class SaveMenuScene(Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.save_menu = SaveMenu(self.surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.save_menu.handle_event(event)
        if action == "back":
            self.manager.pop()
        elif action == "load_save":
            loaded = save_system.load_save(self.save_menu.selected_slot)
            if loaded:
                from scenes.scenes_map import MapScene
                self.manager.reset(MapScene.from_save(self.manager, loaded))
            else:
                print("存档加载失败")
        # save_deleted / delete_error / save_error：留在本界面，无需处理

    def draw(self) -> None:
        self.save_menu.draw()


class SettingScene(Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.setting = Setting(self.surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.setting.handle_event(event)
        if action == "toggle_touch_ui":
            from gameplay import get_touch_ui_visible, set_touch_ui_visible
            set_touch_ui_visible(not get_touch_ui_visible())
        elif action == "back":
            self.manager.pop()
        # "volume"/"quality" 暂未实现，忽略

    def draw(self) -> None:
        self.setting.draw()
