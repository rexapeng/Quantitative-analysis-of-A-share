#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录结构配置文件

该文件定义了项目中所有生成文件的统一目录结构。
"""

import os
import sys
from datetime import datetime

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 基础目录
BASE_DIRS = {
    'DATA': os.path.join(PROJECT_ROOT, 'data'),
    'REPORTS': os.path.join(PROJECT_ROOT, 'reports'),
    'LOGS': os.path.join(PROJECT_ROOT, 'logs'),
    'FACTOR_RESULTS': os.path.join(PROJECT_ROOT, 'factor_results'),
    'BACKTEST_RESULTS': os.path.join(PROJECT_ROOT, 'backtest_results'),
    'TEMP': os.path.join(PROJECT_ROOT, 'temp')
}

# 数据目录细分
DATA_DIRS = {
    'RAW': os.path.join(BASE_DIRS['DATA'], 'raw'),
    'PROCESSED': os.path.join(BASE_DIRS['DATA'], 'processed'),
    'DATABASE': os.path.join(BASE_DIRS['DATA'], 'data')
}

# 报告目录细分
REPORTS_DIRS = {
    'FACTOR_ANALYSIS': os.path.join(BASE_DIRS['REPORTS'], 'factor_analysis'),
    'BACKTEST': os.path.join(BASE_DIRS['REPORTS'], 'backtest'),
    'QLIB': os.path.join(BASE_DIRS['REPORTS'], 'qlib'),
    'SUMMARY': os.path.join(BASE_DIRS['REPORTS'], 'summary')
}

# 日志目录细分
LOGS_DIRS = {
    'DATA_FETCHING': os.path.join(BASE_DIRS['LOGS'], 'data_fetching'),
    'FACTOR_CALCULATION': os.path.join(BASE_DIRS['LOGS'], 'factor_calculation'),
    'FACTOR_ANALYSIS': os.path.join(BASE_DIRS['LOGS'], 'factor_analysis'),
    'BACKTEST': os.path.join(BASE_DIRS['LOGS'], 'backtest'),
    'SYSTEM': os.path.join(BASE_DIRS['LOGS'], 'system')
}

# 因子结果目录细分
FACTOR_RESULTS_DIRS = {
    'CALCULATED': os.path.join(BASE_DIRS['FACTOR_RESULTS'], 'calculated'),
    'ANALYZED': os.path.join(BASE_DIRS['FACTOR_RESULTS'], 'analyzed'),
    'ML': os.path.join(BASE_DIRS['FACTOR_RESULTS'], 'machine_learning')
}

# 回测结果目录细分
BACKTEST_RESULTS_DIRS = {
    'STRATEGY': os.path.join(BASE_DIRS['BACKTEST_RESULTS'], 'strategy'),
    'PORTFOLIO': os.path.join(BASE_DIRS['BACKTEST_RESULTS'], 'portfolio'),
    'PLOTS': os.path.join(BASE_DIRS['BACKTEST_RESULTS'], 'plots')
}

# 为所有目录添加按日期的子目录
def get_date_subdir():
    """获取当前日期的子目录名称，格式为YYYYMMDD"""
    return datetime.now().strftime('%Y%m%d')

def get_datetime_subdir():
    """获取当前日期时间的子目录名称，格式为YYYYMMDD_HHMMSS"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

# 带有日期子目录的完整路径
def get_full_path(base_dir, with_datetime=False):
    """
    获取带有日期或日期时间子目录的完整路径
    
    参数:
        base_dir (str): 基础目录路径
        with_datetime (bool): 是否包含时间信息，默认False
    
    返回:
        str: 完整的路径
    """
    if with_datetime:
        return os.path.join(base_dir, get_datetime_subdir())
    return os.path.join(base_dir, get_date_subdir())

# 创建所有目录的函数
def create_all_directories():
    """创建所有需要的目录"""
    # 合并所有目录
    all_dirs = {**BASE_DIRS, **DATA_DIRS, **REPORTS_DIRS, **LOGS_DIRS, **FACTOR_RESULTS_DIRS, **BACKTEST_RESULTS_DIRS}
    
    for dir_path in all_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
        print(f"已创建目录: {dir_path}")

# 初始化函数
# 只有当直接运行该文件时才创建目录，避免被导入时自动执行
if __name__ == "__main__":
    create_all_directories()