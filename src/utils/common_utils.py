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


def getSamplingMethod(sampling: str):
    match sampling:
        case "lttb":
            return lttbDownsampled
        case "average":
            return averageDownsampled
        case "min":
            return minDownsampled
        case "max":
            return maxDownsampled
        case _:
            return noneDownsampled


def lttbDownsampled(data: np.ndarray, nout: int) -> np.ndarray:
    """
    描述:
        lttb算法的python实现

    参数:
        data (np.ndarray): 原始数组[[x,y],[x,y],[x,y]]
        nout (int): 降采样后的数据点数

    返回值:
        np.ndarray: 降采样后的数据
    """
    # 小于nout和3时直接返回
    if len(data) <= nout or len(data) < 3:
        return data

    n = len(data)
    sampled = [data[0]]  # 永远包括第一个点

    # 每个bucket的大小 (整数)
    bucket_size = (n - 2) // (nout - 2)
    # 剩余点数用于调整最后几个bucket
    leftover = (n - 2) % (nout - 2)
    current_bucket_start = 1

    for i in range(1, nout - 1):
        # 根据剩余点数调整每个bucket的end
        bucket_end = current_bucket_start + bucket_size - 1
        if i <= leftover:
            # 分配剩余点数
            bucket_end += 1

        # 确保不越界
        bucket_end = min(bucket_end, n - 2)

        max_area = -1
        max_area_index = current_bucket_start

        # 遍历bucket内的点，寻找面积最大的点
        for j in range(current_bucket_start, bucket_end + 1):
            # 计算三角形面积
            x1, y1 = sampled[i - 1]
            x2, y2 = data[j]
            x3, y3 = data[bucket_end + 1]
            area = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) * 0.5
            if area > max_area:
                max_area = area
                max_area_index = j

        sampled.append(data[max_area_index])
        current_bucket_start = bucket_end + 1

    # 添加最后一个点
    sampled.append(data[-1])
    return np.array(sampled)


def averageDownsampled(data: np.ndarray, nout: int) -> np.ndarray:
    """
    描述:
        平均采样算法,对数据进行平均值降采样

    参数:
        data (np.ndarray): 原始数据
        nout (int): 降采样后的数据点数

    返回值
        np.ndarray: 降采样后的数据
    """
    if len(data) <= nout:
        # 如果数据点数少于或等于阈值，无需降采样
        return data
    # 使用 np.array_split 均匀分组
    groups = np.array_split(data, nout)
    # 对每一组计算平均值
    downsampledData = np.array([np.mean(group, axis=0) for group in groups])
    return downsampledData


def minDownsampled(data: np.ndarray, nout: int) -> np.ndarray:
    if len(data) <= nout:
        # 如果数据点数少于或等于阈值，无需降采样
        return data
    # 使用 np.array_split 均匀分组
    groups = np.array_split(data, nout)
    downsampledData = []
    for group in groups:
        index = np.argmin(group[:, 1])
        point = group[index]
        downsampledData.append(point)
    return np.array(downsampledData)


def maxDownsampled(data: np.ndarray, nout: int) -> np.ndarray:
    if len(data) <= nout:
        # 如果数据点数少于或等于阈值，无需降采样
        return data
    # 使用 np.array_split 均匀分组
    groups = np.array_split(data, nout)
    downsampledData = []
    for group in groups:
        index = np.argmax(group[:, 1])
        point = group[index]
        downsampledData.append(point)
    return np.array(downsampledData)


def noneDownsampled(data: np.ndarray, nout: int) -> np.ndarray:
    return data
