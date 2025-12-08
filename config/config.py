#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目主配置文件

该文件集中管理项目的所有配置信息，包括目录结构、因子分析、回测等配置。
"""

import os
import sys
import json

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 导入目录配置
from .directory_config import (
    BASE_DIRS, DATA_DIRS, REPORTS_DIRS, LOGS_DIRS, 
    FACTOR_RESULTS_DIRS, BACKTEST_RESULTS_DIRS,
    get_full_path, create_all_directories
)

# 从config.json加载配置
def load_config_json():
    """从config.json加载配置"""
    config_json_path = os.path.join(PROJECT_ROOT, 'config', 'config.json')
    if os.path.exists(config_json_path):
        with open(config_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 数据库配置
config_json = load_config_json()
DATABASE_PATH = config_json.get('DATABASE_PATH', os.path.join(DATA_DIRS['DATABASE'], 'sz50_stock_data.db'))

# 因子分析配置
FACTOR_ANALYSIS_CONFIG = {
    'TEST_SCOPE': 'HS300',  # 测试范围: SZ50/HS300/ZZ500/ZZ1000/ZZ2000/INDIVIDUAL/ALL_A
    'INDIVIDUAL_STOCK': None,  # 单个股票代码 (仅当TEST_SCOPE为INDIVIDUAL时需要)
    'START_DATE': "2015-01-01",  # 开始日期
    'END_DATE': "2025-12-05",  # 结束日期
    'FORWARD_PERIOD': 10,  # 目标收益率周期
    'NORMALIZE_FACTOR': True,  # 是否进行因子横截面标准化
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['ANALYZED']),  # 结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['FACTOR_ANALYSIS'])  # 报告保存目录
}

# 因子计算配置
FACTOR_CALCULATION_CONFIG = {
    'START_DATE': "2015-01-01",  # 开始日期
    'END_DATE': "2025-12-05",  # 结束日期
    'BATCH_SIZE': 100,  # 每批计算的股票数量
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['CALCULATED'])  # 结果保存目录
}

# 回测配置
BACKTEST_CONFIG = {
    'STRATEGY': 'sma',  # 策略名称
    'START_DATE': "2015-01-01",  # 开始日期
    'END_DATE': "2025-12-05",  # 结束日期
    'INITIAL_CASH': 1000000,  # 初始资金
    'COMMISSION': 0.0003,  # 佣金比例
    'SLIPPAGE': 0.001,  # 滑点比例
    'RESULT_DIR': get_full_path(BACKTEST_RESULTS_DIRS['STRATEGY']),  # 结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['BACKTEST'])  # 报告保存目录
}

# SMA策略配置
SMA_CONFIG = {
    'SHORT_PERIOD': 5,  # 短期均线周期
    'LONG_PERIOD': 20  # 长期均线周期
}

# RSI_SMA策略配置
RSI_SMA_CONFIG = {
    'RSI_PERIOD': 14,  # RSI周期
    'RSI_OVERBOUGHT': 70,  # RSI超买阈值
    'RSI_OVERSOLD': 30,  # RSI超卖阈值
    'SMA_PERIOD': 20  # SMA周期
}

# 股票选择策略配置
STOCK_SELECTION_CONFIG = {
    'TOP_N': 10,  # 选择前N只股票
    'REBALANCE_INTERVAL': 20  # 再平衡间隔（交易日）
}

# Qlib配置
QLIB_CONFIG = {
    'USE_QLIB': False,  # 是否使用Qlib进行因子分析
    'USE_QLIB_ML': False,  # 是否使用Qlib进行机器学习因子组合分析
    'INSTRUMENTS': 'csi300',  # 分析标的范围
    'START_TIME': '2015-01-01',  # 开始时间
    'END_TIME': '2023-12-31',  # 结束时间
    'MODELS': ['lgb', 'dnn', 'lstm'],  # 要使用的模型类型
    'TOPK_VALUES': [10, 20, 30, 40, 50],  # TopK策略的k值范围
    'N_DROP_VALUES': [2, 3, 5],  # 每次调仓时卖出的股票数量范围
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['ML']),  # 结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['QLIB'])  # 报告保存目录
}

# 多因子组合分析配置
# 所有可用因子列表（供手动挑选）：
# 价格类因子：close, high, low, open, avg_price, vwap, close_open_ratio, price_rank_{window}, price_decay_{window}, open_close_change, price_mean_{window}
# 成交量类因子：volume, amount, vol_change_{window}, amt_change_{window}, vol_rank_{window}, vol_mean_{window}, vol_std_{window}, vol_to_mean_{window}, vol_amp_{window}, vol_accum_{window}
# 波动性类因子：daily_ret, daily_amp, volatility_{window}, downside_risk_{window}, max_drawdown_{window}, sharpe_{window}, skew_{window}, kurtosis_{window}
# 动量类因子：momentum_{window}, rsi_{window}, macd, wr_{window}, stoch_{window}, roc_{window}
# 自定义因子：custom_factor, kdj_j, macd_diff, custom_momentum_{window}, custom_volatility_{window}, custom_volume_{window}
# 注：{window}表示时间窗口参数，可根据需要替换为具体数字，如momentum_20表示20日动量因子
MULTI_FACTOR_COMBINATION_CONFIG = {
    "FACTORS_LIST": [
        # 形态因子
        "double_bottom_pattern", "double_top_pattern", "head_shoulders_bottom_pattern", 
        "head_shoulders_top_pattern", "triple_bottom_pattern", "triple_top_pattern", 
        "cup_handle_pattern", "inverse_cup_handle_pattern", "v_bottom_pattern", 
        "v_top_pattern", "ascending_triangle_pattern", "descending_triangle_pattern", 
        "symmetrical_triangle_pattern", "ascending_wedge_pattern", "descending_wedge_pattern", 
        "rectangle_pattern", "gap_pattern", "doji_pattern", "hammer_pattern", 
        "shooting_star_pattern", "morning_star_pattern", "evening_star_pattern",
        
        # 成交量因子
        "volume", "amount", "vol_change_{window}", "amt_change_{window}", "vol_rank_{window}",
        "vol_mean_{window}", "vol_std_{window}", "vol_to_mean_{window}",
        "vol_amp_{window}", "vol_accum_{window}", "vol_turnover_{window}",
        "vol_density_{window}",
        
        # 动量因子
        "momentum_{window}", "rsi_{window}", "macd", "wr_{window}",
        "stoch_{window}", "roc_{window}"
    ],
    "START_DATE": "2020-01-01",
    "END_DATE": "2023-12-31",
    "GROUP_NUM": 10,
    "TEST_SCOPE": "all",  # all, index50, industry
    "MODEL_TYPE": "rf",  # linear, rf, gbdt, mlp
    "MODEL_PARAMS": {
        "linear": {
            "alpha": [0.001, 0.01, 0.1, 1.0]
        },
        "rf": {
            "n_estimators": [50, 100, 200],
            "max_depth": [5, 10, 20],
            "min_samples_split": [2, 5, 10]
        },
        "gbdt": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 5, 7]
        },
        "mlp": {
            "hidden_layer_sizes": [(50,), (100,), (50, 50)],
            "learning_rate_init": [0.001, 0.01, 0.1],
            "max_iter": [100, 200]
        }
    },
    "TARGET_RETURN_DAYS": 5,
    "TRANSACTION_COST": 0.0015,
    "RESULTS_PATH": os.path.join(ROOT_DIR, "results", "multi_factor_combination")
}

# 绘图配置
PLOT_CONFIG = {
    'ENABLE': True,  # 是否启用绘图
    'DPI': 300,  # 图像DPI
    'FORMAT': 'png',  # 图像格式
    'WIDTH': 12,  # 图像宽度
    'HEIGHT': 8  # 图像高度
}

# 初始化函数
def init_config():
    """初始化配置，创建所有必要的目录"""
    create_all_directories()

# 导出所有配置
__all__ = [
    # 目录配置
    'BASE_DIRS', 'DATA_DIRS', 'REPORTS_DIRS', 'LOGS_DIRS', 
    'FACTOR_RESULTS_DIRS', 'BACKTEST_RESULTS_DIRS',
    'get_full_path', 'create_all_directories',
    
    # 数据库配置
    'DATABASE_PATH',
    
    # 因子分析配置
    'FACTOR_ANALYSIS_CONFIG',
    
    # 因子计算配置
    'FACTOR_CALCULATION_CONFIG',
    
    # 回测配置
    'BACKTEST_CONFIG', 'SMA_CONFIG', 'RSI_SMA_CONFIG', 'STOCK_SELECTION_CONFIG',
    
    # Qlib配置
    'QLIB_CONFIG',
    
    # 多因子组合分析配置
    'MULTI_FACTOR_COMBINATION_CONFIG',
    
    # 绘图配置
    'PLOT_CONFIG',
    
    # 初始化函数
    'init_config'
]

# 初始化配置
init_config()