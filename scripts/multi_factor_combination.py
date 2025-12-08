#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多因子组合分析脚本

该脚本使用机器学习方法进行多因子组合优化，目标是获得最高平均收益率。
输出包括最优多因子权重比例和10组分组收益多空分析报告。
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置和工具
from config.config import FACTOR_ANALYSIS_CONFIG, PLOT_CONFIG, MULTI_FACTOR_COMBINATION_CONFIG
from config.logger_config import get_logger
from utils.file_manager import save_file
from factor_lib.utils import load_factor_data_by_date_range, load_stock_returns
from analyzer.factor_analyzer import FactorAnalyzer

# 获取日志记录器
logger = get_logger('multi_factor_combination')

class MultiFactorCombination:
    """
    多因子组合分析类
    """
    
    def __init__(self, factors_list, start_date, end_date, forward_period=10, group_num=10):
        """
        初始化多因子组合分析器
        
        参数:
            factors_list (list): 要使用的因子列表
            start_date (str): 开始日期，格式如"2015-01-01"
            end_date (str): 结束日期，格式如"2023-12-31"
            forward_period (int): 目标收益率周期，默认为10个交易日
            group_num (int): 分组数量，默认为10组
        """
        self.factors_list = factors_list
        self.start_date = start_date
        self.end_date = end_date
        self.forward_period = forward_period
        self.group_num = group_num
        self.optimal_weights = None
        self.factor_data = None
        self.return_data = None
        self.combined_factor = None
        self.group_returns = None
        
    def load_data(self):
        """
        加载因子数据和收益率数据
        
        返回:
            bool: 数据加载是否成功
        """
        logger.info(f"正在加载因子数据和收益率数据...")
        logger.info(f"因子列表: {', '.join(self.factors_list)}")
        logger.info(f"时间范围: {self.start_date} 至 {self.end_date}")
        
        try:
            # 加载所有因子数据
            factor_data_list = []
            for factor_name in self.factors_list:
                logger.info(f"加载因子: {factor_name}")
                factor_data = load_factor_data_by_date_range(factor_name, self.start_date, self.end_date)
                if factor_data.empty:
                    logger.warning(f"因子 {factor_name} 没有数据")
                    continue
                
                # 重命名因子列为因子名称
                factor_data = factor_data.rename(columns={'value': factor_name})
                factor_data_list.append(factor_data)
            
            # 合并所有因子数据
            if not factor_data_list:
                logger.error("没有加载到任何因子数据")
                return False
            
            self.factor_data = factor_data_list[0]
            for i in range(1, len(factor_data_list)):
                self.factor_data = pd.merge(self.factor_data, factor_data_list[i], 
                                          on=['code', 'date'], how='inner')
            
            logger.info(f"因子数据加载完成，共 {len(self.factor_data)} 条记录")
            
            # 加载收益率数据
            logger.info(f"加载收益率数据，周期: {self.forward_period} 天")
            self.return_data = load_stock_returns(self.start_date, self.end_date, self.forward_period)
            
            if self.return_data.empty:
                logger.error("没有加载到收益率数据")
                return False
            
            logger.info(f"收益率数据加载完成，共 {len(self.return_data)} 条记录")
            
            # 合并因子数据和收益率数据
            self.data = pd.merge(self.factor_data, self.return_data, on=['code', 'date'], how='inner')
            
            if self.data.empty:
                logger.error("因子数据和收益率数据没有重叠")
                return False
            
            logger.info(f"数据合并完成，共 {len(self.data)} 条有效记录")
            
            # 检查是否有缺失值
            missing_values = self.data.isnull().sum()
            if missing_values.sum() > 0:
                logger.warning(f"数据中存在缺失值: {missing_values.to_dict()}")
                # 删除包含缺失值的行
                self.data = self.data.dropna()
                logger.info(f"删除缺失值后，剩余 {len(self.data)} 条记录")
            
            return True
            
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            return False
    
    def train_model(self, model_type='gbdt', param_grid=None):
        """
        使用机器学习模型训练因子组合
        
        参数:
            model_type (str): 模型类型，可以是 'linear', 'rf', 'gbdt', 'mlp'
            param_grid (dict): 模型参数网格，用于网格搜索
            
        返回:
            object: 训练好的模型
        """
        logger.info(f"开始训练 {model_type} 模型...")
        
        # 准备特征和目标变量
        X = self.data[self.factors_list]
        y = self.data['return']
        
        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 时间序列交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        
        # 选择模型
        if model_type == 'linear':
            model = LinearRegression()
        elif model_type == 'rf':
            model = RandomForestRegressor(random_state=42)
        elif model_type == 'gbdt':
            model = GradientBoostingRegressor(random_state=42)
        elif model_type == 'mlp':
            model = MLPRegressor(random_state=42, max_iter=1000)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 网格搜索
        if param_grid:
            logger.info("使用网格搜索优化模型参数...")
            grid_search = GridSearchCV(model, param_grid, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
            grid_search.fit(X_scaled, y)
            model = grid_search.best_estimator_
            logger.info(f"最佳参数: {grid_search.best_params_}")
        else:
            model.fit(X_scaled, y)
        
        # 模型评估
        y_pred = model.predict(X_scaled)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        logger.info(f"模型评估结果:")
        logger.info(f"  均方误差 (MSE): {mse:.6f}")
        logger.info(f"  R² 得分: {r2:.6f}")
        
        # 获取特征重要性或权重
        if model_type == 'linear':
            # 线性回归的系数作为权重
            self.optimal_weights = dict(zip(self.factors_list, model.coef_))
        elif hasattr(model, 'feature_importances_'):
            # 基于特征重要性的权重
            importances = model.feature_importances_
            self.optimal_weights = dict(zip(self.factors_list, importances))
        else:
            # MLP等没有直接特征重要性的模型，使用默认权重
            self.optimal_weights = {factor: 1.0/len(self.factors_list) for factor in self.factors_list}
        
        # 归一化权重
        total_weight = sum(self.optimal_weights.values())
        self.optimal_weights = {k: v/total_weight for k, v in self.optimal_weights.items()}
        
        logger.info(f"因子最优权重: {json.dumps(self.optimal_weights, indent=2)}")
        
        return model
    
    def calculate_combined_factor(self):
        """
        根据最优权重计算组合因子
        """
        logger.info("计算组合因子...")
        
        if self.optimal_weights is None:
            logger.error("请先训练模型获取最优权重")
            return False
        
        # 计算加权因子和
        combined = 0
        for factor_name, weight in self.optimal_weights.items():
            combined += self.data[factor_name] * weight
        
        self.data['combined_factor'] = combined
        self.combined_factor = self.data[['code', 'date', 'combined_factor']].copy()
        
        logger.info("组合因子计算完成")
        return True
    
    def analyze_group_returns(self):
        """
        分析分组收益
        """
        logger.info(f"进行 {self.group_num} 组分组收益分析...")
        
        if 'combined_factor' not in self.data.columns:
            logger.error("请先计算组合因子")
            return False
        
        # 按日期分组，对每个日期的股票按组合因子值排序并分组
        group_returns_list = []
        
        for date, date_data in self.data.groupby('date'):
            if len(date_data) < self.group_num:
                continue
            
            # 按组合因子排序并分组
            date_data = date_data.sort_values('combined_factor')
            date_data['group'] = pd.qcut(date_data['combined_factor'], self.group_num, labels=False)
            
            # 计算每组的平均收益率
            group_ret = date_data.groupby('group')['return'].mean().reset_index()
            group_ret['date'] = date
            group_returns_list.append(group_ret)
        
        # 合并所有日期的分组收益
        self.group_returns = pd.concat(group_returns_list, ignore_index=True)
        
        logger.info("分组收益分析完成")
        return True
    
    def generate_report(self):
        """
        生成分析报告
        
        返回:
            dict: 包含分析结果的报告
        """
        logger.info("生成分析报告...")
        
        report = {
            'analysis_info': {
                'factors': self.factors_list,
                'time_range': f"{self.start_date} to {self.end_date}",
                'forward_period': self.forward_period,
                'group_num': self.group_num,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'optimal_weights': self.optimal_weights,
            'group_performance': {}
        }
        
        # 计算每组的统计指标
        if self.group_returns is not None:
            group_stats = []
            for group in range(self.group_num):
                group_data = self.group_returns[self.group_returns['group'] == group]
                avg_return = group_data['return'].mean()
                std_return = group_data['return'].std()
                sharpe_ratio = avg_return / std_return if std_return != 0 else 0
                win_rate = (group_data['return'] > 0).mean()
                
                group_stats.append({
                    'group': group + 1,  # 分组从1开始编号
                    'average_return': avg_return,
                    'std_return': std_return,
                    'sharpe_ratio': sharpe_ratio,
                    'win_rate': win_rate,
                    'total_days': len(group_data)
                })
            
            report['group_performance']['group_stats'] = group_stats
            
            # 计算多空收益（最高分组 - 最低分组）
            if len(group_stats) >= 2:
                long_group = group_stats[-1]
                short_group = group_stats[0]
                report['group_performance']['long_short'] = {
                    'long_group': long_group['group'],
                    'short_group': short_group['group'],
                    'average_return': long_group['average_return'] - short_group['average_return'],
                    'std_return': np.sqrt(long_group['std_return']**2 + short_group['std_return']**2),
                    'sharpe_ratio': (long_group['average_return'] - short_group['average_return']) / 
                                  np.sqrt(long_group['std_return']**2 + short_group['std_return']**2) 
                                  if np.sqrt(long_group['std_return']**2 + short_group['std_return']**2) != 0 else 0
                }
        
        logger.info("分析报告生成完成")
        return report
    
    def plot_results(self):
        """
        绘制分析结果图表
        
        返回:
            dict: 保存的图表文件路径
        """
        if not PLOT_CONFIG['ENABLE']:
            logger.info("绘图功能已禁用")
            return {}
        
        logger.info("绘制分析结果图表...")
        
        plots = {}
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 因子权重柱状图
        if self.optimal_weights:
            plt.figure(figsize=(10, 6))
            factors = list(self.optimal_weights.keys())
            weights = list(self.optimal_weights.values())
            plt.bar(factors, weights)
            plt.xlabel('因子')
            plt.ylabel('权重')
            plt.title('因子最优权重分布')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            weight_plot_path = save_file(plt, 'factor_report', 'factor_weights', with_datetime=True, format='png')
            plots['weights'] = weight_plot_path
            plt.close()
        
        # 2. 分组平均收益率图
        if self.group_returns is not None:
            plt.figure(figsize=(10, 6))
            group_avg_returns = self.group_returns.groupby('group')['return'].mean()
            groups = [f'组{i+1}' for i in range(self.group_num)]
            plt.bar(groups, group_avg_returns)
            plt.xlabel('分组')
            plt.ylabel('平均收益率')
            plt.title('各组平均收益率')
            plt.tight_layout()
            
            group_return_plot_path = save_file(plt, 'factor_report', 'group_returns', with_datetime=True, format='png')
            plots['group_returns'] = group_return_plot_path
            plt.close()
        
        # 3. 分组累积收益率图
        if self.group_returns is not None:
            plt.figure(figsize=(12, 8))
            
            # 按日期排序
            dates = sorted(self.group_returns['date'].unique())
            
            for group in range(self.group_num):
                group_data = self.group_returns[self.group_returns['group'] == group]
                # 确保按日期排序
                group_data = group_data.sort_values('date')
                # 计算累积收益率
                cumulative_returns = (1 + group_data['return']).cumprod() - 1
                plt.plot(group_data['date'], cumulative_returns, label=f'组{group+1}')
            
            plt.xlabel('日期')
            plt.ylabel('累积收益率')
            plt.title('各组累积收益率曲线')
            plt.legend()
            plt.tight_layout()
            
            cumulative_return_plot_path = save_file(plt, 'factor_report', 'cumulative_returns', with_datetime=True, format='png')
            plots['cumulative_returns'] = cumulative_return_plot_path
            plt.close()
        
        logger.info("图表绘制完成")
        return plots

def main():
    """
    主函数
    """
    logger.info("========== 多因子组合分析开始 ==========")
    
    # 从配置文件读取参数
    factors_list = MULTI_FACTOR_COMBINATION_CONFIG['FACTORS_LIST']
    start_date = MULTI_FACTOR_COMBINATION_CONFIG['START_DATE']
    end_date = MULTI_FACTOR_COMBINATION_CONFIG['END_DATE']
    forward_period = MULTI_FACTOR_COMBINATION_CONFIG['FORWARD_PERIOD']
    group_num = MULTI_FACTOR_COMBINATION_CONFIG['GROUP_NUM']
    model_type = MULTI_FACTOR_COMBINATION_CONFIG['MODEL_TYPE']
    
    # 可以根据需要在运行时覆盖配置
    # factors_list = ['factor1', 'factor2', 'factor3']  # 自定义因子列表
    # start_date = '2020-01-01'
    # end_date = '2023-12-31'
    # forward_period = 5
    
    # 初始化多因子组合分析器
    multi_factor = MultiFactorCombination(
        factors_list=factors_list,
        start_date=start_date,
        end_date=end_date,
        forward_period=forward_period,
        group_num=group_num
    )
    
    # 加载数据
    if not multi_factor.load_data():
        logger.error("数据加载失败，程序终止")
        return
    
    # 训练模型
    try:
        # 从配置文件读取模型参数网格
        param_grid = MULTI_FACTOR_COMBINATION_CONFIG['MODEL_PARAMS']
        
        model = multi_factor.train_model(model_type=model_type, param_grid=param_grid)
    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        return
    
    # 计算组合因子
    if not multi_factor.calculate_combined_factor():
        logger.error("组合因子计算失败，程序终止")
        return
    
    # 分析分组收益
    if not multi_factor.analyze_group_returns():
        logger.error("分组收益分析失败，程序终止")
        return
    
    # 生成报告
    report = multi_factor.generate_report()
    
    # 绘制图表
    plots = multi_factor.plot_results()
    
    # 保存报告
    logger.info("保存分析报告...")
    report_path = save_file(report, 'factor_report', 'multi_factor_analysis_report', with_datetime=True, format='json')
    logger.info(f"分析报告已保存至: {report_path}")
    
    # 保存最优权重
    weights_path = save_file(report['optimal_weights'], 'factor_report', 'optimal_factor_weights', with_datetime=True, format='json')
    logger.info(f"最优权重已保存至: {weights_path}")
    
    # 保存分组收益数据
    if multi_factor.group_returns is not None:
        group_returns_path = save_file(multi_factor.group_returns, 'factor_report', 'group_returns_data', with_datetime=True, format='csv')
        logger.info(f"分组收益数据已保存至: {group_returns_path}")
    
    # 打印结果摘要
    logger.info("\n========== 分析结果摘要 ==========")
    logger.info(f"使用的因子: {', '.join(factors_list)}")
    logger.info(f"时间范围: {start_date} 至 {end_date}")
    logger.info(f"预测周期: {forward_period} 天")
    logger.info(f"模型类型: {model_type}")
    logger.info(f"\n最优因子权重:")
    for factor, weight in report['optimal_weights'].items():
        logger.info(f"  {factor}: {weight:.4f}")
    
    logger.info(f"\n分组表现:")
    for group_stat in report['group_performance']['group_stats']:
        logger.info(f"  组{group_stat['group']}: 平均收益率 {group_stat['average_return']:.6f}, 夏普比率 {group_stat['sharpe_ratio']:.4f}, 胜率 {group_stat['win_rate']:.4f}")
    
    if 'long_short' in report['group_performance']:
        ls = report['group_performance']['long_short']
        logger.info(f"\n多空策略(组{ls['long_group']}-组{ls['short_group']}):")
        logger.info(f"  平均收益率: {ls['average_return']:.6f}")
        logger.info(f"  夏普比率: {ls['sharpe_ratio']:.4f}")
    
    logger.info(f"\n图表文件:")
    for plot_type, plot_path in plots.items():
        logger.info(f"  {plot_type}: {plot_path}")
    
    logger.info("\n========== 多因子组合分析结束 ==========")

if __name__ == '__main__':
    main()