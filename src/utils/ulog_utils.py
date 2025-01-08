from pyulog import ULog


def get_logged_message(ulog: ULog) -> list:
    """
    描述:
        获取ulog文件记录的信息

    参数:
        ulog (ULog): ulog文件,使用pyulog.ULog创建

    返回值:
        list: [timestamp,level,mesage]列表,对应pyulog.core中的MessageLogging类
    """
    return [
        [
            "{:02d}:{:02d}:{:03d}".format(
                int(m.timestamp // 6e7),
                int(m.timestamp % 6e7 // 1e6),
                int(m.timestamp % 1e6 // 1e3),
            ),
            m.log_level_str(),
            m.message,
        ]
        for m in ulog.logged_messages
    ]


def get_initial_parameters(ulog: ULog) -> dict:
    """
    描述:
        获取ulog文件的初始参数信息

    参数:
        ulog (ULog): ulog文件,使用pyulog.ULog创建

    返回值:
        dict: key-value字典
    """
    # ulog的获取初始参数
    initial_parameters = ulog.initial_parameters
    if len(initial_parameters) == 0:
        initial_parameters = ulog.get_default_parameters(0)
    if len(initial_parameters) == 0:
        initial_parameters = ulog.get_default_parameters(1)
    if len(initial_parameters) == 0:
        initial_parameters = {}
        # changed_parameters参数去重
        for parameters in ulog.changed_parameters:
            if parameters[1] not in initial_parameters.keys():
                initial_parameters[parameters[1]] = parameters[2]
    return initial_parameters


def get_change_parameters(ulog: ULog) -> list:
    """
    描述:
        获取改变了的参数

    参数:
        ulog (ULog): ulog文件,使用pyulog.ULog创建

    返回值:
        list: (timestamp,key,value)元组列表
    """
    changed_parameters = ulog.changed_parameters
    return changed_parameters


def get_fields_dict(ulog: ULog) -> dict:
    """
    描述:
        获取属性字典

    参数:
        ulog (ULog): ulog文件,使用pyulog.ULog创建

    返回值:
        dict: 字典结构如下:
        {
            "顶层属性名":{
                "属性名":{
                    "value":"",
                    "type":""
                    "offset":0.0,
                    "zoom":1.0
                },
                "timestamp":[]
            }
        }
    """
    # 获取ulog文件的数据列表
    data_list = ulog.data_list
    # 获取所有的属性列表
    fields = {}
    for data in data_list:
        fields[data.name] = {}
        t_filed = fields[data.name]
        for field in data.field_data:
            if field.field_name == "timestamp":
                # 时间需要单独处理
                t_filed[field.field_name] = data.data[field.field_name]
            else:
                t_filed[field.field_name] = {
                    "type": field.type_str,
                    "value": data.data[field.field_name],
                    "offset": 0.0,
                    "zoom": 1.0,
                }
    return fields


def get_ulog_info(ulog: ULog, verbose=False) -> tuple:
    """
    描述:
        获取ulog文件的基本信息

    参数:
        ulog (ULog): ulog文件,使用pyulog.ULog创建

    返回值:
        tuple: (dict,list)元组,list为错误信息
    """
    # 如果文件损坏则为True
    errors = []
    if ulog.file_corruption:
        errors.append("Warning: file has data corruption(s)")
    # 计算开始、持续、停止时间
    result = {}
    m1, s1 = divmod(int(ulog.start_timestamp / 1e6), 60)
    h1, m1 = divmod(m1, 60)
    m3, s3 = divmod(int(ulog.last_timestamp / 1e6), 60)
    h3, m3 = divmod(m3, 60)
    m2, s2 = divmod(int((ulog.last_timestamp - ulog.start_timestamp) / 1e6), 60)
    h2, m2 = divmod(m2, 60)
    result["time"] = {
        "start": "{:d}:{:02d}:{:02d}".format(h1, m1, s1),
        "duration": "{:d}:{:02d}:{:02d}".format(h2, m2, s2),
        "stop": "{:d}:{:02d}:{:02d}".format(h3, m3, s3),
    }

    dropout_durations = [dropout.duration for dropout in ulog.dropouts]
    if len(dropout_durations) == 0:
        errors.append("No Dropouts")
    else:
        result["dropouts"] = {
            "count": len(dropout_durations),
            "totalDuration": sum(dropout_durations) / 1000.0,
            "max": max(dropout_durations),
            "min": min(dropout_durations),
            "mean": int(sum(dropout_durations) / len(dropout_durations)),
        }
    # 版本
    version = ulog.get_version_info_str()
    if not version is None:
        result["SW Version"] = version
    if len(ulog.msg_info_dict) > 0:
        result["firmwareVersion"] = ulog.msg_info_dict["ver_sw"]
        result["hardwareVersion"] = ulog.msg_info_dict["ver_hw"]
        result["systemName"] = ulog.msg_info_dict["sys_name"]
    return result, errors


def ulog_timestamp_to_time(timestamp: int, type: int) -> str | float:
    """
    描述:
        将ulog文件的时间戳转换为所需的时间

    参数:
        timestamp (int): 时间戳
        type (int): 所需的时间类型

    返回值:
        str|float: 修改后的时间
    """
    if type == 0:
        # Boot时间
        return timestamp / 1e6
    elif type == 1:
        # GPS时间
        return "{:02d}:{:02d}:{:03d}".format(
            int(timestamp // 6e7),
            int(timestamp % 6e7 // 1e6),
            int(timestamp % 1e6 // 1e3),
        )
    else:
        return timestamp
