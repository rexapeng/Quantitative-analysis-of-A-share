import pandas as pd
import numpy as np
import talib
from .base import Factor


class DailyReturnFactor(Factor):
    """
    日收益率因子
    
    定义：衡量股票每日价格的变化率。
    计算方法：(当日收盘价 - 前一日收盘价) / 前一日收盘价
    说明：日收益率因子反映了股票价格的每日波动情况，正数表示上涨，负数表示下跌，绝对值越大表示波动幅度越大。
    """
    def __init__(self):
        """
        初始化日收益率因子
        
        因子名称: 'daily_ret'
        """
        super().__init__(name='daily_ret')
    
    def calculate(self, data):
        """
        计算日收益率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和日收益率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df[self.name] = df.groupby('ts_code')['close'].pct_change()
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DailyAmplitudeFactor(Factor):
    """
    日振幅因子
    
    定义：衡量股票每日价格的波动幅度。
    计算方法：(当日最高价 - 当日最低价) / 当日收盘价
    说明：日振幅因子反映了股票价格在单个交易日内的波动范围，值越大表示当日价格波动越剧烈。
    """
    def __init__(self):
        """
        初始化日振幅因子
        
        因子名称: 'daily_amp'
        """
        super().__init__(name='daily_amp')
    
    def calculate(self, data):
        """
        计算日振幅因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和日振幅因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        # 计算日振幅
        df[self.name] = (df['high'] - df['low']) / df['close']
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolatilityFactor(Factor):
    """
    波动率因子
    
    定义：衡量股票价格在一段时间内的波动程度。
    计算方法：过去window个交易日日收益率的标准差 * sqrt(252)（年化处理）
    说明：波动率因子反映了股票价格的不确定性，值越大表示价格波动越剧烈，风险越高。
    """
    def __init__(self, window=20):
        """
        初始化波动率因子
        
        参数:
            window: 计算波动率的时间窗口大小，默认为20个交易日
        
        因子名称: f'volatility_{window}'
        """
        super().__init__(name=f'volatility_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算波动率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和波动率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算波动率
        df[self.name] = df.groupby('ts_code')['daily_return'].transform(
            lambda x: x.rolling(window=self.window).std() * np.sqrt(252)
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DownsideRiskFactor(Factor):
    """
    下行风险因子
    
    定义：衡量股票价格下跌的风险程度。
    计算方法：过去window个交易日中所有负收益率的标准差 * sqrt(252)（年化处理）
    说明：下行风险因子只考虑收益率为负的情况，反映了投资者最关心的下跌风险，值越大表示下跌风险越高。
    """
    def __init__(self, window=20):
        """
        初始化下行风险因子
        
        参数:
            window: 计算下行风险的时间窗口大小，默认为20个交易日
        
        因子名称: f'downside_risk_{window}'
        """
        super().__init__(name=f'downside_risk_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算下行风险因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和下行风险因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算下行风险
        def calc_downside_risk(x):
            if len(x) < self.window:
                return None
            returns = x.iloc[-self.window:].dropna()
            downside_returns = returns[returns < 0]
            if len(downside_returns) == 0:
                return 0
            return np.sqrt((downside_returns ** 2).mean()) * np.sqrt(252)
        
        df[self.name] = df.groupby('ts_code')['daily_return'].transform(calc_downside_risk)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class MaximumDrawdownFactor(Factor):
    """
    最大回撤因子
    
    定义：衡量股票价格从历史高点下跌的最大幅度。
    计算方法：min((当前价格 - 历史最高价) / 历史最高价)，在过去window个交易日内
    说明：最大回撤因子反映了股票价格的下跌风险，值越小（越负）表示最大跌幅越大。
    """
    def __init__(self, window=20):
        """
        初始化最大回撤因子
        
        参数:
            window: 计算最大回撤的时间窗口大小，默认为20个交易日
        
        因子名称: f'max_drawdown_{window}'
        """
        super().__init__(name=f'max_drawdown_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算最大回撤因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和最大回撤因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算最大回撤
        def calc_max_drawdown(x):
            if len(x) < self.window:
                return None
            prices = x.iloc[-self.window:]
            peak = prices.cummax()
            drawdown = (prices - peak) / peak
            return drawdown.min()
        
        df[self.name] = df.groupby('ts_code')['close'].transform(calc_max_drawdown)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class SharpeRatioFactor(Factor):
    """
    夏普比率因子
    
    定义：衡量股票的风险调整后收益。
    计算方法：(年化平均收益率 - 无风险利率) / 年化波动率
    说明：夏普比率因子反映了每承担一单位风险所获得的超额收益，值越大表示投资效率越高。
    """
    def __init__(self, window=20, risk_free_rate=0.03):
        """
        初始化夏普比率因子
        
        参数:
            window: 计算夏普比率的时间窗口大小，默认为20个交易日
            risk_free_rate: 无风险利率，默认为0.03（3%）
        
        因子名称: f'sharpe_{window}'
        """
        super().__init__(name=f'sharpe_{window}')
        self.window = window
        self.risk_free_rate = risk_free_rate
    
    def calculate(self, data):
        """
        计算夏普比率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和夏普比率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算夏普比率
        def calc_sharpe_ratio(x):
            if len(x) < self.window:
                return None
            returns = x.iloc[-self.window:].dropna()
            if len(returns) == 0:
                return None
            mean_return = returns.mean() * 252
            std_return = returns.std() * np.sqrt(252)
            if std_return == 0:
                return None
            return (mean_return - self.risk_free_rate) / std_return
        
        df[self.name] = df.groupby('ts_code')['daily_return'].transform(calc_sharpe_ratio)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class SkewnessFactor(Factor):
    """
    偏度因子
    
    定义：衡量股票收益率分布的不对称程度。
    计算方法：E[((X - μ) / σ)^3]，即标准化收益率的三阶矩
        - E[ ]: 期望值
        - X: 收益率
        - μ: 平均收益率
        - σ: 收益率标准差
    说明：偏度因子为正表示收益率分布右偏（极端正收益出现的概率较高），为负表示收益率分布左偏（极端负收益出现的概率较高）。
    """
    def __init__(self, window=20):
        """
        初始化偏度因子
        
        参数:
            window: 计算偏度的时间窗口大小，默认为20个交易日
        
        因子名称: f'skew_{window}'
        """
        super().__init__(name=f'skew_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算偏度因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和偏度因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算偏度
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window + 1:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算偏度
                # talib.SKEW计算的是价格的偏度，而我们需要的是收益率的偏度
                # 所以需要对收益率序列应用talib.SKEW
                returns = group['daily_return'].values
                # 移除第一个NaN值（因为是pct_change产生的）
                returns = returns[~np.isnan(returns)]
                if len(returns) < self.window:
                    group[self.name] = np.nan
                else:
                    # 使用滚动窗口计算偏度
                    skew_values = np.full_like(returns, np.nan)
                    for i in range(self.window - 1, len(returns)):
                        window_returns = returns[i - self.window + 1:i + 1]
                        skew_values[i] = np.nanmean(np.power((window_returns - np.nanmean(window_returns)) / np.nanstd(window_returns), 3))
                    # 将结果放回到原始长度的数组中（包括第一个NaN）
                    result = np.full(len(group), np.nan)
                    result[1:len(skew_values) + 1] = skew_values
                    group[self.name] = result
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class KurtosisFactor(Factor):
    """
    峰度因子
    
    定义：衡量股票收益率分布的尖峰程度。
    计算方法：E[((X - μ) / σ)^4] - 3，即标准化收益率的四阶矩减去3
        - E[ ]: 期望值
        - X: 收益率
        - μ: 平均收益率
        - σ: 收益率标准差
    说明：峰度因子为正表示收益率分布尖峰厚尾（极端收益出现的概率较高），为负表示收益率分布平坦。
    """
    def __init__(self, window=20):
        """
        初始化峰度因子
        
        参数:
            window: 计算峰度的时间窗口大小，默认为20个交易日
        
        因子名称: f'kurtosis_{window}'
        """
        super().__init__(name=f'kurtosis_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算峰度因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和峰度因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算峰度
        results = []
        for ts_code, group in df.groupby('ts_code'):
            if len(group) < self.window + 1:
                # 如果数据长度不足，填充NaN
                group[self.name] = np.nan
            else:
                # 使用talib计算峰度
                # talib.KURT计算的是价格的峰度，而我们需要的是收益率的峰度
                # 所以需要对收益率序列应用talib.KURT
                returns = group['daily_return'].values
                # 移除第一个NaN值（因为是pct_change产生的）
                returns = returns[~np.isnan(returns)]
                if len(returns) < self.window:
                    group[self.name] = np.nan
                else:
                    # 使用滚动窗口计算峰度
                    kurt_values = np.full_like(returns, np.nan)
                    for i in range(self.window - 1, len(returns)):
                        window_returns = returns[i - self.window + 1:i + 1]
                        kurt_values[i] = np.nanmean(np.power((window_returns - np.nanmean(window_returns)) / np.nanstd(window_returns), 4)) - 3
                    # 将结果放回到原始长度的数组中（包括第一个NaN）
                    result = np.full(len(group), np.nan)
                    result[1:len(kurt_values) + 1] = kurt_values
                    group[self.name] = result
            results.append(group)
        
        # 合并结果
        df = pd.concat(results)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df