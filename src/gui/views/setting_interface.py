from qfluentwidgets import (
    PrimaryPushSettingCard,
    ComboBoxSettingCard,
    SmoothScrollArea,
    SettingCardGroup,
    HyperlinkCard,
    FluentIcon as Icons,
    setTheme,
    InfoBar,
    InfoBarPosition,
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QDesktopServices
from loguru import logger
import sys, json
import http.client
from urllib.parse import urlparse
from src.gui.components import InputSettingCard
from src.common import SOFTWARE_COPYRIGHT, appConfig


class GetVersionThread(QThread):
    getResponse = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def run(self):
        try:
            parsedUrl = urlparse(
                "https://api.github.com/repos/nichijoux/UlogAnalyse/releases/latest"
            )
            connection = http.client.HTTPSConnection(parsedUrl.netloc)
            connection.request(
                "GET",
                parsedUrl.path,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                },
            )
            response = connection.getresponse()
            if response.status == 200:
                content = json.loads(response.read().decode())
                tagName = content["tag_name"]
                # 获取新版本和当前版本的版本号
                latestVersion = list(map(int, tagName.split(".")))
                currentVersion = list(map(int, SOFTWARE_COPYRIGHT["VERSION"].split(".")))
                # 如果存在新版本则跳转
                if latestVersion > currentVersion:
                    self.getResponse.emit(content)
                else:
                    self.getResponse.emit({"INFO": "当前版本已是最新版本"})
            else:
                logger.error(f"Error: {response.status}")
                self.getResponse.emit({"ERROR": f"获取更新失败:{response.status}"})
        except Exception as e:
            logger.error(f"获取更新失败：{e}")
            self.getResponse.emit({"ERROR": f"获取更新失败:{repr(e)}"})


class SettingInterface(SmoothScrollArea):
    chartRedrawSignal = pyqtSignal()

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
        self.ulogFieldsConfigCard = PrimaryPushSettingCard(
            "选择配置文件",
            Icons.DOCUMENT,
            "属性参数配置映射文件",
            appConfig.get(appConfig.fieldsConfig),
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
        self.chartSamplingCard = ComboBoxSettingCard(
            appConfig.chartSampling,
            Icons.CLIPPING_TOOL,
            "图表采样算法",
            "选择切换echart图表采样算法,默认使用lttb算法采样,none表示不进行采样,不同采样算法能不同程度上提高echart绘图速度。",
            texts=["lttb", "average", "min", "max", "none"],
            parent=self.softGroup,
        )
        self.insidePointNumCard = InputSettingCard(
            configItem=appConfig.insidePointNum,
            regStr=r"^\d+$",
            icon=Icons.FONT_SIZE,
            title="可视区采样点数量",
            content="数据量超过阈值时则将使用采样算法,可视区采样后将降低到的采样点数量",
            parent=self.softGroup,
        )
        self.partPointNumCard = InputSettingCard(
            configItem=appConfig.partPointNum,
            regStr=r"^\d+$",
            icon=Icons.FONT_SIZE,
            title="部分可视区采样点数量",
            content="数据量超过阈值时则将使用采样算法,部分可视区域外将降低到的采样点数量",
            parent=self.softGroup,
        )
        self.outsidePointNumCard = InputSettingCard(
            configItem=appConfig.outsidePointNum,
            regStr=r"^\d+$",
            icon=Icons.FONT_SIZE,
            title="完全不可视区采样点数量",
            content="数据量超过阈值时则将使用采样算法,完全不可视区域将降低到的采样点数量",
            parent=self.softGroup,
        )
        # 添加进SettingCardGroup中
        self.softGroup.addSettingCard(self.importDirCard)
        self.softGroup.addSettingCard(self.ulogFieldsConfigCard)
        self.softGroup.addSettingCard(self.chartTypeCard)
        self.softGroup.addSettingCard(self.chartSamplingCard)
        self.softGroup.addSettingCard(self.insidePointNumCard)
        self.softGroup.addSettingCard(self.partPointNumCard)
        self.softGroup.addSettingCard(self.outsidePointNumCard)

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
        self.personalGroup.addSettingCard(self.zoomCard)

    def initAboutWidget(self):
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.authorCard = HyperlinkCard(
            SOFTWARE_COPYRIGHT["AUTHOR_URL"],
            "打开作者的个人空间",
            Icons.PROJECTOR,
            "了解作者",
            f"发现更多 {SOFTWARE_COPYRIGHT['AUTHOR']} 的作品",
            self.aboutGroup,
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            Icons.FEEDBACK,
            "提供反馈",
            "通过提供反馈来改进该项目",
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            Icons.INFO,
            "关于",
            "© "
            + "Copyright"
            + f" {SOFTWARE_COPYRIGHT['YEAR']}, {SOFTWARE_COPYRIGHT['AUTHOR']}. "
            + f"Version {SOFTWARE_COPYRIGHT['VERSION']}",
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

    def loadUlogConfigFile(self):
        """
        加载ulog配置参数文件,文件应该为.json
        """
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择参数配置文件", "", "json文件(*.json)"
        )
        if not filename:
            return
        appConfig.set(appConfig.fieldsConfig, filename)

    def showResponse(self, parent, content: dict):
        if "INFO" in content:
            InfoBar.info(
                title="当前已是最新版本",
                content="",
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
                duration=5000,
            )
        elif "ERROR" in content:
            InfoBar.error(
                title="检查更新失败",
                content=content["ERROR"],
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
                duration=5000,
            )
        else:
            # 直接跳转
            InfoBar.info(
                title="检测到新版本,正在跳转",
                content="",
                position=InfoBarPosition.TOP_RIGHT,
                parent=parent,
                duration=5000,
            )
            QDesktopServices.openUrl(QUrl(SOFTWARE_COPYRIGHT["PROJECT_DOWNLOAD_URL"]))

    def checkUpdate(self, parent):
        thread = GetVersionThread(parent)
        thread.getResponse.connect(lambda content: self.showResponse(parent, content))
        thread.start()

    def onChartTypeChanged(self, text):
        # 类型不同则进行重绘
        if text != appConfig.get(appConfig.chartType):
            appConfig.set(appConfig.chartType, text)
            InfoBar.success("提示", "图表类型修改成功", duration=1500, parent=self)
            self.chartRedrawSignal.emit()

    def onChartSamplingChanged(self, text):
        """
        描述:
            图表采样算法改变

        参数:
            text (_type_): _description_
        """
        # 类型不同则进行重绘
        if text != appConfig.get(appConfig.chartSampling):
            appConfig.set(appConfig.chartSampling, text)
            InfoBar.success("提示", "采样算法修改成功", duration=1500, parent=self)
            self.chartRedrawSignal.emit()

    def onInsidePointNumChanged(self):
        value = self.insidePointNumCard.inputEdit.text()
        if value != appConfig.get(appConfig.insidePointNum):
            appConfig.set(appConfig.insidePointNum, value)
            InfoBar.success("提示", "参数修改成功", duration=1500, parent=self)
            self.chartRedrawSignal.emit()

    def onPartPointNumChanged(self):
        value = self.partPointNumCard.inputEdit.text()
        if value != appConfig.get(appConfig.partPointNum):
            appConfig.set(appConfig.partPointNum, value)
            InfoBar.success("提示", "参数修改成功", duration=1500, parent=self)
            self.chartRedrawSignal.emit()

    def onOutsidePointNumChanged(self):
        value = self.outsidePointNumCard.inputEdit.text()
        if value != appConfig.get(appConfig.outsidePointNum):
            appConfig.set(appConfig.outsidePointNum, value)
            InfoBar.success("提示", "参数修改成功", duration=1500, parent=self)
            self.chartRedrawSignal.emit()

    def onBackgroundEffectCardChanged(self, option):
        self.window().applyBackgroundEffectByConfig()

    def onAboutClicked(self):
        # 提示信息
        InfoBar.info(
            "请稍候",
            "正在检查更新...",
            position=InfoBarPosition.TOP_RIGHT,
            duration=1000,
            parent=self,
        )
        # 检测更新
        self.checkUpdate(self.window())

    def initConnect(self):
        # 重启提示
        appConfig.appRestartSig.connect(self.showRestartTooltip)
        appConfig.themeChanged.connect(setTheme)
        # 软件设置
        self.importDirCard.clicked.connect(self.setImportDir)
        self.ulogFieldsConfigCard.clicked.connect(self.loadUlogConfigFile)
        # echart图表设置
        self.chartTypeCard.comboBox.currentTextChanged.connect(self.onChartTypeChanged)
        self.chartSamplingCard.comboBox.currentTextChanged.connect(
            self.onChartSamplingChanged
        )
        self.insidePointNumCard.inputEdit.editingFinished.connect(
            self.onInsidePointNumChanged
        )
        self.partPointNumCard.inputEdit.editingFinished.connect(
            self.onPartPointNumChanged
        )
        self.outsidePointNumCard.inputEdit.editingFinished.connect(
            self.onOutsidePointNumChanged
        )
        # 个性化
        if sys.platform == "win32":
            self.backgroundEffectCard.comboBox.currentIndexChanged.connect(
                self.onBackgroundEffectCardChanged
            )
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(SOFTWARE_COPYRIGHT["FEEDBACK_URL"]))
        )
        # 检测更新
        self.aboutCard.clicked.connect(self.onAboutClicked)
