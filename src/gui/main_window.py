from qfluentwidgets import (
    MSFluentWindow,
    FluentIcon as Icons,
    NavigationItemPosition,
    setThemeColor,
    setTheme,
    Theme,
)
import sys, darkdetect
from qframelesswindow.utils import getSystemAccentColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QThread, QTimer
from src.gui.views.main_interface import MainInterface
from src.gui.views.setting_interface import SettingInterface
from src.utils.resource_utils import getResource
from src.common.config import appConfig


class ThemeChangedListener(QThread):
    themeChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        darkdetect.listener(self.themeChanged.emit)


class MainWindow(MSFluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 添加界面
        self.mainInterface = MainInterface(self)
        self.settingInterface = SettingInterface(self)
        # 窗口信息初始化
        self.initNavigation()
        self.initWindow()
        # 初始化connect事件
        self.initConnect()
        # 只能获取 Windows 和 macOS 的主题色
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=False)
            # 初始时设置主题模式
        setTheme(Theme.AUTO)
        # 创建检测主题色更改线程
        self.themeChangedListener = ThemeChangedListener(self)
        self.themeChangedListener.themeChanged.connect(self.toggleTheme)
        self.themeChangedListener.start()

    def initWindow(self):
        # 设置窗口大小
        if appConfig.geometry.value == "Default":
            self.resize(1080, 880)
        else:
            try:
                self.setGeometry(appConfig.get(appConfig.geometry))
            except Exception as e:
                # 重置为default
                appConfig.set(appConfig.geometry, "Default")
                self.resize(1080, 880)
        # 允许拖放
        self.setAcceptDrops(True)
        # 居中显示
        desktop = QApplication.primaryScreen().geometry()
        self.move(
            (desktop.width() - self.width()) // 2,
            (desktop.height() - self.height()) // 2,
        )
        # 设置图标和标题
        self.setWindowIcon(QIcon(getResource("src/resources/images/icon.jpg")))
        self.setWindowTitle("Ulog Analysis")

    def initNavigation(self):
        """
        描述:
            初始化侧边导航栏
        """
        self.addSubInterface(self.mainInterface, Icons.HOME, "主页")
        self.addSubInterface(
            self.settingInterface,
            Icons.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM,
        )

    def initConnect(self):
        # 重新画图
        self.settingInterface.chartTypeChanged.connect(
            lambda: self.mainInterface.drawChart()
        )

    def applyBackgroundEffectByConfig(self):
        if sys.platform == "win32":
            # 移除当前背景效果
            self.windowEffect.removeBackgroundEffect(self.winId())
            if appConfig.backgroundEffect.value == "Acrylic":
                self.windowEffect.setAcrylicEffect(
                    self.winId(), "00000030" if darkdetect.isDark() else "F2F2F230"
                )
            elif appConfig.backgroundEffect.value == "Mica":
                self.windowEffect.setMicaEffect(self.winId(), darkdetect.isDark())
            elif appConfig.backgroundEffect.value == "MicaAlt":
                self.windowEffect.setMicaEffect(self.winId(), darkdetect.isDark(), True)
            elif appConfig.backgroundEffect.value == "Aero":
                self.windowEffect.setAeroEffect(self.winId())

    def closeEvent(self, e):
        # 保存窗口位置
        appConfig.set(appConfig.geometry, self.geometry())
        # 停止监听器线程
        self.themeChangedListener.terminate()
        self.themeChangedListener.deleteLater()
        super().closeEvent(e)

    def toggleTheme(self, theme: str):
        if theme == "Dark":
            # PyQt6需要添加重试
            setTheme(Theme.DARK, save=False)
            if appConfig.backgroundEffect.value in ["Mica", "MicaAlt"]:
                # 重新启用云母特效
                QTimer.singleShot(300, self.applyBackgroundEffectByConfig)
        else:
            setTheme(Theme.LIGHT, save=False)
        self.applyBackgroundEffectByConfig()
        # 切换echart的主题
        self.mainInterface.toggleEchartTheme(theme == "Dark")
