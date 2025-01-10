from PyQt6.QtCore import QTimer
from functools import wraps
import time, numpy as np


def debounce(wait_ms):
    """防抖装饰器,毫秒"""

    def decorator(fn):
        @wraps(fn)  # 保持原函数签名
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, "_timer"):
                wrapper._timer.stop()
            wrapper._timer = QTimer()
            wrapper._timer.setSingleShot(True)
            wrapper._timer.timeout.connect(lambda: fn(*args, **kwargs))
            wrapper._timer.start(wait_ms)

        return wrapper

    return decorator


def throttle(wait_ms):
    """节流装饰器,毫秒"""

    def decorator(fn):
        @wraps(fn)  # 保持原函数签名
        def wrapper(*args, **kwargs):
            # 创建一个装饰器内部的闭包变量来存储每次调用的时间戳
            if not hasattr(wrapper, "_last_call"):
                # 初始化时让函数能立刻调用
                wrapper._last_call = time.time() - wait_ms / 1e3
            current_time = time.time()
            if current_time - wrapper._last_call >= wait_ms / 1e3:
                fn(*args, **kwargs)
                wrapper._last_call = current_time

        return wrapper

    return decorator


def lttb_downsampled(data: np.ndarray, threshold: int) -> np.ndarray:
    """
    描述:
        lttb算法的python实现

    参数:
        data (np.ndarray): 原始数组[[x,y],[x,y],[x,y]]
        threshold (int): 阈值

    返回值:
        np.ndarray: 仍返回一个numpy数组
    """

    # 小于阈值时直接返回
    if len(data) <= threshold:
        return data

    # Calculate the number of points to skip in the buckets
    n = len(data)
    # 永远包括第一个点
    sampled = [data[0]]
    # lttb算法的bucket数量
    bucket_size = (n - 2) // (threshold - 2)
    # 遍历数据并计算最大的三角形
    for i in range(1, threshold - 1):
        max_area = -1
        max_area_index = 0
        start = i * bucket_size
        # 确保下标不越界
        end = min((i + 1) * bucket_size, n - 1)
        # 循环遍历start,end中的数据
        for j in range(start, end):
            # 计算由点data[i - 1]、data[j] 和 data[i + 1]形成的三角形的面积
            area = area_of_triangle(data[i - 1], data[j], data[i + 1])
            # 更新最大面积和下标
            if area > max_area:
                max_area = area
                max_area_index = j
        # 将面积最大的点添加到采样点列表中
        sampled.append(data[max_area_index])
    # 添加最后一个点
    sampled.append(data[-1])
    return np.array(sampled)


def area_of_triangle(p1, p2, p3):
    """
    计算由 3 个点形成的三角形的面积，使用由点形成的矩阵的行列式。
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) * 0.5
