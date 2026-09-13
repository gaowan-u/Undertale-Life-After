"""地图边界加载与点碰撞检测。

边界 JSON 由 MapBoundaryDetector 工具生成，存放于 data/ 目录。
支持多场景：按文件名加载并缓存多边形。
"""
import json
import os
from typing import Dict, List, Optional, Tuple

from resources import DATA_FOLDER

_boundary_cache: Dict[str, List[Tuple[float, float]]] = {}


def load_boundary(filename: str) -> List[Tuple[float, float]]:
    """按文件名（相对 data/）加载边界多边形，带缓存。"""
    if filename in _boundary_cache:
        return _boundary_cache[filename]

    path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(path):
        print(f"警告: 地图边界文件不存在: {path}")
        _boundary_cache[filename] = []
        return []

    try:
        with open(path, "r") as f:
            data = json.load(f)
        polygon = [(p["x"], p["y"]) for p in data["boundary_points"]]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"错误: 无法解析地图边界文件 {filename}: {e}")
        polygon = []

    _boundary_cache[filename] = polygon
    return polygon


def is_point_inside(x: float, y: float, polygon: Optional[List[Tuple[float, float]]] = None) -> bool:
    """射线法判断点是否在多边形内。polygon 为空时视为无边界（自由行走）。"""
    if polygon is None:
        return True
    inside = False
    n = len(polygon)
    if n < 3:
        return True
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside
