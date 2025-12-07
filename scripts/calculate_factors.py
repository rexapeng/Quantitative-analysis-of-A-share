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

# 导入因子库
from factor_lib import (
    # 基础类
    Factor, FactorManager,
    
    # 价格类因子
    ClosePriceFactor, HighPriceFactor, LowPriceFactor, OpenPriceFactor,
    AveragePriceFactor, VWAPFactor, CloseToOpenRatioFactor, PriceRankFactor,
    PriceDecayFactor, OpenToCloseChangeFactor, PriceMeanFactor,
    
    # 成交量类因子
    VolumeFactor, AmountFactor, VolumeChangeRateFactor, AmountChangeRateFactor,
    VolumeRankFactor, VolumeMeanFactor, VolumeStdFactor, VolumeToMeanFactor,
    VolumeAmplitudeFactor, VolumeAccumulationFactor,
    
    # 波动性类因子
    DailyReturnFactor, DailyAmplitudeFactor, VolatilityFactor, DownsideRiskFactor,
    MaximumDrawdownFactor, SharpeRatioFactor, SkewnessFactor, KurtosisFactor,
    
    # 动量类因子
    MomentumFactor, RSIFactor, MACDFactor, WilliamsRFactor, StochasticFactor,
    RateOfChangeFactor,
    
    # 自定义因子
    KDJ_J_Factor, MACD_DIFF_Factor,
    
    # 工具函数
    get_database_connection, load_stock_data, clean_factor_data, create_factor_table
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calculate_factors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_all_factors():
    """
    获取所有因子实例
    
    返回:
        list: 因子实例列表
    """
    factors = []
    
    # 价格类因子
    factors.append(ClosePriceFactor())
    factors.append(HighPriceFactor())
    factors.append(LowPriceFactor())
    factors.append(OpenPriceFactor())
    factors.append(AveragePriceFactor())
    factors.append(VWAPFactor())
    factors.append(CloseToOpenRatioFactor())
    factors.append(PriceRankFactor(window=20))
    factors.append(PriceDecayFactor(window=10))
    factors.append(OpenToCloseChangeFactor())
    factors.append(PriceMeanFactor(window=20))
    
    # 自定义因子
    factors.append(KDJ_J_Factor())
    factors.append(MACD_DIFF_Factor())
    
    # 成交量类因子
    factors.append(VolumeFactor())
    factors.append(AmountFactor())
    factors.append(VolumeChangeRateFactor(window=5))
    factors.append(AmountChangeRateFactor(window=5))
    factors.append(VolumeRankFactor(window=20))
    factors.append(VolumeMeanFactor(window=20))
    factors.append(VolumeStdFactor(window=20))
    factors.append(VolumeToMeanFactor(window=20))
    factors.append(VolumeAmplitudeFactor(window=20))
    factors.append(VolumeAccumulationFactor())
    
    # 波动性类因子
    factors.append(DailyReturnFactor())
    factors.append(DailyAmplitudeFactor())
    factors.append(VolatilityFactor(window=20))
    factors.append(DownsideRiskFactor(window=20))
    factors.append(MaximumDrawdownFactor(window=20))
    factors.append(SharpeRatioFactor(window=20, risk_free_rate=0.02))
    factors.append(SkewnessFactor(window=20))
    factors.append(KurtosisFactor(window=20))
    
    # 动量类因子
    factors.append(MomentumFactor(window=20))
    factors.append(RSIFactor(window=14))
    factors.append(MACDFactor())
    factors.append(WilliamsRFactor(window=14))
    factors.append(StochasticFactor(window=14))
    factors.append(RateOfChangeFactor(window=20))
    
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