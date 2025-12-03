import backtrader as bt
from datetime import datetime
import pandas as pd
from data.data_feed import MultiStockDataLoader
from strategies.sma_strategy import SMAStrategy
from strategies.rsi_sma_strategy import RSIStrategy
from utils.analyzer import add_analyzers
from logger_config import engine_logger
# 导入新增的配置项
from config import INITIAL_CASH, COMMISSION_RATE, STAMP_DUTY_RATE, BACKTEST_CONFIG

class BacktestEngine:
    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.logger = engine_logger
        
    def setup_broker(self):
        """设置经纪人"""
        # 设置初始资金
        self.cerebro.broker.setcash(INITIAL_CASH)
        
        # 设置手续费
        self.cerebro.broker.setcommission(commission=COMMISSION_RATE)
        
        # 添加印花税（仅在卖出时）
        # 注意：Backtrader默认不支持单边收取印花税，这里仅为示意
        # 实际应用中可以通过自定义佣金模式实现
        
        self.logger.info(f"初始资金设置为: ¥{INITIAL_CASH:,}")
        self.logger.info(f"手续费率: {COMMISSION_RATE*100:.2f}%")
        
    def load_data(self):
        """加载数据"""
        # 使用MultiStockDataLoader加载清洗后的数据
        # 传入回测配置的时间范围和标的列表
        data_loader = MultiStockDataLoader()
        data_loader.load_data(
            stock_list=BACKTEST_CONFIG['symbols'] or None,
            start_date=BACKTEST_CONFIG['start_date'],
            end_date=BACKTEST_CONFIG['end_date']
        )
        
        # 添加所有数据到cerebro
        data_feeds = data_loader.get_all_data_feeds()
        for stock_code, data_feed in data_feeds.items():
            self.cerebro.adddata(data_feed, name=stock_code)
            
        self.logger.info(f"成功加载 {len(data_feeds)} 只股票的数据")
        
    def setup_strategy(self, strategy_name='sma', **kwargs):
        """设置策略"""
        # 根据策略名称选择不同的策略
        strategy_map = {
            'sma': SMAStrategy,
            'rsi_sma': RSIStrategy,
        }
        
        strategy_class = strategy_map.get(strategy_name, SMAStrategy)
        
        # 添加策略并传入参数
        self.cerebro.addstrategy(strategy_class, **kwargs)
        self.logger.info(f"{strategy_class.__name__} 策略添加完成")
        
    def setup_analyzers(self):
        """设置分析器"""
        add_analyzers(self.cerebro)
        self.logger.info("分析器添加完成")
        
    def execute(self, strategy_name='sma', **strategy_params):
        """执行回测"""
        self.logger.info("开始执行回测")
        
        # 设置经纪人
        self.setup_broker()
        
        # 加载数据
        self.load_data()
        
        # 设置策略
        self.setup_strategy(strategy_name, **strategy_params)
        
        # 设置分析器
        self.setup_analyzers()
        
        # 运行回测
        results = self.cerebro.run()
        
        self.logger.info("回测执行完成")
        # 确保返回结果
        return results if results else []