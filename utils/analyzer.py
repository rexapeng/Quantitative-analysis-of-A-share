import backtrader.analyzers as btanalyzers
import backtrader as bt

def add_analyzers(cerebro):
    """添加分析器到Cerebro引擎"""
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')

def print_analysis(results):
    """打印分析结果"""
    strat = results[0]
    
    # 夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    print(f"夏普比率: {sharpe.get('sharperatio', 'N/A')}")
    
    # 最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f"最大回撤: {drawdown.max.drawdown:.2f}%")
    
    # 收益率
    returns = strat.analyzers.returns.get_analysis()
    print(f"年化收益率: {returns.rnorm*100:.2f}%")
    
    # 交易统计
    trades = strat.analyzers.trades.get_analysis()
    if hasattr(trades, 'total'):
        print(f"总交易数: {trades.total.total}")
        if hasattr(trades, 'won'):
            print(f"盈利交易数: {trades.won.total}")
            print(f"亏损交易数: {trades.lost.total}")