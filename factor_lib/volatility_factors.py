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


class TrueRangeFactor(Factor):
    """
    真实波幅因子
    
    定义：衡量股票价格的真实波动幅度。
    计算方法：TR = max(High - Low, abs(High - Close_prev), abs(Low - Close_prev))
        - High: 当日最高价
        - Low: 当日最低价
        - Close_prev: 前一日收盘价
        
    说明：真实波幅因子考虑了跳空缺口的影响，更准确地反映了股票价格的真实波动幅度。
    """
    def __init__(self):
        """
        初始化真实波幅因子
        
        因子名称: 'tr'
        """
        super().__init__(name='tr')
    
    def calculate(self, data):
        """
        计算真实波幅因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和真实波幅因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算前一日收盘价
        df['prev_close'] = df.groupby('ts_code')['close'].shift(1)
        
        # 计算真实波幅
        df['h_l'] = df['high'] - df['low']
        df['h_pc'] = abs(df['high'] - df['prev_close'])
        df['l_pc'] = abs(df['low'] - df['prev_close'])
        
        df[self.name] = df[['h_l', 'h_pc', 'l_pc']].max(axis=1)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class AverageTrueRangeFactor(Factor):
    """
    平均真实波幅因子
    
    定义：真实波幅的移动平均值，用于衡量市场波动性。
    计算方法：ATR = (前一个ATR × (n-1) + 当前TR) / n
        - TR: 真实波幅
        - n: 时间周期，默认为14天
        
    说明：平均真实波幅因子平滑了真实波幅的波动，更好地反映市场的长期波动水平。
    """
    def __init__(self, window=14):
        """
        初始化平均真实波幅因子
        
        参数:
            window: 计算平均真实波幅的时间窗口大小，默认为14个交易日
            
        因子名称: f'atr_{window}'
        """
        super().__init__(name=f'atr_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算平均真实波幅因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和平均真实波幅因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算真实波幅
        df['prev_close'] = df.groupby('ts_code')['close'].shift(1)
        df['h_l'] = df['high'] - df['low']
        df['h_pc'] = abs(df['high'] - df['prev_close'])
        df['l_pc'] = abs(df['low'] - df['prev_close'])
        df['tr'] = df[['h_l', 'h_pc', 'l_pc']].max(axis=1)
        
        # 计算平均真实波幅
        df[self.name] = df.groupby('ts_code')['tr'].transform(
            lambda x: x.rolling(window=self.window).mean()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DownsideDeviationFactor(Factor):
    """
    下行标准差因子
    
    定义：衡量股票收益率低于目标收益率的波动程度。
    计算方法：DD = sqrt(sum(min(0, Ri - T)^2) / N)
        - Ri: 第i期的实际收益率
        - T: 目标收益率（通常设为0）
        - N: 样本数量
        
    说明：下行标准差因子只考虑收益率为负的情况，更好地反映了投资者面临的真实风险。
    """
    def __init__(self, window=20, target_return=0):
        """
        初始化下行标准差因子
        
        参数:
            window: 计算下行标准差的时间窗口大小，默认为20个交易日
            target_return: 目标收益率，默认为0
            
        因子名称: f'downside_dev_{window}'
        """
        super().__init__(name=f'downside_dev_{window}')
        self.window = window
        self.target_return = target_return
    
    def calculate(self, data):
        """
        计算下行标准差因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和下行标准差因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算日收益率
        df['daily_return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算下行标准差
        def calc_downside_dev(x):
            if len(x) < self.window:
                return None
            returns = x.iloc[-self.window:].dropna()
            downside_returns = returns[returns < self.target_return]
            if len(downside_returns) == 0:
                return 0
            return np.sqrt((downside_returns ** 2).mean())
        
        df[self.name] = df.groupby('ts_code')['daily_return'].transform(calc_downside_dev)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class UlcerIndexFactor(Factor):
    """
    溃疡指数因子
    
    定义：衡量股票价格回撤的深度和持续时间。
    计算方法：
        1. 计算每日回撤百分比: (当前价格 / 历史最高价 - 1) × 100%
        2. 计算溃疡指数: sqrt(sum(回撤百分比^2) / n)
        
    说明：溃疡指数因子综合考虑了回撤的幅度和持续时间，值越大表示投资者承受的心理压力越大。
    """
    def __init__(self, window=14):
        """
        初始化溃疡指数因子
        
        参数:
            window: 计算溃疡指数的时间窗口大小，默认为14个交易日
            
        因子名称: f'ulcer_index_{window}'
        """
        super().__init__(name=f'ulcer_index_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算溃疡指数因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和溃疡指数因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算历史最高价
        df['peak'] = df.groupby('ts_code')['close'].expanding().max().reset_index(level=0, drop=True)
        
        # 计算回撤百分比
        df['drawdown_pct'] = (df['close'] / df['peak'] - 1) * 100
        
        # 计算溃疡指数
        def calc_ulcer_index(x):
            if len(x) < self.window:
                return None
            drawdowns = x.iloc[-self.window:]
            return np.sqrt((drawdowns ** 2).mean())
        
        df[self.name] = df.groupby('ts_code')['drawdown_pct'].transform(calc_ulcer_index)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class HistoricalVolatilityFactor(Factor):
    """
    历史波动率因子
    
    定义：衡量股票价格的历史波动程度。
    计算方法：HV = std(ln(Pt/Pt-1)) × sqrt(N)
        - Pt: 第t期的价格
        - N: 年化因子（通常为252个交易日）
        
    说明：历史波动率因子反映了股票价格的历史波动水平，是期权定价等金融工程中的重要参数。
    """
    def __init__(self, window=20):
        """
        初始化历史波动率因子
        
        参数:
            window: 计算历史波动率的时间窗口大小，默认为20个交易日
            
        因子名称: f'historical_vol_{window}'
        """
        super().__init__(name=f'historical_vol_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算历史波动率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和历史波动率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算对数收益率
        df['log_return'] = df.groupby('ts_code')['close'].transform(lambda x: np.log(x / x.shift(1)))
        
        # 计算历史波动率
        df[self.name] = df.groupby('ts_code')['log_return'].transform(
            lambda x: x.rolling(window=self.window).std() * np.sqrt(252)
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class ParkinsonVolatilityFactor(Factor):
    """
    帕金森波动率因子
    
    定义：基于最高价和最低价计算的波动率估计。
    计算方法：PV = sqrt((1/(4*N*ln(2))) * sum(ln(Hi/Li)^2))
        - Hi: 第i期的最高价
        - Li: 第i期的最低价
        - N: 时间周期
        
    说明：帕金森波动率因子利用了价格的高低点信息，相比仅使用收盘价的历史波动率更加高效。
    """
    def __init__(self, window=20):
        """
        初始化帕金森波动率因子
        
        参数:
            window: 计算帕金森波动率的时间窗口大小，默认为20个交易日
            
        因子名称: f'parkinson_vol_{window}'
        """
        super().__init__(name=f'parkinson_vol_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算帕金森波动率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'high'（最高价）和'low'（最低价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和帕金森波动率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ln(Hi/Li)^2
        df['ln_hl'] = np.log(df['high'] / df['low']) ** 2
        
        # 计算帕金森波动率
        df[self.name] = df.groupby('ts_code')['ln_hl'].transform(
            lambda x: np.sqrt(x.rolling(window=self.window).mean() / (4 * np.log(2))) * np.sqrt(252)
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class BollingerBandsFactor(Factor):
    """
    布林带因子
    
    定义：基于移动平均线和标准差构建的技术指标。
    计算方法：
        中轨线(Middle Band) = N日移动平均线
        上轨线(Upper Band) = 中轨线 + K × N日标准差
        下轨线(Lower Band) = 中轨线 - K × N日标准差
        其中N通常为20，K通常为2
        
    说明：布林带因子反映了股价的波动区间和趋势强度，当股价触及上轨时可能超买，
         触及下轨时可能超卖，布林带收窄时表示波动性降低。
    """
    def __init__(self, window=20, num_std=2):
        """
        初始化布林带因子
        
        参数:
            window: 计算布林带的时间窗口大小，默认为20个交易日
            num_std: 标准差倍数，默认为2
            
        因子名称: f'bb_{window}_{num_std}'
        """
        super().__init__(name=f'bb_{window}_{num_std}')
        self.window = window
        self.num_std = num_std
    
    def calculate(self, data):
        """
        计算布林带因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和布林带因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算布林带
        rolling_mean = df.groupby('ts_code')['close'].transform(lambda x: x.rolling(window=self.window).mean())
        rolling_std = df.groupby('ts_code')['close'].transform(lambda x: x.rolling(window=self.window).std())
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        
        # 计算布林带宽度因子（带宽）
        bbw = (upper_band - lower_band) / rolling_mean
        df[f'{self.name}_width'] = bbw
        
        # 计算布林带百分比因子（%B）
        bb_percent = (df['close'] - lower_band) / (upper_band - lower_band)
        df[f'{self.name}_percent'] = bb_percent
        
        # 重新组织列
        df = df[['ts_code', 'trade_date', f'{self.name}_width', f'{self.name}_percent']]
        self.data = df
        return df