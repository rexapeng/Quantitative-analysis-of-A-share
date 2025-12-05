# -*- coding: utf-8 -*-
"""
量化分析项目初始化文件
设置本地QLib库路径，确保优先使用本地克隆的版本
"""

import os
import sys

# 获取当前文件的目录（项目根目录）
project_root = os.path.dirname(os.path.abspath(__file__))

# 将本地克隆的QLib库路径添加到Python路径的最前面
local_qlib_path = os.path.join(project_root, 'qlib')
if local_qlib_path not in sys.path:
    sys.path.insert(0, local_qlib_path)

# 打印调试信息（可选）
# print(f"项目根目录: {project_root}")
# print(f"本地QLib路径: {local_qlib_path}")
# print(f"Python路径: {sys.path[:5]}")

__version__ = "1.0.0"
