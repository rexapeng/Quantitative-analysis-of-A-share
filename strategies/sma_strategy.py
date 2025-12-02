import backtrader as bt
from .base_strategy import BaseStrategy
from logger_config import strategy_logger

class SMAStrategy(BaseStrategy):
    """
    简单移动平均线交叉策略
    支持单股票或多股票回测
    """
    
    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('stake', 100),
    )
    
    def __init__(self):
        super().__init__()
        self.logger = strategy_logger
        
        # 为每个数据源创建指标
        self.sma_short = {}
        self.sma_long = {}
        self.crossover = {}
        
        for d in self.datas:
            # 计算移动平均线
            self.sma_short[d] = bt.indicators.SimpleMovingAverage(
                d, period=self.params.short_period
            )
            self.sma_long[d] = bt.indicators.SimpleMovingAverage(
                d, period=self.params.long_period
            )
            
            # 计算交叉信号
            self.crossover[d] = bt.indicators.CrossOver(
                self.sma_short[d], self.sma_long[d]
            )
        
        self.logger.info(f"初始化SMA策略，短周期:{self.params.short_period}，长周期:{self.params.long_period}")
        
    def next(self):
        """每个周期执行一次"""
        for i, d in enumerate(self.datas):
            # 获取当前数据的名称
            dataname = d._name
            
            # 如果有未完成的订单，不进行新操作
            if self.getposition(d).size:
                # 检查是否需要卖出
                if self.crossover[d] < 0:  # 短期均线下穿长期均线
                    self.log(f'{dataname} 卖出信号 | 价格: {d.close[0]:.2f}')
                    self.sell(data=d, size=self.params.stake)
            else:
                # 没有持仓，寻找买入机会
                if self.crossover[d] > 0:  # 短期均线上穿长期均线
                    self.log(f'{dataname} 买入信号 | 价格: {d.close[0]:.2f}')
                    self.buy(data=d, size=self.params.stake)
                    
    def stop(self):
        """策略结束"""
        self.log(f'策略结束，最终资金: {self.broker.getvalue():.2f}')