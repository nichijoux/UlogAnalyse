from qfluentwidgets import StrongBodyLabel, CardWidget, BodyLabel
from PyQt6.QtWidgets import QHBoxLayout


class LabelTextCard(CardWidget):

    def setText(self, text: str):
        self.text.setText(text)

    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 12, 5, 12)

        self.label = StrongBodyLabel(label)
        # 设置字体大小
        self.label.setStyleSheet("font-size: 16px;font-weight:bold;")
        # 文字
        self.text = BodyLabel()

        layout.addSpacing(12)
        layout.addWidget(self.label)
        layout.addStretch(0)
        layout.addWidget(self.text)
        layout.addSpacing(12)

        self.setLayout(layout)
