import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from logger_config import data_logger

class FactorAnalyzer:
    """
    因子分析器，用于分析因子有效性
    """
    
    def __init__(self):
        self.logger = data_logger
        self.analysis_results = {}
        
    def analyze_factor_returns(self, df: pd.DataFrame, forward_periods: List[int] = [1, 5, 10]) -> Dict:
        """
        分析因子与未来收益的相关性
        
        Parameters:
        df: 包含因子和收益率的数据
        forward_periods: 向前预测的周期列表
        
        Returns:
        分析结果字典
        """
        results = {}
        
        # 计算未来收益
        for period in forward_periods:
            df[f'FWD_RETURN_{period}'] = df['close'].shift(-period) / df['close'] - 1
            
        # 获取因子列
        basic_cols = ['open', 'high', 'low', 'close', 'volume', 'preclose', 'turn', 'pctChg', 'date']
        factor_cols = [col for col in df.columns if col not in basic_cols and not col.startswith('FWD_RETURN')]
        
        self.logger.info(f"开始分析{len(factor_cols)}个因子对未来收益的预测能力")
        
        # 计算每个因子与未来收益的相关性
        for factor in factor_cols:
            if factor not in df.columns:
                continue
                
            results[factor] = {}
            for period in forward_periods:
                fwd_return_col = f'FWD_RETURN_{period}'
                if fwd_return_col not in df.columns:
                    continue
                    
                # 去除空值
                valid_data = df[[factor, fwd_return_col]].dropna()
                
                if len(valid_data) < 30:  # 数据量太少则跳过
                    results[factor][period] = {
                        'pearson_corr': np.nan,
                        'pearson_pvalue': np.nan,
                        'spearman_corr': np.nan,
                        'spearman_pvalue': np.nan,
                        'ic': np.nan
                    }
                    continue
                
                # 计算相关系数
                pearson_corr, pearson_p = pearsonr(valid_data[factor], valid_data[fwd_return_col])
                spearman_corr, spearman_p = spearmanr(valid_data[factor], valid_data[fwd_return_col])
                
                results[factor][period] = {
                    'pearson_corr': pearson_corr,
                    'pearson_pvalue': pearson_p,
                    'spearman_corr': spearman_corr,
                    'spearman_pvalue': spearman_p,
                    'ic': pearson_corr  # IC值通常使用皮尔逊相关系数
                }
                
        self.analysis_results = results
        self.logger.info("因子收益分析完成")
        return results
    
    def get_top_factors(self, period: int = 1, top_n: int = 10) -> pd.DataFrame:
        """
        获取表现最好的因子
        
        Parameters:
        period: 预测周期
        top_n: 返回前N个因子
        
        Returns:
        包含因子IC值的DataFrame
        """
        if not self.analysis_results:
            raise ValueError("尚未进行因子分析，请先调用analyze_factor_returns方法")
            
        factor_ic = []
        for factor, results in self.analysis_results.items():
            if period in results and not np.isnan(results[period]['ic']):
                factor_ic.append({
                    'factor': factor,
                    'ic': results[period]['ic'],
                    'abs_ic': abs(results[period]['ic']),
                    'pearson_pvalue': results[period]['pearson_pvalue']
                })
                
        df_ic = pd.DataFrame(factor_ic)
        df_ic = df_ic.sort_values('abs_ic', ascending=False).head(top_n)
        
        return df_ic
    
    def analyze_factor_stability(self, df: pd.DataFrame, factor: str, window: int = 60) -> Dict:
        """
        分析因子稳定性（滚动IC）
        
        Parameters:
        df: 数据
        factor: 因子名称
        window: 滚动窗口大小
        
        Returns:
        稳定性分析结果
        """
        if factor not in df.columns:
            raise ValueError(f"因子 {factor} 不存在于数据中")
            
        # 计算未来1日收益
        df['FWD_RETURN_1'] = df['close'].shift(-1) / df['close'] - 1
        
        # 滚动计算IC值
        rolling_ic = []
        for i in range(window, len(df)):
            window_data = df.iloc[i-window:i]
            valid_data = window_data[[factor, 'FWD_RETURN_1']].dropna()
            
            if len(valid_data) > 10:
                ic, _ = pearsonr(valid_data[factor], valid_data['FWD_RETURN_1'])
                rolling_ic.append({
                    'date': df.index[i],
                    'ic': ic
                })
                
        if rolling_ic:
            ic_series = pd.DataFrame(rolling_ic).set_index('date')['ic']
            stability_metrics = {
                'mean_ic': ic_series.mean(),
                'std_ic': ic_series.std(),
                'ir': ic_series.mean() / ic_series.std() if ic_series.std() != 0 else 0,  # 信息比率
                'positive_ic_rate': (ic_series > 0).mean(),  # 正向IC占比
                'ic_series': ic_series
            }
            return stability_metrics
        else:
            return {}