# 测试验证vol_change、vol_rank、vol_std因子是否已被成功删除

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_volume_factors_deletion():
    """
    测试验证vol_change、vol_rank、vol_std因子是否已被成功删除
    """
    print("=== 测试vol_change、vol_rank、vol_std因子删除 ===")
    
    # 测试1: 导入factor_lib模块，验证基础功能正常
    print("\n测试1: 导入factor_lib模块...")
    try:
        import factor_lib
        from factor_lib import categories, get_all_factor_classes
        print("✓ factor_lib模块导入成功")
    except ImportError as e:
        print(f"✗ factor_lib模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 导入过程中发生意外错误: {e}")
        return False
    
    # 测试2: 检查所有因子类中是否不包含已删除的因子
    print("\n测试2: 检查已删除因子是否不在因子类列表中...")
    try:
        all_factors = get_all_factor_classes()
        deleted_factor_names = ['VolumeChangeRateFactor', 'VolumeRankFactor', 'VolumeStdFactor']
        
        # 检查是否存在已删除的因子类
        for factor_name in deleted_factor_names:
            if factor_name in all_factors:
                print(f"✗ 错误: {factor_name} 仍然存在于因子类列表中")
                return False
        print(f"✓ 已确认所有要删除的因子类不在列表中")
    except Exception as e:
        print(f"✗ 检查因子类时发生错误: {e}")
        return False
    
    # 测试3: 检查成交量类因子列表中是否不包含已删除的因子
    print("\n测试3: 检查成交量类因子列表...")
    try:
        volume_factors = categories.get('volume', [])
        deleted_factor_names = ['VolumeChangeRateFactor', 'VolumeRankFactor', 'VolumeStdFactor']
        
        # 检查是否存在已删除的因子
        for factor_name in deleted_factor_names:
            if factor_name in volume_factors:
                print(f"✗ 错误: {factor_name} 仍然存在于成交量类因子列表中")
                return False
        print("✓ 成交量类因子列表中已删除所有指定因子")
    except Exception as e:
        print(f"✗ 检查成交量类因子时发生错误: {e}")
        return False
    
    # 测试4: 验证无法导入已删除的因子
    print("\n测试4: 验证无法导入已删除的因子...")
    try:
        from factor_lib import VolumeChangeRateFactor
        print("✗ 错误: VolumeChangeRateFactor 仍然可以导入")
        return False
    except ImportError:
        print("✓ VolumeChangeRateFactor 无法导入，删除成功")
    
    try:
        from factor_lib import VolumeRankFactor
        print("✗ 错误: VolumeRankFactor 仍然可以导入")
        return False
    except ImportError:
        print("✓ VolumeRankFactor 无法导入，删除成功")
    
    try:
        from factor_lib import VolumeStdFactor
        print("✗ 错误: VolumeStdFactor 仍然可以导入")
        return False
    except ImportError:
        print("✓ VolumeStdFactor 无法导入，删除成功")
    
    # 测试5: 验证剩余的成交量类因子是否正常工作
    print("\n测试5: 验证剩余的成交量类因子是否正常工作...")
    try:
        # 导入剩余的成交量类因子
        from factor_lib import VolumeFactor, AmountFactor, AmountChangeRateFactor
        from factor_lib import VolumeMeanFactor, VolumeToMeanFactor
        from factor_lib import VolumeAmplitudeFactor, VolumeAccumulationFactor
        
        # 检查这些因子是否能正常初始化
        test_factors = [
            VolumeFactor(),
            AmountFactor(),
            AmountChangeRateFactor(),
            VolumeMeanFactor(),
            VolumeToMeanFactor(),
            VolumeAmplitudeFactor(),
            VolumeAccumulationFactor()
        ]
        
        for factor in test_factors:
            print(f"✓ {factor.__class__.__name__} 初始化成功")
            print(f"  因子名称: {factor.name}")
    except Exception as e:
        print(f"✗ 验证剩余因子时发生错误: {e}")
        return False
    
    print("\n=== 所有测试通过！因子删除成功且代码正常运行 ===")
    return True

if __name__ == "__main__":
    test_volume_factors_deletion()
