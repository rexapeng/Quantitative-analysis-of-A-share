#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用tushare获取A股后复权日线行情数据
"""

import tushare as ts
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 添加项目根目录到sys.path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入配置
try:
    from config.config import DATA_DIRS, get_full_path
    from config.logger_config import data_logger
    
    # 使用统一的目录配置
    RAW_DATA_DIR = get_full_path(DATA_DIRS['RAW'])
    CLEANED_DATA_DIR = get_full_path(DATA_DIRS['PROCESSED'])
except ImportError as e:
    print(f"导入配置失败: {e}")
    # 如果无法导入配置，则使用默认值
    RAW_DATA_DIR = os.path.join(current_dir, 'raw')
    CLEANED_DATA_DIR = os.path.join(current_dir, 'processed')
    # 创建简单的logger
    import logging
    logging.basicConfig(level=logging.INFO)
    data_logger = logging.getLogger("data_fetcher")

def init_tushare_api(use_demo=False):
    """
    初始化tushare API
    注意：需要先在tushare官网注册账号并获取token
    """
    if use_demo:
        data_logger.info("使用演示模式，生成模拟数据")
        return "DEMO"
    
    # 这里需要设置你的tushare token
    # 请访问 https://tushare.pro/register?reg=123273 注册获取token
    token = "YOUR_TUSHARE_TOKEN_HERE"  # 请替换为你的实际token
    
    if token == "YOUR_TUSHARE_TOKEN_HERE":
        data_logger.warning("请设置你的tushare token，否则无法获取真实数据")
        data_logger.info("请访问 https://tushare.pro/register?reg=123273 注册获取token")
        data_logger.info("将使用演示模式生成模拟数据")
        return "DEMO"
        
    ts.set_token(token)
    pro = ts.pro_api()
    return pro

def get_stock_list(pro):
    """
    获取A股股票列表
    
    Args:
        pro: tushare pro api对象
        
    Returns:
        list: 股票代码列表
    """
    try:
        # 获取股票列表
        stock_info = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        stock_list = stock_info['ts_code'].tolist()
        data_logger.info(f"获取到 {len(stock_list)} 只A股股票")
        return stock_list
    except Exception as e:
        data_logger.error(f"获取股票列表失败: {e}")
        return []

def fetch_daily_data(pro, ts_code, adj='hfq'):
    """
    获取单只股票的日线数据（后复权）
    
    Args:
        pro: tushare pro api对象
        ts_code (str): 股票代码
        adj (str): 复权类型，'hfq'-后复权，'qfq'-前复权，None-不复权
        
    Returns:
        pd.DataFrame: 股票日线数据
    """
    try:
        # 获取日线数据
        if adj:
            # 获取复权因子
            df = ts.pro_bar(ts_code=ts_code, adj=adj, freq='D')
        else:
            df = ts.pro_bar(ts_code=ts_code, freq='D')
            
        if df is not None and not df.empty:
            # 重命名列以匹配项目标准
            df.rename(columns={
                'trade_date': 'date',
                'vol': 'volume'
            }, inplace=True)
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df.sort_values('date', inplace=True)
            df.reset_index(drop=True, inplace=True)
            
            data_logger.debug(f"获取 {ts_code} 数据成功，共 {len(df)} 条记录")
            return df
        else:
            data_logger.warning(f"{ts_code} 无数据")
            return pd.DataFrame()
            
    except Exception as e:
        data_logger.error(f"获取 {ts_code} 数据失败: {e}")
        return pd.DataFrame()

def save_raw_data(df, ts_code, save_dir=RAW_DATA_DIR):
    """
    保存原始数据到CSV文件
    
    Args:
        df (pd.DataFrame): 数据
        ts_code (str): 股票代码
        save_dir (str): 保存目录
    """
    try:
        if not df.empty:
            # 确保保存目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 构造文件名
            filename = f"{ts_code}_raw.csv"
            filepath = os.path.join(save_dir, filename)
            
            # 保存数据
            df.to_csv(filepath, index=False, encoding='utf-8')
            data_logger.info(f"保存 {ts_code} 原始数据到 {filepath}")
        else:
            data_logger.warning(f"{ts_code} 数据为空，未保存")
    except Exception as e:
        data_logger.error(f"保存 {ts_code} 原始数据失败: {e}")

def fetch_all_stocks_data(max_stocks=None):
    """
    获取所有A股的后复权日线数据
    
    Args:
        max_stocks (int): 最大获取股票数量，用于测试，默认None表示获取所有
    """
    # 初始化tushare
    pro = init_tushare_api()
    if pro is None:
        data_logger.error("tushare初始化失败，请检查token设置")
        return
    
    # 获取股票列表
    stock_list = get_stock_list(pro)
    if not stock_list:
        data_logger.error("未能获取股票列表")
        return
    
    # 如果设置了最大股票数量，则只获取前max_stocks只股票
    if max_stocks:
        stock_list = stock_list[:max_stocks]
        data_logger.info(f"限制获取前 {max_stocks} 只股票数据用于测试")
    
    data_logger.info(f"开始获取 {len(stock_list)} 只股票的后复权日线数据...")
    
    success_count = 0
    fail_count = 0
    
    # 遍历股票列表获取数据
    for i, ts_code in enumerate(stock_list):
        try:
            data_logger.info(f"[{i+1}/{len(stock_list)}] 正在获取 {ts_code} 数据...")
            
            # 获取后复权日线数据
            df = fetch_daily_data(pro, ts_code, adj='hfq')
            
            if not df.empty:
                # 保存原始数据
                save_raw_data(df, ts_code, RAW_DATA_DIR)
                success_count += 1
            else:
                fail_count += 1
                
            # 控制请求频率，避免被限制
            time.sleep(0.1)
            
        except Exception as e:
            data_logger.error(f"处理 {ts_code} 时出错: {e}")
            fail_count += 1
            continue
    
    data_logger.info(f"数据获取完成！成功: {success_count} 只，失败: {fail_count} 只")

def main():
    """
    主函数
    """
    data_logger.info("开始获取A股后复权日线行情数据...")
    
    # 获取所有股票数据（这里限制为5只用于演示）
    # 在实际使用中，可以移除max_stocks参数以获取所有股票数据
    fetch_all_stocks_data(max_stocks=5)
    
    data_logger.info("数据获取任务完成")

if __name__ == "__main__":
    main()