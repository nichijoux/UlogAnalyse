import sys, re

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


class ThresholdValidator(ConfigValidator):
    defaultValue: int

    def __init__(self, value: int):
        super().__init__()
        self.defaultValue = value

    """
    图像采样阈值设置

    参数:
        ConfigValidator (_type_): _description_
    """

    def validate(self, value: str) -> bool:
        if type(value) == str and re.match(r"^\d+$", value):
            return True
        else:
            return False

    def correct(self, value) -> str:
        return value if self.validate(value) else "6000"


class Config(QConfig):
    # 导出路径
    importFolder = ConfigItem(
        "Software", "ImportFolder", QDir.currentPath(), FolderValidator()
    )
    # 参数配置文件
    fieldsConfig = ConfigItem("Software", "FieldsConfig", "", restart=True)
    # 图表类型
    chartType = OptionsConfigItem(
        "Software",
        "ChartType",
        "line",
        OptionsValidator(["line", "scatter"]),
        restart=False,
    )
    # 图表采样
    chartSampling = OptionsConfigItem(
        "Software",
        "ChartSampling",
        "lttb",
        OptionsValidator(["lttb", "average", "min", "max", "none"]),
        restart=False,
    )
    # 图表采样阈值
    insidePointNum = ConfigItem(
        "Software",
        "InsidePointNum",
        "1000",
        ThresholdValidator(1000),
        restart=False,
    )
    partPointNum = ConfigItem(
        "Software",
        "PartPointNum",
        "200",
        ThresholdValidator(200),
        restart=False,
    )
    outsidePointNum = ConfigItem(
        "Software",
        "OutsidePointNum",
        "100",
        ThresholdValidator(100),
        restart=False,
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
    "VERSION": "1.2.0",
    "AUTHOR_URL": "https://github.com/nichijoux",
    "PROJECT_DOWNLOAD_URL": "https://github.com/nichijoux/UlogAnalyse/releases",
    "FEEDBACK_URL": "https://github.com/nichijoux/UlogAnalyse/issues",
}

appConfig = Config()
