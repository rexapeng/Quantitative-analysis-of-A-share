import pandas as pd
import sqlite3
from abc import ABC, abstractmethod
from tqdm import tqdm

class Factor(ABC):
    """
    因子基类，所有因子都继承自这个类
    
    设计意图：提供因子计算、存储和加载的统一接口，实现因子的标准化管理
    主要功能：
    1. 定义因子的基本属性和抽象计算方法
    2. 提供因子数据的数据库存储和加载功能
    3. 支持因子数据的清洗和预处理
    
    使用示例：
    class MyFactor(Factor):
        def __init__(self, name='my_factor'):
            super().__init__(name=name)
        
        def calculate(self, data):
            # 实现因子计算逻辑
            return factor_values
    """
    def __init__(self, name, factor_table='factors'):
        """
        初始化因子
        
        Parameters:
            name: str, 因子名称，用于标识和存储因子
            factor_table: str, 因子数据存储的数据库表名，默认为'factors'
        """
        self.name = name
        self.factor_table = factor_table
        self.data = None  # 存储计算后的因子数据
        
    @abstractmethod
    def calculate(self, data):
        """
        计算因子值的抽象方法，子类必须实现
        
        Parameters:
            data: pd.DataFrame, 原始股票数据，包含必要的价格、成交量等字段
            
        Returns:
            pd.DataFrame: 包含因子值的DataFrame，必须包含ts_code、trade_date和因子值列
        """
        pass
    
    def store_to_db(self, conn):
        """
        将因子值存储到数据库（存储前会进行数据清洗）
        
        Parameters:
            conn: sqlite3.Connection, 数据库连接对象
            
        Returns:
            bool: 存储是否成功
        """
        if self.data is None or self.data.empty:
            print(f"因子 {self.name} 数据为空，不存储")
            return False
        
        try:
            # 导入清洗函数
            from .utils import clean_factor_data
            
            # 清洗因子数据
            cleaned_data = clean_factor_data(self.data, self.name)
            if cleaned_data is None or cleaned_data.empty:
                print(f"因子 {self.name} 清洗后数据为空，不存储")
                return False
            
            # 创建因子表（如果不存在）
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.factor_table} (
                    ts_code TEXT,
                    trade_date TEXT,
                    factor_name TEXT,
                    factor_value REAL,
                    PRIMARY KEY (ts_code, trade_date, factor_name)
                )
            """)
            conn.commit()
            
            # 存储因子值
            data_to_insert = []
            for _, row in cleaned_data.iterrows():
                data_to_insert.append((
                    row['ts_code'],
                    row['trade_date'],
                    self.name,
                    row[self.name]
                ))
            
            cursor.executemany(f"""
                INSERT OR REPLACE INTO {self.factor_table} 
                (ts_code, trade_date, factor_name, factor_value)
                VALUES (?, ?, ?, ?)
            """, data_to_insert)
            conn.commit()
            
            print(f"因子 {self.name} 已存储到数据库")
            return True
        except Exception as e:
            print(f"存储因子 {self.name} 到数据库错误: {e}")
            return False
    
    def load_from_db(self, conn, ts_code=None, start_date=None, end_date=None):
        """
        从数据库加载因子值
        
        Parameters:
            conn: sqlite3.Connection, 数据库连接对象
            ts_code: str, 股票代码，None表示加载所有股票的因子值
            start_date: str, 开始日期，格式为'YYYYMMDD'，None表示不限制开始日期
            end_date: str, 结束日期，格式为'YYYYMMDD'，None表示不限制结束日期
        
        Returns:
            pd.DataFrame or None: 包含因子值的DataFrame，包含ts_code、trade_date和因子值列；如果没有数据则返回None
        """
        try:
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = [f"factor_name = '{self.name}'"]
            if ts_code:
                conditions.append(f"ts_code = '{ts_code}'")
            if start_date:
                conditions.append(f"trade_date >= '{start_date}'")
            if end_date:
                conditions.append(f"trade_date <= '{end_date}'")
            
            where_clause = " AND ".join(conditions) if conditions else "1"
            
            # 执行查询
            query = f"""
                SELECT ts_code, trade_date, factor_value 
                FROM {self.factor_table} 
                WHERE {where_clause}
                ORDER BY ts_code, trade_date
            """
            
            df = pd.read_sql(query, conn)
            if not df.empty:
                df = df.rename(columns={'factor_value': self.name})
                self.data = df
                return df
            else:
                return None
        except Exception as e:
            print(f"从数据库加载因子 {self.name} 错误: {e}")
            return None


class FactorManager:
    """
    因子管理器，用于管理和计算多个因子
    
    设计意图：提供统一的接口来管理多个因子，实现批量计算和存储因子值
    主要功能：
    1. 添加和管理多个因子对象
    2. 批量计算所有因子值
    3. 批量将因子值存储到数据库
    
    使用示例：
    # 创建因子管理器
    manager = FactorManager()
    
    # 添加因子
    manager.add_factor(PriceMeanFactor(window=20))
    manager.add_factor(VolumeFactor())
    manager.add_factor(MomentumFactor(window=10))
    
    # 批量计算因子
    factor_results = manager.calculate_all(stock_data)
    
    # 批量存储因子值到数据库
    with sqlite3.connect('stock_data.db') as conn:
        success_count = manager.store_all_to_db(conn)
    """
    def __init__(self):
        """
        初始化因子管理器
        """
        self.factors = []  # 存储所有因子对象的列表
    
    def add_factor(self, factor):
        """
        添加因子到管理器
        
        Parameters:
            factor: Factor, 要添加的因子对象，必须是Factor类的子类
        """
        self.factors.append(factor)
    
    def calculate_all(self, data):
        """
        批量计算所有因子值
        
        Parameters:
            data: pd.DataFrame, 原始股票数据，包含所有因子计算所需的字段
        
        Returns:
            list: 包含所有因子计算结果的列表，每个元素是一个DataFrame
        """
        results = []
        for factor in tqdm(self.factors, desc="计算因子"):
            print(f"正在计算因子: {factor.name}")
            result = factor.calculate(data)
            if result is not None and not result.empty:
                results.append(result)
        return results
    
    def store_all_to_db(self, conn):
        """
        存储所有因子值到数据库
        
        Parameters:
        conn: 数据库连接对象
        """
        success_count = 0
        for factor in tqdm(self.factors, desc="存储因子"):
            if factor.store_to_db(conn):
                success_count += 1
        return success_count


if __name__ == "__main__":
    pass