#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试get_all_factor_classes函数是否正确返回当前代码中存在的因子类
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_get_all_factor_classes')

# 导入要测试的函数
from factor_lib import get_all_factor_classes

def main():
    """
    主函数
    """
    try:
        # 调用测试函数
        factor_classes = get_all_factor_classes()
        
        logger.info(f"动态获取的因子类数量: {len(factor_classes)}")
        logger.info("因子类列表:")
        for factor_class in factor_classes:
            logger.info(f"  - {factor_class.__name__}")
            
        # 检查是否包含已删除的顶部形态因子类
        deleted_top_pattern_classes = [
            'DoubleTopFactor', 
            'HeadShoulderTopFactor', 
            'TripleTopFactor'
        ]
        
        logger.info("\n检查是否包含已删除的顶部形态因子类:")
        for deleted_class in deleted_top_pattern_classes:
            found = any(factor_class.__name__ == deleted_class for factor_class in factor_classes)
            if found:
                logger.warning(f"  - {deleted_class} 仍然存在于因子类列表中")
            else:
                logger.info(f"  - {deleted_class} 已成功从因子类列表中移除")
                
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")

if __name__ == "__main__":
    main()