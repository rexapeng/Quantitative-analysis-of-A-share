import sys
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_maximize_return():
    """测试最大化平均收益率的功能"""
    print("测试最大化平均收益率的功能...")
    
    # 模拟因子列表
    factors_list = ['atr_14', 'dma', 'volume', 'macd_diff', 'volatility_20', 'roc_20', 'kdj_j', 'momentum_10']
    
    # 生成模拟数据
    np.random.seed(42)
    n_samples = 1000
    
    # 生成因子数据
    factors_data = np.random.randn(n_samples, len(factors_list))
    
    # 生成收益率数据：使用因子的线性组合，包含正负相关
    # 权重设置为我们期望的最优权重
    true_weights = np.array([0.5, -0.3, 0.2, -0.4, 0.6, -0.1, 0.3, -0.2])
    
    # 计算收益率：线性组合 + 噪声
    returns = np.dot(factors_data, true_weights) + np.random.randn(n_samples) * 0.1
    
    # 创建DataFrame
    data = pd.DataFrame(factors_data, columns=factors_list)
    data['return'] = returns
    
    print("\n原始因子数据和收益率数据生成完成")
    print(f"数据形状: {data.shape}")
    print(f"真实权重: {true_weights}")
    
    # 1. 使用线性回归直接预测收益率（支持正负权重）
    print("\n1. 使用线性回归直接预测收益率：")
    
    X = data[factors_list]
    y = data['return']
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 训练线性回归模型
    linear_model = LinearRegression()
    linear_model.fit(X_scaled, y)
    
    # 获取权重
    linear_weights = linear_model.coef_
    linear_r2 = linear_model.score(X_scaled, y)
    
    print(f"线性回归权重: {linear_weights}")
    print(f"R² 得分: {linear_r2:.6f}")
    print(f"是否有负数权重: {any(w < 0 for w in linear_weights)}")
    
    # 2. 使用随机森林（只能生成非负权重）
    print("\n2. 使用随机森林：")
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_scaled, y)
    
    # 获取特征重要性（作为权重）
    rf_importances = rf_model.feature_importances_
    rf_r2 = rf_model.score(X_scaled, y)
    
    # 归一化
    rf_weights = rf_importances / sum(rf_importances)
    
    print(f"随机森林权重: {rf_weights}")
    print(f"R² 得分: {rf_r2:.6f}")
    print(f"是否有负数权重: {any(w < 0 for w in rf_weights)}")
    
    # 3. 计算组合因子并比较收益率
    print("\n3. 比较不同权重的组合因子收益率：")
    
    # 线性回归组合因子
    data['linear_combined'] = np.dot(X_scaled, linear_weights)
    
    # 随机森林组合因子
    data['rf_combined'] = np.dot(X_scaled, rf_weights)
    
    # 等权重组合因子
    equal_weights = np.ones(len(factors_list)) / len(factors_list)
    data['equal_combined'] = np.dot(X_scaled, equal_weights)
    
    # 按组合因子分组，计算每组的平均收益率
    n_groups = 10
    
    for method in ['linear_combined', 'rf_combined', 'equal_combined']:
        # 按组合因子排序
        data_sorted = data.sort_values(method)
        
        # 分组
        data_sorted['group'] = pd.qcut(data_sorted[method], n_groups, labels=False)
        
        # 计算每组的平均收益率
        group_returns = data_sorted.groupby('group')['return'].mean()
        
        # 计算最高组收益率
        highest_group_return = group_returns.iloc[-1]
        
        # 计算多空收益
        long_short_return = group_returns.iloc[-1] - group_returns.iloc[0]
        
        print(f"\n{method}:")
        print(f"  各组平均收益率: {group_returns.values}")
        print(f"  最高组平均收益率: {highest_group_return:.6f}")
        print(f"  多空收益: {long_short_return:.6f}")
    
    # 4. 验证线性回归的权重是否接近真实权重
    print("\n4. 权重比较：")
    print(f"真实权重: {true_weights}")
    print(f"线性回归权重: {linear_weights}")
    
    # 计算权重的相关性
    weight_corr = np.corrcoef(true_weights, linear_weights)[0, 1]
    print(f"真实权重与线性回归权重的相关性: {weight_corr:.6f}")
    
    return {
        'true_weights': true_weights,
        'linear_weights': linear_weights,
        'rf_weights': rf_weights,
        'equal_weights': equal_weights,
        'group_returns': group_returns
    }

if __name__ == "__main__":
    test_maximize_return()
