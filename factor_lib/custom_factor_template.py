import pandas as pd
import numpy as np
import talib
from .base import Factor


class CustomFactorTemplate(Factor):
    """
    自定义因子模板
    
    定义：提供创建自定义因子的框架，展示如何基于价格和成交量构建复合因子
    计算方法：结合多维度指标的加权平均，示例中包含：
    1. param1日收益率：(当前收盘价 - param1日前收盘价) / param1日前收盘价
    2. param2日成交量移动平均：过去param2个交易日成交量的简单平均值
    3. param2日价格波动率：过去param2个交易日收盘价的标准差
    最终因子值为上述三个指标的平均值
    说明：用户可以根据策略需求修改计算逻辑，自定义复合因子
    """
    def __init__(self, name='custom_factor', param1=5, param2=10):
        """
        初始化自定义因子模板
        
        参数:
            name: 因子名称
            param1: 计算收益率的时间窗口（交易日）
            param2: 计算成交量移动平均和价格波动率的时间窗口（交易日）
        """
        super().__init__(name=name)
        self.param1 = param1
        self.param2 = param2
    
    def calculate(self, data):
        """
        计算自定义因子
        
        参数:
            data: 股票数据，包含以下必要列:
                - ts_code: 股票代码
                - trade_date: 交易日期
                - close: 收盘价
                - high: 最高价
                - low: 最低价
                - vol: 成交量
                - amount: 成交额
        
        返回:
            pandas.DataFrame: 包含ts_code, trade_date和因子值的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 复制数据以避免修改原始数据
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low', 'vol', 'amount']].copy()
        
        # 确保数据按股票代码和交易日期排序
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 示例1: 计算5日收益率
        df['return_5d'] = df.groupby('ts_code')['close'].pct_change(periods=self.param1)
        
        # 示例2: 计算10日成交量移动平均
        df['vol_mean_10d'] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.param2).mean()
        )
        
        # 示例3: 计算价格波动率
        df['price_volatility'] = df.groupby('ts_code')['close'].transform(
            lambda x: x.rolling(window=self.param2).std()
        )
        
        # 示例4: 创建复合因子 - 这里可以根据你的策略自定义计算逻辑
        df[self.name] = (df['return_5d'] + df['vol_mean_10d'] + df['price_volatility']) / 3
        
        # 选择需要返回的列
        df = df[['ts_code', 'trade_date', self.name]]
        
        # 保存计算结果
        self.data = df
        
        return df


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


class CustomVolatilityFactor(Factor):
    """
    自定义波动率因子示例
    
    定义：衡量股票价格在过去window个交易日内的波动程度，反映价格的不确定性
    计算方法: 
    1. 计算每日收益率：(当前收盘价 - 前一日收盘价) / 前一日收盘价
    2. 计算window天收益率的标准差
    说明：波动率越大，价格波动越剧烈，投资风险越高；波动率越小，价格越稳定
    """
    def __init__(self, window=20):
        """
        初始化CustomVolatilityFactor
        
        参数:
            window: 计算波动率的时间窗口（交易日）
        """
        super().__init__(name=f'custom_volatility_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算自定义波动率因子
        
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
        
        # 计算收益率
        df['return'] = df.groupby('ts_code')['close'].pct_change()
        
        # 计算波动率
        df[self.name] = df.groupby('ts_code')['return'].transform(
            lambda x: x.rolling(window=self.window).std()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class CustomVolumeFactor(Factor):
    """
    自定义成交量因子示例
    
    定义：衡量当前成交量相对于过去window个交易日平均成交量的比例，反映市场交投活跃度的变化
    计算方法: 当前成交量 / window天平均成交量
    说明：比值大于1表示当前成交量高于平均水平，市场活跃度较高；比值小于1表示当前成交量低于平均水平，市场活跃度较低
    """
    def __init__(self, window=20):
        """
        初始化CustomVolumeFactor
        
        参数:
            window: 计算平均成交量的时间窗口（交易日）
        """
        super().__init__(name=f'custom_volume_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算自定义成交量因子
        
        参数:
            data: 股票数据，包含以下必要列:
                - ts_code: 股票代码
                - trade_date: 交易日期
                - vol: 成交量
        
        返回:
            pandas.DataFrame: 包含ts_code, trade_date和因子值的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算平均成交量
        df['vol_mean'] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).mean()
        )
        
        # 计算成交量比率
        df[self.name] = df['vol'] / df['vol_mean']
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df