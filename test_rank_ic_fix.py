import pandas as pd
import numpy as np
from analyzer.factor_analyzer import FactorAnalyzer

# 创建一个FactorAnalyzer实例
fa = FactorAnalyzer()

# 生成模拟数据
dates = pd.date_range('2020-01-01', '2020-01-10')
stock_codes = [f'STOCK{i:03d}' for i in range(1, 60)]  # 59只股票

# 生成因子数据 - 所有交易日因子值都相同（模拟导致Rank IC全为NaN的情况）
factor_data = []
for date in dates:
    for code in stock_codes:
        factor_data.append({
            'ts_code': code,
            'trade_date': date.strftime('%Y%m%d'),
            'factor_value': 1.0  # 恒定因子值
        })
factor_df = pd.DataFrame(factor_data)

# 生成收益率数据
return_data = []
for date in dates:
    for code in stock_codes:
        return_data.append({
            'ts_code': code,
            'trade_date': date.strftime('%Y%m%d'),
            'return_1d': np.random.randn()
        })
return_df = pd.DataFrame(return_data)

# 保存测试数据
factor_df.to_csv('test_factor_data.csv', index=False)
return_df.to_csv('test_return_data.csv', index=False)

print("测试数据生成完成")
print(f"因子数据形状: {factor_df.shape}")
print(f"收益率数据形状: {return_df.shape}")
print("\n前几行因子数据:")
print(factor_df.head())
print("\n前几行收益率数据:")
print(return_df.head())

# 测试因子分析（这应该会触发Rank IC全为NaN的情况）
try:
    print("\n开始测试因子分析（全NaN情况）...")
    result = fa.analyze_factor('test_factor_data.csv', 'test_return_data.csv', factor_name='test_factor')
    print("因子分析结果:")
    print(result)
    print("测试通过：因子分析在Rank IC全为NaN时没有崩溃")
except Exception as e:
    print(f"测试失败：因子分析在Rank IC全为NaN时崩溃")
    print(f"错误信息: {str(e)}")

# 生成正常因子数据（非恒定值）
factor_data_normal = []
for date in dates:
    for code in stock_codes:
        factor_data_normal.append({
            'ts_code': code,
            'trade_date': date.strftime('%Y%m%d'),
            'factor_value': np.random.randn()  # 随机因子值
        })
factor_df_normal = pd.DataFrame(factor_data_normal)

# 保存正常测试数据
factor_df_normal.to_csv('test_factor_data_normal.csv', index=False)

# 测试正常情况
try:
    print("\n开始测试因子分析（正常情况）...")
    result = fa.analyze_factor('test_factor_data_normal.csv', 'test_return_data.csv', factor_name='test_factor_normal')
    print("因子分析结果:")
    print(result)
    print("测试通过：正常情况下因子分析工作正常")
except Exception as e:
    print(f"测试失败：正常情况下因子分析崩溃")
    print(f"错误信息: {str(e)}")

print("\n所有测试完成")