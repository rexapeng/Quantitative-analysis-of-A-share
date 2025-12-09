#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具

该模块提供统一的文件保存和目录管理功能，确保所有生成的文件都按照类型和日期存储在正确的位置。
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config.config import (
    REPORTS_DIRS, FACTOR_RESULTS_DIRS, BACKTEST_RESULTS_DIRS,
    get_full_path, create_all_directories
)

class FileManager:
    """
    文件管理器类，用于统一管理文件的保存
    """
    
    def __init__(self):
        """初始化文件管理器"""
        # 确保所有目录都已创建
        create_all_directories()
        
    def save_file(self, content, file_type, file_name, with_datetime=False, **kwargs):
        """
        保存文件到相应的目录
        
        参数:
            content: 要保存的内容，可以是字符串、DataFrame或其他可序列化对象
            file_type (str): 文件类型，决定保存的目录
            file_name (str): 文件名（不含扩展名）
            with_datetime (bool): 是否在文件名中包含日期时间，默认False
            **kwargs: 其他参数，如格式等
            
        返回:
            str: 保存的文件路径
        """
        # 根据文件类型选择目录
        dir_map = {
            # 报告类型
            'factor_report': get_full_path(REPORTS_DIRS['FACTOR_ANALYSIS']),
            'backtest_report': get_full_path(REPORTS_DIRS['BACKTEST']),
            'qlib_report': get_full_path(REPORTS_DIRS['QLIB']),
            'summary_report': get_full_path(REPORTS_DIRS['SUMMARY']),
            
            # 因子结果类型
            'calculated_factor': get_full_path(FACTOR_RESULTS_DIRS['CALCULATED']),
            'analyzed_factor': get_full_path(FACTOR_RESULTS_DIRS['ANALYZED']),
            'ml_factor': get_full_path(FACTOR_RESULTS_DIRS['ML']),
            
            # 回测结果类型
            'strategy_result': get_full_path(BACKTEST_RESULTS_DIRS['STRATEGY']),
            'portfolio_result': get_full_path(BACKTEST_RESULTS_DIRS['PORTFOLIO']),
            'backtest_plot': get_full_path(BACKTEST_RESULTS_DIRS['PLOTS'])
        }
        
        if file_type not in dir_map:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        # 获取保存目录
        save_dir = dir_map[file_type]
        
        # 创建目录（如果不存在）
        os.makedirs(save_dir, exist_ok=True)
        
        # 处理文件名
        if with_datetime:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_file_name = f"{file_name}_{timestamp}{self._get_extension(content, kwargs.get('format'))}"
        else:
            full_file_name = f"{file_name}{self._get_extension(content, kwargs.get('format'))}"
        
        # 完整文件路径
        file_path = os.path.join(save_dir, full_file_name)
        
        # 保存文件
        self._save_content(content, file_path, **kwargs)
        
        return file_path
    
    def _get_extension(self, content, format=None):
        """
        根据内容类型和格式获取文件扩展名
        
        参数:
            content: 要保存的内容
            format (str): 指定的格式
            
        返回:
            str: 文件扩展名（包含点）
        """
        if format:
            return f".{format.lower()}"
        
        if isinstance(content, pd.DataFrame):
            return ".csv"
        elif isinstance(content, dict) or isinstance(content, list):
            return ".json"
        elif isinstance(content, str):
            return ".txt"
        else:
            return ".txt"
    
    def _save_content(self, content, file_path, **kwargs):
        """
        根据内容类型保存文件
        
        参数:
            content: 要保存的内容
            file_path (str): 文件路径
            **kwargs: 其他参数
        """
        if isinstance(content, pd.DataFrame):
            # 保存为CSV
            content.to_csv(file_path, index=kwargs.get('index', True), encoding='utf-8')
        elif isinstance(content, dict) or isinstance(content, list):
            # 保存为JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=kwargs.get('indent', 2), ensure_ascii=False)
        elif isinstance(content, str):
            # 保存为文本文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # 尝试序列化其他类型
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(content))

# 全局文件管理器实例（延迟初始化）
file_manager = None

# 便捷函数
def save_file(content, file_type, file_name, with_datetime=False, **kwargs):
    """便捷函数，调用全局文件管理器的save_file方法"""
    global file_manager
    if file_manager is None:
        file_manager = FileManager()
    return file_manager.save_file(content, file_type, file_name, with_datetime, **kwargs)