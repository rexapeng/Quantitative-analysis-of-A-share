import sys
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_negative_weights():
    """测试负权重功能"""
    print("测试负权重功能...")
    
    # 模拟因子列表
    factors_list = ['atr_14', 'dma', 'ma_cross_5_10', 'mtm_12', 'rsi_6', 'vr_24', 'wr_6', 'wr_14']
    
    # 模拟随机森林模型
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # 生成模拟数据
    X = np.random.rand(1000, len(factors_list))
    y = np.sum(X * np.array([0.2, 0.1, -0.3, 0.4, -0.1, 0.2, -0.3, 0.1]), axis=1) + np.random.randn(1000) * 0.1
    
    # 训练模型
    model.fit(X, y)
    
    # 获取特征重要性
    importances = model.feature_importances_
    print(f"原始特征重要性: {importances}")
    print(f"原始特征重要性之和: {sum(importances):.6f}")
    print(f"是否有负数: {any(imp < 0 for imp in importances)}")
    
    # 传统归一化（仅非负）
    total_weight = sum(importances)
    non_negative_weights = importances / total_weight
    print(f"\n传统归一化权重: {non_negative_weights}")
    print(f"传统归一化权重之和: {sum(non_negative_weights):.6f}")
    print(f"是否有负数: {any(weight < 0 for weight in non_negative_weights)}")
    
    # 中心化处理（产生负权重）
    mean_weight = sum(importances) / len(importances)
    centered_weights = importances - mean_weight
    print(f"\n中心化权重: {centered_weights}")
    print(f"中心化权重之和: {sum(centered_weights):.6f}")
    print(f"是否有负数: {any(weight < 0 for weight in centered_weights)}")
    
    # 显示各因子的权重
    print("\n因子权重详情:")
    for factor, raw, norm, cent in zip(factors_list, importances, non_negative_weights, centered_weights):
        print(f"{factor}: 原始={raw:.6f}, 传统归一化={norm:.6f}, 中心化={cent:.6f}")
    
    return {
        'raw_importances': importances,
        'non_negative_weights': non_negative_weights,
        'centered_weights': centered_weights
    }

if __name__ == "__main__":
    test_negative_weights()
