# 测试因子库导入是否正常

# 测试1：导入factor_lib模块
try:
    import factor_lib
    print("✅ 成功导入factor_lib模块")
except Exception as e:
    print(f"❌ 导入factor_lib模块失败: {e}")

# 测试2：获取所有因子类别
try:
    all_factors = factor_lib.get_all_factor_classes()
    print(f"✅ 成功获取所有因子类别，共 {len(all_factors)} 个因子")
    print("因子列表:", all_factors)
except Exception as e:
    print(f"❌ 获取因子类别失败: {e}")

# 测试3：检查趋势类因子中是否不再包含EMA和SMA因子
try:
    from factor_lib import get_factor_classes_by_category
    categories = get_factor_classes_by_category()
    trend_factors = categories.get('trend', [])
    
    # 检查是否存在EMA或SMA因子
    ema_sma_factors = [factor for factor in trend_factors if 'EMA' in factor or 'SMA' in factor]
    
    if not ema_sma_factors:
        print("✅ 趋势类因子中已成功删除所有EMA和SMA因子")
        print("当前趋势类因子:", trend_factors)
    else:
        print(f"❌ 趋势类因子中仍存在EMA/SMA因子: {ema_sma_factors}")
except Exception as e:
    print(f"❌ 检查趋势类因子失败: {e}")

# 测试4：尝试导入删除的因子，应该失败
try:
    from factor_lib import EMA5Factor
    print("❌ 仍然可以导入EMA5Factor，删除失败")
except ImportError:
    print("✅ 无法导入EMA5Factor，删除成功")

try:
    from factor_lib import SMA60Factor
    print("❌ 仍然可以导入SMA60Factor，删除失败")
except ImportError:
    print("✅ 无法导入SMA60Factor，删除成功")

print("\n测试完成")