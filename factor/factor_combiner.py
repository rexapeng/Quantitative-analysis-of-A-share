import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from config.logger_config import data_logger

class FactorCombiner:
    """
    因子组合器，用于构建因子组合
    """
    
    def __init__(self):
        self.logger = data_logger
        self.combined_factors = {}
        
    def combine_factors_ic_weighted(self, df: pd.DataFrame, factors: List[str], 
                                   factor_weights: Dict[str, float] = None) -> pd.Series:
        """
        使用IC加权法合成因子
        
        Parameters:
        df: 数据
        factors: 因子列表
        factor_weights: 因子权重，如果为None则使用等权
        
        Returns:
        合成因子序列
        """
        if factor_weights is None:
            # 等权
            weights = {factor: 1.0/len(factors) for factor in factors}
        else:
            weights = factor_weights
            
        # 标准化因子
        self.logger.info("开始标准化因子数据...")
        scaler = StandardScaler()
        factor_data = df[factors].dropna()
        scaled_factors = pd.DataFrame(
            scaler.fit_transform(factor_data),
            columns=factors,
            index=factor_data.index
        )
        self.logger.info(f"因子标准化完成，处理了{len(factor_data)}条有效数据")
        
        # 加权合成
        combined_factor = pd.Series(0, index=scaled_factors.index)
        for factor in factors:
            if factor in weights:
                combined_factor += scaled_factors[factor] * weights[factor]
                
        self.combined_factors['ic_weighted'] = combined_factor
        self.logger.info(f"使用IC加权法合成了{len(factors)}个因子")
        return combined_factor
    
    def combine_factors_regression(self, df: pd.DataFrame, factors: List[str], 
                                  target_col: str = 'pctChg') -> pd.Series:
        """
        使用回归法合成因子
        
        Parameters:
        df: 数据
        factors: 因子列表
        target_col: 目标变量列名
        
        Returns:
        合成因子序列
        """
        # 准备数据
        self.logger.info("开始准备回归模型数据...")
        data = df[factors + [target_col]].dropna()
        X = data[factors]
        y = data[target_col]
        self.logger.info(f"回归数据准备完成，处理了{len(data)}条有效数据")
        
        # 标准化
        self.logger.info("开始标准化回归数据...")
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1)).flatten()
        self.logger.info("数据标准化完成")
        
        # 回归
        self.logger.info("开始训练回归模型...")
        model = LinearRegression()
        model.fit(X_scaled, y_scaled)
        self.logger.info("回归模型训练完成")
        
        # 合成因子
        combined_factor = pd.Series(
            model.predict(X_scaled),
            index=data.index
        )
        
        # 保存权重
        self.combined_factors['regression_weights'] = dict(zip(factors, model.coef_))
        self.combined_factors['regression_combined'] = combined_factor
        
        self.logger.info(f"使用回归法合成了{len(factors)}个因子")
        return combined_factor
    
    def combine_factors_rank_sum(self, df: pd.DataFrame, factors: List[str]) -> pd.Series:
        """
        使用排序和法合成因子
        
        Parameters:
        df: 数据
        factors: 因子列表
        
        Returns:
        合成因子序列
        """
        # 获取因子数据
        factor_data = df[factors].dropna()
        
        # 排序转换
        rank_sum = pd.Series(0, index=factor_data.index)
        for factor in factors:
            rank_sum += factor_data[factor].rank(pct=True)
            
        # 平均排名
        combined_factor = rank_sum / len(factors)
        
        self.combined_factors['rank_sum'] = combined_factor
        self.logger.info(f"使用排序和法合成了{len(factors)}个因子")
        return combined_factor