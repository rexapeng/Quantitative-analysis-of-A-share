#基础策略模版
import backtrader as bt
from tqdm import tqdm
import sys

class BaseStrategy(bt.Strategy):
    """基础策略类"""
    
    params = (
        ('stake', 100),  # 交易数量
    )
    
    def __init__(self):
        """初始化策略"""
        # 初始化进度条相关变量
        self.pbar = None
        self.total_bars = 0
        self.current_bar = 0
        
        # 计算总周期数
        if self.datas:
            self.total_bars = len(self.datas[0])
            # 初始化进度条，使用file=sys.stdout确保在终端中显示
            if self.total_bars > 0:
                self.pbar = tqdm(
                    total=self.total_bars, 
                    desc="回测进度", 
                    leave=True,
                    file=sys.stdout,
                    dynamic_ncols=True
                )
        
        # 初始化策略变量
        self.data_close = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
    def next(self):
        # 更新进度条
        if self.pbar:
            self.current_bar += 1
            self.pbar.update(1)
            self.pbar.set_postfix_str(f"完成 {self.current_bar}/{self.total_bars}")
        
    def buy_signal(self):
        """买入信号"""
        return False
        
    def sell_signal(self):
        """卖出信号"""
        return False
        
    def log(self, txt, dt=None):
        """记录日志"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        
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
        # 关闭进度条
        if self.pbar:
            self.pbar.close()