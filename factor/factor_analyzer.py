import pandas as pd
import numpy as np
import alphalens as al
from logger_config import data_logger

class FactorAnalyzer:
    """
    因子分析器，使用Alphalens库进行专业的因子分析
    """
    
    def __init__(self, settings=None):
        self.logger = data_logger
        self.settings = settings or {
            'periods': [1, 5, 10],
            'quantiles': 5,
            'max_loss': 0.25
        }
        self.analysis_results = {}
        
    def analyze_factor(self, factor_data, prices, factor_name, asset_name='stock'):
        """
        使用Alphalens分析单个因子
        
        Parameters:
        factor_data: 因子值序列 (pandas Series)
        prices: 价格数据 (pandas DataFrame)
        factor_name: 因子名称
        asset_name: 资产名称
        
        Returns:
        分析结果字典
        """
        try:
            # 准备Alphalens所需的数据格式
            factor_series = pd.Series(factor_data.values, 
                                    index=pd.MultiIndex.from_arrays([
                                        factor_data.index, 
                                        [asset_name] * len(factor_data)
                                    ], names=['date', 'asset']))
            
            # 获取干净的因子和未来收益数据
            factor_clean = al.utils.get_clean_factor_and_forward_returns(
                factor=factor_series,
                prices=prices,
                periods=self.settings['periods'],
                max_loss=self.settings['max_loss'],
                quantiles=self.settings['quantiles']
            )
            
            # 计算各项指标
            # 1. 分位数组平均收益
            mean_ret_by_q = al.performance.mean_return_by_quantile(factor_clean)
            
            # 2. 信息系数(IC)
            ic = al.performance.factor_information_coefficient(factor_clean)
            
            # 3. 因子自相关性（换手率）
            turnover = al.performance.factor_rank_autocorrelation(factor_clean)
            
            # 4. 累积收益
            cumulative_ret = al.performance.cumulative_returns_by_quantile(factor_clean, period=1)
            
            results = {
                'factor_name': factor_name,
                'clean_factor_data': factor_clean,
                'mean_return_by_quantile': mean_ret_by_q,
                'information_coefficient': ic,
                'turnover': turnover,
                'cumulative_returns': cumulative_ret
            }
            
            self.analysis_results[factor_name] = results
            self.logger.info(f"{factor_name}因子分析完成")
            return results
            
        except Exception as e:
            self.logger.error(f"{factor_name}因子分析失败: {e}")
            return None
    
    def get_factor_summary(self, factor_name):
        """
        获取因子分析摘要
        
        Parameters:
        factor_name: 因子名称
        
        Returns:
        因子摘要信息
        """
        if factor_name not in self.analysis_results:
            return None
            
        result = self.analysis_results[factor_name]
        ic = result['information_coefficient']
        mean_ret = result['mean_return_by_quantile'][0]
        
        summary = {
            'factor_name': factor_name,
            'ic_mean': ic.mean().to_dict(),
            'ic_std': ic.std().to_dict(),
            'ic_ir': (ic.mean() / ic.std()).to_dict(),  # 信息比率
            'best_quantile_return': mean_ret.iloc[:, -1].mean(),  # 最高分位数组平均收益
            'worst_quantile_return': mean_ret.iloc[:, 0].mean()   # 最低分位数组平均收益
        }
        
        return summary
    
    def get_top_factors(self, top_n=10):
        """
        根据IC值获取表现最好的因子
        
        Parameters:
        top_n: 返回前N个因子
        
        Returns:
        包含因子IC值的DataFrame
        """
        summaries = []
        for factor_name in self.analysis_results.keys():
            summary = self.get_factor_summary(factor_name)
            if summary:
                # 计算平均IC值作为排序依据
                avg_ic = np.mean(list(summary['ic_mean'].values()))
                summaries.append({
                    'factor': factor_name,
                    'avg_ic': avg_ic,
                    'abs_avg_ic': abs(avg_ic),
                    'best_quantile_return': summary['best_quantile_return']
                })
        
        df_summary = pd.DataFrame(summaries)
        if not df_summary.empty:
            df_summary = df_summary.sort_values('abs_avg_ic', ascending=False).head(top_n)
        
        return df_summary