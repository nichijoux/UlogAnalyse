from qfluentwidgets import FluentStyleSheet, TitleLabel, TableWidget
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt, QMetaObject


class LogInfoDialogUI(object):
    def initUI(self, dialog):
        self.dialogLayout = QVBoxLayout(dialog)

        titleLayout = QHBoxLayout()
        titleLayout.setContentsMargins(5, 5, 5, 5)
        self.title = TitleLabel("日志信息")
        titleLayout.addStretch()
        titleLayout.addWidget(self.title)
        titleLayout.addStretch()
        # 信息表格
        self.infoTable = TableWidget()
        self.infoTable.setRowCount(11)
        self.infoTable.horizontalHeader().setMinimumWidth(100)
        self.infoTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # 启用边框并设置圆角
        self.infoTable.setBorderVisible(True)
        self.infoTable.setBorderRadius(8)
        # 设置行列数
        self.infoTable.setColumnCount(2)
        # 设置水平表头
        self.infoTable.setHorizontalHeaderLabels(["参数", "值"])
        # 隐藏垂直表头
        self.infoTable.verticalHeader().hide()
        # 单选模式
        self.infoTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 禁止双击编辑
        self.infoTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 设置换行
        self.infoTable.setWordWrap(False)

        self.parameterTable = TableWidget()
        self.parameterTable.horizontalHeader().setMinimumWidth(100)
        self.parameterTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # 启用边框并设置圆角
        self.parameterTable.setBorderVisible(True)
        self.parameterTable.setBorderRadius(8)
        # 设置行列数
        self.parameterTable.setColumnCount(2)
        # 设置水平表头
        self.parameterTable.setHorizontalHeaderLabels(["参数", "值"])
        # 隐藏垂直表头
        self.parameterTable.verticalHeader().hide()
        # 单选模式
        self.parameterTable.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        # 禁止双击编辑
        self.parameterTable.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        # 设置换行
        self.parameterTable.setWordWrap(False)

        # 添加标题
        self.dialogLayout.addWidget(self.title)
        # 添加表格信息
        tableLayout = QHBoxLayout()
        tableLayout.addSpacing(8)
        tableLayout.addWidget(self.infoTable)
        tableLayout.addSpacing(12)
        tableLayout.addWidget(self.parameterTable)
        tableLayout.addSpacing(8)

        # 组装UI
        self.dialogLayout.setContentsMargins(36, 24, 36, 24)
        self.dialogLayout.addLayout(titleLayout)
        self.dialogLayout.addSpacing(12)
        self.dialogLayout.addLayout(tableLayout)
        QMetaObject.connectSlotsByName(dialog)
