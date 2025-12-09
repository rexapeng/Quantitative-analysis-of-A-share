# 测试删除custom_factor和custom_volatility_20因子后，代码是否正常工作

# 测试1：导入factor_lib模块
try:
    import factor_lib
    print("✅ 成功导入factor_lib模块")
except Exception as e:
    print(f"❌ 导入factor_lib模块失败: {e}")

# 测试2：检查自定义因子类别
try:
    from factor_lib import get_factor_classes_by_category
    categories = get_factor_classes_by_category()
    custom_factors = categories.get('custom', [])
    
    print(f"当前自定义因子列表: {custom_factors}")
    
    # 检查是否存在CustomFactorTemplate因子
    if 'CustomFactorTemplate' not in custom_factors:
        print("✅ CustomFactorTemplate因子已成功删除")
    else:
        print("❌ CustomFactorTemplate因子未被删除")
    
    # 检查是否存在CustomVolatilityFactor相关因子
    volatility_factors = [factor for factor in custom_factors if 'Volatility' in factor]
    if not volatility_factors:
        print("✅ 所有Volatility因子已成功删除")
    else:
        print(f"❌ 仍存在Volatility因子: {volatility_factors}")
    
except Exception as e:
    print(f"❌ 获取自定义因子类别失败: {e}")

# 测试3：尝试直接导入被删除的因子
try:
    from factor_lib import CustomFactorTemplate
    print("❌ 仍然可以导入CustomFactorTemplate，删除失败")
except ImportError:
    print("✅ 无法导入CustomFactorTemplate，删除成功")

try:
    from factor_lib import CustomVolatilityFactor
    print("❌ 仍然可以导入CustomVolatilityFactor，删除失败")
except ImportError:
    print("✅ 无法导入CustomVolatilityFactor，删除成功")

# 测试4：获取所有因子并检查
try:
    all_factors = factor_lib.get_all_factor_classes()
    
    # 检查是否存在包含'custom_volatility'的因子
    custom_vol_factors = [factor for factor in all_factors if 'custom_volatility' in factor.lower()]
    
    if not custom_vol_factors:
        print("✅ 所有custom_volatility相关因子已成功删除")
    else:
        print(f"❌ 仍存在custom_volatility相关因子: {custom_vol_factors}")
        
    # 检查是否存在包含'custom_factor'的因子
    custom_factors_found = [factor for factor in all_factors if 'custom_factor' in factor.lower()]
    
    if not custom_factors_found:
        print("✅ 所有custom_factor相关因子已成功删除")
    else:
        print(f"❌ 仍存在custom_factor相关因子: {custom_factors_found}")
        
except Exception as e:
    print(f"❌ 获取所有因子失败: {e}")

# 测试5：验证剩余的自定义因子是否可以正常导入
try:
    from factor_lib import CustomMomentumFactor, CustomVolumeFactor
    print("✅ 剩余的自定义因子可以正常导入")
except Exception as e:
    print(f"❌ 导入剩余自定义因子失败: {e}")

print("\n测试完成")