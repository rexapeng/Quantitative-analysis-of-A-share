import pandas as pd
import numpy as np
import os
import sys
import logging
import time
from datetime import datetime
import json

# 导入项目的日志配置
from config.logger_config import system_logger as logger

def get_database_connection(config_file=None):
    """
    获取数据库连接
    
    参数:
        config_file: 配置文件路径
        
    返回:
        sqlite3.Connection: 数据库连接对象
    """
    try:
        import sqlite3
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 如果没有提供配置文件路径，使用默认路径
        if config_file is None:
            config_file = os.path.join(project_root, 'config', 'config.json')
        
        # 读取配置文件
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        db_path = config.get('DATABASE_PATH', 'data/data/stock_data.db')
        
        # 如果数据库路径是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            db_path = os.path.join(project_root, db_path)
        
        # 创建数据库目录（如果不存在）
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        logger.info(f"成功连接到数据库: {db_path}")
        return conn
    
    except Exception as e:
        logger.error(f"连接数据库失败: {str(e)}")
        return None

def load_stock_data(conn, table_name='daily_quotes', ts_codes=None, start_date=None, end_date=None):
    """
    从数据库加载股票数据
    
    参数:
        conn: 数据库连接对象
        table_name: 表名
        ts_codes: 股票代码列表（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        
    返回:
        pandas.DataFrame: 股票数据
    """
    try:
        query = f"SELECT * FROM {table_name}"
        conditions = []
        
        if ts_codes:
            if isinstance(ts_codes, list):
                codes_str = ', '.join([f"'{code}'" for code in ts_codes])
                conditions.append(f"ts_code IN ({codes_str})")
            else:
                conditions.append(f"ts_code = '{ts_codes}'")
        
        if start_date:
            conditions.append(f"trade_date >= '{start_date}'")
        
        if end_date:
            conditions.append(f"trade_date <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn)
        logger.info(f"成功加载 {len(df)} 条股票数据")
        return df
    
    except Exception as e:
        logger.error(f"加载股票数据失败: {str(e)}")
        return None

def load_stock_list(conn, table_name='stock_list'):
    """
    从数据库加载股票列表
    
    参数:
        conn: 数据库连接对象
        table_name: 表名
        
    返回:
        pandas.DataFrame: 股票列表
    """
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        logger.info(f"成功加载 {len(df)} 只股票列表")
        return df
    
    except Exception as e:
        logger.error(f"加载股票列表失败: {str(e)}")
        return None

def batch_process(data, batch_size=100):
    """
    批量处理数据
    
    参数:
        data: 要处理的数据
        batch_size: 批次大小
        
    返回:
        generator: 数据批次生成器
    """
    for i in range(0, len(data), batch_size):
        yield data.iloc[i:i+batch_size]

def calculate_execution_time(func):
    """
    计算函数执行时间的装饰器
    
    参数:
        func: 要装饰的函数
        
    返回:
        function: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.2f} 秒")
        return result
    return wrapper

def validate_factor_data(data, required_columns=['ts_code', 'trade_date']):
    """
    验证因子数据
    
    参数:
        data: 因子数据
        required_columns: 必需的列名列表
        
    返回:
        bool: 验证结果
    """
    if data is None:
        logger.error("因子数据为空")
        return False
    
    if not isinstance(data, pd.DataFrame):
        logger.error("因子数据必须是pandas.DataFrame类型")
        return False
    
    for column in required_columns:
        if column not in data.columns:
            logger.error(f"因子数据缺少必需的列: {column}")
            return False
    
    return True

def clean_factor_data(data, factor_name):
    """
    清洗因子数据
    
    参数:
        data: 因子数据
        factor_name: 因子名称
        
    返回:
        pandas.DataFrame: 清洗后的因子数据
    """
    if not validate_factor_data(data):
        return None
    
    # 移除重复数据
    df = data.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
    
    # 移除缺失值
    original_count = len(df)
    
    # 获取所有因子值列（以factor_name开头的列）
    factor_value_columns = [col for col in df.columns if col.startswith(factor_name)]
    
    if factor_value_columns:
        # 如果找到以factor_name开头的列，使用这些列来移除缺失值
        df = df.dropna(subset=factor_value_columns, how='all')  # 只移除所有因子列都缺失的行
    else:
        # 否则使用factor_name列
        try:
            df = df.dropna(subset=[factor_name])
        except KeyError:
            logger.error(f"因子数据中没有找到列: {factor_name}")
            return None
    
    cleaned_count = len(df)
    
    if original_count != cleaned_count:
        logger.info(f"因子 {factor_name} 移除了 {original_count - cleaned_count} 条缺失的因子数据")
    
    return df

def get_factor_table_name(factor_name):
    """
    获取因子表名
    
    参数:
        factor_name: 因子名称
        
    返回:
        str: 表名
    """
    return f"factor_{factor_name.lower().replace(' ', '_').replace('.', '_')}"

def create_factor_table(conn, factor_name, df):
    """
    创建因子表
    
    参数:
        conn: 数据库连接对象
        factor_name: 因子名称
        df: 因子数据
        
    返回:
        bool: 创建结果
    """
    try:
        table_name = get_factor_table_name(factor_name)
        
        # 创建表
        df.to_sql(table_name, conn, index=False, if_exists='replace')
        logger.info(f"成功创建因子表: {table_name}")
        
        # 添加主键约束
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ts_code' in columns and 'trade_date' in columns:
            cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_ts_code_trade_date ON {table_name}(ts_code, trade_date)")
            logger.info(f"成功添加主键约束到因子表: {table_name}")
        
        conn.commit()
        return True
    
    except Exception as e:
        logger.error(f"创建因子表失败: {str(e)}")
        conn.rollback()
        return False

def update_factor_table(conn, factor_name, df):
    """
    更新因子表
    
    参数:
        conn: 数据库连接对象
        factor_name: 因子名称
        df: 因子数据
        
    返回:
        bool: 更新结果
    """
    try:
        table_name = get_factor_table_name(factor_name)
        
        # 检查表是否存在
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 表存在，使用replace模式更新
            df.to_sql(table_name, conn, index=False, if_exists='replace')
        else:
            # 表不存在，创建表
            return create_factor_table(conn, factor_name, df)
        
        logger.info(f"成功更新因子表: {table_name}")
        return True
    
    except Exception as e:
        logger.error(f"更新因子表失败: {str(e)}")
        conn.rollback()
        return False

def get_all_factor_tables(conn):
    """
    获取所有因子表
    
    参数:
        conn: 数据库连接对象
        
    返回:
        list: 因子表名列表
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'factor_%'")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"找到 {len(tables)} 个因子表")
        return tables
    
    except Exception as e:
        logger.error(f"获取因子表失败: {str(e)}")
        return []