import sys

from PyQt6.QtCore import QRect, QDir
from qfluentwidgets import (
    QConfig,
    ConfigItem,
    OptionsConfigItem,
    OptionsValidator,
    ConfigValidator,
    ConfigSerializer,
    FolderValidator,
)


class GeometryValidator(ConfigValidator):
    """
    描述:
        geometry 为程序的位置和大小, 保存为字符串 "x,y,w,h," 默认为 Default
    """

    def validate(self, value: QRect) -> bool:
        if value == "Default":
            return True
        if type(value) == QRect:
            return True

    def correct(self, value) -> str:
        return value if self.validate(value) else "Default"


class GeometrySerializer(ConfigSerializer):
    """
    描述:
        字符串 "x,y,w,h," 转换为QRect (x, y, w, h), "Default" 除外

    参数:
        ConfigSerializer (_type_): _description_
    """

    def serialize(self, value: QRect) -> str:
        if value == "Default":
            return value
        return f"{value.x()},{value.y()},{value.width()},{value.height()}"

    def deserialize(self, value: str) -> QRect:
        if value == "Default":
            return value
        x, y, w, h = map(int, value.split(","))
        return QRect(x, y, w, h)


class Config(QConfig):
    # 导出路径
    importFolder = ConfigItem(
        "Import", "ImportFolder", QDir.currentPath(), FolderValidator()
    )
    if sys.platform == "win32":
        backgroundEffect = OptionsConfigItem(
            "Personalization",
            "BackgroundEffect",
            "Mica",
            OptionsValidator(["Acrylic", "Mica", "MicaAlt", "Aero"]),
        )
    # dpi缩放
    dpiScale = OptionsConfigItem(
        "Personalization",
        "DpiScale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )
    # 是否显示警告信息
    dangerMessage = OptionsConfigItem(
        "Personalization",
        "DangerMessage",
        "一直显示",
        OptionsValidator(["一直显示", "不再显示"]),
        restart=False,
    )
    # 图标类型
    chartType = OptionsConfigItem(
        "Software",
        "ChartType",
        "line",
        OptionsValidator(["line", "scatter"]),
        restart=False,
    )
    # 保存程序的位置和大小, Validator 在 mainWindow 中设置
    geometry = ConfigItem(
        "Software", "Geometry", "Default", GeometryValidator(), GeometrySerializer()
    )

    # 程序运行路径
    def __init__(self):
        super().__init__()


COPYRIGHT = {
    "YEAR": 2025,
    "AUTHOR": "nichijoux",
    "VERSION": "1.0.0",
    "AUTHOR_URL": "https://github.com/nichijoux",
    "FEEDBACK_URL": "https://github.com/nichijoux/UlogAnalyse/issues",
}


appConfig = Config()
