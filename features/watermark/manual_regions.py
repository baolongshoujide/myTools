"""Validate normalized manual selections independently of the AI runtime."""
import math


def validate_regions(regions):
    if not isinstance(regions, list) or not 1 <= len(regions) <= 20:
        raise ValueError("请圈选1到20处需要修复的区域")
    result = []
    for region in regions:
        if not isinstance(region, dict):
            raise ValueError("选区格式不正确，请重新圈选")
        values = [region.get(key) for key in ("x", "y", "width", "height")]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
            raise ValueError("选区坐标无效，请重新圈选")
        x, y, width, height = values
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1.000001 or y + height > 1.000001:
            raise ValueError("选区超出图片范围，请重新圈选")
        result.append({"x": x, "y": y, "width": width, "height": height})
    return result


def region_boxes(regions, width, height):
    boxes = []
    for region in validate_regions(regions):
        left = math.floor(region["x"] * width)
        top = math.floor(region["y"] * height)
        right = math.ceil((region["x"] + region["width"]) * width)
        bottom = math.ceil((region["y"] + region["height"]) * height)
        if right - left < 2 or bottom - top < 2:
            raise ValueError("选区太小，请稍微扩大后重试")
        # Cover anti-aliased edges around the selected watermark.
        boxes.append([max(0, left - 3), max(0, top - 3), min(width, right + 3), min(height, bottom + 3)])
    return boxes
