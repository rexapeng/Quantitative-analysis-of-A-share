import pandas as pd
import numpy as np
import talib
from .base import Factor


class MomentumFactor(Factor):
    """
    动量因子
    
    定义：衡量股票价格在一段时间内的上涨或下跌趋势。
    计算方法：(当前收盘价 - window天前的收盘价) / window天前的收盘价
    说明：动量因子为正表示价格在window天内上涨，为负表示价格在window天内下跌，绝对值越大表示动量越强。
    """
    def __init__(self, window=20):
        """
        初始化动量因子
        
        参数:
            window: 计算动量的时间窗口大小，默认为20个交易日
        
        因子名称: f'momentum_{window}'
        """
        super().__init__(name=f'momentum_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算动量因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和动量因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算动量因子
        df[self.name] = df.groupby('ts_code')['close'].transform(
            lambda x: x.iloc[-1] / x.iloc[0] - 1
            if len(x) >= self.window else None
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class RSIFactor(Factor):
    """
    相对强弱指标因子
    
    定义：衡量股票价格上涨和下跌动量的相对强度。
    计算方法：RSI = 100 - (100 / (1 + (平均上涨幅度 / 平均下跌幅度)))
    说明：RSI值在0-100之间，通常认为RSI>70表示超买，RSI<30表示超卖。
    """
    def __init__(self, window=14):
        """
        初始化相对强弱指标因子
        
        参数:
            window: 计算RSI的时间窗口大小，默认为14个交易日
        
        因子名称: f'rsi_{window}'
        """
        super().__init__(name=f'rsi_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算相对强弱指标因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和RSI因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI指标
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window + 1:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算RSI
                rsi = talib.RSI(group['close'].values, timeperiod=self.window)
                group[self.name] = rsi
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class MACDFactor(Factor):
    """
    MACD因子
    
    定义：移动平均收敛发散指标，用于衡量股票价格的趋势强度和反转信号。
    计算方法：MACD = 2 * (DIF - DEA)
        - DIF（离差值）= 12日EMA - 26日EMA
        - DEA（信号线）= DIF的9日EMA
    说明：MACD值为正表示多头市场，为负表示空头市场，MACD柱状图的变化可以反映趋势的强度变化。
    """
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        """
        初始化MACD因子
        
        参数:
            fast_period: 快速EMA的周期，默认为12
            slow_period: 慢速EMA的周期，默认为26
            signal_period: 信号线EMA的周期，默认为9
        
        因子名称: 'macd'
        """
        super().__init__(name='macd')
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, data):
        """
        计算MACD因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和MACD因子值列的DataFrame
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
                # 原始代码中MACD = 2*(DIF - DEA)，而talib的macdhist = DIF - DEA
                # 所以需要乘以2来保持一致
                macd_value = 2 * macdhist
                group[self.name] = macd_value
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class WilliamsRFactor(Factor):
    """
    威廉指标因子
    
    定义：衡量股票价格的超买超卖程度。
    计算方法：WR = (Hn - C) / (Hn - Ln) * 100
        - Hn: window天内的最高价
        - Ln: window天内的最低价
        - C: 当前收盘价
    说明：WR值在0到-100之间，WR > -20表示超买，WR < -80表示超卖。
    """
    def __init__(self, window=14):
        """
        初始化威廉指标因子
        
        参数:
            window: 计算威廉指标的时间窗口大小，默认为14个交易日
        
        因子名称: f'wr_{window}'
        """
        super().__init__(name=f'wr_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算威廉指标因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'close'（收盘价）、'high'（最高价）和'low'（最低价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和威廉指标因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算威廉指标
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算威廉指标
                willr = talib.WILLR(
                    group['high'].values,
                    group['low'].values,
                    group['close'].values,
                    timeperiod=self.window
                )
                group[self.name] = willr
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class StochasticFactor(Factor):
    """
    随机指标因子
    
    定义：衡量股票价格在一段时间内的相对位置，用于判断超买超卖。
    计算方法：%K = (C - Ln) / (Hn - Ln) * 100
        - C: 当前收盘价
        - Ln: window天内的最低价
        - Hn: window天内的最高价
    说明：%K值在0到100之间，%K > 80表示超买，%K < 20表示超卖。
    """
    def __init__(self, window=14):
        """
        初始化随机指标因子
        
        参数:
            window: 计算随机指标的时间窗口大小，默认为14个交易日
        
        因子名称: f'stoch_{window}'
        """
        super().__init__(name=f'stoch_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算随机指标因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'close'（收盘价）、'high'（最高价）和'low'（最低价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和随机指标因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算随机指标
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算快速随机指标（%K线）
                fastk, fastd = talib.STOCHF(
                    group['high'].values,
                    group['low'].values,
                    group['close'].values,
                    fastk_period=self.window,
                    fastd_period=1,  # 不进行平滑
                    fastd_matype=0   # 简单移动平均
                )
                group[self.name] = fastk
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class RateOfChangeFactor(Factor):
    """
    变化率因子
    
    定义：衡量股票价格在一段时间内的变化速度。
    计算方法：(当前收盘价 - window天前的收盘价) / window天前的收盘价 * 100
    说明：ROC因子反映了价格变化的百分比，值越大表示价格变化速度越快。
    """
    def __init__(self, window=20):
        """
        初始化变化率因子
        
        参数:
            window: 计算变化率的时间窗口大小，默认为20个交易日
        
        因子名称: f'roc_{window}'
        """
        super().__init__(name=f'roc_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算变化率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和变化率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算变化率
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window + 1:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算ROC指标
                roc = talib.ROC(group['close'].values, timeperiod=self.window)
                group[self.name] = roc
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df