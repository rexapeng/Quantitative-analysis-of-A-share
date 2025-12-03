#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.backtest_engine import BacktestEngine
from engine.report_generator import ReportGenerator
from utils.plotter import Plotter
from logger_config import main_logger
from config import PLOT_ENABLE, BACKTEST_CONFIG, SMA_CONFIG, RSI_SMA_CONFIG

def main():
    """主程序入口"""
    try:
        # 初始化回测引擎
        backtest_engine = BacktestEngine()
        
        # 根据配置选择策略和参数
        strategy_name = BACKTEST_CONFIG.get('strategy', 'sma')
        
        # 获取对应的策略配置
        if strategy_name == 'rsi_sma':
            strategy_params = RSI_SMA_CONFIG
        else:
            strategy_params = SMA_CONFIG
        
        print(f"使用策略: {strategy_name}")
        print(f"策略参数: {strategy_params}")
        
        # 执行回测
        results = backtest_engine.execute(strategy_name=strategy_name, **strategy_params)
        
        # 生成报告
        report_gen = ReportGenerator(results, backtest_engine.cerebro)
        summary = report_gen.generate_report()
        
        # 绘制并保存图表
        if PLOT_ENABLE:
            plotter = Plotter(backtest_engine.cerebro)
            plotter.save_plot()
            print("图表保存成功")
        
        print("\n=== 回测完成 ===")
        print(f"最终资金: ¥{summary['final_value']:,.2f}")
        print(f"总收益率: {summary['total_return_pct']:.2f}%")
        print(f"详细报告已保存至: results/")
        
    except Exception as e:
        print(f"回测过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()