from qfluentwidgets import FluentStyleSheet, PushButton, TitleLabel
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QColor

class MessageDialog(MaskDialogBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        FluentStyleSheet.DIALOG.apply(self)
        # 设置遮罩
        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self.setClosableOnMaskClicked(True)
        self.setContentsMargins(40, 40, 40, 40)
        # 布局
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        # 信息区
        messageLayout = QHBoxLayout()
        self.message = TitleLabel("信息")
        messageLayout.addStretch()
        messageLayout.addWidget(self.message)
        messageLayout.addStretch()
        # 按钮区
        self.yesButton = PushButton("确定")
        self.cancelButton = PushButton("不再显示")
        buttonLayout = QHBoxLayout()
        buttonLayout.addSpacing(12)
        buttonLayout.addWidget(self.yesButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addSpacing(12)
        # 设置布局
        layout.addSpacing(10)
        layout.addLayout(messageLayout)
        layout.addSpacing(10)
        layout.addLayout(buttonLayout)
        layout.addSpacing(10)
        self.widget.setLayout(layout)
