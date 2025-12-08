#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因子计算主脚本

该脚本用于计算所有因子并将结果保存在数据库中。
"""

import os
import sys
import time
import json
import logging
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入因子库基础类和工具函数
from factor_lib import (
    Factor, FactorManager,
    get_all_factor_classes, get_factor_classes_by_category,
    get_database_connection, load_stock_data, clean_factor_data, create_factor_table
)

# 设置日志
from config.logger_config import factor_calculation_logger
from config.config import FACTOR_CALCULATION_CONFIG, get_full_path

logger = factor_calculation_logger

# 从配置文件获取配置
START_DATE = FACTOR_CALCULATION_CONFIG['START_DATE']
END_DATE = FACTOR_CALCULATION_CONFIG['END_DATE']
BATCH_SIZE = FACTOR_CALCULATION_CONFIG['BATCH_SIZE']
RESULT_DIR = FACTOR_CALCULATION_CONFIG['RESULT_DIR']


def get_all_factors():
    """
    获取所有因子实例
    
    返回:
        list: 因子实例列表
    """
    factors = []
    
    # 获取所有因子类
    factor_classes = get_all_factor_classes()
    
    # 为不同类型的因子提供不同的窗口参数
    window_params = {
        'VolumeChangeRateFactor': [5, 10, 20],
        'AmountChangeRateFactor': [5, 10, 20],
        'VolumeRankFactor': [10, 20, 30],
        'VolumeMeanFactor': [10, 20, 30],
        'VolumeStdFactor': [10, 20, 30],
        'VolumeToMeanFactor': [10, 20, 30],
        'VolumeAmplitudeFactor': [10, 20, 30],
        'MomentumFactor': [5, 10, 20, 30],
        'RSIFactor': [6, 14, 24],
        'WilliamsRFactor': [10, 20],
        'StochasticFactor': [14, 20],
        'RateOfChangeFactor': [5, 10, 20],
        'BollingerBandsFactor': [20],
        'AverageTrueRangeFactor': [14, 20],
        'VolatilityFactor': [10, 20, 30],
        'DownsideDeviationFactor': [20, 30],
        'UlcerIndexFactor': [14, 20],
        'HistoricalVolatilityFactor': [20, 30],
        'ParkinsonVolatilityFactor': [10, 20]
    }
    
    # 创建因子实例
    for factor_class in factor_classes:
        class_name = factor_class.__name__
        
        # 为需要窗口参数的因子创建多个实例
        if class_name in window_params:
            for window in window_params[class_name]:
                try:
                    factors.append(factor_class(window=window))
                except Exception as e:
                    logger.warning(f"无法创建因子 {class_name}(window={window}): {e}")
        else:
            # 无参数或默认参数的因子
            try:
                factors.append(factor_class())
            except Exception as e:
                logger.warning(f"无法创建因子 {class_name}: {e}")
    
    logger.info(f"已初始化 {len(factors)} 个因子")
    return factors


def calculate_all_factors():
    """
    计算所有因子
    """
    try:
        # 开始时间
        start_time = time.time()
        logger.info("开始计算所有因子...")
        
        # 连接数据库
        conn = get_database_connection()
        if conn is None:
            logger.error("无法连接到数据库，程序退出")
            return False
        
        # 加载股票数据
        logger.info("加载股票数据...")
        stock_data = load_stock_data(conn)
        if stock_data is None or stock_data.empty:
            logger.error("没有加载到股票数据，程序退出")
            conn.close()
            return False
        
        # 初始化因子
        factors = get_all_factors()
        
        # 创建因子管理器
        factor_manager = FactorManager()
        
        # 添加所有因子
        for factor in factors:
            factor_manager.add_factor(factor)
        
        # 计算所有因子
        logger.info("开始计算因子...")
        factor_manager.calculate_all(stock_data)
        
        # 保存因子数据到数据库
        logger.info("保存因子数据到数据库...")
        factor_manager.store_all_to_db(conn)
        
        # 关闭数据库连接
        conn.close()
        
        # 结束时间
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"所有因子计算完成！总耗时: {execution_time:.2f} 秒")
        
        return True
    
    except Exception as e:
        logger.error(f"计算因子时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def calculate_selected_factors(factor_names=None):
    """
    计算指定的因子
    
    参数:
        factor_names: 因子名称列表
    """
    try:
        # 开始时间
        start_time = time.time()
        logger.info(f"开始计算指定因子: {factor_names}...")
        
        # 连接数据库
        conn = get_database_connection()
        if conn is None:
            logger.error("无法连接到数据库，程序退出")
            return False
        
        # 加载股票数据
        logger.info("加载股票数据...")
        stock_data = load_stock_data(conn)
        if stock_data is None or stock_data.empty:
            logger.error("没有加载到股票数据，程序退出")
            conn.close()
            return False
        
        # 初始化所有因子
        all_factors = get_all_factors()
        
        # 选择指定的因子
        if factor_names:
            selected_factors = [f for f in all_factors if f.name in factor_names]
        else:
            selected_factors = all_factors
        
        if not selected_factors:
            logger.error(f"没有找到指定的因子: {factor_names}")
            conn.close()
            return False
        
        logger.info(f"已选择 {len(selected_factors)} 个因子进行计算")
        
        # 创建因子管理器
        factor_manager = FactorManager(selected_factors)
        
        # 计算因子
        logger.info("开始计算因子...")
        factor_manager.calculate_all(stock_data)
        
        # 保存因子数据到数据库
        logger.info("保存因子数据到数据库...")
        factor_manager.store_all_to_db(conn)
        
        # 关闭数据库连接
        conn.close()
        
        # 结束时间
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"因子计算完成！总耗时: {execution_time:.2f} 秒")
        
        return True
    
    except Exception as e:
        logger.error(f"计算因子时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """
    主函数
    """
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='计算因子并保存到数据库')
    parser.add_argument('--factors', type=str, nargs='+', help='指定要计算的因子名称')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    if args.factors:
        # 计算指定的因子
        success = calculate_selected_factors(args.factors)
    else:
        # 计算所有因子
        success = calculate_all_factors()
    
    if success:
        logger.info("程序执行成功")
        sys.exit(0)
    else:
        logger.error("程序执行失败")
        sys.exit(1)


if __name__ == '__main__':
    main()