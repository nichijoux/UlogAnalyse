from qfluentwidgets import qconfig
from PyQt6.QtWidgets import QApplication
import sys, os
from src.gui.main_window import MainWindow
from src.common.config import appConfig

# 设置环境变量以禁用沙箱
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

if __name__ == "__main__":
    # 加载配置
    qconfig.load("config/config.json", appConfig)
    # 在app创建前设置缩放比例
    if appConfig.get(appConfig.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(appConfig.get(appConfig.dpiScale))
    # 启动程序
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    # 重新启用云母特效
    w.setMicaEffectEnabled(True)
    app.exec()
