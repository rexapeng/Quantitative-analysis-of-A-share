# 测试脚本：验证待删除因子是否已成功移除

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 待删除的因子列表
deleted_factors = [
    'CustomVolumeFactor',
    'MACD_HistogramFactor',
    'RSI3Factor',
    'StochasticFactor',
    'DojiPatternFactor',
    'BollingerBandFactor',
    'RSI7Factor',
    'WilliamsRFactor',
    'DownsideDeviationFactor',
    'UlcerIndexFactor',
    'ParabolicSARFactor',
    'CCI21Factor',
    'ADX20Factor',
    'ADX28Factor',
    'MACD_CrossoverFactor'
]

print("=" * 60)
print("测试脚本：验证待删除因子是否已成功移除")
print("=" * 60)

# 测试1：尝试导入每个被删除的因子
success_count = 0
print("\n1. 测试导入被删除的因子（预期：全部导入失败）：")
print("-" * 50)

for factor_name in deleted_factors:
    try:
        # 尝试从factor_lib导入因子
        exec(f"from factor_lib import {factor_name}")
        print(f"❌ 错误：仍然可以导入 {factor_name}")
    except ImportError:
        print(f"✅ 正确：无法导入 {factor_name}（已成功删除）")
        success_count += 1
    except Exception as e:
        print(f"⚠️  警告：导入 {factor_name} 时发生意外错误：{e}")

# 测试2：检查factor_lib.__all__中是否不包含这些因子
print(f"\n2. 测试factor_lib.__all__中是否不包含被删除的因子：")
print("-" * 50)

try:
    import factor_lib
    
    # 检查__all__中是否包含任何被删除的因子
    found_in_all = [factor for factor in deleted_factors if factor in factor_lib.__all__]
    
    if not found_in_all:
        print("✅ 正确：factor_lib.__all__中不包含任何被删除的因子")
        success_count += 1
    else:
        print(f"❌ 错误：factor_lib.__all__中仍然包含以下被删除的因子：{found_in_all}")
        
except Exception as e:
    print(f"⚠️  警告：检查factor_lib.__all__时发生错误：{e}")

# 测试3：检查get_all_factor_classes()返回的结果中是否不包含这些因子
print(f"\n3. 测试get_all_factor_classes()中是否不包含被删除的因子：")
print("-" * 50)

try:
    from factor_lib import get_all_factor_classes
    
    all_factors = get_all_factor_classes()
    found_in_all_classes = [factor for factor in deleted_factors if factor in all_factors]
    
    if not found_in_all_classes:
        print("✅ 正确：get_all_factor_classes()中不包含任何被删除的因子")
        success_count += 1
    else:
        print(f"❌ 错误：get_all_factor_classes()中仍然包含以下被删除的因子：{found_in_all_classes}")
        
except Exception as e:
    print(f"⚠️  警告：检查get_all_factor_classes()时发生错误：{e}")

# 测试4：检查get_factor_classes_by_category()返回的结果中是否不包含这些因子
print(f"\n4. 测试get_factor_classes_by_category()中是否不包含被删除的因子：")
print("-" * 50)

try:
    from factor_lib import get_factor_classes_by_category
    
    categories = get_factor_classes_by_category()
    
    found_in_categories = []
    for category, factors in categories.items():
        for factor in factors:
            if factor in deleted_factors:
                found_in_categories.append((category, factor))
    
    if not found_in_categories:
        print("✅ 正确：get_factor_classes_by_category()中不包含任何被删除的因子")
        success_count += 1
    else:
        print(f"❌ 错误：get_factor_classes_by_category()中仍然包含以下被删除的因子：")
        for category, factor in found_in_categories:
            print(f"   - {category}: {factor}")
            
except Exception as e:
    print(f"⚠️  警告：检查get_factor_classes_by_category()时发生错误：{e}")

# 测试5：验证整体因子导入功能正常
print(f"\n5. 验证整体因子导入功能正常：")
print("-" * 50)

try:
    import factor_lib
    from factor_lib import get_all_factor_classes, get_factor_classes_by_category
    
    # 确保至少有一些因子可用
    all_factors = get_all_factor_classes()
    categories = get_factor_classes_by_category()
    
    if len(all_factors) > 0 and len(categories) > 0:
        print(f"✅ 正确：因子库整体功能正常，当前共有 {len(all_factors)} 个因子可用")
        success_count += 1
    else:
        print("❌ 错误：因子库中没有可用因子")
        
except Exception as e:
    print(f"⚠️  警告：验证整体因子导入功能时发生错误：{e}")

# 总结测试结果
print("\n" + "=" * 60)
print("测试结果总结：")
print("=" * 60)

if success_count == 5:
    print(f"🎉 所有测试通过！{len(deleted_factors)}个因子已全部成功移除。")
else:
    print(f"❌ 测试未全部通过。成功：{success_count}/5，失败：{5 - success_count}/5")

print("\n测试完成。")
