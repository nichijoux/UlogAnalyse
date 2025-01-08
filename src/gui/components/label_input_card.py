from qfluentwidgets import StrongBodyLabel, LineEdit, CardWidget
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtCore import QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator


class LabelInputCard(CardWidget):
    # 定义信号
    editingFinished = pyqtSignal(float)

    def setInitValue(self, initValue: float):
        """
        描述:
            设置初始值

        参数:
            initValue (float): 初始值
        """
        self.inputEdit.setText(str(initValue))

    def setRegularExpression(self, regStr: str):
        """
        描述:
            设置正则字符串规则
        参数:
            regStr (str): 正则字符串
        """
        expression = QRegularExpression(regStr)
        validator = QRegularExpressionValidator(self)
        validator.setRegularExpression(expression)
        self.inputEdit.setValidator(validator)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.text = StrongBodyLabel(text)
        # 设置字体大小
        self.text.setStyleSheet("font-size: 16px;font-weight:bold;")
        self.inputEdit = LineEdit()
        # 设置为按下回车、返回或失去焦点时触发
        self.inputEdit.editingFinished.connect(
            lambda: self.editingFinished.emit(float(self.inputEdit.text()))
        )

        layout.addSpacing(12)
        layout.addWidget(self.text)
        layout.addStretch(0)
        layout.addWidget(self.inputEdit)
        layout.addSpacing(12)
        # 设置窗体布局和大小
        self.setLayout(layout)
