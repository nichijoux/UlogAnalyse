<p align="center">
    <h1>UlogAnalyse</h1>
    <br>
    <div align="center">
        <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-1082C3" alt="Platform">
        <img src="https://img.shields.io/github/downloads/nichijoux/UlogAnalyse/total?color=1082C3" alt="Downloads">
        <img src="https://img.shields.io/github/license/nichijoux/UlogAnalyse?color=1082C3" alt="License">
    </div>
</p>

## 介绍

UlogAnalyse 日志分析软件是一个基于 PyQt6、qfluentwidgets、pyulog 和 EChart 的日志查看工具，可以通过图形化的界面查看 ulg 文件的各项参数

## 特色

- 支持打开一个和多个 ulg 文件
  - 可对 ulg 数据进行显示
  - 可对 ulg 属性进行缩放和偏移
  - 同时打开多个 ulg 文件,软件将会视其为同一组 ulg 文件,属性将被合并
- 将ulg文件导出csv文件
- 现代化的 UI 界面
  - 适配浅色和深色模式跟随
  - 基于 qfluentwidgets 的 UI
  - 基于 echart 的数据图像显示
  - 可对图像进行局部缩放和拖动显示
  - 点击日志表格项可添加和删除指示线
- 个性化设置
  - 设置导出文件路径
  - 设置导出
  - 设置 echart 图表采样算法和阈值
  - 可根据 json 文件显示 ulg 对应属性名,如根据 parameter_dict.json 可在选中 flight.flight_mode 时在显示对应配置

## 使用方法

<p align="center">
    <img src="images/usage.gif" width=88% alt="usage">
</p>

1. 点击打开日志按钮，选择一个或一组 ulg 文件
2. 点击左侧属性列表，选择日志所拥有的属性
3. 可对属性值进行缩放
4. 查看右边图表

## 反馈

如需要更多功能支持，请在 Issues 中提出，酌情添加

如遇到程序错误，请在 Issues 中详细描述，并告知所用操作系统（Windows 11 or macOS 14.2）

## 致谢

[[pyulog]](https://github.com/PX4/pyulog) ulog 日志解析的 python 库

[[Ghost-Downloader-3]](https://github.com/XiaoYouChR/Ghost-Downloader-3/tree/main) 参考了其部分实现代码

[[bangumi-renamer]](https://github.com/nuthx/bangumi-renamer) 参考了其部分代码和构建脚本

## 免责

本项目代码仅供学习交流，不得用于商业用途，若侵权请联系
