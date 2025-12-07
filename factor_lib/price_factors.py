import pandas as pd
from .base import Factor


class ClosePriceFactor(Factor):
    """
    收盘价因子
    
    定义：股票在交易日的收盘价。
    计算方法：直接取交易日的收盘价数据。
    说明：收盘价是股票分析中最基本的数据之一，代表了当天交易的最后价格。
    """
    def __init__(self):
        """
        初始化收盘价因子
        
        因子名称: 'close'
        """
        super().__init__(name='close')
    
    def calculate(self, data):
        """
        计算收盘价因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'close'（收盘价因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.rename(columns={'close': self.name})
        self.data = df
        return df


class HighPriceFactor(Factor):
    """
    最高价因子
    
    定义：股票在交易日的最高价。
    计算方法：直接取交易日的最高价数据。
    说明：最高价反映了当天股票交易的最高价格水平。
    """
    def __init__(self):
        """
        初始化最高价因子
        
        因子名称: 'high'
        """
        super().__init__(name='high')
    
    def calculate(self, data):
        """
        计算最高价因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'high'（最高价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'high'（最高价因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high']].copy()
        df = df.rename(columns={'high': self.name})
        self.data = df
        return df


class LowPriceFactor(Factor):
    """
    最低价因子
    
    定义：股票在交易日的最低价。
    计算方法：直接取交易日的最低价数据。
    说明：最低价反映了当天股票交易的最低价格水平。
    """
    def __init__(self):
        """
        初始化最低价因子
        
        因子名称: 'low'
        """
        super().__init__(name='low')
    
    def calculate(self, data):
        """
        计算最低价因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'low'（最低价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'low'（最低价因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'low']].copy()
        df = df.rename(columns={'low': self.name})
        self.data = df
        return df


class OpenPriceFactor(Factor):
    """
    开盘价因子
    
    定义：股票在交易日的开盘价。
    计算方法：直接取交易日的开盘价数据。
    说明：开盘价反映了当天股票交易的起始价格水平。
    """
    def __init__(self):
        """
        初始化开盘价因子
        
        因子名称: 'open'
        """
        super().__init__(name='open')
    
    def calculate(self, data):
        """
        计算开盘价因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'open'（开盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'open'（开盘价因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open']].copy()
        df = df.rename(columns={'open': self.name})
        self.data = df
        return df


class AveragePriceFactor(Factor):
    """
    平均价因子
    
    定义：股票在交易日的平均价格，通常使用OHLC（开盘、最高、最低、收盘）的平均值。
    计算方法：(开盘价 + 最高价 + 最低价 + 收盘价) / 4
    说明：平均价提供了当天交易价格的综合参考水平。
    """
    def __init__(self):
        """
        初始化平均价因子
        
        因子名称: 'avg_price'
        """
        super().__init__(name='avg_price')
    
    def calculate(self, data):
        """
        计算平均价因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'avg_price'（平均价因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df[self.name] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VWAPFactor(Factor):
    """
    成交量加权平均价格因子 (Volume Weighted Average Price)
    
    定义：按成交量加权的平均价格，反映了当天交易的平均成本。
    计算方法：成交金额 / 成交量
    说明：VWAP是机构投资者常用的交易参考指标，用于评估交易执行的质量。
    """
    def __init__(self):
        """
        初始化成交量加权平均价格因子
        
        因子名称: 'vwap'
        """
        super().__init__(name='vwap')
    
    def calculate(self, data):
        """
        计算成交量加权平均价格因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'amount'（成交金额）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'vwap'（成交量加权平均价格因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'amount', 'vol']].copy()
        df[self.name] = df['amount'] / df['vol']
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class CloseToOpenRatioFactor(Factor):
    """
    收盘价与开盘价比率因子
    
    定义：衡量收盘价相对于开盘价的比例，反映当天价格的整体变动情况。
    计算方法：收盘价 / 开盘价
    说明：该因子大于1表示当天价格上涨，小于1表示当天价格下跌，等于1表示价格不变。
    """
    def __init__(self):
        """
        初始化收盘价与开盘价比率因子
        
        因子名称: 'close_open_ratio'
        """
        super().__init__(name='close_open_ratio')
    
    def calculate(self, data):
        """
        计算收盘价与开盘价比率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'close_open_ratio'（收盘价与开盘价比率因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'open']].copy()
        df[self.name] = df['close'] / df['open']
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class PriceRankFactor(Factor):
    """
    价格排名因子
    
    定义：衡量当前价格在过去一段时间窗口内的相对位置，反映价格的短期表现。
    计算方法：当前价格在过去window个交易日中的排名百分比
    说明：取值范围为0到1，接近1表示价格处于近期高位，接近0表示价格处于近期低位。
    """
    def __init__(self, window=20):
        """
        初始化价格排名因子
        
        参数:
            window: 计算排名的时间窗口大小，默认为20个交易日
        
        因子名称: f'price_rank_{window}'
        """
        super().__init__(name=f'price_rank_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算价格排名因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和价格排名因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算价格排名
        df[self.name] = df.groupby('ts_code')['close'].transform(
            lambda x: x.rolling(window=self.window).apply(lambda y: y.rank(pct=True).iloc[-1])
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class PriceDecayFactor(Factor):
    """
    价格衰减因子
    
    定义：使用加权平均的方式计算价格的衰减趋势，赋予更近的价格更高的权重。
    计算方法：最近的window个交易日收盘价的加权平均，权重随时间线性衰减
    说明：权重计算公式为[1/window, 2/window, ..., 1]，反映了价格的近期趋势，更近的价格对结果影响更大。
    """
    def __init__(self, window=20):
        """
        初始化价格衰减因子
        
        参数:
            window: 计算衰减的时间窗口大小，默认为20个交易日
        
        因子名称: f'price_decay_{window}'
        """
        super().__init__(name=f'price_decay_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算价格衰减因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和价格衰减因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算价格衰减
        def calc_decay(x):
            if len(x) < self.window:
                return None
            weights = [i / self.window for i in range(1, self.window + 1)]
            return (x.iloc[-self.window:] * weights).sum() / sum(weights)
        
        df[self.name] = df.groupby('ts_code')['close'].transform(calc_decay)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class OpenToCloseChangeFactor(Factor):
    """
    开盘价与收盘价变化率因子
    
    定义：衡量从收盘到次日开盘的价格变动百分比，反映隔夜价格波动。
    计算方法：(次日开盘价 - 当日收盘价) / 当日收盘价
    说明：该因子大于0表示隔夜价格上涨，小于0表示隔夜价格下跌，绝对值越大表示隔夜价格波动越大。
    """
    def __init__(self):
        """
        初始化开盘价与收盘价变化率因子
        
        因子名称: 'open_close_change'
        """
        super().__init__(name='open_close_change')
    
    def calculate(self, data):
        """
        计算开盘价与收盘价变化率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'open_close_change'（开盘价与收盘价变化率因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算开盘价与收盘价变化率
        df[self.name] = (df['open'] - df['close']) / df['close']
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class PriceMeanFactor(Factor):
    """
    价格均值因子
    
    定义：计算过去一段时间窗口内的平均价格，反映价格的中长期趋势。
    计算方法：过去window个交易日收盘价的简单移动平均
    说明：常用的技术分析指标，如MA20（20日均线）、MA60（60日均线）等，用于判断价格趋势。
    """
    def __init__(self, window=20):
        """
        初始化价格均值因子
        
        参数:
            window: 计算均值的时间窗口大小，默认为20个交易日
        
        因子名称: f'price_mean_{window}'
        """
        super().__init__(name=f'price_mean_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算价格均值因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和价格均值因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算价格均值
        df[self.name] = df.groupby('ts_code')['close'].transform(
            lambda x: x.rolling(window=self.window).mean()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df