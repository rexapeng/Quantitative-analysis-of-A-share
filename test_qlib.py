#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from factor.qlib_factor_analyzer import QlibFactorAnalyzer
from config.logger_config import data_logger

def test_qlib_factor_analyzer():
    """
    测试Qlib因子分析器
    """
    try:
        print("=== 测试Qlib因子分析器 ===")
        
        # 创建Qlib因子分析器实例
        analyzer = QlibFactorAnalyzer()
        
        # 测试数据加载
        print("1. 测试数据加载...")
        handler = analyzer.load_data(
            instruments="csi300",
            start_time="2015-01-01",
            end_time="2015-12-31",
            freq="day"
        )
        print("数据加载成功")
        
        # 测试因子计算
        print("2. 测试因子计算...")
        factors, labels = analyzer.calculate_factors(handler)
        print(f"因子计算成功，共{len(factors.columns)}个因子")
        print(f"前5个因子: {factors.columns[:5].tolist()}")
        
        # 测试因子分析
        print("3. 测试因子分析...")
        analysis_result = analyzer.analyze_factors(factors, labels)
        print(f"因子分析成功")
        print(f"平均IC: {analysis_result['ic_mean'].mean():.4f}")
        print(f"平均IR: {analysis_result['ic_ir'].mean():.4f}")
        
        # 测试端到端分析（简化版）
        print("4. 测试端到端分析（简化版）...")
        results = analyzer.run_end_to_end_analysis(
            instruments="csi300",
            start_time="2015-01-01",
            end_time="2016-12-31"
        )
        print("端到端分析成功")
        
        print("\n=== Qlib因子分析器测试通过 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == '__main__':
    test_qlib_factor_analyzer()