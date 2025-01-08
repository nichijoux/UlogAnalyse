from qfluentwidgets import (
    PrimaryPushSettingCard,
    ComboBoxSettingCard,
    SmoothScrollArea,
    SettingCardGroup,
    HyperlinkCard,
    FluentIcon as Icons,
    setTheme,
    InfoBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QDesktopServices
import sys
from src.common.config import COPYRIGHT, appConfig


class SettingInterface(SmoothScrollArea):
    chartTypeChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")
        self.initUI()
        # 设置背景颜色为透明
        self.setStyleSheet(
            """
            QScrollArea, .QWidget {
                border: none;
                background-color: transparent;
            }"""
        )
        self.initConnect()

    def initSoftWidget(self):
        self.softGroup = SettingCardGroup("软件相关", self.scrollWidget)
        self.importDirCard = PrimaryPushSettingCard(
            "选择文件夹",
            Icons.DOWNLOAD,
            "导出路径",
            appConfig.get(appConfig.importFolder),
            self.softGroup,
        )
        self.chartTypeCard = ComboBoxSettingCard(
            appConfig.chartType,
            Icons.CHAT,
            "图表类型",
            "选择切换主页右侧图表类型",
            texts=["line", "scatter"],
            parent=self.softGroup,
        )
        self.softGroup.addSettingCard(self.importDirCard)
        self.softGroup.addSettingCard(self.chartTypeCard)

    def initPersonalWidget(self):
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        if sys.platform == "win32":
            self.backgroundEffectCard = ComboBoxSettingCard(
                appConfig.backgroundEffect,
                Icons.BRUSH,
                "窗口背景透明材质",
                texts=["Acrylic", "Mica", "MicaAlt", "Aero"],
                parent=self.personalGroup,
            )
            self.personalGroup.addSettingCard(self.backgroundEffectCard)
        self.zoomCard = ComboBoxSettingCard(
            appConfig.dpiScale,
            Icons.ZOOM,
            "界面缩放",
            "改变应用程序界面的缩放比例",
            texts=["100%", "125%", "150%", "175%", "200%", "自动"],
            parent=self.personalGroup,
        )
        self.dangerMessageCard = ComboBoxSettingCard(
            appConfig.dangerMessage,
            Icons.DATE_TIME,
            "警告信息",
            "是否显示显示警告信息",
            texts=["一直显示", "不再显示"],
            parent=self.personalGroup,
        )
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.dangerMessageCard)

    def initAboutWidget(self):
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.authorCard = HyperlinkCard(
            COPYRIGHT["AUTHOR_URL"],
            "打开作者的个人空间",
            Icons.PROJECTOR,
            "了解作者",
            f"发现更多 {COPYRIGHT['AUTHOR']} 的作品",
            self.aboutGroup,
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            Icons.FEEDBACK,
            "提供反馈",
            "通过提供反馈来帮助我们改进该项目",
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            Icons.INFO,
            "关于",
            "© "
            + "Copyright"
            + f" {COPYRIGHT['YEAR']}, {COPYRIGHT['AUTHOR']}. "
            + f"Version {COPYRIGHT['VERSION']}",
            self.aboutGroup,
        )
        self.aboutGroup.addSettingCard(self.authorCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

    def initUI(self):
        self.scrollWidget = QWidget()
        # 布局设置
        expandLayout = QVBoxLayout()
        expandLayout.setSpacing(20)
        expandLayout.setContentsMargins(36, 24, 36, 24)
        # 软件配置项
        self.initSoftWidget()
        # 个性化项
        self.initPersonalWidget()
        # 关于项
        self.initAboutWidget()
        # 添加配置项
        expandLayout.addWidget(self.softGroup)
        expandLayout.addWidget(self.personalGroup)
        expandLayout.addWidget(self.aboutGroup)
        # 设置
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollWidget.setLayout(expandLayout)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

    def showRestartTooltip(self):
        InfoBar.success("已配置", "重启软件后生效", duration=1500, parent=self)

    def setImportDir(self):
        """
        设置导出目录
        """
        dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if dir:
            # 更改配置
            appConfig.set(appConfig.importFolder, dir)
            # 更新ui
            self.importDirCard.setContent(dir)

    def onBackgroundEffectCardChanged(self, option):
        self.window().applyBackgroundEffectByConfig()

    def onDangerMessageChanged(self, index):
        if index == 0:
            appConfig.set(appConfig.dangerMessage, "一直显示")
        else:
            appConfig.set(appConfig.dangerMessage, "不再显示")

    def onChartTypeChanged(self, index):
        if index == 0:
            appConfig.set(appConfig.chartType, "line")
        else:
            appConfig.set(appConfig.chartType, "scatter")
        self.chartTypeChanged.emit()

    def initConnect(self):
        # 重启提示
        appConfig.appRestartSig.connect(self.showRestartTooltip)
        appConfig.themeChanged.connect(setTheme)
        # 导出目录设置
        self.importDirCard.clicked.connect(self.setImportDir)
        self.chartTypeCard.comboBox.currentIndexChanged.connect(self.onChartTypeChanged)
        # 个性化
        if sys.platform == "win32":
            self.backgroundEffectCard.comboBox.currentIndexChanged.connect(
                self.onBackgroundEffectCardChanged
            )
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(COPYRIGHT["FEEDBACK_URL"]))
        )
        # 警告信息
        self.dangerMessageCard.comboBox.currentIndexChanged.connect(
            self.onDangerMessageChanged
        )
