import os
import json
from datetime import datetime
from config import RESULT_DIR, TIMESTAMP, REPORT_FORMAT
from logger_config import engine_logger
from utils.analyzer import print_analysis

class ReportGenerator:
    def __init__(self, results, cerebro):
        self.results = results
        self.cerebro = cerebro
        self.logger = engine_logger
        
    def generate_summary_stats(self):
        """生成摘要统计信息"""
        strat = self.results[0]
        
        # 获取分析结果
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        sqn = strat.analyzers.sqn.get_analysis()
        
        summary = {
            "timestamp": TIMESTAMP,
            "initial_cash": self.cerebro.broker.startingcash,
            "final_value": self.cerebro.broker.getvalue(),
            "total_pnl": self.cerebro.broker.getvalue() - self.cerebro.broker.startingcash,
            "total_return_pct": ((self.cerebro.broker.getvalue() / self.cerebro.broker.startingcash) - 1) * 100,
            "sharpe_ratio": sharpe.get('sharperatio', 'N/A'),
            "max_drawdown_pct": drawdown.max.drawdown,
            "annual_return_pct": returns.rnorm * 100 if hasattr(returns, 'rnorm') else 'N/A',
            "sqn": sqn.sqn if hasattr(sqn, 'sqn') else 'N/A',
            "total_trades": trades.total.total if hasattr(trades, 'total') else 0,
            "winning_trades": trades.won.total if hasattr(trades, 'won') else 0,
            "losing_trades": trades.lost.total if hasattr(trades, 'lost') else 0
        }
        
        return summary
        
    def save_json_report(self, summary):
        """保存JSON格式报告"""
        filename = os.path.join(RESULT_DIR, f"report_{TIMESTAMP}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.logger.info(f"JSON报告已保存: {filename}")
        
    def save_html_report(self, summary):
        """保存HTML格式报告"""
        filename = os.path.join(RESULT_DIR, f"report_{TIMESTAMP}.html")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>回测报告</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary-table {{ border-collapse: collapse; width: 100%; }}
        .summary-table td, .summary-table th {{ border: 1px solid #ddd; padding: 8px; }}
        .summary-table tr:nth-child(even){{ background-color: #f2f2f2; }}
        .summary-table th {{ padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>回测报告</h1>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>摘要统计</h2>
    <table class="summary-table">
        <tr><td>初始资金</td><td>¥{summary['initial_cash']:,.2f}</td></tr>
        <tr><td>最终价值</td><td>¥{summary['final_value']:,.2f}</td></tr>
        <tr><td>总盈亏</td><td>¥{summary['total_pnl']:,.2f}</td></tr>
        <tr><td>总收益率</td><td>{summary['total_return_pct']:.2f}%</td></tr>
        <tr><td>夏普比率</td><td>{summary['sharpe_ratio']}</td></tr>
        <tr><td>最大回撤</td><td>{summary['max_drawdown_pct']:.2f}%</td></tr>
        <tr><td>年化收益率</td><td>{summary['annual_return_pct']}%</td></tr>
        <tr><td>SQN</td><td>{summary['sqn']}</td></tr>
        <tr><td>总交易数</td><td>{summary['total_trades']}</td></tr>
        <tr><td>盈利交易数</td><td>{summary['winning_trades']}</td></tr>
        <tr><td>亏损交易数</td><td>{summary['losing_trades']}</td></tr>
    </table>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"HTML报告已保存: {filename}")
        
    def generate_report(self):
        """生成报告"""
        self.logger.info("开始生成报告")
        try:
            summary = self.generate_summary_stats()
            
            if REPORT_FORMAT == "json":
                self.save_json_report(summary)
            elif REPORT_FORMAT == "html":
                self.save_html_report(summary)
            else:
                self.save_json_report(summary)
                self.save_html_report(summary)
                
            self.logger.info("报告生成完成")
            return summary
        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            raise