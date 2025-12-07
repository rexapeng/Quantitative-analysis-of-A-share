import pandas as pd
from .base import Factor


class VolumeFactor(Factor):
    """
    成交量因子
    
    定义：股票在交易日的成交数量，反映市场交易活跃度。
    计算方法：直接取交易日的成交量数据。
    说明：成交量是市场情绪的重要指标，高成交量通常表示市场对该股票的关注度高。
    """
    def __init__(self):
        """
        初始化成交量因子
        
        因子名称: 'volume'
        """
        super().__init__(name='volume')
    
    def calculate(self, data):
        """
        计算成交量因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'volume'（成交量因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.rename(columns={'vol': self.name})
        self.data = df
        return df


class AmountFactor(Factor):
    """
    成交额因子
    
    定义：股票在交易日的成交金额，反映市场资金活跃度。
    计算方法：直接取交易日的成交额数据。
    说明：成交额结合了价格和成交量信息，更全面地反映市场交易强度。
    """
    def __init__(self):
        """
        初始化成交额因子
        
        因子名称: 'amount'
        """
        super().__init__(name='amount')
    
    def calculate(self, data):
        """
        计算成交额因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'amount'（成交额）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和'amount'（成交额因子值）列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'amount']].copy()
        self.data = df
        return df


class VolumeChangeRateFactor(Factor):
    """
    成交量变化率因子
    
    定义：衡量当前成交量相对于过去某一交易日的变化百分比。
    计算方法：(当前成交量 - 过去window个交易日的成交量) / 过去window个交易日的成交量
    说明：该因子大于0表示成交量增加，小于0表示成交量减少，绝对值越大表示成交量变化越剧烈。
    """
    def __init__(self, window=1):
        """
        初始化成交量变化率因子
        
        参数:
            window: 比较的时间窗口大小，默认为1个交易日（即与前一交易日比较）
        
        因子名称: f'vol_change_{window}'
        """
        super().__init__(name=f'vol_change_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量变化率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量变化率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量变化率
        df[self.name] = df.groupby('ts_code')['vol'].pct_change(periods=self.window)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class AmountChangeRateFactor(Factor):
    """
    成交额变化率因子
    
    定义：衡量当前成交额相对于过去某一交易日的变化百分比。
    计算方法：(当前成交额 - 过去window个交易日的成交额) / 过去window个交易日的成交额
    说明：该因子大于0表示成交额增加，小于0表示成交额减少，绝对值越大表示成交额变化越剧烈。
    """
    def __init__(self, window=1):
        """
        初始化成交额变化率因子
        
        参数:
            window: 比较的时间窗口大小，默认为1个交易日（即与前一交易日比较）
        
        因子名称: f'amt_change_{window}'
        """
        super().__init__(name=f'amt_change_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交额变化率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'amount'（成交额）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交额变化率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'amount']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交额变化率
        df[self.name] = df.groupby('ts_code')['amount'].pct_change(periods=self.window)
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeRankFactor(Factor):
    """
    成交量排名因子
    
    定义：衡量当前成交量在过去一段时间窗口内的相对位置，反映成交量的短期表现。
    计算方法：当前成交量在过去window个交易日中的排名百分比
    说明：取值范围为0到1，接近1表示成交量处于近期高位，接近0表示成交量处于近期低位。
    """
    def __init__(self, window=20):
        """
        初始化成交量排名因子
        
        参数:
            window: 计算排名的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_rank_{window}'
        """
        super().__init__(name=f'vol_rank_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量排名因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量排名因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量排名
        df[self.name] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).apply(lambda y: y.rank(pct=True).iloc[-1])
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeMeanFactor(Factor):
    """
    成交量均值因子
    
    定义：计算过去一段时间窗口内的平均成交量，反映成交量的中长期趋势。
    计算方法：过去window个交易日成交量的简单移动平均
    说明：常用的技术分析指标，用于判断成交量的趋势和强度。
    """
    def __init__(self, window=20):
        """
        初始化成交量均值因子
        
        参数:
            window: 计算均值的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_mean_{window}'
        """
        super().__init__(name=f'vol_mean_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量均值因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量均值因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量均值
        df[self.name] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).mean()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeStdFactor(Factor):
    """
    成交量标准差因子
    
    定义：衡量过去一段时间窗口内成交量的波动程度。
    计算方法：过去window个交易日成交量的标准差
    说明：该因子值越大表示成交量波动越剧烈，市场情绪可能越不稳定；值越小表示成交量越稳定。
    """
    def __init__(self, window=20):
        """
        初始化成交量标准差因子
        
        参数:
            window: 计算标准差的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_std_{window}'
        """
        super().__init__(name=f'vol_std_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量标准差因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量标准差因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量标准差
        df[self.name] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).std()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeToMeanFactor(Factor):
    """
    成交量与均值比率因子
    
    定义：衡量当前成交量相对于过去一段时间窗口内平均成交量的比例。
    计算方法：当前成交量 / 过去window个交易日的平均成交量
    说明：该因子大于1表示当前成交量高于近期平均水平，小于1表示当前成交量低于近期平均水平，反映成交量的相对强弱。
    """
    def __init__(self, window=20):
        """
        初始化成交量与均值比率因子
        
        参数:
            window: 计算平均成交量的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_to_mean_{window}'
        """
        super().__init__(name=f'vol_to_mean_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量与均值比率因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量与均值比率因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量均值
        volume_mean = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).mean()
        )
        
        # 计算成交量与均值比率
        df[self.name] = df['vol'] / volume_mean
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeAmplitudeFactor(Factor):
    """
    成交量振幅因子
    
    定义：衡量过去一段时间窗口内成交量的波动幅度。
    计算方法：(过去window个交易日的最大成交量 - 过去window个交易日的最小成交量) / 过去window个交易日的最小成交量
    说明：该因子值越大表示成交量波动越剧烈，市场情绪可能越不稳定；值越小表示成交量越稳定。
    """
    def __init__(self, window=20):
        """
        初始化成交量振幅因子
        
        参数:
            window: 计算振幅的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_amp_{window}'
        """
        super().__init__(name=f'vol_amp_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量振幅因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量振幅因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量振幅
        volume_max = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).max()
        )
        volume_min = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).min()
        )
        
        df[self.name] = (volume_max - volume_min) / volume_min
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VolumeAccumulationFactor(Factor):
    """
    成交量累积因子
    
    定义：计算过去一段时间窗口内的累积成交量，反映资金的流入流出情况。
    计算方法：过去window个交易日的成交量之和
    说明：该因子可以反映市场对该股票的累积关注度，高累积成交量通常表示有较大的资金活动。
    """
    def __init__(self, window=20):
        """
        初始化成交量累积因子
        
        参数:
            window: 计算累积的时间窗口大小，默认为20个交易日
        
        因子名称: f'vol_accum_{window}'
        """
        super().__init__(name=f'vol_accum_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算成交量累积因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'vol'（成交量）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和成交量累积因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'vol']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算成交量累积
        df[self.name] = df.groupby('ts_code')['vol'].transform(
            lambda x: x.rolling(window=self.window).sum()
        )
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df