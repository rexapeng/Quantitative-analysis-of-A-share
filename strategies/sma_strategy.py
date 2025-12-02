import backtrader as bt
from .base_strategy import BaseStrategy

class SMAStrategy(BaseStrategy):
    """
    简单移动平均线交叉策略
    当短期均线上穿长期均线时买入，下穿时卖出
    """
    
    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('stake', 100),
    )
    
    def __init__(self):
        super().__init__()
        
        # 计算移动平均线
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long_period
        )
        
        # 计算交叉信号
        self.crossover = bt.indicators.CrossOver(self.sma_short, self.sma_long)
        
        # 添加指标到观察器
        bt.indicators.MovingAverageSimple(self.datas[0], period=20)
        
    def next(self):
        """每个周期执行一次"""
        # 如果有未完成的订单，不进行新操作
        if self.order:
            return
            
        # 检查是否有持仓
        if not self.position:
            # 没有持仓，寻找买入机会
            if self.crossover > 0:  # 短期均线上穿长期均线
                self.log(f'买入信号 | 价格: {self.data_close[0]:.2f}')
                self.order = self.buy(size=self.params.stake)
        else:
            # 有持仓，寻找卖出机会
            if self.crossover < 0:  # 短期均线下穿长期均线
                self.log(f'卖出信号 | 价格: {self.data_close[0]:.2f}')
                self.order = self.sell(size=self.params.stake)