"""背景音乐管理：记录当前曲目，同名曲目在场景切换时不重播，避免音乐断续。"""
import pygame

_current: str | None = None


def _available() -> bool:
    """mixer 未初始化（如 --mute 静音启动）时静默跳过，不刷警告。"""
    return pygame.mixer.get_init() is not None


def play(path: str) -> None:
    """循环播放指定音乐。若与当前曲目相同则什么都不做。"""
    global _current
    if not _available() or _current == path:
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
        _current = path
    except pygame.error as e:
        print(f"警告：无法播放音乐：{path} ({e})")


def stop() -> None:
    global _current
    if not _available():
        _current = None
        return
    pygame.mixer.music.stop()
    _current = None
