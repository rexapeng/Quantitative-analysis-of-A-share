#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HistoricalVolatilityFactor修复效果的脚本
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要测试的因子
from factor_lib.volatility_factors import HistoricalVolatilityFactor

# 创建测试数据
def create_test_data():
    """创建测试用的股票数据"""
    # 创建5只股票，每只股票有100天的数据
    ts_codes = ['000001.SZ', '000002.SZ', '600000.SH', '600001.SH', '600002.SH']
    trade_dates = pd.date_range('2020-01-01', periods=100, freq='B').strftime('%Y%m%d')
    
    data = []
    for ts_code in ts_codes:
        # 创建模拟的收盘价数据（使用随机游走）
        np.random.seed(int(ts_code[:6]))
        returns = np.random.normal(0, 0.01, size=len(trade_dates))
        close = 10 * np.exp(np.cumsum(returns))
        
        for i, (trade_date, close_price) in enumerate(zip(trade_dates, close)):
            data.append({
                'ts_code': ts_code,
                'trade_date': trade_date,
                'close': close_price
            })
    
    return pd.DataFrame(data)

# 测试HistoricalVolatilityFactor
def test_historical_volatility():
    """测试HistoricalVolatilityFactor"""
    print("创建测试数据...")
    data = create_test_data()
    
    print(f"测试数据形状: {data.shape}")
    print(f"股票数量: {data['ts_code'].nunique()}")
    print(f"日期范围: {data['trade_date'].min()} 到 {data['trade_date'].max()}")
    
    # 测试窗口为20和30的因子
    for window in [20, 30]:
        print(f"\n测试HistoricalVolatilityFactor(window={window})...")
        factor = HistoricalVolatilityFactor(window=window)
        
        try:
            result = factor.calculate(data)
            print(f"✓ 因子计算成功!")
            print(f"因子数据形状: {result.shape}")
            print(f"因子名称: {factor.name}")
            
            # 检查结果数据
            if result is not None:
                print(f"包含的股票数量: {result['ts_code'].nunique()}")
                print(f"非空因子值数量: {result[factor.name].notna().sum()}")
                print(f"空值因子值数量: {result[factor.name].isna().sum()}")
                
                # 显示前几行数据
                print("前5行因子数据:")
                print(result.head())
            
        except Exception as e:
            print(f"✗ 因子计算失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_historical_volatility()