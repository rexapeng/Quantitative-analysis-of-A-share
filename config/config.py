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
ROOT_DIR = PROJECT_ROOT

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
# 数据库配置
# DATABASE_PATH: 股票数据库文件路径，优先从config.json加载，如不存在则使用默认路径
DATABASE_PATH = config_json.get('DATABASE_PATH', os.path.join(DATA_DIRS['DATABASE'], 'data', 'sz50_stock_data.db'))

# 因子分析配置
FACTOR_ANALYSIS_CONFIG = {
    'TEST_SCOPE': 'SZ50',  # 测试范围：SZ50/HS300/ZZ500/ZZ1000/ZZ2000/INDIVIDUAL/ALL_A
    'INDIVIDUAL_STOCK': None,  # 单个股票代码 (仅当TEST_SCOPE为INDIVIDUAL时需要)
    'START_DATE': "2015-01-01",  # 分析开始日期
    'END_DATE': "2025-12-05",  # 分析结束日期
    'FORWARD_PERIOD': 20,  # 目标收益率计算周期（交易日数）
    'NORMALIZE_FACTOR': True,  # 是否进行因子横截面标准化（Z-score标准化）
    'GROUP_NUM': 10,  # 分组收益分析的分组数量
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['ANALYZED']),  # 分析结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['FACTOR_ANALYSIS'])  # 分析报告保存目录
}

# 因子计算配置
FACTOR_CALCULATION_CONFIG = {
    'START_DATE': "2015-01-01",  # 计算开始日期
    'END_DATE': "2025-12-05",  # 计算结束日期
    'BATCH_SIZE': 100,  # 每批计算的股票数量（控制内存使用）
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['CALCULATED'])  # 因子计算结果保存目录
}

# 回测配置
BACKTEST_CONFIG = {
    'STRATEGY': 'sma',  # 回测策略名称
    'START_DATE': "2015-01-01",  # 回测开始日期
    'END_DATE': "2025-12-05",  # 回测结束日期
    'INITIAL_CASH': 1000000,  # 初始资金（元）
    'COMMISSION': 0.0003,  # 交易佣金比例（0.03%）
    'SLIPPAGE': 0.001,  # 滑点比例（0.1%）
    'RESULT_DIR': get_full_path(BACKTEST_RESULTS_DIRS['STRATEGY']),  # 回测结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['BACKTEST'])  # 回测报告保存目录
}

# SMA策略配置（移动平均线策略）
SMA_CONFIG = {
    'SHORT_PERIOD': 5,  # 短期均线周期（交易日数）
    'LONG_PERIOD': 20  # 长期均线周期（交易日数）
}

# RSI_SMA策略配置（相对强弱指标+移动平均线策略）
RSI_SMA_CONFIG = {
    'RSI_PERIOD': 14,  # RSI计算周期（交易日数）
    'RSI_OVERBOUGHT': 70,  # RSI超买阈值
    'RSI_OVERSOLD': 30,  # RSI超卖阈值
    'SMA_PERIOD': 20  # SMA辅助判断周期（交易日数）
}

# 股票选择策略配置
STOCK_SELECTION_CONFIG = {
    'TOP_N': 10,  # 每轮选择的最优股票数量
    'REBALANCE_INTERVAL': 20  # 组合再平衡间隔（交易日数）
}

# Qlib配置（量化金融库配置）
QLIB_CONFIG = {
    'USE_QLIB': False,  # 是否使用Qlib进行因子分析
    'USE_QLIB_ML': False,  # 是否使用Qlib进行机器学习因子组合分析
    'INSTRUMENTS': 'csi300',  # 分析标的范围（如csi300、sz50等）
    'START_TIME': '2015-01-01',  # 分析开始时间
    'END_TIME': '2023-12-31',  # 分析结束时间
    'MODELS': ['lgb', 'dnn', 'lstm'],  # 要使用的机器学习模型类型
    'TOPK_VALUES': [10, 20, 30, 40, 50],  # TopK策略的k值范围（选择前k只股票）
    'N_DROP_VALUES': [2, 3, 5],  # 每次调仓时卖出的股票数量范围
    'RESULT_DIR': get_full_path(FACTOR_RESULTS_DIRS['ML']),  # 机器学习结果保存目录
    'REPORT_DIR': get_full_path(REPORTS_DIRS['QLIB'])  # Qlib分析报告保存目录
}

# 多因子组合分析配置
# =============================================================================
# 多因子组合手动挑选因子方法
# =============================================================================
#
# 一、因子挑选的基本原则
# 1. 因子有效性：选择具有显著IC值（信息系数）的因子，通常IC绝对值应大于0.05
# 2. 因子相关性：选择相关性较低的因子，避免信息冗余，因子间相关系数应小于0.5
# 3. 因子单调性：选择分组收益具有明显单调性的因子
# 4. 因子稳定性：选择在不同市场环境下表现稳定的因子
# 5. 因子互补性：选择从不同维度刻画股票特征的因子（如价格、成交量、波动性、动量等）
#
# 二、因子挑选的步骤
# 1. 单因子分析：对每个候选因子进行IC分析、分组收益分析、稳定性测试
# 2. 因子相关性分析：计算因子间相关系数矩阵，剔除高度相关的因子
# 3. 因子组合测试：测试不同因子组合的效果，评估组合IC、IR和分组收益单调性
# 4. 因子权重优化：确定各因子的权重，可采用等权、IC加权或机器学习方法
#
# 三、手动挑选因子示例
# 以下是一个均衡配置的因子组合示例，覆盖不同维度的因子：
# - 价格/趋势类：macd, macd_signal
# - 成交量类：volume, vol_mean_10
# - 波动性类：volatility_20, atr_14
# - 动量类：momentum_20, rsi_24
# - 形态类：double_bottom_pattern, rectangle_pattern
#
# 四、在配置中使用手动挑选的因子
# 方法一：直接在FACTORS_LIST中列出要使用的因子
# 方法二：使用因子类别筛选，然后手动调整
#
# 五、所有可用因子列表（供手动挑选）
# 价格类因子：close, high, low, open, avg_price, vwap, close_open_ratio, price_rank_{window}, price_decay_{window}, open_close_change, price_mean_{window}
# 成交量类因子：volume, amount, vol_change_{window}, amt_change_{window}, vol_rank_{window}, vol_mean_{window}, vol_std_{window}, vol_to_mean_{window}, vol_amp_{window}, vol_accum_{window}
# 波动性类因子：daily_ret, daily_amp, volatility_{window}, downside_risk_{window}, max_drawdown_{window}, sharpe_{window}, skew_{window}, kurtosis_{window}
# 动量类因子：momentum_{window}, rsi_{window}, macd, wr_{window}, stoch_{window}, roc_{window}
# 自定义因子：custom_factor, kdj_j, macd_diff, custom_momentum_{window}, custom_volatility_{window}, custom_volume_{window}
# 注：{window}表示时间窗口参数，可根据需要替换为具体数字，如momentum_20表示20日动量因子
#
# 六、因子挑选的注意事项
# 1. 避免过度拟合：不要仅根据历史表现选择因子，应考虑因子的经济逻辑
# 2. 考虑交易成本：高换手率的因子组合可能导致较高的交易成本
# 3. 定期重新评估：市场环境变化可能导致因子有效性变化，应定期重新评估因子组合
# 4. 控制因子数量：因子数量不宜过多，通常5-10个因子为宜
#
# =============================================================================
MULTI_FACTOR_COMBINATION_CONFIG = {
    "# 因子挑选说明": "手动挑选因子时，请根据上述原则和步骤选择合适的因子，并将其添加到FACTORS_LIST中",
    "# 因子挑选示例": "示例：['macd', 'volume', 'rsi_24', 'momentum_20', 'volatility_20', 'double_bottom_pattern']",
    "FACTORS_LIST": [
        # 示例：手动挑选的均衡因子组合
        "atr_14", "dma", "volume", "macd_diff", "volatility_20", "roc_20",
        "kdj_j", "momentum_10"
    ],
    "START_DATE": "2012-01-01",  # 分析开始日期
    "END_DATE": "2025-12-01",  # 分析结束日期
    "GROUP_NUM": 10,  # 分组收益分析的分组数量
    "TEST_SCOPE": "SZ50",  # 测试范围：SZ50/HS300/ZZ500/ZZ1000/ZZ2000/INDIVIDUAL/ALL_A
    "MODEL_TYPE": "linear",  # 机器学习模型类型：linear(线性回归)/rf(随机森林)/gbdt(梯度提升树)/mlp(多层感知器)
    "MODEL_PARAMS": {
        "linear": {
            "alpha": [0.001, 0.01, 0.1, 1.0]  # 正则化参数
        },
        "rf": {
            "n_estimators": [50, 100, 200],  # 树的数量
            "max_depth": [5, 10, 20],  # 树的最大深度
            "min_samples_split": [2, 5, 10]  # 分裂节点所需的最小样本数
        },
        "gbdt": {
            "n_estimators": [50, 100, 200],  # 树的数量
            "learning_rate": [0.01, 0.1, 0.2],  # 学习率
            "max_depth": [3, 5, 7]  # 树的最大深度
        },
        "mlp": {
            "hidden_layer_sizes": [(50,), (100,), (50, 50)],  # 隐藏层大小
            "learning_rate_init": [0.001, 0.01, 0.1],  # 初始学习率
            "max_iter": [100, 200]  # 最大迭代次数
        }
    },
    "TARGET_RETURN_DAYS": 20,  # 目标收益率预测周期（交易日数）
    "TRANSACTION_COST": 0.0015,  # 交易成本比例（0.15%）
    "RESULTS_PATH": os.path.join(ROOT_DIR, "results", "multi_factor_combination")  # 多因子组合分析结果保存路径
}

# 绘图配置
PLOT_CONFIG = {
    'ENABLE': True,  # 是否启用绘图功能
    'DPI': 300,  # 图像分辨率（DPI）
    'FORMAT': 'png',  # 图像保存格式（支持png、jpg、pdf等）
    'WIDTH': 12,  # 图像宽度（英寸）
    'HEIGHT': 8  # 图像高度（英寸）
}

# 初始化函数
def init_config():
    """初始化配置，创建所有必要的目录"""
    create_all_directories()

# 不再自动调用目录创建函数
# create_all_directories()

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

# 初始化配置已移除 - 不再自动创建文件夹