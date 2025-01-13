import numpy as np
from collections import defaultdict
from pyulog import ULog
from src.utils.common_utils import *
from src.utils.ulog_utils import get_fields_dict

fields = get_fields_dict(ULog("/mnt/d/work/1.ulg"))

times = fields["flight"]["timestamp"]
positions = fields["flight"]["velocity[0]"]["value"]

datas = np.stack((times, positions), axis=1)

xs = 329697158.0
xe = 575084270.0
ys = -134.9
ye = 122.5

insideThreshold = 1000
partThreshold = 200
outsideThreshold = 100

x_condition = (datas[:, 0] >= xs) & (datas[:, 0] <= xe)
y_condition = (datas[:, 1] >= ys) & (datas[:, 1] <= ye)
condition = x_condition & y_condition

x_left_condition = datas[:, 0] <= xs
x_right_condition = datas[:, 0] >= xe

y_top_condition = datas[:, 1] >= ye
y_bottom_condition = datas[:, 1] <= ys

insideData = datas[condition]

leftData = datas[x_left_condition]
rightData = datas[x_right_condition]

topData = datas[x_condition & y_top_condition]
bottomData = datas[x_condition & y_bottom_condition]

# 先对topData、insideData、bottomData合并
sampled = getSamplingMethod("min")


# insideData = sampled(insideData, insideThreshold)

# centerData = np.concatenate(
#     (
#         sampled(topData, partThreshold),
#         insideData,
#         sampled(bottomData, partThreshold),
#     ),
#     axis=0,
# )
# # centerData需要排序
# centerData = centerData[np.argsort(centerData[:, 0])]

# leftData = sampled(leftData, outsideThreshold)
# rightData = sampled(rightData, outsideThreshold)

# optionData = np.concatenate((leftData, centerData, rightData), axis=0)

# print(optionData)
# print(len(optionData))

datas = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [7, 9]])



print(np.min(datas, axis=0))

print(sampled(datas, 3))
