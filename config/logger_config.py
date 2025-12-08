#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置文件

该文件定义了项目中所有模块的日志配置，确保所有日志都输出到统一的目录结构中。
"""

import os
import logging
from datetime import datetime

# 导入目录配置
from .directory_config import LOGS_DIRS, get_date_subdir

# 创建日志目录（如果不存在）
for dir_path in LOGS_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)

# 获取当前日期的日志目录
def get_log_file_path(log_type):
    """
    获取日志文件的完整路径
    
    参数:
        log_type (str): 日志类型，对应LOGS_DIRS中的键
    
    返回:
        str: 日志文件的完整路径
    """
    if log_type not in LOGS_DIRS:
        log_type = 'SYSTEM'  # 默认使用系统日志目录
    
    date_subdir = get_date_subdir()
    log_dir = os.path.join(LOGS_DIRS[log_type], date_subdir)
    os.makedirs(log_dir, exist_ok=True)
    
    current_time = datetime.now().strftime('%H%M%S')
    log_file = f"{log_type.lower()}_{current_time}.log"
    
    return os.path.join(log_dir, log_file)

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 创建不同类型的日志记录器
def create_logger(name, log_type='SYSTEM', level=logging.INFO):
    """
    创建一个自定义的日志记录器
    
    参数:
        name (str): 日志记录器的名称
        log_type (str): 日志类型，对应LOGS_DIRS中的键
        level (int): 日志级别
    
    返回:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建文件处理器
        log_file = get_log_file_path(log_type)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# 预定义的日志记录器
data_logger = create_logger('data', 'DATA_FETCHING')
factor_calculation_logger = create_logger('factor_calculation', 'FACTOR_CALCULATION')
factor_analysis_logger = create_logger('factor_analysis', 'FACTOR_ANALYSIS')
backtest_logger = create_logger('backtest', 'BACKTEST')
system_logger = create_logger('system', 'SYSTEM')