#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证momentum因子周期配置

验证MomentumFactor的周期是否已经正确修改为10、50、100。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from factor_lib import get_all_factor_classes
from scripts.calculate_factors import get_all_factors


def test_momentum_factors_window():
    """测试momentum因子的周期配置"""
    print("=== 测试momentum因子周期配置 ===")
    
    # 测试1：获取window_params中的MomentumFactor配置
    print("\n1. 检查window_params配置:")
    from scripts.calculate_factors import get_all_factors as calc_get_all_factors
    import inspect
    import ast
    
    # 获取get_all_factors函数的源代码
    source = inspect.getsource(calc_get_all_factors)
    tree = ast.parse(source)
    
    # 查找window_params字典定义
    window_params = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'window_params':
                    # 提取字典内容
                    if isinstance(node.value, ast.Dict):
                        window_params = {}
                        for key, value in zip(node.value.keys, node.value.values):
                            key_str = ast.literal_eval(key)
                            values = ast.literal_eval(value)
                            window_params[key_str] = values
                        break
            if window_params:
                break
    
    if window_params and 'MomentumFactor' in window_params:
        momentum_windows = window_params['MomentumFactor']
        print(f"   MomentumFactor配置的周期: {momentum_windows}")
        expected_windows = [10, 50, 100]
        if momentum_windows == expected_windows:
            print("   ✓ window_params配置正确")
        else:
            print(f"   ✗ window_params配置错误，期望 {expected_windows}")
    else:
        print("   ✗ 未找到MomentumFactor的window_params配置")
    
    # 测试2：获取实际创建的因子实例
    print("\n2. 检查实际创建的Momentum因子实例:")
    factors = get_all_factors()
    momentum_factors = [f for f in factors if isinstance(f, f.__class__) and f.__class__.__name__ == 'MomentumFactor']
    
    if momentum_factors:
        print(f"   找到 {len(momentum_factors)} 个MomentumFactor实例")
        actual_windows = [f.window for f in momentum_factors]
        actual_windows.sort()
        print(f"   实际的周期: {actual_windows}")
        
        expected_windows = [10, 50, 100]
        if actual_windows == expected_windows:
            print("   ✓ 实际创建的因子周期正确")
        else:
            print(f"   ✗ 实际创建的因子周期错误，期望 {expected_windows}")
    else:
        print("   ✗ 未找到MomentumFactor实例")
    
    # 测试3：验证因子名称格式
    print("\n3. 检查Momentum因子名称格式:")
    if momentum_factors:
        for factor in momentum_factors:
            expected_name = f'momentum_{factor.window}'
            if factor.name == expected_name:
                print(f"   ✓ {factor.name} 名称格式正确")
            else:
                print(f"   ✗ {factor.name} 名称格式错误，期望 {expected_name}")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_momentum_factors_window()
