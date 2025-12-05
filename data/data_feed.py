import backtrader as bt
import pandas as pd
from datetime import datetime
import os
import sys
from tqdm import tqdm

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 添加项目根目录到sys.path
sys.path.append(project_root)

# 现在可以直接导入logger_config和config模块
try:
    # 因为config目录已经添加到sys.path中，所以可以直接导入
    from config.logger_config import data_logger
    print("[OK] 成功导入 config.logger_config.data_logger")
except Exception as e:
    print(f"[ERROR] 导入 config.logger_config.data_logger 失败: {e}")
    # 如果导入失败，创建一个简单的logger
    import logging
    logging.basicConfig(level=logging.INFO)
    data_logger = logging.getLogger("data_logger")

# 尝试导入CLEANED_DATA_DIR
try:
    from config.config import CLEANED_DATA_DIR
    print("[OK] 成功导入 config.config.CLEANED_DATA_DIR")
except Exception as e:
    print(f"[ERROR] 导入 config.config.CLEANED_DATA_DIR 失败: {e}")
    # 如果导入失败，使用默认值
    CLEANED_DATA_DIR = "cleaned_data/"

class AStockDataLoader:
    @staticmethod
    def load_single_csv(file_path, start_date=None, end_date=None):
        """
        加载单个CSV格式的A股数据
        
        Args:
            file_path (str): CSV文件路径，格式如"sh.600999.csv"
            start_date (str): 开始日期 'YYYY-MM-DD'
            end_date (str): 结束日期 'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        # 注释掉加载数据文件的日志，避免过多打印
        # data_logger.info(f"加载数据文件: {file_path}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            # 注释掉原始数据形状日志
            # data_logger.info(f"原始数据形状: {df.shape}")
            
            # 检查必要的列是否存在
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            # 转换日期列为datetime类型
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 按日期过滤
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
                
            # 确保数值列为正确类型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 删除包含NaN的行
            df.dropna(inplace=True)
            
            # 注释掉处理后数据形状日志
            # data_logger.info(f"处理后数据形状: {df.shape}")
            return df
            
        except Exception as e:
            data_logger.error(f"加载数据失败 {file_path}: {e}")
            raise

    @staticmethod
    def load_multiple_stocks(data_dir, stock_list=None, start_date=None, end_date=None):
        """
        加载多个股票数据
        
        Args:
            data_dir (str): 包含股票数据CSV文件的目录
            stock_list (list): 股票代码列表，如['sh.600999', 'sz.000001']，None表示加载所有
            start_date (str): 开始日期
            end_date (str): 结束日期
            
        Returns:
            dict: 股票数据字典 {stock_code: DataFrame}
        """
        stock_data = {}
        
        # 获取目录中的所有CSV文件
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        # 如果指定了股票列表，则只加载这些股票的数据
        if stock_list:
            # 修改：适应新的文件命名方式 sh.600999_(日期).csv 和清洗后的命名方式
            csv_files = [f for f in csv_files if any(stock in f.split('_')[0] for stock in stock_list)]
        
        data_logger.info(f"找到 {len(csv_files)} 个CSV文件")
        
        # 使用tqdm显示加载进度
        for csv_file in tqdm(csv_files, desc="加载股票数据", unit="只"):
            try:
                file_path = os.path.join(data_dir, csv_file)
                # 修改：提取股票代码的方式适配新命名规则
                stock_code = csv_file.split('_')[0]  # 提取股票代码部分
                
                df = AStockDataLoader.load_single_csv(file_path, start_date, end_date)
                stock_data[stock_code] = df
                data_logger.debug(f"成功加载 {stock_code} 数据，共 {len(df)} 条记录")
                
            except Exception as e:
                data_logger.warning(f"跳过文件 {csv_file}: {e}")
                continue
                
        return stock_data
    
    @staticmethod
    def create_data_feed(df, stock_code=None):
        """
        将pandas DataFrame转换为Backtrader数据源
        
        Args:
            df (pd.DataFrame): 包含股票数据的DataFrame
            stock_code (str): 股票代码（可选）
            
        Returns:
            bt.feeds.PandasData: Backtrader数据源
        """
        return bt.feeds.PandasData(
            dataname=df,
            name=stock_code or 'stock',
            datetime=None,  # 使用索引作为日期
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1  # 不使用未平仓量
        )

class MultiStockDataLoader:
    """
    多股票数据加载器，支持同时加载和处理多个股票
    """
    
    def __init__(self, data_dir=None):
        # 修改：默认使用清洗后的数据目录
        self.data_dir = data_dir or CLEANED_DATA_DIR
        self.stock_data = {}
        
    def load_data(self, stock_list=None, start_date=None, end_date=None):
        """
        加载股票数据
        
        Args:
            stock_list (list): 股票代码列表
            start_date (str): 开始日期
            end_date (str): 结束日期
        """
        self.stock_data = AStockDataLoader.load_multiple_stocks(
            self.data_dir, stock_list, start_date, end_date
        )
        data_logger.info(f"总共加载了 {len(self.stock_data)} 只股票的数据")
        
    def get_data_feed(self, stock_code):
        """
        获取指定股票的数据源
        
        Args:
            stock_code (str): 股票代码
            
        Returns:
            bt.feeds.PandasData: Backtrader数据源
        """
        if stock_code not in self.stock_data:
            raise ValueError(f"未找到股票 {stock_code} 的数据")
            
        return AStockDataLoader.create_data_feed(self.stock_data[stock_code], stock_code)
        
    def get_all_data_feeds(self):
        """
        获取所有股票的数据源
        
        Returns:
            dict: {stock_code: data_feed}
        """
        return {
            stock_code: AStockDataLoader.create_data_feed(df, stock_code)
            for stock_code, df in self.stock_data.items()
        }