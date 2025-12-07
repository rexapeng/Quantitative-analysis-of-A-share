import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from factor_lib.utils import get_database_connection

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置参数
START_DATE = '2015-01-01'
END_DATE = '2025-12-05'
FORWARD_PERIOD = 10
NORMALIZE_FACTOR = True
TEST_SCOPE = 'HS300'
INDIVIDUAL_STOCK = None

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 导入FactorAnalyzer类
from analyzer.factor_analyzer import FactorAnalyzer

# 主函数
def main():
    try:
        # 连接数据库
        conn = get_database_connection()
        logger.info("成功连接到数据库")
        
        # 创建FactorAnalyzer实例
        analyzer = FactorAnalyzer(conn)
        
        # 设置测试范围
        analyzer.set_test_scope(TEST_SCOPE, INDIVIDUAL_STOCK)
        
        # 测试多个因子
        test_factors = ['macd_diff', 'rsi_14', 'kdj_j']
        
        for test_factor in test_factors:
            logger.info(f"\n===== 开始分析因子: {test_factor} =====")
            
            # 执行分组收益分析
            try:
                logger.info("正在调用analyze_group_returns方法...")
                group_result = analyzer.analyze_group_returns(test_factor, num_groups=20, forward_period=FORWARD_PERIOD, start_date=START_DATE, end_date=END_DATE)
                logger.info("analyze_group_returns方法调用完成")
            except Exception as e:
                logger.error(f"调用analyze_group_returns方法时发生异常: {str(e)}")
                import traceback
                traceback.print_exc()
                group_result = None
            
            if group_result:
                logger.info(f"因子 {test_factor} 的分组收益分析成功完成")
                logger.info(f"共分析了 {group_result['total_days']} 个交易日")
                
                # 详细展示分组收益结果
                logger.info("\n平均分组收益率（按因子值从低到高分组）:")
                for group_num in sorted(group_result['avg_group_returns'].keys()):
                    logger.info(f"  第 {group_num} 组: {group_result['avg_group_returns'][group_num]:.4f}%")
                
                # 计算多空组合收益率（最后一组 - 第一组）
                if len(group_result['avg_group_returns']) >= 2:
                    sorted_groups = sorted(group_result['avg_group_returns'].keys())
                    long_short_return = group_result['avg_group_returns'][sorted_groups[-1]] - group_result['avg_group_returns'][sorted_groups[0]]
                    logger.info(f"\n多空组合收益率（高分组 - 低分组）: {long_short_return:.4f}%")
                
                # 检查单调性
                returns_list = [group_result['avg_group_returns'][g] for g in sorted(group_result['avg_group_returns'].keys())]
                is_monotonic = all(returns_list[i] <= returns_list[i+1] for i in range(len(returns_list)-1)) or all(returns_list[i] >= returns_list[i+1] for i in range(len(returns_list)-1))
                logger.info(f"分组收益单调性: {'是' if is_monotonic else '否'}")
            else:
                logger.error(f"因子 {test_factor} 的分组收益分析失败")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        conn.close()

if __name__ == "__main__":
    main()