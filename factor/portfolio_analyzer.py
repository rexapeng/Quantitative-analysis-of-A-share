import pandas as pd
import numpy as np
from typing import Dict, List
from config.logger_config import data_logger

class PortfolioAnalyzer:
    """
    组合分析器，用于分析基于因子的投资组合表现
    """
    
    def __init__(self):
        self.logger = data_logger
        self.portfolio_metrics = {}
        
    def construct_factor_portfolio(self, df: pd.DataFrame, factor: str, 
                                 n_quantiles: int = 5) -> pd.DataFrame:
        """
        根据因子值构建投资组合
        
        Parameters:
        df: 包含因子的数据
        factor: 因子名称
        n_quantiles: 分组数量
        
        Returns:
        包含组合标签的数据
        """
        if factor not in df.columns:
            raise ValueError(f"因子 {factor} 不存在")
            
        portfolio_df = df.copy()
        
        # 去除因子为空的行
        self.logger.info(f"开始构建因子组合，因子: {factor}")
        portfolio_df = portfolio_df.dropna(subset=[factor])
        self.logger.info(f"去除空值后，剩余{len(portfolio_df)}条数据")
        
        # 按因子值分组
        self.logger.info(f"开始将数据分为{n_quantiles}个组合")
        portfolio_df['portfolio'] = pd.qcut(
            portfolio_df[factor], 
            q=n_quantiles, 
            labels=[f'Q{i+1}' for i in range(n_quantiles)],
            duplicates='drop'
        )
        
        self.logger.info(f"根据因子{factor}将股票分为{n_quantiles}个组合")
        return portfolio_df
    
    def calculate_portfolio_returns(self, df: pd.DataFrame, 
                                  portfolio_col: str = 'portfolio',
                                  return_col: str = 'ten_day_return') -> pd.DataFrame:
        """
        计算各组合的收益率
        
        Parameters:
        df: 包含组合标签和收益率的数据
        portfolio_col: 组合列名
        return_col: 收益率列名
        
        Returns:
        各组合收益率统计
        """
        # 使用observed=True参数解决FutureWarning警告
        portfolio_returns = df.groupby(portfolio_col, observed=True)[return_col].agg([
            'mean', 'std', 'count'
        ]).rename(columns={'mean': 'avg_return', 'std': 'volatility'})
        
        # 计算夏普比率（假设无风险利率为0）
        portfolio_returns['sharpe'] = portfolio_returns['avg_return'] / portfolio_returns['volatility']
        
        self.portfolio_metrics['returns'] = portfolio_returns
        self.logger.info("组合收益率计算完成")
        return portfolio_returns
    
    def calculate_ic_metrics(self, df: pd.DataFrame, factor: str, 
                           return_col: str = 'ten_day_return') -> Dict:
        """
        计算因子IC相关指标
        
        Parameters:
        df: 数据
        factor: 因子名称
        return_col: 收益率列名
        
        Returns:
        IC指标字典
        """
        data = df[[factor, return_col]].dropna()
        
        if len(data) < 2:
            return {}
            
        # 计算IC值
        ic, ic_pvalue = pd.Series(data[factor]).corr(pd.Series(data[return_col]), method='pearson'), \
                       pd.Series(data[factor]).corr(pd.Series(data[return_col]), method='spearman')
        
        # 计算ICIR
        rolling_ic = []
        window = min(60, len(data)//4)  # 窗口大小
        for i in range(window, len(data)):
            window_data = data.iloc[i-window:i]
            window_ic = pd.Series(window_data[factor]).corr(pd.Series(window_data[return_col]))
            rolling_ic.append(window_ic)
            
        ic_series = pd.Series(rolling_ic)
        icir = ic_series.mean() / ic_series.std() if ic_series.std() != 0 else 0
        
        metrics = {
            'ic': ic,
            'ic_ir': icir,
            'ic_pvalue': ic_pvalue,
            'ic_std': ic_series.std(),
            'positive_ic_rate': (ic_series > 0).mean()
        }
        
        self.portfolio_metrics['ic_metrics'] = metrics
        return metrics