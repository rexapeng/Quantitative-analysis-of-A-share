import pandas as pd
import numpy as np
import talib
from .base import Factor





class KDJ_J_Factor(Factor):
    """
    KDJ指标的J线因子
    
    定义：KDJ指标的J线，是K线和D线的派生指标，用于衡量股价超买超卖状态
    计算方法：
    1. 计算K线：快速随机指标线，通过最近fastk_period天的最高价、最低价和收盘价计算
    2. 计算D线：慢速随机指标线，是K线的slowk_period日移动平均
    3. 计算J线：J = 3*K - 2*D
    说明：J线是KDJ指标中最敏感的线，通常J>100表示超买，J<0表示超卖
    """
    def __init__(self, fastk_period=9, slowk_period=3, slowd_period=3):
        """
        初始化KDJ_J_Factor
        
        参数:
            fastk_period: 快速K线的计算周期（交易日）
            slowk_period: 慢速K线的计算周期（交易日）
            slowd_period: 慢速D线的计算周期（交易日）
        """
        super().__init__(name='kdj_j')
        self.fastk_period = fastk_period
        self.slowk_period = slowk_period
        self.slowd_period = slowd_period
    
    def calculate(self, data):
        """
        计算KDJ的J线因子
        
        参数:
            data: 股票数据，包含以下必要列:
                - ts_code: 股票代码
                - trade_date: 交易日期
                - close: 收盘价
                - high: 最高价
                - low: 最低价
        
        返回:
            pandas.DataFrame: 包含ts_code, trade_date和kdj_j因子值的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算KDJ指标
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.fastk_period:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算KD指标
                slowk, slowd = talib.STOCH(
                    group['high'].values,
                    group['low'].values,
                    group['close'].values,
                    fastk_period=self.fastk_period,
                    slowk_period=self.slowk_period,
                    slowk_matype=0,  # 简单移动平均
                    slowd_period=self.slowd_period,
                    slowd_matype=0   # 简单移动平均
                )
                # 计算J线: J = 3*K - 2*D
                slowj = 3 * slowk - 2 * slowd
                group[self.name] = slowj
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class MACD_DIFF_Factor(Factor):
    """
    MACD指标的DIFF线因子
    
    定义：MACD指标的差离值线，反映短期与长期移动平均线之间的差异
    计算方法：
    1. 计算fast_period日指数移动平均线（EMA）
    2. 计算slow_period日指数移动平均线（EMA）
    3. DIFF = fast_period日EMA - slow_period日EMA
    说明：DIFF线是MACD指标的核心，反映市场的动量变化，通常与DEA线和柱状图配合使用
    """
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        """
        初始化MACD_DIFF_Factor
        
        参数:
            fast_period: 快速EMA的计算周期（交易日）
            slow_period: 慢速EMA的计算周期（交易日）
            signal_period: 信号线（DEA）的计算周期（交易日）
        """
        super().__init__(name='macd_diff')
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, data):
        """
        计算MACD的DIFF线因子
        
        参数:
            data: 股票数据，包含以下必要列:
                - ts_code: 股票代码
                - trade_date: 交易日期
                - close: 收盘价
        
        返回:
            pandas.DataFrame: 包含ts_code, trade_date和macd_diff因子值的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算MACD指标
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.slow_period:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算MACD指标
                macd, macdsignal, macdhist = talib.MACD(
                    group['close'].values,
                    fastperiod=self.fast_period,
                    slowperiod=self.slow_period,
                    signalperiod=self.signal_period
                )
                # DIFF线就是macd值
                group[self.name] = macd
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class CustomMomentumFactor(Factor):
    """
    自定义动量因子示例
    
    定义：衡量股票价格在过去window个交易日内的上涨或下跌幅度，反映价格趋势的强弱
    计算方法: (当前价格 - window天前价格) / window天前价格
    说明：正动量表示价格上涨趋势，负动量表示价格下跌趋势，绝对值越大趋势越强
    """
    def __init__(self, window=20):
        """
        初始化CustomMomentumFactor
        
        参数:
            window: 计算动量的时间窗口（交易日）
        """
        super().__init__(name=f'custom_momentum_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算自定义动量因子
        
        参数:
            data: 股票数据，包含以下必要列:
                - ts_code: 股票代码
                - trade_date: 交易日期
                - close: 收盘价
        
        返回:
            pandas.DataFrame: 包含ts_code, trade_date和因子值的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算动量因子
        df[self.name] = df.groupby('ts_code')['close'].transform(
            lambda x: (x - x.shift(self.window)) / x.shift(self.window)
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df





