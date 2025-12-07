#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因子分析器，用于计算因子的Rank IC和IR
"""

# ---------------------- 配置部分 ----------------------
# 测试范围: SZ50/HS300/ZZ500/ZZ1000/ZZ2000/INDIVIDUAL/ALL_A
TEST_SCOPE = 'HS300'

# 单个股票代码 (仅当TEST_SCOPE为INDIVIDUAL时需要)
INDIVIDUAL_STOCK = None

# 测试日期范围
START_DATE = "2015-01-01"  # 格式: YYYY-MM-DD
END_DATE = "2025-12-05"  # 格式: YYYY-MM-DD

# 目标收益率周期
FORWARD_PERIOD = 10

# 是否进行因子横截面标准化
NORMALIZE_FACTOR = True

# ---------------------------------------------------

import pandas as pd
import numpy as np
import os
import sys
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from datetime import datetime

# 设置pandas参数以抑制FutureWarning
pd.options.mode.chained_assignment = None  # 关闭链式赋值警告
pd.options.future.infer_string = True  # 启用字符串类型推断

# 设置matplotlib参数
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']  # 设置中文显示，添加多种字体备选
plt.rcParams['font.family'] = 'sans-serif'  # 使用无衬线字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.style.use('seaborn-v0_8-whitegrid')  # 设置绘图风格

# 测试matplotlib字体是否支持中文
try:
    import matplotlib.font_manager
    # 获取所有可用字体
    fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    # 检查是否有支持中文的字体
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    available_chinese_fonts = [f for f in chinese_fonts if f in fonts]
    if available_chinese_fonts:
        plt.rcParams['font.sans-serif'] = available_chinese_fonts + ['DejaVu Sans', 'Arial']
        # 使用print代替logger，因为logger还未初始化
        print(f"已设置matplotlib中文字体: {available_chinese_fonts}")
    else:
        print("未找到支持中文的字体，可能会导致中文显示异常")
except Exception as e:
    print(f"设置matplotlib字体时出错: {e}")

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具函数
from factor_lib.utils import get_database_connection, load_stock_data

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('factor_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FactorAnalyzer:
    """
    因子分析器类，用于计算因子的Rank IC和IR
    """
    
    def __init__(self, conn):
        """
        初始化因子分析器
        
        参数:
            conn: 数据库连接对象
        """
        self.conn = conn
        self.stock_data = None
        self.factor_data = None
        self.return_data = None
        self.test_scope = 'ALL_A'
        self.individual_stock = None
        
    def set_test_scope(self, test_scope, individual_stock=None):
        """
        设置测试范围
        
        参数:
            test_scope: 测试范围
            individual_stock: 单个股票代码（仅当test_scope为INDIVIDUAL时需要）
        """
        self.test_scope = test_scope
        if test_scope == 'INDIVIDUAL':
            if not individual_stock:
                raise ValueError("当test_scope为INDIVIDUAL时，必须指定individual_stock参数")
            self.individual_stock = individual_stock
        else:
            self.individual_stock = None
        
        logger.info(f"测试范围已设置为: {test_scope}")
        if test_scope == 'INDIVIDUAL':
            logger.info(f"  单个股票: {individual_stock}")
    
    def get_test_stocks(self):
        """
        获取测试范围内的股票列表
        
        返回:
            list: 股票代码列表
        """
        try:
            if self.test_scope == 'INDIVIDUAL':
                return [self.individual_stock]
            
            # 直接从daily_quotes表获取所有唯一股票代码
            # 目前数据库中没有指数成分股表，所以不管选择什么测试范围，都返回所有股票
            query = "SELECT DISTINCT ts_code FROM daily_quotes"
            df = pd.read_sql_query(query, self.conn)
            stocks_list = df['ts_code'].tolist()
            
            logger.info(f"获取到 {len(stocks_list)} 只股票")
            return stocks_list
        except Exception as e:
            logger.error(f"获取测试范围内股票列表失败: {str(e)}")
            logger.info("默认返回空列表")
            return []
        
    def load_factor_data(self, factor_name, start_date=None, end_date=None, normalize=True):
        """
        加载因子数据
        
        参数:
            factor_name: 因子名称
            start_date: 开始日期
            end_date: 结束日期
            normalize: 是否进行横截面标准化
        """
        try:
            query = f"SELECT ts_code, trade_date, factor_value FROM factors WHERE factor_name = '{factor_name}'"
            
            conditions = []
            if start_date:
                conditions.append(f"trade_date >= '{start_date}'")
            if end_date:
                conditions.append(f"trade_date <= '{end_date}'")
            
            # 添加测试范围过滤
            test_stocks = self.get_test_stocks()
            if test_stocks and len(test_stocks) > 0:
                if len(test_stocks) == 1:
                    conditions.append(f"ts_code = '{test_stocks[0]}'")
                else:
                    stocks_tuple = tuple(test_stocks)
                    conditions.append(f"ts_code IN {stocks_tuple}")
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            self.factor_data = pd.read_sql_query(query, self.conn)
            self.factor_data['trade_date'] = pd.to_datetime(self.factor_data['trade_date'])
            self.factor_data = self.factor_data.sort_values(['ts_code', 'trade_date'])
            
            # 单因子标准化（时间序列标准化）
            self.time_series_normalize()
            logger.info(f"因子 {factor_name} 数据已进行时间序列标准化")
            
            # 横截面标准化
            if normalize:
                self.cross_sectional_normalize()
                logger.info(f"因子 {factor_name} 数据已进行横截面标准化")
            
            logger.info(f"成功加载因子 {factor_name} 数据: {len(self.factor_data)} 条")
            return True
        except Exception as e:
            logger.error(f"加载因子数据失败: {str(e)}")
            return False
    
    def time_series_normalize(self):
        """
        对因子数据进行时间序列标准化（单因子标准化）
        对每个股票的因子值在时间序列上进行标准化
        """
        if self.factor_data is None:
            logger.error("因子数据未加载，无法进行时间序列标准化")
            return
        
        try:
            # 对每个股票进行时间序列标准化
            def normalize(group):
                mean = group['factor_value'].mean()
                std = group['factor_value'].std()
                if std > 0:
                    group['factor_value'] = (group['factor_value'] - mean) / std
                return group
            
            self.factor_data = self.factor_data.groupby('ts_code', group_keys=False).apply(normalize).reset_index(drop=True)
            logger.info("因子数据时间序列标准化完成")
        except Exception as e:
            logger.error(f"因子数据时间序列标准化失败: {str(e)}")
    
    def cross_sectional_normalize(self):
        """
        对因子数据进行横截面标准化
        """
        if self.factor_data is None:
            logger.error("因子数据未加载，无法进行标准化")
            return
        
        try:
            # 对每个交易日进行横截面标准化
            def normalize(group):
                mean = group['factor_value'].mean()
                std = group['factor_value'].std()
                if std > 0:
                    group['factor_value'] = (group['factor_value'] - mean) / std
                return group
            
            self.factor_data = self.factor_data.groupby('trade_date', group_keys=False).apply(normalize).reset_index(drop=True)
            logger.info("因子数据横截面标准化完成")
        except Exception as e:
            logger.error(f"因子数据标准化失败: {str(e)}")
    
    def load_return_data(self, start_date=None, end_date=None, forward_period=1):
        """
        加载收益率数据
        
        参数:
            start_date: 开始日期
            end_date: 结束日期
            forward_period: 向前预测的周期数
        """
        try:
            # 加载原始价格数据
            price_query = "SELECT ts_code, trade_date, close FROM daily_quotes"
            
            conditions = []
            if start_date:
                conditions.append(f"trade_date >= '{start_date}'")
            if end_date:
                conditions.append(f"trade_date <= '{end_date}'")
            
            # 添加测试范围过滤
            test_stocks = self.get_test_stocks()
            if test_stocks and len(test_stocks) > 0:
                if len(test_stocks) == 1:
                    conditions.append(f"ts_code = '{test_stocks[0]}'")
                else:
                    stocks_tuple = tuple(test_stocks)
                    conditions.append(f"ts_code IN {stocks_tuple}")
            
            if conditions:
                price_query += " WHERE " + " AND ".join(conditions)
            
            price_data = pd.read_sql_query(price_query, self.conn)
            price_data['trade_date'] = pd.to_datetime(price_data['trade_date'])
            price_data = price_data.sort_values(['ts_code', 'trade_date'])
            
            # 计算收益率
            price_data['next_close'] = price_data.groupby('ts_code')['close'].shift(-forward_period)
            price_data['return'] = (price_data['next_close'] - price_data['close']) / price_data['close']
            
            # 移除最后forward_period天的数据
            price_data = price_data.dropna(subset=['return'])
            
            self.return_data = price_data[['ts_code', 'trade_date', 'return']]
            logger.info(f"成功加载收益率数据: {len(self.return_data)} 条")
            return True
        except Exception as e:
            logger.error(f"加载收益率数据失败: {str(e)}")
            return False
    
    def calculate_rank_ic(self):
        """
        计算Rank IC
        
        返回:
            pandas.DataFrame: 每日Rank IC值
        """
        if self.factor_data is None:
            logger.error("因子数据未加载")
            return None
        
        if self.return_data is None:
            logger.error("收益率数据未加载")
            return None
        
        try:
            # 合并因子数据和收益率数据
            merged_data = pd.merge(
                self.factor_data,
                self.return_data,
                on=['ts_code', 'trade_date'],
                how='inner'
            )
            
            logger.info(f"合并后数据量: {len(merged_data)} 条")
            
            # 计算每日Rank IC
            def calc_daily_rank_ic(group):
                if len(group) < 2:
                    return pd.Series({'rank_ic': np.nan})
                
                # 计算秩相关系数
                rank_ic, p_value = spearmanr(group['factor_value'], group['return'])
                return pd.Series({'rank_ic': rank_ic, 'p_value': p_value})
            
            daily_rank_ic = merged_data.groupby('trade_date', group_keys=False).apply(calc_daily_rank_ic).reset_index()
            daily_rank_ic = daily_rank_ic.sort_values('trade_date')
            
            logger.info(f"Rank IC计算完成，共 {len(daily_rank_ic)} 个交易日")
            return daily_rank_ic
        except Exception as e:
            logger.error(f"计算Rank IC失败: {str(e)}")
            return None
    
    def calculate_ir(self, rank_ic_data):
        """
        计算IR (Information Ratio)
        
        参数:
            rank_ic_data: Rank IC数据
            
        返回:
            float: IR值
        """
        if rank_ic_data is None or 'rank_ic' not in rank_ic_data.columns:
            logger.error("无效的Rank IC数据")
            return None
        
        try:
            # 移除NaN值
            valid_rank_ic = rank_ic_data['rank_ic'].dropna()
            
            if len(valid_rank_ic) == 0:
                logger.error("没有有效的Rank IC数据")
                return None
            
            # 计算IR
            mean_rank_ic = valid_rank_ic.mean()
            std_rank_ic = valid_rank_ic.std()
            
            if std_rank_ic == 0:
                logger.error("Rank IC的标准差为0，无法计算IR")
                return None
            
            ir = mean_rank_ic / std_rank_ic
            logger.info(f"IR计算完成: 均值={mean_rank_ic:.4f}, 标准差={std_rank_ic:.4f}, IR={ir:.4f}")
            return ir
        except Exception as e:
            logger.error(f"计算IR失败: {str(e)}")
            return None
    
    def analyze_factor(self, factor_name, forward_period=1, start_date=None, end_date=None):
        """
        完整分析一个因子
        
        参数:
            factor_name: 因子名称
            forward_period: 向前预测的周期数
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            dict: 分析结果
        """
        try:
            logger.info(f"开始分析因子: {factor_name}")
            
            # 加载因子数据
            if not self.load_factor_data(factor_name, start_date, end_date, normalize=NORMALIZE_FACTOR):
                return None
            
            # 加载收益率数据 - 调整结束日期以确保有足够数据计算远期收益
            # 收益率计算需要forward_period天的后续数据，所以结束日期应后移
            return_end_date = None
            if end_date:
                # 将结束日期转换为datetime并添加forward_period天
                end_date_dt = pd.to_datetime(end_date)
                return_end_date = (end_date_dt + pd.Timedelta(days=forward_period)).strftime('%Y-%m-%d')
            
            if not self.load_return_data(start_date, return_end_date, forward_period):
                return None
            
            # 计算Rank IC
            rank_ic_data = self.calculate_rank_ic()
            if rank_ic_data is None:
                return None
            
            # 计算IR
            ir = self.calculate_ir(rank_ic_data)
            
            # 计算统计指标
            valid_rank_ic = rank_ic_data['rank_ic'].dropna()
            mean_rank_ic = valid_rank_ic.mean()
            std_rank_ic = valid_rank_ic.std()
            positive_days = len(valid_rank_ic[valid_rank_ic > 0])
            total_days = len(valid_rank_ic)
            positive_ratio = positive_days / total_days if total_days > 0 else 0
            
            result = {
                'factor_name': factor_name,
                'forward_period': forward_period,
                'mean_rank_ic': mean_rank_ic,
                'std_rank_ic': std_rank_ic,
                'ir': ir,
                'positive_ratio': positive_ratio,
                'total_days': total_days,
                'positive_days': positive_days,
                'rank_ic_data': rank_ic_data
            }
            
            logger.info(f"因子 {factor_name} 分析完成:")
            logger.info(f"  平均Rank IC: {mean_rank_ic:.4f}")
            logger.info(f"  Rank IC标准差: {std_rank_ic:.4f}")
            logger.info(f"  IR: {ir:.4f}")
            logger.info(f"  正相关天数比例: {positive_ratio:.2%}")
            logger.info(f"  有效交易天数: {total_days}")
            
            return result
        except Exception as e:
            logger.error(f"因子分析失败: {str(e)}")
            return None
    
    def plot_ic_time_series(self, factor_name, rank_ic_data, save_path=None):
        """
        绘制并保存因子的IC时间序列图
        
        参数:
            factor_name: 因子名称
            rank_ic_data: Rank IC数据
            save_path: 保存路径
        """
        try:
            if rank_ic_data is None or 'rank_ic' not in rank_ic_data.columns:
                logger.error("无效的Rank IC数据")
                return False
            
            # 确保目录存在
            if not os.path.exists('report/figures'):
                os.makedirs('report/figures')
            
            # 绘制IC时间序列图
            plt.figure(figsize=(15, 8))
            plt.plot(rank_ic_data['trade_date'], rank_ic_data['rank_ic'], 
                     color='#1f77b4', alpha=0.8, linewidth=2, label='Rank IC')
            
            # 添加均值线
            mean_ic = rank_ic_data['rank_ic'].mean()
            plt.axhline(y=mean_ic, color='#ff7f0e', linestyle='--', linewidth=2, 
                       label=f'平均Rank IC: {mean_ic:.4f}')
            
            # 添加零线
            plt.axhline(y=0, color='#2ca02c', linestyle='-', linewidth=1)
            
            # 设置图表标题和标签
            plt.title(f'{factor_name} 因子 Rank IC 时间序列', fontsize=16)
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('Rank IC 值', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=12)
            
            # 旋转x轴标签
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # 保存图片
            if not save_path:
                save_path = f'report/figures/{factor_name}_ic_time_series_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"因子 {factor_name} 的IC时间序列图已保存至: {save_path}")
            return True
        except Exception as e:
            logger.error(f"绘制IC时间序列图失败: {str(e)}")
            return False
    
    def analyze_group_returns(self, factor_name, num_groups=5, forward_period=10, start_date=None, end_date=None):
        """
        分组收益分析：将资产按因子值分组，计算每组的平均收益率
        
        参数:
            factor_name: 因子名称
            num_groups: 分组数量
            forward_period: 向前预测周期
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            dict: 分组收益分析结果
        """
        try:
            logger.info(f"开始对因子 {factor_name} 进行分组收益分析...")
            
            # 加载因子数据
            if not self.load_factor_data(factor_name, start_date, end_date, normalize=NORMALIZE_FACTOR):
                return None
            
            # 加载收益率数据
            return_end_date = None
            if end_date:
                end_date_dt = pd.to_datetime(end_date)
                return_end_date = (end_date_dt + pd.Timedelta(days=forward_period)).strftime('%Y-%m-%d')
            
            if not self.load_return_data(start_date, return_end_date, forward_period):
                return None
            
            # 合并因子数据和收益率数据
            merged_data = pd.merge(
                self.factor_data,
                self.return_data,
                on=['ts_code', 'trade_date'],
                how='inner'
            )
            
            if merged_data.empty:
                logger.error("合并后的因子和收益率数据为空")
                return None
            
            logger.info(f"分组分析合并后数据量: {len(merged_data)} 条")
            
            # 按因子值分组并计算每组的平均收益率
            def group_and_calc_return(daily_data):
                # 获取当前交易日
                trade_date = daily_data['trade_date'].iloc[0] if not daily_data.empty else None
                
                # 按因子值排序并分组
                daily_data = daily_data.sort_values('factor_value')
                
                # 确保有足够的数据进行分组
                if len(daily_data) < num_groups:
                    return pd.DataFrame(columns=['trade_date', 'group', 'return'])
                
                # 使用pandas的rank和cut函数进行分组
                daily_data['factor_rank'] = daily_data['factor_value'].rank(method='first')
                daily_data['group'] = pd.cut(daily_data['factor_rank'], bins=num_groups, labels=False) + 1
                
                # 计算每组的平均收益率
                group_returns = daily_data.groupby('group')['return'].mean().reset_index()
                
                # 添加trade_date列
                group_returns['trade_date'] = trade_date
                
                return group_returns
            
            # 按日期分组计算每日的分组收益率
            daily_group_returns = merged_data.groupby('trade_date', group_keys=False).apply(group_and_calc_return)
            
            # 确保结果是DataFrame格式
            if isinstance(daily_group_returns, pd.Series):
                daily_group_returns = daily_group_returns.to_frame()
            
            # 重置索引（如果需要）
            if daily_group_returns.index.nlevels > 1:
                daily_group_returns = daily_group_returns.reset_index(drop=True)
            
            # 确保有trade_date列
            if 'trade_date' not in daily_group_returns.columns and not daily_group_returns.empty:
                # 尝试从索引中获取trade_date
                if hasattr(daily_group_returns.index, 'get_level_values') and 'trade_date' in daily_group_returns.index.names:
                    daily_group_returns['trade_date'] = daily_group_returns.index.get_level_values('trade_date')
                    daily_group_returns = daily_group_returns.reset_index(drop=True)
            
            # 确保有数据进行后续处理
            if daily_group_returns.empty:
                logger.error("分组收益率数据为空")
                return None
            
            # 检查列名
            logger.debug(f"daily_group_returns columns: {daily_group_returns.columns.tolist()}")
            
            # 计算各组的平均收益率
            avg_group_returns = daily_group_returns.groupby('group')['return'].mean() * 100  # 转换为百分比
            
            logger.info(f"分组收益分析完成，共 {len(daily_group_returns['trade_date'].unique())} 个交易日")
            # 使用group_num作为循环变量名，避免与pandas内部变量冲突
            for group_num in range(1, num_groups + 1):
                if group_num in avg_group_returns.index:
                    logger.info(f"  第 {group_num} 组平均收益率: {avg_group_returns[group_num]:.4f}%")
            
            # 绘制分组收益单调性图表
            self.plot_group_returns(factor_name, avg_group_returns, num_groups)
            
            return {
                'factor_name': factor_name,
                'num_groups': num_groups,
                'forward_period': forward_period,
                'avg_group_returns': avg_group_returns.to_dict(),
                'daily_group_returns': daily_group_returns,
                'total_days': len(daily_group_returns['trade_date'].unique())
            }
        except Exception as e:
            logger.error(f"分组收益分析失败: {str(e)}")
            import traceback
            logger.error(f"异常堆栈信息: {traceback.format_exc()}")
            return None
    
    def plot_group_returns(self, factor_name, avg_group_returns, num_groups):
        """
        绘制分组收益单调性图表
        
        参数:
            factor_name: 因子名称
            avg_group_returns: 各组平均收益率
            num_groups: 分组数量
        """
        try:
            # 确保目录存在
            if not os.path.exists('report/figures'):
                os.makedirs('report/figures')
            
            plt.figure(figsize=(12, 8))
            
            # 获取分组和对应的收益率
            groups = list(avg_group_returns.index)
            returns = list(avg_group_returns.values)
            
            # 绘制柱状图
            bars = plt.bar(groups, returns, color='#1f77b4', alpha=0.8, edgecolor='black', linewidth=1)
            
            # 在柱状图上添加数值标签
            for bar, value in zip(bars, returns):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height, 
                        f'{value:.4f}%', ha='center', va='bottom', fontsize=10)
            
            # 绘制折线图（显示单调性）
            plt.plot(groups, returns, color='#ff7f0e', marker='o', linewidth=3, markersize=8)
            
            # 设置图表标题和标签
            plt.title(f'{factor_name} 因子分组收益分析 (Top{int(num_groups/2)} - Bottom{int(num_groups/2)} = {returns[-1] - returns[0]:.4f}%)', 
                      fontsize=16)
            plt.xlabel('因子分组 (1=最低因子值, {}=最高因子值)'.format(num_groups), fontsize=12)
            plt.ylabel('平均收益率 (%)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # 设置x轴刻度
            plt.xticks(groups)
            
            plt.tight_layout()
            
            # 保存图片
            save_path = f'report/figures/{factor_name}_group_returns_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"因子 {factor_name} 的分组收益图已保存至: {save_path}")
            return True
        except Exception as e:
            logger.error(f"绘制分组收益图失败: {str(e)}")
            return False
    
    def analyze_factor_correlation(self, factor_names, start_date=None, end_date=None):
        """
        因子间相关性分析：计算因子之间的相关系数矩阵
        
        参数:
            factor_names: 要分析的因子名称列表
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            dict: 因子相关性分析结果
        """
        try:
            logger.info("开始进行因子间相关性分析...")
            
            # 加载所有因子数据
            factor_data_dict = {}
            for factor_name in factor_names:
                if not self.load_factor_data(factor_name, start_date, end_date, normalize=NORMALIZE_FACTOR):
                    logger.warning(f"无法加载因子 {factor_name} 的数据，跳过该因子")
                    continue
                
                # 保留需要的列
                factor_data = self.factor_data[['ts_code', 'trade_date', 'factor_value']].copy()
                factor_data_dict[factor_name] = factor_data
            
            if not factor_data_dict:
                logger.error("没有成功加载任何因子数据")
                return None
            
            logger.info(f"成功加载 {len(factor_data_dict)} 个因子的数据")
            
            # 合并所有因子数据
            merged_factor_data = None
            for factor_name, factor_data in factor_data_dict.items():
                if merged_factor_data is None:
                    merged_factor_data = factor_data
                    merged_factor_data = merged_factor_data.rename(columns={'factor_value': factor_name})
                else:
                    merged_factor_data = pd.merge(
                        merged_factor_data,
                        factor_data,
                        on=['ts_code', 'trade_date'],
                        how='inner'
                    )
                    merged_factor_data = merged_factor_data.rename(columns={'factor_value': factor_name})
            
            if merged_factor_data.empty:
                logger.error("合并后的因子数据为空")
                return None
            
            logger.info(f"因子相关性分析合并后数据量: {len(merged_factor_data)} 条")
            
            # 计算因子间的相关系数矩阵
            # 选择所有因子列（排除ts_code和trade_date）
            factor_columns = [col for col in merged_factor_data.columns if col not in ['ts_code', 'trade_date']]
            
            if len(factor_columns) < 2:
                logger.error("因子数量不足，无法计算相关系数")
                return None
            
            # 计算相关系数矩阵
            correlation_matrix = merged_factor_data[factor_columns].corr(method='pearson')
            logger.info(f"因子间相关系数矩阵计算完成")
            
            # 绘制相关系数热力图
            self.plot_factor_correlation(correlation_matrix)
            
            return {
                'factor_names': factor_columns,
                'correlation_matrix': correlation_matrix.to_dict(),
                'total_observations': len(merged_factor_data)
            }
        except Exception as e:
            logger.error(f"因子间相关性分析失败: {str(e)}")
            return None
    
    def plot_factor_correlation(self, correlation_matrix):
        """
        绘制因子间相关系数热力图
        
        参数:
            correlation_matrix: 相关系数矩阵
        """
        try:
            # 确保目录存在
            if not os.path.exists('report/figures'):
                os.makedirs('report/figures')
            
            plt.figure(figsize=(15, 12))
            
            # 绘制热力图
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # 遮盖上三角
            sns.heatmap(
                correlation_matrix,
                mask=mask,
                annot=True,
                cmap='coolwarm',
                center=0,
                fmt='.4f',
                linewidths=0.5,
                square=True,
                cbar_kws={'shrink': 0.8},
                annot_kws={'size': 8}  # 调整标注文字大小
            )
            
            # 调整坐标轴刻度字体大小
            plt.tick_params(axis='both', labelsize=8)
            
            # 设置图表标题和标签
            plt.title('因子间相关系数矩阵', fontsize=16)
            plt.tight_layout()
            
            # 保存图片
            save_path = f'report/figures/factor_correlation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"因子间相关系数热力图已保存至: {save_path}")
            return True
        except Exception as e:
            logger.error(f"绘制因子相关系数热力图失败: {str(e)}")
            return False


def get_all_available_factors(conn):
    """
    获取所有可用的因子名称
    
    参数:
        conn: 数据库连接对象
        
    返回:
        list: 因子名称列表
    """
    try:
        query = "SELECT DISTINCT factor_name FROM factors"
        df = pd.read_sql_query(query, conn)
        return df['factor_name'].tolist()
    except Exception as e:
        logger.error(f"获取因子列表失败: {str(e)}")
        return []


def main():
    """
    主函数
    """
    # 显示当前配置
    logger.info(f"当前测试配置:")
    logger.info(f"  测试范围: {TEST_SCOPE}")
    if TEST_SCOPE == 'INDIVIDUAL' and INDIVIDUAL_STOCK:
        logger.info(f"  股票代码: {INDIVIDUAL_STOCK}")
    if START_DATE:
        logger.info(f"  开始日期: {START_DATE}")
    if END_DATE:
        logger.info(f"  结束日期: {END_DATE}")
    logger.info(f"  目标收益率周期: {FORWARD_PERIOD}")
    logger.info(f"  因子标准化: {NORMALIZE_FACTOR}")
    
    # 获取数据库连接
    conn = get_database_connection()
    if conn is None:
        logger.error("无法连接数据库，程序退出")
        return
    
    try:
        # 创建因子分析器
        analyzer = FactorAnalyzer(conn)
        
        # 设置测试范围
        analyzer.set_test_scope(TEST_SCOPE, INDIVIDUAL_STOCK)
        
        # 获取所有可用因子
        factors = get_all_available_factors(conn)
        logger.info(f"可用因子列表: {factors}")
        
        # 分析所有因子
        results = []
        for factor in factors:
            logger.info(f"开始分析因子: {factor}")
            result = analyzer.analyze_factor(factor, forward_period=FORWARD_PERIOD, 
                                           start_date=START_DATE, 
                                           end_date=END_DATE)
            if result:
                # 绘制IC时间序列图
                analyzer.plot_ic_time_series(factor, result['rank_ic_data'])
                
                # 分组收益分析
                analyzer.analyze_group_returns(factor, forward_period=FORWARD_PERIOD, start_date=START_DATE, end_date=END_DATE)
                
                results.append(result)
                logger.info(f"因子 {factor} 分析完成")
            else:
                logger.warning(f"因子 {factor} 分析失败，跳过该因子")
        
        # 因子间相关性分析
        if results:
            logger.info("开始进行因子间相关性分析...")
            analyzer.analyze_factor_correlation(factors, start_date=START_DATE, end_date=END_DATE)
        
        # 打印分析结果汇总 - 按IC绝对值排序
        if results:
            # 按平均Rank IC的绝对值排序
            results_sorted = sorted(results, key=lambda x: abs(x['mean_rank_ic']), reverse=True)
            
            logger.info("\n因子分析结果汇总 (按IC绝对值排序):")
            logger.info("-" * 90)
            logger.info(f"{'因子名称':<25} {'平均Rank IC':<15} {'IC绝对值':<10} {'IR':<10} {'正相关比例':<15} {'有效天数':<10}")
            logger.info("-" * 90)
            
            for result in results_sorted:
                ic_abs = abs(result['mean_rank_ic'])
                logger.info(f"{result['factor_name']:<25} {result['mean_rank_ic']:<15.4f} {ic_abs:<10.4f} {result['ir']:<10.4f} {result['positive_ratio']:<15.2%} {result['total_days']:<10}")
            
            logger.info("-" * 90)
            
            # 生成分析报告
            import json
            from datetime import datetime
            
            # 准备报告数据
            report_data = {
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'test_config': {
                    'test_scope': TEST_SCOPE,
                    'start_date': START_DATE,
                    'end_date': END_DATE,
                    'forward_period': FORWARD_PERIOD,
                    'normalize_factor': NORMALIZE_FACTOR
                },
                'factors': []
            }
            
            for result in results:
                # 转换rank_ic_data为列表以便JSON序列化
                rank_ic_df = result['rank_ic_data'].copy()
                
                # 将所有Timestamp类型的列转换为字符串
                for col in rank_ic_df.columns:
                    if pd.api.types.is_datetime64_any_dtype(rank_ic_df[col]):
                        rank_ic_df[col] = rank_ic_df[col].dt.strftime('%Y-%m-%d')
                
                rank_ic_data_list = rank_ic_df.to_dict('records')
                
                factor_report = {
                    'factor_name': result['factor_name'],
                    'mean_rank_ic': result['mean_rank_ic'],
                    'std_rank_ic': result['std_rank_ic'],
                    'ir': result['ir'],
                    'positive_ratio': result['positive_ratio'],
                    'total_days': result['total_days'],
                    'positive_days': result['positive_days'],
                    'rank_ic_data': rank_ic_data_list
                }
                report_data['factors'].append(factor_report)
            
            # 保存报告到JSON文件
            report_filename = f"factor_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = f"report/{report_filename}"
            
            # 确保report目录存在
            import os
            if not os.path.exists('report'):
                os.makedirs('report')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析报告已保存到: {report_path}")
            
            # 保存分析结果到CSV文件（方便查看）
            import pandas as pd
            
            # 准备CSV数据
            csv_data = []
            for result in results:
                csv_data.append({
                    '因子名称': result['factor_name'],
                    '平均Rank IC': result['mean_rank_ic'],
                    'Rank IC标准差': result['std_rank_ic'],
                    'IR': result['ir'],
                    '正相关比例': result['positive_ratio'],
                    '有效天数': result['total_days'],
                    '正相关天数': result['positive_days']
                })
            
            df_csv = pd.DataFrame(csv_data)
            csv_filename = f"factor_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = f"report/{csv_filename}"
            
            df_csv.to_csv(csv_path, index=False, encoding='utf-8-sig')
            logger.info(f"分析结果CSV已保存到: {csv_path}")
            
            # 生成详细的txt报告
            txt_filename = f"factor_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            txt_path = f"report/{txt_filename}"
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("因子分析详细报告\n")
                f.write("=" * 100 + "\n")
                f.write(f"分析时间范围: {START_DATE} 至 {END_DATE}\n")
                test_stocks = analyzer.get_test_stocks()
                f.write(f"测试股票数量: {len(test_stocks)}\n")
                f.write(f"分析因子数量: {len(results)}\n")
                f.write("=" * 100 + "\n\n")
                
                # 按IC绝对值排序后写入详细结果
                results_sorted = sorted(results, key=lambda x: abs(x['mean_rank_ic']), reverse=True)
                
                f.write("因子分析结果汇总 (按IC绝对值排序):\n")
                f.write("-" * 90 + "\n")
                f.write(f"{'因子名称':<25} {'平均Rank IC':<15} {'IC绝对值':<10} {'IR':<10} {'正相关比例':<15} {'有效天数':<10}\n")
                f.write("-" * 90 + "\n")
                
                for result in results_sorted:
                    ic_abs = abs(result['mean_rank_ic'])
                    f.write(f"{result['factor_name']:<25} {result['mean_rank_ic']:<15.4f} {ic_abs:<10.4f} {result['ir']:<10.4f} {result['positive_ratio']:<15.2%} {result['total_days']:<10}\n")
                
                f.write("-" * 90 + "\n\n")
                
                # 写入每个因子的详细信息
                f.write("各因子详细信息:\n")
                f.write("=" * 100 + "\n\n")
                
                for result in results_sorted:
                    f.write(f"因子名称: {result['factor_name']}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"平均Rank IC: {result['mean_rank_ic']:.6f}\n")
                    f.write(f"IC绝对值: {abs(result['mean_rank_ic']):.6f}\n")
                    f.write(f"信息比率(IR): {result['ir']:.6f}\n")
                    f.write(f"正相关比例: {result['positive_ratio']:.2%}\n")
                    f.write(f"负相关比例: {(1 - result['positive_ratio']):.2%}\n")
                    f.write(f"有效天数: {result['total_days']}\n")
                    f.write(f"总分析天数: {result['total_days']}\n")
                    f.write(f"IC标准差: {result['std_rank_ic']:.6f}\n")
                    
                    # 提取Rank IC值列表
                    rank_ics = result['rank_ic_data']['rank_ic'].dropna().tolist()
                    if rank_ics:
                        f.write(f"Rank IC最大值: {max(rank_ics):.6f}\n")
                        f.write(f"Rank IC最小值: {min(rank_ics):.6f}\n")
                        f.write(f"Rank IC中位数: {np.median(rank_ics):.6f}\n")
                        f.write(f"Rank IC上四分位数: {np.percentile(rank_ics, 75):.6f}\n")
                        f.write(f"Rank IC下四分位数: {np.percentile(rank_ics, 25):.6f}\n")
                    
                    f.write("\n")
                
                f.write("=" * 100 + "\n")
                f.write("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                f.write("=" * 100 + "\n")
            
            logger.info(f"详细txt报告已保存到: {txt_path}")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
    finally:
        # 关闭数据库连接
        conn.close()


if __name__ == "__main__":
    main()