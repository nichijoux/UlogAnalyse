from qfluentwidgets import SettingCard, LineEdit, ConfigItem, qconfig

from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator


class InputSettingCard(SettingCard):

    def __init__(
        self,
        configItem: ConfigItem,
        regStr: str,
        icon,
        title,
        content=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        # 配置项
        self.configItem = configItem
        # 输入框
        self.inputEdit = LineEdit()
        self.inputEdit.setText(qconfig.get(configItem))
        # 设置输入正则
        if regStr:
            expression = QRegularExpression(regStr)
            validator = QRegularExpressionValidator(self)
            validator.setRegularExpression(expression)
            self.inputEdit.setValidator(validator)
        # 添加ui
        self.hBoxLayout.addWidget(self.inputEdit, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        # 初始化connect
        # 将configItem的值改变和setValue关联起来
        configItem.valueChanged.connect(self.setValue)

    def setValue(self, value):
        """
        描述:
            此函数是用来设置初始值的

        参数:
            value (_type_): inputEdit的参数
        """
        self.inputEdit.setText(value)
        qconfig.set(self.configItem, value)
