import backtrader as bt
import pandas as pd
from datetime import datetime

class AStockDataLoader:
    @staticmethod
    def load_csv_data(file_path, start_date=None, end_date=None):
        """
        加载CSV格式的A股数据
        
        Args:
            file_path (str): CSV文件路径
            start_date (str): 开始日期 'YYYY-MM-DD'
            end_date (str): 结束日期 'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        # 假设CSV包含以下列: date, open, high, low, close, volume
        df = pd.read_csv(file_path)
        
        # 转换日期列
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # 按日期过滤
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
            
        return df
    
    @staticmethod
    def create_data_feed(df):
        """
        将pandas DataFrame转换为Backtrader数据源
        
        Args:
            df (pd.DataFrame): 包含股票数据的DataFrame
            
        Returns:
            bt.feeds.PandasData: Backtrader数据源
        """
        return bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为日期
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1  # 不使用未平仓量
        )