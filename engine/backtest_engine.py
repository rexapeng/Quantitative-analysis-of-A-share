import backtrader as bt
from config import *
from logger_config import engine_logger
from data.data_feed import AStockDataLoader, MultiStockDataLoader
import importlib

class BacktestEngine:
    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.results = None
        self.logger = engine_logger
        self.data_loader = None
        
    def setup_broker(self):
        """设置经纪人参数"""
        self.logger.info("设置经纪人参数")
        self.cerebro.broker.setcash(INITIAL_CASH)
        self.cerebro.broker.setcommission(commission=COMMISSION)
        if SLIPPAGE > 0:
            self.cerebro.broker.set_slippage_fixed(SLIPPAGE)  # 注意：这里修正了API调用
            
    def load_data(self):
        """加载数据"""
        self.logger.info(f"数据模式: {BACKTEST_MODE}")
        
        if BACKTEST_MODE == "single":
            self._load_single_stock()
        elif BACKTEST_MODE == "multi":
            self._load_multi_stock()
        else:
            raise ValueError(f"未知的回测模式: {BACKTEST_MODE}")
            
    def _load_single_stock(self):
        """加载单个股票数据"""
        file_path = os.path.join(DATA_DIR, f"{SINGLE_STOCK}.csv")
        self.logger.info(f"正在加载单个股票数据: {file_path}")
        
        try:
            df = AStockDataLoader.load_single_csv(file_path, START_DATE, END_DATE)
            self.logger.info(f"数据加载完成，共{len(df)}条记录")
            
            data_feed = AStockDataLoader.create_data_feed(df, SINGLE_STOCK)
            self.cerebro.adddata(data_feed)
            self.logger.info("数据添加到引擎成功")
        except Exception as e:
            self.logger.error(f"单个股票数据加载失败: {e}")
            raise
            
    def _load_multi_stock(self):
        """加载多个股票数据"""
        self.logger.info(f"正在加载多个股票数据从目录: {DATA_DIR}")
        
        try:
            self.data_loader = MultiStockDataLoader(DATA_DIR)
            self.data_loader.load_data(STOCK_LIST, START_DATE, END_DATE)
            
            # 添加所有数据到引擎
            data_feeds = self.data_loader.get_all_data_feeds()
            for stock_code, data_feed in data_feeds.items():
                self.cerebro.adddata(data_feed)
                self.logger.info(f"已添加股票数据: {stock_code}")
                
            self.logger.info(f"总共添加了 {len(data_feeds)} 只股票的数据")
            
        except Exception as e:
            self.logger.error(f"多股票数据加载失败: {e}")
            raise
            
    def add_strategy(self):
        """添加策略"""
        self.logger.info(f"添加策略: {STRATEGY_NAME}")
        try:
            # 动态导入策略类
            module_name = f"strategies.{STRATEGY_NAME.lower()}"
            strategy_module = importlib.import_module(module_name)
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
        from utils.analyzer import add_analyzers
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