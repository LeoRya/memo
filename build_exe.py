# -*- coding: utf-8 -*-
"""
打包脚本：将备忘录程序打包成exe文件
"""
import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller参数
args = [
    'memo_app.py',  # 主程序文件
    '--name=备忘录',  # 应用程序名称
    '--onefile',  # 打包成单个exe文件
    '--windowed',  # 使用窗口模式，不显示控制台
    '--icon=icon.png',  # 程序图标
    '--add-data=icon.png;.',  # 包含图标文件
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
    # 隐藏导入的模块
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
]

# 运行PyInstaller
PyInstaller.__main__.run(args)

print("打包完成！exe文件位于 dist 文件夹中。")
