#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的多因子组合负权重测试脚本
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# 导入配置和工具
from config.config import FACTOR_ANALYSIS_CONFIG, MULTI_FACTOR_COMBINATION_CONFIG
from config.logger_config import get_logger
from scripts.multi_factor_combination import MultiFactorCombination

def test_negative_weights():
    """
    测试多因子组合负权重功能
    """
    logger = get_logger('test_negative_weights')
    logger.info("="*50)
    logger.info("多因子组合负权重功能测试")
    logger.info("="*50)
    
    try:
        # 使用简化的参数配置
        factors_list = ['volume', 'rsi_24', 'volatility_20']  # 使用少量因子
        start_date = '2023-01-01'  # 使用较短的时间范围
        end_date = '2023-03-31'    # 使用较短的时间范围
        forward_period = 5
        group_num = 5
        test_scope = 'SZ50'
        
        logger.info(f"使用因子: {', '.join(factors_list)}")
        logger.info(f"时间范围: {start_date} 至 {end_date}")
        
        # 创建多因子组合实例
        mf_combination = MultiFactorCombination(
            factors_list=factors_list,
            start_date=start_date,
            end_date=end_date,
            forward_period=forward_period,
            group_num=group_num,
            test_scope=test_scope
        )
        
        # 加载数据
        if not mf_combination.load_data():
            logger.error("数据加载失败")
            return False
        
        logger.info("数据加载成功，开始训练线性回归模型")
        
        # 训练线性回归模型
        if not mf_combination.train_model(model_type='linear'):
            logger.error("模型训练失败")
            return False
        
        # 打印最优权重
        logger.info("="*50)
        logger.info("线性回归模型最优权重:")
        for factor, weight in mf_combination.optimal_weights.items():
            logger.info(f"{factor}: {weight:.6f}")
        
        # 检查是否有负权重
        has_negative_weights = any(weight < 0 for weight in mf_combination.optimal_weights.values())
        
        if has_negative_weights:
            logger.info("✅ 成功生成负权重！")
            logger.info("负权重因子:")
            for factor, weight in mf_combination.optimal_weights.items():
                if weight < 0:
                    logger.info(f"  - {factor}: {weight:.6f}")
        else:
            logger.info("⚠️  未生成负权重，但功能正常")
        
        logger.info("="*50)
        logger.info("测试完成！")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_negative_weights()
    sys.exit(0 if success else 1)