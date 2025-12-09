#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试get_all_available_factors函数是否正确返回当前代码中存在的因子
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_available_factors')

# 导入要测试的函数
from analyzer.factor_analyzer import get_all_available_factors
from factor_lib import get_database_connection

def main():
    """
    主函数
    """
    # 获取数据库连接
    conn = get_database_connection()
    if conn is None:
        logger.error("无法连接数据库")
        return
    
    try:
        # 调用测试函数
        factors = get_all_available_factors(conn)
        
        logger.info(f"动态获取的因子数量: {len(factors)}")
        logger.info("因子列表:")
        for factor in factors:
            logger.info(f"  - {factor}")
            
        # 检查是否包含顶部形态因子
        top_pattern_factors = [
            'head_shoulder_top_30', 
            'triple_top_40', 
            'double_top_20'
        ]
        
        logger.info("\n检查是否包含已删除的顶部形态因子:")
        for top_factor in top_pattern_factors:
            if top_factor in factors:
                logger.warning(f"  - {top_factor} 仍然存在于因子列表中")
            else:
                logger.info(f"  - {top_factor} 已成功从因子列表中移除")
                
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()