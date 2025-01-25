from qfluentwidgets import FluentStyleSheet
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QColor

from src.gui.components import LogInfoDialogUI


class LogInfoDialog(MaskDialogBase, LogInfoDialogUI):
    def __init__(self, infoData=None, parameterData=None, parent=None):
        super().__init__(parent=parent)
        # 应用样式
        FluentStyleSheet.DIALOG.apply(self.widget)
        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self.setClosableOnMaskClicked(True)
        self.setContentsMargins(40, 40, 40, 40)
        # 初始化UI
        self.initUI(self.widget)
        self.widget.setLayout(self.dialogLayout)
        # 展示数据
        self.displayInfoData(infoData)
        # 展示初始参数
        self.displayParameterData(parameterData)

    def displayInfoData(self, infoData):
        """
        描述:
            初始化表格信息

        参数:
            infoData (_type_): _description_
        """
        if not infoData:
            return
        self.infoTable.setItem(0, 0, QTableWidgetItem("开始时间"))
        self.infoTable.setItem(0, 1, QTableWidgetItem(infoData["time"]["start"]))
        self.infoTable.setItem(1, 0, QTableWidgetItem("持续时间"))
        self.infoTable.setItem(1, 1, QTableWidgetItem(infoData["time"]["duration"]))
        self.infoTable.setItem(2, 0, QTableWidgetItem("结束时间"))
        self.infoTable.setItem(2, 1, QTableWidgetItem(infoData["time"]["stop"]))
        self.infoTable.setItem(3, 0, QTableWidgetItem("dropouts.count"))
        self.infoTable.setItem(4, 0, QTableWidgetItem("dropouts.totalDuration"))
        self.infoTable.setItem(5, 0, QTableWidgetItem("dropouts.max"))
        self.infoTable.setItem(6, 0, QTableWidgetItem("dropouts.min"))
        self.infoTable.setItem(7, 0, QTableWidgetItem("dropouts.mean"))
        self.infoTable.setItem(8, 0, QTableWidgetItem("固件版本"))
        self.infoTable.setItem(9, 0, QTableWidgetItem("硬件版本"))
        self.infoTable.setItem(10, 0, QTableWidgetItem("系统名称"))

        # dropouts
        if "dropouts" in infoData:
            # 有dropouts
            self.infoTable.setItem(
                3, 1, QTableWidgetItem(infoData["dropouts"]["count"])
            )
            self.infoTable.setItem(
                3, 1, QTableWidgetItem(infoData["dropouts"]["totalDuration"])
            )
            self.infoTable.setItem(3, 1, QTableWidgetItem(infoData["dropouts"]["min"]))
            self.infoTable.setItem(3, 1, QTableWidgetItem(infoData["dropouts"]["max"]))
            self.infoTable.setItem(3, 1, QTableWidgetItem(infoData["dropouts"]["mean"]))

        if "firmwareVersion" in infoData:
            self.infoTable.setItem(8, 1, QTableWidgetItem("firmwareVersion"))
        if "hardwareVersion" in infoData:
            self.infoTable.setItem(9, 1, QTableWidgetItem("hardwareVersion"))
        if "systemName" in infoData:
            self.infoTable.setItem(9, 1, QTableWidgetItem("systemName"))

    def displayParameterData(self, parameterData):
        if not parameterData:
            return
        self.parameterTable.setRowCount(len(parameterData))
        for i, key in enumerate(parameterData):
            self.parameterTable.setItem(i, 0, QTableWidgetItem(key))
            self.parameterTable.setItem(i, 1, QTableWidgetItem(str(parameterData[key])))
