import pandas as pd
import numpy as np
from typing import List
from sklearn.preprocessing import StandardScaler
from config.logger_config import data_logger

class FactorPreprocessor:
    """
    因子预处理器，用于标准化、去极值等预处理操作
    """
    
    def __init__(self):
        self.logger = data_logger
        self.scalers = {}
        
    def preprocess_factors(self, df: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
        """
        对因子进行预处理
        
        Parameters:
        df: 包含因子的DataFrame
        method: 预处理方法 ('standard', 'minmax', 'rank')
        
        Returns:
        预处理后的DataFrame
        """
        processed_df = df.copy()
        
        # 获取因子列（排除基本的价格和成交量列，以及股票代码和日期列）
        basic_cols = ['open', 'high', 'low', 'close', 'volume', 'preclose', 'turn', 'pctChg', 'code', 'stock', 'ten_day_return']
        factor_cols = [col for col in df.columns if col not in basic_cols and col != 'date']
        
        # 去掉单只股票的预处理开始日志，在汇总时统一显示
        
        if method == 'standard':
            processed_df = self._standardize(processed_df, factor_cols)
        elif method == 'winsorize':
            processed_df = self._winsorize(processed_df, factor_cols)
        elif method == 'rank':
            processed_df = self._rank_transform(processed_df, factor_cols)
            
        # 去掉单只股票的预处理完成日志，在汇总时统一显示
        return processed_df
    
    def _standardize(self, df: pd.DataFrame, factor_cols: List[str]) -> pd.DataFrame:
        """标准化处理"""
        processed_df = df.copy()
        
        for col in factor_cols:
            if col in processed_df.columns:
                # 检查是否为二值因子（只有0和1两个值）
                unique_values = processed_df[col].unique()
                is_binary_factor = len(unique_values) == 2 and set(unique_values).issubset({0, 1})
                
                if is_binary_factor:
                    # 二值因子跳过标准化，保持原始值
                    continue
                else:
                    # 去除极值（MAD方法）
                    processed_df[col] = self._remove_outliers_mad(processed_df[col])
                    
                    # 标准化
                    scaler = StandardScaler()
                    processed_df[col] = scaler.fit_transform(processed_df[[col]])
                    self.scalers[col] = scaler
                
        return processed_df
    
    def _winsorize(self, df: pd.DataFrame, factor_cols: List[str]) -> pd.DataFrame:
        """Winsorization处理（缩尾）"""
        processed_df = df.copy()
        
        for col in factor_cols:
            if col in processed_df.columns:
                # 1%和99%分位数缩尾
                q_low = processed_df[col].quantile(0.01)
                q_high = processed_df[col].quantile(0.99)
                processed_df[col] = processed_df[col].clip(lower=q_low, upper=q_high)
                
        return processed_df
    
    def _rank_transform(self, df: pd.DataFrame, factor_cols: List[str]) -> pd.DataFrame:
        """排序转换"""
        processed_df = df.copy()
        
        for col in factor_cols:
            if col in processed_df.columns:
                # 排名转换（0-1之间）
                processed_df[col] = processed_df[col].rank(pct=True)
                
        return processed_df
    
    def _remove_outliers_mad(self, series: pd.Series, n_mad: float = 3) -> pd.Series:
        """使用MAD方法去除极值"""
        median = series.median()
        mad = np.median(np.abs(series - median))
        threshold = n_mad * 1.4826 * mad
        
        # 替换极值为边界值
        lower_bound = median - threshold
        upper_bound = median + threshold
        
        return series.clip(lower=lower_bound, upper=upper_bound)