import backtrader as bt
from config import *
from logger_config import engine_logger
from data.data_feed import AStockDataLoader
from strategies.sma_strategy import SMAStrategy
from utils.analyzer import add_analyzers
import importlib

class BacktestEngine:
    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.results = None
        self.logger = engine_logger
        
    def setup_broker(self):
        """设置经纪人参数"""
        self.logger.info("设置经纪人参数")
        self.cerebro.broker.setcash(INITIAL_CASH)
        self.cerebro.broker.setcommission(commission=COMMISSION)
        if SLIPPAGE > 0:
            self.cerebro.broker.set_slippage_perc(SLIPPAGE)
            
    def load_data(self):
        """加载数据"""
        self.logger.info(f"正在加载数据: {DATA_PATH}")
        try:
            df = AStockDataLoader.load_csv_data(DATA_PATH, START_DATE, END_DATE)
            self.logger.info(f"数据加载完成，共{len(df)}条记录")
            
            data_feed = AStockDataLoader.create_data_feed(df)
            self.cerebro.adddata(data_feed)
            self.logger.info("数据添加到引擎成功")
        except Exception as e:
            self.logger.error(f"数据加载失败: {e}")
            raise
            
    def add_strategy(self):
        """添加策略"""
        self.logger.info(f"添加策略: {STRATEGY_NAME}")
        try:
            # 动态导入策略类
            strategy_module = importlib.import_module(f"strategies.{STRATEGY_NAME.lower()}")
            strategy_class = getattr(strategy_module, STRATEGY_NAME)
            
            self.cerebro.addstrategy(strategy_class, **STRATEGY_PARAMS)
            self.logger.info("策略添加成功")
        except Exception as e:
            self.logger.error(f"策略添加失败: {e}")
            raise
            
    def run_backtest(self):
        """运行回测"""
        self.logger.info("开始运行回测")
        self.logger.info(f'初始资金: {self.cerebro.broker.getvalue():.2f}')
        
        # 添加分析器
        add_analyzers(self.cerebro)
        
        # 运行回测
        self.results = self.cerebro.run()
        
        final_value = self.cerebro.broker.getvalue()
        profit = final_value - INITIAL_CASH
        
        self.logger.info(f'最终资金: {final_value:.2f}')
        self.logger.info(f'总收益: {profit:.2f}')
        self.logger.info(f'收益率: {(profit/INITIAL_CASH)*100:.2f}%')
        
        return self.results
        
    def execute(self):
        """执行完整的回测流程"""
        self.logger.info("开始执行回测流程")
        try:
            self.setup_broker()
            self.load_data()
            self.add_strategy()
            results = self.run_backtest()
            self.logger.info("回测执行完成")
            return results
        except Exception as e:
            self.logger.error(f"回测执行失败: {e}")
            raise