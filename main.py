#!/usr/bin/env python3

from engine.backtest_engine import BacktestEngine
from engine.report_generator import ReportGenerator
from utils.plotter import Plotter
from logger_config import main_logger
from config import PLOT_ENABLE

def main():
    """主程序入口"""
    main_logger.info("启动回测系统")
    
    try:
        # 初始化回测引擎
        engine = BacktestEngine()
        
        # 执行回测
        results = engine.execute()
        
        # 生成报告
        report_gen = ReportGenerator(results, engine.cerebro)
        summary = report_gen.generate_report()
        
        # 绘制并保存图表
        if PLOT_ENABLE:
            plotter = Plotter(engine.cerebro)
            plotter.save_plot()
            
        main_logger.info("回测系统执行完成")
        print("\n=== 回测完成 ===")
        print(f"最终资金: ¥{summary['final_value']:,.2f}")
        print(f"总收益率: {summary['total_return_pct']:.2f}%")
        print(f"详细报告已保存至: results/")
        
    except Exception as e:
        main_logger.error(f"回测系统执行失败: {e}")
        raise

if __name__ == '__main__':
    main()