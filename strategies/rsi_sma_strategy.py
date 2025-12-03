import backtrader as bt
from .base_strategy import BaseStrategy
from logger_config import strategy_logger

class RSIStrategy(BaseStrategy):
    """
    结合RSI和SMA的复合策略
    特点：
    1. 使用RSI指标判断超买超卖
    2. 使用SMA交叉确认趋势
    3. 实现止损止盈功能
    4. 仓位管理（根据ATR调整仓位）
    """
    
    params = (
        ('sma_short_period', 10),
        ('sma_long_period', 30),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('stop_loss', 0.05),  # 止损比例
        ('take_profit', 0.10),  # 止盈比例
        ('risk_per_trade', 0.02),  # 每笔交易风险比例
    )
    
    def __init__(self):
        super().__init__()
        self.logger = strategy_logger
        
        # 为每个数据源创建指标
        self.indicators = {}
        
        for d in self.datas:
            # 先创建各个指标
            sma_short = bt.indicators.SimpleMovingAverage(d.close, period=self.params.sma_short_period)
            sma_long = bt.indicators.SimpleMovingAverage(d.close, period=self.params.sma_long_period)
            
            # 创建交叉指标
            sma_crossover = bt.indicators.CrossOver(sma_short, sma_long)
            
            indicators = {
                'sma_short': sma_short,
                'sma_long': sma_long,
                'sma_crossover': sma_crossover,
                'rsi': bt.indicators.RelativeStrengthIndex(d.close, period=self.params.rsi_period),
                'atr': bt.indicators.AverageTrueRange(d, period=14),
            }
            
            # 记录买入价格，用于止损止盈
            indicators['buy_price'] = None
            
            self.indicators[d] = indicators
        
        self.logger.info(
            f"初始化RSI-SMA策略，"
            f"短周期SMA:{self.params.sma_short_period}，"
            f"长周期SMA:{self.params.sma_long_period}，"
            f"RSI周期:{self.params.rsi_period}，"
            f"超买:{self.params.rsi_overbought}，"
            f"超卖:{self.params.rsi_oversold}"
        )
        
    def calculate_position_size(self, data):
        """
        根据ATR和风险比例计算仓位大小
        """
        if len(data) < 15:  # ATR需要14个周期
            return self.params.stake  # 默认仓位
        
        # 当前资产
        current_value = self.broker.getvalue()
        
        # 每笔交易可承受的风险金额
        risk_amount = current_value * self.params.risk_per_trade
        
        # 根据ATR计算止损金额
        atr = self.indicators[data]['atr'][0]
        stop_loss_amount = data.close[0] * self.params.stop_loss
        
        # 取ATR和固定比例止损中的最大值
        actual_stop_loss = max(atr, stop_loss_amount)
        
        # 计算仓位大小
        position_size = risk_amount / actual_stop_loss
        
        # 转换为整数股数
        position_size = int(position_size / 100) * 100
        
        # 确保仓位大小不小于最小交易单位
        return max(position_size, 100)
    
    def next(self):
        """每个周期执行一次"""
        for d in self.datas:
            # 获取当前数据的名称
            dataname = d._name
            ind = self.indicators[d]
            
            # 获取当前价格
            current_price = d.close[0]
            
            # 如果有未完成的订单，不进行新操作
            if self.getposition(d).size:
                # 检查是否需要止盈
                if current_price >= ind['buy_price'] * (1 + self.params.take_profit):
                    self.log(f'{dataname} 止盈信号 | 价格: {current_price:.2f} | 买入价: {ind["buy_price"]:.2f}')
                    self.sell(data=d, size=self.getposition(d).size)
                    ind['buy_price'] = None
                    continue
                    
                # 检查是否需要止损
                if current_price <= ind['buy_price'] * (1 - self.params.stop_loss):
                    self.log(f'{dataname} 止损信号 | 价格: {current_price:.2f} | 买入价: {ind["buy_price"]:.2f}')
                    self.sell(data=d, size=self.getposition(d).size)
                    ind['buy_price'] = None
                    continue
                    
                # 检查是否需要根据趋势卖出
                if ind['sma_crossover'] < 0 and ind['rsi'] > self.params.rsi_overbought:
                    self.log(f'{dataname} 趋势反转卖出信号 | 价格: {current_price:.2f} | RSI: {ind["rsi"][0]:.2f}')
                    self.sell(data=d, size=self.getposition(d).size)
                    ind['buy_price'] = None
            else:
                # 没有持仓，寻找买入机会
                # 条件：RSI在超卖区域，且短期均线上穿长期均线
                if ind['rsi'] < self.params.rsi_oversold and ind['sma_crossover'] > 0:
                    # 计算仓位大小
                    position_size = self.calculate_position_size(d)
                    
                    self.log(f'{dataname} 买入信号 | 价格: {current_price:.2f} | RSI: {ind["rsi"][0]:.2f} | 仓位: {position_size}')
                    self.buy(data=d, size=position_size)
                    ind['buy_price'] = current_price
                    
                # 额外的买入条件：RSI在正常区域但快速上升，且均线多头排列
                elif (self.params.rsi_oversold < ind['rsi'] < 50 and 
                      ind['rsi'][0] > ind['rsi'][-1] and 
                      ind['sma_short'][0] > ind['sma_long'][0] and 
                      ind['sma_short'][-1] <= ind['sma_long'][-1]):
                    # 计算仓位大小
                    position_size = self.calculate_position_size(d)
                    
                    self.log(f'{dataname} 强势买入信号 | 价格: {current_price:.2f} | RSI: {ind["rsi"][0]:.2f} | 仓位: {position_size}')
                    self.buy(data=d, size=position_size)
                    ind['buy_price'] = current_price
                    
    def notify_trade(self, trade):
        """
        交易状态通知，扩展基类方法
        """
        if not trade.isclosed:
            return
            
        self.log(f'交易利润 | 毛利: {trade.pnl:.2f} | 净利: {trade.pnlcomm:.2f} | 收益率: {(trade.pnlcomm / trade.price * 100):.2f}%')
        
    def stop(self):
        """
        策略结束，输出策略统计信息
        """
        total_return = (self.broker.getvalue() - self.broker.startingcash) / self.broker.startingcash * 100
        self.log(f'策略结束 | 最终资金: {self.broker.getvalue():.2f} | 总收益率: {total_return:.2f}%')
