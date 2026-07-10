import json
import os
from typing import List, Tuple

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
BOUNDARY_FILE = os.path.join(DATA_FOLDER, "map_boundary.json")

_boundary_polygon: List[Tuple[float, float]] = []


def _load_boundary() -> List[Tuple[float, float]]:
    with open(BOUNDARY_FILE, "r") as f:
        data = json.load(f)
    return [(p["x"], p["y"]) for p in data["boundary_points"]]


def get_boundary() -> List[Tuple[float, float]]:
    global _boundary_polygon
    if not _boundary_polygon:
        _boundary_polygon = _load_boundary()
    return _boundary_polygon


def is_point_inside(x: float, y: float, polygon: List[Tuple[float, float]] = None) -> bool:
    if polygon is None:
        polygon = get_boundary()
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside
