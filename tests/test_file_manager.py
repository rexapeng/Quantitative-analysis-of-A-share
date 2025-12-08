#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一文件管理系统
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_manager import save_file
from config.logger_config import system_logger

# 创建测试数据
test_data = {
    'factor_name': ['MOM', 'RSI', 'MACD'],
    'ic': [0.05, 0.03, 0.04],
    'ir': [0.3, 0.2, 0.25]
}

test_df = pd.DataFrame(test_data)
test_json = {'test_key': 'test_value', 'test_list': [1, 2, 3]}
test_str = "这是一个测试文本文件"

# 测试保存不同类型的文件
try:
    # 测试保存DataFrame
    df_path = save_file(test_df, 'factor_report', 'test_factor_report')
    system_logger.info(f"已保存DataFrame到: {df_path}")
    
    # 测试保存JSON
    json_path = save_file(test_json, 'backtest_report', 'test_backtest_report')
    system_logger.info(f"已保存JSON到: {json_path}")
    
    # 测试保存文本
    str_path = save_file(test_str, 'summary_report', 'test_summary_report')
    system_logger.info(f"已保存文本到: {str_path}")
    
    # 测试保存带日期时间的文件
    datetime_path = save_file(test_df, 'qlib_report', 'test_qlib_report', with_datetime=True)
    system_logger.info(f"已保存带日期时间的文件到: {datetime_path}")
    
    # 测试保存因子结果
    factor_path = save_file(test_df, 'analyzed_factor', 'test_analyzed_factor')
    system_logger.info(f"已保存因子结果到: {factor_path}")
    
    print("所有文件保存测试通过！")
    print(f"保存的文件路径：")
    print(f"1. DataFrame: {df_path}")
    print(f"2. JSON: {json_path}")
    print(f"3. 文本: {str_path}")
    print(f"4. 带日期时间的文件: {datetime_path}")
    print(f"5. 因子结果: {factor_path}")
    
    # 验证文件是否存在
    for path in [df_path, json_path, str_path, datetime_path, factor_path]:
        if os.path.exists(path):
            print(f"✓ 文件存在: {path}")
        else:
            print(f"✗ 文件不存在: {path}")
            
except Exception as e:
    system_logger.error(f"文件保存测试失败: {e}")
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()