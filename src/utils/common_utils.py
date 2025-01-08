from PyQt6.QtCore import QTimer
from functools import wraps
import time, os


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
