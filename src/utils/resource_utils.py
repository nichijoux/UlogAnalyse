import os, sys


def getResource(path):
    """
    根据系统环境，输出资源文件的最终路径
    :param path: 相对路径
    :return: 最终路径
    """
    # 系统环境中存在_MEIPASS属性说明程序已被打包
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path).replace("\\", "/")
    else:
        return os.path.join(os.path.abspath("."), path).replace("\\", "/")

# def getThemeColor():
#     if sys.platform in ['win32','darwin']:
#         setThemeColor()