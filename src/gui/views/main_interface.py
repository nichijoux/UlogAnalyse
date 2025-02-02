from qfluentwidgets import (
    CardWidget,
    PushButton,
    ComboBox,
    LineEdit,
    TreeWidget,
    TableWidget,
    ProgressBar,
    FluentIcon as Icons,
    InfoBar,
    InfoBarPosition,
    CaptionLabel,
    isDarkTheme,
    ToolTipFilter,
)
from qframelesswindow.webengine import FramelessWebEngineView
from PyQt6.QtCore import Qt, QUrl, QObject, pyqtSlot, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QTableWidgetItem,
    QHeaderView,
    QTreeWidgetItem,
    QFrame,
    QAbstractItemView,
    QSplitter,
)
from PyQt6.QtWebChannel import QWebChannel
import numpy as np
import os, json, sys
from collections import defaultdict
from src.common import appConfig
from src.gui.components import LabelInputCard, LabelTextCard, LogInfoDialog
from src.utils import *


class EChartHandler(QObject):
    echartZoomed = pyqtSignal(float, float, float, float)

    @pyqtSlot(float, float, float, float)
    def zoomAxis(self, xS, xE, yS, yE):
        self.echartZoomed.emit(xS, xE, yS, yE)


class ExportThread(QThread):
    # 当前导出进度的信号
    progressChanged = pyqtSignal(int)

    exportStarted = pyqtSignal()

    exportFinished = pyqtSignal()

    def __init__(self, fields: dict, parent=None):
        super().__init__(parent=parent)
        self.fields = fields

    def run(self):
        self.exportStarted.emit()
        delimiter = ","
        progress = 0
        for topField in self.fields:
            out_file_name = os.path.join(
                appConfig.get(appConfig.importFolder), topField + ".csv"
            )
            with open(out_file_name, "w", encoding="utf-8") as csvfile:
                # 写入属性行
                csvfile.write(
                    delimiter.join([inner for inner in self.fields[topField]]) + "\n"
                )
                # 挨个写入属性值(按行写入)
                for i in range(len(self.fields[topField]["timestamp"])):
                    for k, innerField in enumerate(self.fields[topField]):
                        if innerField == "timestamp":
                            csvfile.write(str(self.fields[topField][innerField][i]))
                        else:
                            csvfile.write(
                                str(self.fields[topField][innerField]["value"][i])
                            )
                        if k != len(self.fields[topField]) - 1:
                            csvfile.write(delimiter)
                    # 写入回车
                    csvfile.write("\n")
                progress += 1
                self.progressChanged.emit(progress)
        self.exportFinished.emit()


class MainInterface(CardWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MainInterface")
        # 初始化UI界面
        self.initUI()
        # 初始化控件事件
        self.initConnect()
        # 初始化其他参数
        self.initInterface()

    def initInterface(self):
        # 初始化interface
        configFilePath = appConfig.get(appConfig.fieldsConfig)
        if configFilePath != "":
            with open(configFilePath, "r") as configFile:
                self.fieldConfig = json.load(configFile)
        # 初始画图相关信息
        self.canDraw = True

    # ui 部分
    def initHeaderLayout(self):
        headerLayout = QHBoxLayout()
        # 打开文件按钮
        self.openButton = PushButton(Icons.FOLDER, "打开日志")
        self.openButton.setToolTip(
            "打开单个或多个ulg日志文件,若同时打开多个ulg文件则软件将其视为同一个文件"
        )
        self.openButton.setToolTipDuration(1000)
        self.openButton.installEventFilter(ToolTipFilter(self.openButton))
        # 日志参数
        self.parameterButton = PushButton(Icons.INFO, "日志参数")
        self.parameterButton.setToolTip(
            "打开日志参数对话框,对话框将显示ulg日志参数信息"
        )
        self.parameterButton.setToolTipDuration(1000)
        self.parameterButton.installEventFilter(ToolTipFilter(self.parameterButton))
        # 选项按钮
        self.viewSelectBox = ComboBox()
        self.viewSelectBox.addItems(["Boot时间", "GPS时间"])
        self.viewSelectBox.setCurrentIndex(0)
        self.viewSelectBox.setToolTip("切换右侧图表x轴显示方式")
        self.viewSelectBox.setToolTipDuration(1000)
        self.viewSelectBox.installEventFilter(ToolTipFilter(self.viewSelectBox))
        # 导出按钮
        self.exportButton = PushButton(Icons.IMAGE_EXPORT, "导出CSV")
        self.exportButton.setHidden(True)
        self.exportButton.setToolTip("将ulg日志数据导出为csv文件")
        self.exportButton.setToolTipDuration(1000)
        self.exportButton.installEventFilter(ToolTipFilter(self.exportButton))
        # 布局设置
        headerLayout.setContentsMargins(5, 5, 5, 5)
        headerLayout.addWidget(self.openButton)
        headerLayout.addSpacing(4)
        headerLayout.addWidget(self.parameterButton)
        headerLayout.addSpacing(4)
        headerLayout.addWidget(self.viewSelectBox)
        headerLayout.addSpacing(4)
        headerLayout.addStretch(0)
        headerLayout.addWidget(self.exportButton)
        headerLayout.addSpacing(4)
        return headerLayout

    def initFieldTreeWidget(self):
        self.fieldTree = TreeWidget()
        # 隐藏表头
        self.fieldTree.setHeaderHidden(True)

    def initFieldZoomWidget(self):
        self.fieldZoom = QFrame()

        layout = QVBoxLayout()

        self.fieldLabelCard = LabelTextCard(label="参数")
        self.fieldOffsetCard = LabelInputCard(text="偏移")
        self.fieldOffsetCard.setRegularExpression("^(-?\d+)(\.\d+)?$")
        self.fieldZoomCard = LabelInputCard(text="缩放")
        self.fieldZoomCard.setRegularExpression("^(-?\d+)(\.\d+)?$")

        layout.addWidget(self.fieldLabelCard)
        layout.addWidget(self.fieldOffsetCard)
        layout.addWidget(self.fieldZoomCard)
        self.fieldZoom.setLayout(layout)

    def initLogTableWidget(self):
        # 日志表格
        self.logTable = TableWidget()
        self.logTable.horizontalHeader().setMinimumWidth(100)
        self.logTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.logTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.logTable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # 启用边框并设置圆角
        self.logTable.setBorderVisible(True)
        self.logTable.setBorderRadius(8)
        # 设置行列数
        self.logTable.setColumnCount(3)
        # 设置水平表头
        self.logTable.setHorizontalHeaderLabels(["时间", "日志等级", "消息"])
        # 隐藏垂直表头
        self.logTable.verticalHeader().hide()
        # 单选模式
        self.logTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 选中整行
        self.logTable.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        # 禁止双击编辑
        self.logTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 设置换行
        self.logTable.setWordWrap(False)

    def initLeftWidget(self):
        """
        初始化左侧组件
        """
        # 搜索框
        self.searchEdit = LineEdit()
        # 参数表格
        self.initFieldTreeWidget()
        # 参数调整界面
        self.initFieldZoomWidget()
        # 日志信息表格
        self.initLogTableWidget()
        # 布局添加窗口
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.addWidget(self.searchEdit)
        leftLayout.addWidget(self.fieldTree)
        leftLayout.addWidget(self.fieldZoom)
        leftLayout.addWidget(self.logTable)
        # 左侧窗口
        leftWidget = QFrame()
        leftWidget.setMinimumWidth(300)
        # 设置左侧窗口布局
        leftWidget.setLayout(leftLayout)
        return leftWidget

    def initRightWidget(self):
        """
        初始化右侧组件
        """
        self.htmlWidget = FramelessWebEngineView(self)
        self.htmlWidget.setStyleSheet("background-color: transparent;")
        # 打开本地html文件
        self.htmlWidget.load(
            QUrl("file:///" + getResource("src/resources/html/index.html"))
        )
        # 注册html的channel
        self.channel = QWebChannel()
        # 注册html的object
        self.echartHandler = EChartHandler()
        self.channel.registerObject("echartHandler", self.echartHandler)
        self.htmlWidget.page().setWebChannel(self.channel)
        return self.htmlWidget

    def initCenterWidget(self):
        # 可调整布局设置
        # 布局添加窗口
        # 1. 左侧为搜索按钮、属性列信息和日志信息表格（垂直布局）
        contentSpliter = QSplitter(Qt.Orientation.Horizontal)
        contentSpliter.setStyleSheet("background-color:transparent;")
        # 调整操作完成后一次性重绘
        contentSpliter.setOpaqueResize(False)
        # 初始化左侧组件
        leftWidget = self.initLeftWidget()
        # 初始化右侧组件
        rightWidget = self.initRightWidget()
        # 添加窗口
        contentSpliter.addWidget(leftWidget)
        contentSpliter.addWidget(rightWidget)
        contentSpliter.setStretchFactor(0, 1)
        contentSpliter.setStretchFactor(1, 7)
        return contentSpliter

    def initStatusLayout(self):
        statusLayout = QVBoxLayout()
        self.statusWidget = CaptionLabel("状态:")
        self.statusProgressBar = ProgressBar()
        # 先隐藏
        self.statusProgressBar.setHidden(True)
        # 布局添加
        statusLayout.addWidget(self.statusWidget)
        statusLayout.addSpacing(5)
        statusLayout.addWidget(self.statusProgressBar)
        return statusLayout

    def initUI(self):
        # 菜单区
        headerLayout = self.initHeaderLayout()
        # 核心区
        centerWidget = self.initCenterWidget()
        # 底部区域
        statusLayout = self.initStatusLayout()
        # 组装为UI界面
        layout = QVBoxLayout()
        # 添加顶部区域
        layout.setSpacing(12)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.addLayout(headerLayout)
        # # 设置中间区域最大
        layout.addWidget(centerWidget)
        layout.addLayout(statusLayout)
        # 设置核心部件撑满
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        layout.setStretch(2, 0)
        self.setLayout(layout)

    def initConnect(self):
        """
        初始化控件事件
        """
        # 打开文件按钮
        self.openButton.clicked.connect(self.openUlog)
        # 日志参数按钮
        self.parameterButton.clicked.connect(self.openInfoDialog)
        # 视图选项
        self.viewSelectBox.currentIndexChanged.connect(lambda: self.drawChart())
        # 导出按钮
        self.exportButton.clicked.connect(self.exportCSV)
        # 搜索框
        self.searchEdit.textChanged.connect(self.onSearchTextChanged)
        # 参数列表
        self.fieldTree.itemChanged.connect(self.onFieldChanged)
        self.fieldTree.itemClicked.connect(self.onFieldClicked)
        # 日志表格双击事件
        self.logTable.itemDoubleClicked.connect(self.onLogTableDoubleClicked)
        # 缩放参数
        self.fieldOffsetCard.editingFinished.connect(self.onOffsetChanged)
        self.fieldZoomCard.editingFinished.connect(self.onZoomChanged)
        # 设置背景颜色
        self.htmlWidget.loadFinished.connect(
            lambda: self.toggleEchartTheme(isDarkTheme())
        )
        # js和python间事件注册
        self.echartHandler.echartZoomed.connect(self.zoomDrawChart)

    def openUlog(self):
        """
        打开ulog文件并解析(可以打开多个)
        """
        # 在打开文件前,存储已经展示了哪些属性
        displayedFields = defaultdict(dict)
        for i in range(self.fieldTree.topLevelItemCount()):
            topItem = self.fieldTree.topLevelItem(i)
            topField = topItem.text(0)
            # 遍历子项
            for j in range(topItem.childCount()):
                innerItem = topItem.child(j)
                if innerItem.checkState(0) == Qt.CheckState.Checked:
                    # 被选中了
                    innerField = innerItem.text(0)
                    # 原地修改
                    displayedFields[topField][innerField] = {
                        "zoom": self.fields[topField][innerField]["zoom"],
                        "offset": self.fields[topField][innerField]["offset"],
                    }
        # 使用QFileDialog打开文件对话框
        fileList, _ = QFileDialog.getOpenFileNames(
            self, "选择文件", "", "ulog文件(*.ulg)"
        )
        if len(fileList) == 0:
            return
        self.exportButton.setHidden(False)
        # 清空数据
        files = ",".join(map(os.path.basename, fileList))
        self.statusWidget.setText(f"当前打开文件:{files}")
        self.clearData()
        # 遍历所有打开的日志
        for filepath in fileList:
            ulog = ULog(filepath)
            if len(self.initialParameters) == 0:
                # 初始化参数以第一个文件为主
                self.initialParameters = get_initial_parameters(ulog)
            # 拼接日志
            self.logMesasges += get_logged_message(ulog)
            self.changedParameters += get_change_parameters(ulog)
            # 拼接参数
            if len(self.fields) == 0:
                self.fields = get_fields_dict(ulog)
            else:
                fields = get_fields_dict(ulog)
                # 拼接数据
                for topKey, innerFields in self.fields.items():
                    if topKey not in fields:
                        continue
                    for innerKey, fieldData in innerFields.items():
                        if innerKey in fields[topKey]:
                            if innerKey == "timestamp":
                                self.fields[topKey][innerKey] = np.concatenate(
                                    (fieldData, fields[topKey][innerKey]), axis=0
                                )
                            else:
                                self.fields[topKey][innerKey]["value"] = np.concatenate(
                                    (
                                        fieldData["value"],
                                        fields[topKey][innerKey]["value"],
                                    ),
                                    axis=0,
                                )
        # 日志信息以最后一个为准
        self.ulogInfo, errors = get_ulog_info(ulog)
        # 显示属性
        self.displayFields()
        # 勾选对应属性,并赋予offset和zoom
        self.fieldTree.blockSignals(True)
        for i in range(self.fieldTree.topLevelItemCount()):
            topItem = self.fieldTree.topLevelItem(i)
            topField = topItem.text(0)
            checked = 0
            if topField in displayedFields:
                # 如果属性存在则遍历子项
                for j in range(topItem.childCount()):
                    innerItem = topItem.child(j)
                    innerField = innerItem.text(0)
                    if innerField in displayedFields[topField]:
                        checked += 1
                        innerItem.setCheckState(0, Qt.CheckState.Checked)
                        # 更新zoom和offset
                        fieldData = displayedFields[topField][innerField]
                        self.fields[topField][innerField].update(
                            {"zoom": fieldData["zoom"], "offset": fieldData["offset"]}
                        )
            # 检查父项,是否需要勾选
            if checked == topItem.childCount():
                topItem.setCheckState(0, Qt.CheckState.Checked)
            elif checked > 0:
                topItem.setCheckState(0, Qt.CheckState.PartiallyChecked)
            else:
                topItem.setCheckState(0, Qt.CheckState.Unchecked)
        self.fieldTree.blockSignals(False)
        # 显示数据
        self.displayLogMessage()
        # 错误提示
        for error in errors:
            InfoBar.warning(title="警告", content=error, duration=2500, parent=self)
        # 重新画图
        if len(displayedFields) > 0:
            self.drawChart()

    def openInfoDialog(self):
        ulogInfo = None
        if hasattr(self, "ulogInfo"):
            ulogInfo = self.ulogInfo
        initialParameters = None
        if hasattr(self, "initialParameters"):
            initialParameters = self.initialParameters
        # 显示窗口
        w = LogInfoDialog(
            infoData=ulogInfo, parameterData=initialParameters, parent=self.window()
        )
        w.exec()

    def onExportStart(self):
        """
        导出开始的函数
        """
        self.statusProgressBar.setRange(0, len(self.fields))
        self.statusProgressBar.setHidden(False)

    def onExportFinised(self):
        """
        导出完成的函数
        """
        self.statusProgressBar.setHidden(True)
        InfoBar.success(
            "提示",
            "导出成功",
            duration=1500,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )

    def exportCSV(self):
        """
        将ulg数据导出为csv
        """
        exportThread = ExportThread(fields=self.fields, parent=self.window())
        # 导出开始
        exportThread.exportStarted.connect(self.onExportStart)
        # 导出完成
        exportThread.exportFinished.connect(self.onExportFinised)
        # 导出进行中
        exportThread.progressChanged.connect(
            lambda value: self.statusProgressBar.setValue(value)
        )
        exportThread.start()

    def onFieldClicked(self, item: QTreeWidgetItem, column: int):
        """
        描述:
            点击某个属性的处理函数

        参数:
            item (QTreeWidgetItem): 树的子项
            column (int): 第几列
        """
        parent = item.parent()
        if parent:
            topField, innerField = parent.text(column), item.text(column)
            data = self.fields[topField][innerField]
            translate = (
                getattr(self, "fieldConfig", {}).get(topField, {}).get(innerField)
            )
            # 改变数据
            self.fieldLabelCard.setText(
                f"{topField}.{innerField}({translate})"
                if translate
                else f"{topField}.{innerField}"
            )
            self.fieldOffsetCard.setInitValue(data["offset"])
            self.fieldZoomCard.setInitValue(data["zoom"])
            # 设置当前选中了那个元素
            self.selectTopField, self.selectInnerField = topField, innerField

    def onFieldChanged(self, item: QTreeWidgetItem, column: int):
        # 禁止再次发送信号
        self.fieldTree.blockSignals(True)
        # 联动子节点状态
        if item.checkState(column) != Qt.CheckState.PartiallyChecked:
            # 存储节点状态防止联动时导致状态进行改变
            state = item.checkState(column)
            # 遍历所有子节点,将其状态设置为父节点的状态
            for i in range(item.childCount()):
                child = item.child(i)
                # 如果没有设置为隐藏,则设置其状态
                if not child.isHidden():
                    child.setCheckState(column, state)
        # 联动父节点状态
        parent = item.parent()
        if parent is not None:
            # 统计子节点的选中和未选中状态
            visible_children = [
                child
                for i in range(parent.childCount())
                if not (child := parent.child(i)).isHidden()
            ]
            checked = sum(
                child.checkState(column) == Qt.CheckState.Checked
                for child in visible_children
            )
            unchecked = sum(
                child.checkState(column) == Qt.CheckState.Unchecked
                for child in visible_children
            )
            # 设置父节点状态
            if checked == len(visible_children):
                parent.setCheckState(column, Qt.CheckState.Checked)  # 全选
            elif unchecked == len(visible_children):
                parent.setCheckState(column, Qt.CheckState.Unchecked)  # 未选中
            else:
                parent.setCheckState(column, Qt.CheckState.PartiallyChecked)  # 部分选中
        # 可以再次触发信号
        self.fieldTree.blockSignals(False)
        # 绘制图表
        self.drawChart()

    def onLogTableDoubleClicked(self, item: QTableWidgetItem):
        # 获取行列
        timeItem = self.logTable.item(item.row(), 0)
        # 在图像上添加一列数据
        timestamp = timeItem.text()
        timeValue = (
            int(timestamp[0:2]) * 6e7
            + int(timestamp[3:5]) * 1e6
            + int(timestamp[6:]) * 1e3
        )
        # 在右侧添加一条垂线
        self.htmlWidget.page().runJavaScript(
            f"""
            setMarkLine({timeValue})
            """
        )

    def onOffsetChanged(self, value: float):
        if self.selectTopField and self.selectInnerField:
            self.fields[self.selectTopField][self.selectInnerField]["offset"] = value
            # 重绘图表
            self.drawChart()

    def onZoomChanged(self, value: float):
        if self.selectTopField and self.selectInnerField:
            self.fields[self.selectTopField][self.selectInnerField]["zoom"] = value
            # 重绘图表
            self.drawChart()

    @debounce(1000)
    @throttle(500)
    def onSearchTextChanged(self, text: str):
        """
        描述:
            用于展示搜索的函数

        参数:
            text (str): 参数
        """
        for i in range(self.fieldTree.topLevelItemCount()):
            topItem = self.fieldTree.topLevelItem(i)
            innerHidenCount = 0
            # 遍历子项
            for j in range(topItem.childCount()):
                innerItem = topItem.child(j)
                if text not in innerItem.text(0):
                    innerItem.setHidden(True)
                    innerHidenCount += 1
                else:
                    innerItem.setHidden(False)
            # 如果隐藏的子项和节点的子项数量相等且父项中不存在text,则将topItem也隐藏
            if innerHidenCount == topItem.childCount() and text not in topItem.text(0):
                topItem.setHidden(True)
            else:
                topItem.setHidden(False)
        # 最后检测一遍父项状态
        for i in range(self.fieldTree.topLevelItemCount()):
            topItem = self.fieldTree.topLevelItem(i)
            checked = 0
            unchecked = 0
            count = 0
            for j in range(topItem.childCount()):
                innerItem = topItem.child(j)
                if not innerItem.isHidden():
                    checked += innerItem.checkState(0) == Qt.CheckState.Checked
                    unchecked += innerItem.checkState(0) == Qt.CheckState.Unchecked
                    count += 1
            # 如果checked项目数量和topItem的child数量相等
            topState = topItem.checkState(0)
            topNextState = None
            if checked == count and topState != Qt.CheckState.Checked:
                topNextState = Qt.CheckState.Checked
            elif unchecked == count and topState != Qt.CheckState.Unchecked:
                topNextState = Qt.CheckState.Unchecked
            elif (
                checked > 0
                and unchecked > 0
                and topState != Qt.CheckState.PartiallyChecked
            ):
                topNextState = Qt.CheckState.PartiallyChecked
                # 设置其状态
            if topNextState is not None:
                self.fieldTree.blockSignals(True)
                topItem.setCheckState(0, topNextState)
                self.fieldTree.blockSignals(False)

    def clearData(self):
        """
        清空数据
        """
        # 清除过滤信息
        self.searchEdit.clear()
        # 日志信息
        self.logMesasges = []
        # 初始化参数
        self.initialParameters = {}
        # 变化的参数
        self.changedParameters = []
        # 属性参数信息
        self.fields = {}
        # ulog信息
        self.ulogInfo = {}
        # 选择信息
        self.selectTopField = None
        self.selectInnerField = None
        # 清除表格信息
        self.logTable.clear()
        self.logTable.setRowCount(0)
        self.fieldTree.clear()

    def displayFields(self):
        """
        显示属性
        """
        for topField in self.fields:
            # 顶级属性
            topItem = QTreeWidgetItem([topField])
            topItem.setFlags(topItem.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            topItem.setCheckState(0, Qt.CheckState.Unchecked)
            for innerField in self.fields[topField]:
                # timestamp不创建选项
                if innerField == "timestamp":
                    continue
                # 属性选项
                innerItem = QTreeWidgetItem([innerField])
                innerItem.setFlags(innerItem.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                innerItem.setCheckState(0, Qt.CheckState.Unchecked)
                topItem.addChild(innerItem)
            self.fieldTree.addTopLevelItem(topItem)

    def displayLogMessage(self):
        """
        显示日志信息
        """
        # 设置表格调整方式
        self.logTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.logTable.setRowCount(len(self.logMesasges))
        # 设置表格内容
        for i, message in enumerate(self.logMesasges):
            for j in range(3):
                self.logTable.setItem(i, j, QTableWidgetItem(message[j]))

    def toggleEchartTheme(self, isDark: bool):
        """
        切换echart主题
        """
        if isDark:
            theme = "dark"
        else:
            theme = "light"
        self.htmlWidget.page().runJavaScript(
            f"""
                registerEChart('{theme}')
                setBodyBackground('{theme}')
            """
        )

    def drawChart(self):
        if not self.canDraw:
            return
        # 清除图像
        self.htmlWidget.page().runJavaScript("myChart.clear()")
        # 获取options
        options = self.getOptions()
        if len(options["series"]) == 0:
            return
        # 绘图
        self.htmlWidget.page().runJavaScript(
            f"""
            options = eval({options})
            options.tooltip.formatter = eval(options.tooltip.formatter)
            options.xAxis.axisLabel.formatter = eval(options.xAxis.axisLabel.formatter)
            myChart.setOption(options);
            """
        )
        self.canDraw = True

    def getOptions(self) -> dict:
        """
        描述:
            获取echart参数配置

        Returns:
            _type_: echart配置
        """
        options = {
            "animation": "false",
            "title": {"text": ""},
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": "true",
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"},
                "showDelay": "300",
                "formatter": "tooltipFormatter",
            },
            "legend": {"data": [], "animation": "false"},
            "toolbox": {
                "feature": {
                    "dataZoom": {"filterMode": "none"},
                }
            },
            "xAxis": {
                "type": "value",
                "max": "dataMax",
                "axisLabel": {
                    "formatter": f"value => ulogTimestampToTime(value, {self.viewSelectBox.currentIndex()});"
                },
            },
            "yAxis": {"type": "value"},
            "dataZoom": [
                {
                    "id": "insideX",
                    # 通过滚轮缩放
                    "type": "inside",
                    "xAxisIndex": [0],
                    "throttle": 200,
                    "filterMode": "none",
                },
                {
                    "id": "insideY",
                    # 通过滚轮缩放
                    "type": "inside",
                    "yAxisIndex": [0],
                    "throttle": 200,
                    "filterMode": "none",
                },
            ],
            "series": [],
        }
        series = self.seriesPreprocessing()
        # 折线属性
        options["legend"]["data"] = list(map(lambda item: item["name"], series))
        options["series"] = series
        return options

    def seriesPreprocessing(
        self,
        xs: float = -sys.float_info.max,
        xe: float = sys.float_info.max,
        ys: float = -sys.float_info.max,
        ye: float = sys.float_info.max,
    ) -> dict:
        """
        描述:
            通过采样算法和要绘制的图形区域，预处理要绘制的数据

        参数:
            xs (float, optional): 缩放后x轴的起始值
            xe (float, optional): 缩放后x轴的终止值
            ys (float, optional): 缩放后y轴的起始值
            ye (float, optional): 缩放后y轴的终止值

        返回值:
            dict: echart中option的series项
        """
        # 获取算法
        samplingMethod = getSamplingMethod(appConfig.get(appConfig.chartSampling))
        # 获取降采样点后的数量
        insidePointNum = int(appConfig.get(appConfig.insidePointNum))
        partPointNum = int(appConfig.get(appConfig.partPointNum))
        outsidePointNum = int(appConfig.get(appConfig.outsidePointNum))
        # 图像绘制预处理
        series = []
        for i in range(self.fieldTree.topLevelItemCount()):
            topItem = self.fieldTree.topLevelItem(i)
            for j in range(topItem.childCount()):
                # 父选项名称
                topFieldText = topItem.text(0)
                # 子选项
                innerItem = topItem.child(j)
                # 如果属性被选中
                if innerItem.checkState(0) == Qt.CheckState.Checked:
                    # 获取属性
                    innerFieldText = innerItem.text(0)
                    data = self.fields[topFieldText][innerFieldText]
                    # 折线属性
                    times = self.fields[topFieldText]["timestamp"]
                    values = data["value"]
                    zoom, offset = data["zoom"], data["offset"]
                    # numpy合并
                    optionData = np.stack((times, values * zoom + offset), axis=1)
                    # 使用布尔索引过滤数据
                    # x轴方向条件
                    x_condition = (optionData[:, 0] >= xs) & (optionData[:, 0] <= xe)
                    x_left_condition = optionData[:, 0] <= xs
                    x_right_condition = optionData[:, 0] >= xe
                    # y轴方向条件
                    y_condition = (optionData[:, 1] >= ys) & (optionData[:, 1] <= ye)
                    y_top_condition = optionData[:, 1] >= ye
                    y_bottom_condition = optionData[:, 1] <= ys
                    # 画图区域被划为五部分、分别是左侧x_left、y_top、inside、y_bottom、x_right
                    # 其中x_left和x_right区域完全不会显示出
                    # y_top和y_bottom则可能存在部分点和inside部分有联系
                    insideData = optionData[x_condition & y_condition]
                    leftData = optionData[x_left_condition]
                    rightData = optionData[x_right_condition]
                    topData = optionData[x_condition & y_top_condition]
                    bottomData = optionData[x_condition & y_bottom_condition]
                    # 对topData、insideData、rightData采样和合并
                    centerData = np.concatenate(
                        (
                            samplingMethod(topData, partPointNum),
                            samplingMethod(insideData, insidePointNum),
                            samplingMethod(bottomData, partPointNum),
                        ),
                        axis=0,
                    )
                    # 按时间排序
                    centerData = centerData[np.argsort(centerData[:, 0])]
                    # 完全合并
                    optionData = np.concatenate(
                        (
                            samplingMethod(leftData, outsidePointNum),
                            centerData,
                            samplingMethod(rightData, outsidePointNum),
                        ),
                        axis=0,
                    ).tolist()
                    series.append(
                        {
                            "name": f"{topFieldText}.{innerFieldText}",
                            "type": appConfig.get(appConfig.chartType),
                            "data": optionData,
                            # 点大小
                            "symbolSize": 2,
                            # 关闭动画
                            "animation": "false",
                            # 大数据优化,对type为line不生效
                            "large": "true",
                        }
                    )
        return series

    def zoomDrawChart(
        self,
        xs: float = -sys.float_info.max,
        xe: float = sys.float_info.max,
        ys: float = -sys.float_info.max,
        ye: float = sys.float_info.max,
    ):
        """
        描述:
            缩放后重绘echart图像

        参数:
            xs (float): 缩放后x轴的起始值
            xe (float): 缩放后x轴的终止值
            ys (float): 缩放后y轴的起始值
            ye (float): 缩放后y轴的终止值
        """
        series = self.seriesPreprocessing(xs, xe, ys, ye)
        # 对insideX和insideY设置缩放后的起始值和终止值
        options = {
            "dataZoom": [
                {"id": "insideX", "startValue": xs, "endValue": xe},
                {"id": "insideY", "startValue": ys, "endValue": ye},
            ],
            "series": series,
        }
        # 画图
        self.htmlWidget.page().runJavaScript(
            f"""
            myChart.setOption(eval({options}))
            """
        )
