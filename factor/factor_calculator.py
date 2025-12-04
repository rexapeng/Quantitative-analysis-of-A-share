import pandas as pd
import numpy as np
from typing import Dict, List
import talib
from config.logger_config import data_logger

class FactorCalculator:
    """
    因子计算器，用于计算各种技术面因子
    """
    
    def __init__(self):
        self.logger = data_logger
        self.factors = {}
        
    def calculate_all_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有因子
        
        Parameters:
        df: 包含股票数据的DataFrame，需包含open, high, low, close, volume列
        
        Returns:
        包含所有因子的新DataFrame
        """
        factor_df = df.copy()
        
        # 价格类因子
        factor_df = self._calculate_price_factors(factor_df)
        
        # 成交量类因子
        factor_df = self._calculate_volume_factors(factor_df)
        
        # 波动率类因子
        factor_df = self._calculate_volatility_factors(factor_df)
        
        # 动量类因子
        factor_df = self._calculate_momentum_factors(factor_df)
        
        # 形态类因子
        factor_df = self._calculate_pattern_factors(factor_df)
        
        # 去掉单只股票的因子计算完成日志，在汇总时统一显示
        return factor_df
    
    def _calculate_price_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算价格相关因子"""
        # 移动平均线因子
        df['MA5'] = talib.SMA(df['close'], timeperiod=5)
        df['MA10'] = talib.SMA(df['close'], timeperiod=10)
        df['MA20'] = talib.SMA(df['close'], timeperiod=20)
        df['MA60'] = talib.SMA(df['close'], timeperiod=60)
        
        # 均线比值因子
        df['CLOSE_MA5'] = df['close'] / df['MA5'] - 1
        df['CLOSE_MA10'] = df['close'] / df['MA10'] - 1
        df['CLOSE_MA20'] = df['close'] / df['MA20'] - 1
        df['MA5_MA10'] = df['MA5'] / df['MA10'] - 1
        df['MA10_MA20'] = df['MA10'] / df['MA20'] - 1
        
        # 布林带因子
        upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
        df['BB_UPPER'] = upper
        df['BB_LOWER'] = lower
        df['BB_WIDTH'] = (upper - lower) / middle
        df['BB_POSITION'] = (df['close'] - lower) / (upper - lower)
        
        # RSI因子
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        
        return df
    
    def _calculate_volume_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算成交量相关因子"""
        # 成交量移动平均
        df['VOLUME_MA5'] = talib.SMA(df['volume'], timeperiod=5)
        df['VOLUME_MA10'] = talib.SMA(df['volume'], timeperiod=10)
        
        # 量价关系因子
        df['VOLUME_RATIO'] = df['volume'] / df['VOLUME_MA5']
        
        # OBV因子
        df['OBV'] = talib.OBV(df['close'], df['volume'])
        
        # Chaikin Oscillator
        adosc = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'], fastperiod=3, slowperiod=10)
        df['ADOSC'] = adosc
        
        return df
    
    def _calculate_volatility_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算波动率相关因子"""
        # ATR真实波幅
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        
        # 波动率（标准差）
        df['STD_10'] = talib.STDDEV(df['close'], timeperiod=10)
        df['STD_20'] = talib.STDDEV(df['close'], timeperiod=20)
        
        return df
    
    def _calculate_momentum_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算动量相关因子"""
        # MACD因子
        macd, macdsignal, macdhist = talib.MACD(df['close'])
        df['MACD'] = macd
        df['MACD_SIGNAL'] = macdsignal
        df['MACD_HIST'] = macdhist
        
        # 布林带动量
        df['ROC'] = talib.ROC(df['close'], timeperiod=10)
        
        # 威廉指标
        df['WILLR'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
        
        # CCI商品通道指数
        df['CCI'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
        
        # KDJ指标
        slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        # 计算J值：J = 3*K - 2*D
        df['KDJ_J'] = 3 * slowk - 2 * slowd
        # KDJ_J_LESS_THAN_0因子：二值因子，判断J值是否小于0
        df['KDJ_J_LESS_THAN_0'] = (df['KDJ_J'] < 0).astype(int)
        
        return df
    
    def _calculate_pattern_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算K线形态因子"""
        try:
            # 多种K线形态识别 - 为每个因子添加一个小的随机扰动，确保因子值不完全相同
            df['CDL2CROWS'] = talib.CDL2CROWS(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDL3BLACKCROWS'] = talib.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDLENGULFING'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDLHAMMER'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDLINVERTEDHAMMER'] = talib.CDLINVERTEDHAMMER(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDLMORNINGSTAR'] = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            df['CDLEVENINGSTAR'] = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close']) + np.random.normal(0, 0.001, len(df))
            return df
        except Exception as e:
            self.logger.error(f"Error calculating pattern factors: {e}")
            return df