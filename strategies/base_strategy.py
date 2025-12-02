#基础策略模版import backtrader as bt

class BaseStrategy(bt.Strategy):
    """
    所有策略的基类，包含通用功能
    """
    
    params = (
        ('stake', 100),  # 交易数量
    )
    
    def log(self, txt, dt=None):
        """记录日志"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        
    def __init__(self):
        """初始化策略"""
        self.data_close = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交/已接受 - 无事可做
            return
            
        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入执行 | 价格: {order.executed.price:.2f} | 成本: {order.executed.value:.2f} | 手续费: {order.executed.comm:.2f}'
                )
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            else:
                self.log(
                    f'卖出执行 | 价格: {order.executed.price:.2f} | 成本: {order.executed.value:.2f} | 手续费: {order.executed.comm:.2f}'
                )
                
            self.bar_executed = len(self)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')
            
        self.order = None
        
    def notify_trade(self, trade):
        """交易状态通知"""
        if not trade.isclosed:
            return
            
        self.log(f'交易利润 | 毛利: {trade.pnl:.2f} | 净利: {trade.pnlcomm:.2f}')
        
    def start(self):
        """策略开始"""
        self.log('策略开始')
        
    def stop(self):
        """策略结束"""
        self.log('策略结束')