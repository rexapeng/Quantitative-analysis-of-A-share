import pandas as pd
import numpy as np
from .base import Factor





class MACDFactor(Factor):
    """
    MACD因子
    """
    def __init__(self):
        super().__init__(name='macd')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算MACD
        for ts_code, group in df.groupby('ts_code'):
            # 计算12日EMA
            ema12 = group['close'].ewm(span=12, adjust=False).mean()
            # 计算26日EMA
            ema26 = group['close'].ewm(span=26, adjust=False).mean()
            # 计算MACD线
            macd_line = ema12 - ema26
            df.loc[group.index, self.name] = macd_line
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MACD_SignalFactor(Factor):
    """
    MACD信号线因子
    """
    def __init__(self):
        super().__init__(name='macd_signal')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算MACD信号线
        for ts_code, group in df.groupby('ts_code'):
            # 计算12日EMA
            ema12 = group['close'].ewm(span=12, adjust=False).mean()
            # 计算26日EMA
            ema26 = group['close'].ewm(span=26, adjust=False).mean()
            # 计算MACD线
            macd_line = ema12 - ema26
            # 计算信号线（9日EMA）
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            df.loc[group.index, self.name] = signal_line
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df



class RSI14Factor(Factor):
    """
    14日相对强弱指标因子
    """
    def __init__(self):
        super().__init__(name='rsi14')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI
        def rsi(series, window=14):
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # 逐组计算并使用loc赋值，避免索引不匹配问题
        for ts_code, group in df.groupby('ts_code'):
            rsi_values = rsi(group['close'], window=14)
            df.loc[group.index, self.name] = rsi_values
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df



class RSI21Factor(Factor):
    """
    21日相对强弱指标因子
    """
    def __init__(self):
        super().__init__(name='rsi21')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI
        def rsi(series, window=21):
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # 逐组计算并使用loc赋值，避免索引不匹配问题
        for ts_code, group in df.groupby('ts_code'):
            rsi_values = rsi(group['close'], window=21)
            df.loc[group.index, self.name] = rsi_values
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ADXFactor(Factor):
    """
    平均趋向指数因子
    """
    def __init__(self, window=14):
        super().__init__(name=f'adx_{window}')
        self.window = window
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ADX
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算+DM和-DM
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            # 计算+DI、-DI和ADX
            atr = tr.rolling(window=self.window).mean()
            plus_di = 100 * (plus_dm.rolling(window=self.window).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=self.window).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = adx
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ATRFactor(Factor):
    """
    平均真实波幅因子
    """
    def __init__(self, window=14):
        super().__init__(name=f'atr_{window}')
        self.window = window
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ATR
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算ATR
            atr = tr.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = atr
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df





class CCI14Factor(Factor):
    """
    14日顺势指标因子
    """
    def __init__(self, window=14):
        super().__init__(name=f'cci_{window}')
        self.window = window
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算CCI
        for ts_code, group in df.groupby('ts_code'):
            # 计算典型价格
            tp = (group['high'] + group['low'] + group['close']) / 3
            # 计算移动平均典型价格
            tp_ma = tp.rolling(window=self.window).mean()
            # 计算平均偏差
            mean_dev = tp.rolling(window=self.window).apply(lambda x: np.mean(np.abs(x - x.mean())))
            # 计算CCI
            cci = (tp - tp_ma) / (0.015 * mean_dev)
            
            df.loc[group.index, self.name] = cci
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class DMAFactor(Factor):
    """
    平行线差指标因子
    """
    def __init__(self):
        super().__init__(name='dma')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算DMA
        for ts_code, group in df.groupby('ts_code'):
            # 计算10日简单移动平均线
            ma10 = group['close'].rolling(window=10).mean()
            # 计算50日简单移动平均线
            ma50 = group['close'].rolling(window=50).mean()
            # 计算DMA
            dma = ma10 - ma50
            df.loc[group.index, self.name] = dma
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df







class RSI28Factor(Factor):
    """
    28日相对强弱指标因子（长期）
    """
    def __init__(self):
        super().__init__(name='rsi28')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI
        def rsi(series, window=28):
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # 逐组计算并使用loc赋值，避免索引不匹配问题
        for ts_code, group in df.groupby('ts_code'):
            rsi_values = rsi(group['close'], window=28)
            df.loc[group.index, self.name] = rsi_values
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ADX20Factor(Factor):
    """
    20日平均趋向指数因子
    """
    def __init__(self):
        super().__init__(name='adx_20')
        self.window = 20
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ADX
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算+DM和-DM
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            # 计算+DI、-DI和ADX
            atr = tr.rolling(window=self.window).mean()
            plus_di = 100 * (plus_dm.rolling(window=self.window).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=self.window).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = adx
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ADX28Factor(Factor):
    """
    28日平均趋向指数因子
    """
    def __init__(self):
        super().__init__(name='adx_28')
        self.window = 28
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ADX
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算+DM和-DM
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            # 计算+DI、-DI和ADX
            atr = tr.rolling(window=self.window).mean()
            plus_di = 100 * (plus_dm.rolling(window=self.window).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=self.window).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = adx
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ATR7Factor(Factor):
    """
    7日平均真实波幅因子
    """
    def __init__(self):
        super().__init__(name='atr_7')
        self.window = 7
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ATR
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算ATR
            atr = tr.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = atr
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ATR20Factor(Factor):
    """
    20日平均真实波幅因子
    """
    def __init__(self):
        super().__init__(name='atr_20')
        self.window = 20
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算ATR
        for ts_code, group in df.groupby('ts_code'):
            high = group['high']
            low = group['low']
            close = group['close']
            
            # 计算真实波幅（TR）
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # 计算ATR
            atr = tr.rolling(window=self.window).mean()
            
            df.loc[group.index, self.name] = atr
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class CCI7Factor(Factor):
    """
    7日顺势指标因子
    """
    def __init__(self):
        super().__init__(name='cci_7')
        self.window = 7
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算CCI
        for ts_code, group in df.groupby('ts_code'):
            # 计算典型价格
            tp = (group['high'] + group['low'] + group['close']) / 3
            # 计算移动平均典型价格
            tp_ma = tp.rolling(window=self.window).mean()
            # 计算平均偏差
            mean_dev = tp.rolling(window=self.window).apply(lambda x: np.mean(np.abs(x - x.mean())))
            # 计算CCI
            cci = (tp - tp_ma) / (0.015 * mean_dev)
            
            df.loc[group.index, self.name] = cci
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class CCI21Factor(Factor):
    """
    21日顺势指标因子
    """
    def __init__(self):
        super().__init__(name='cci_21')
        self.window = 21
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算CCI
        for ts_code, group in df.groupby('ts_code'):
            # 计算典型价格
            tp = (group['high'] + group['low'] + group['close']) / 3
            # 计算移动平均典型价格
            tp_ma = tp.rolling(window=self.window).mean()
            # 计算平均偏差
            mean_dev = tp.rolling(window=self.window).apply(lambda x: np.mean(np.abs(x - x.mean())))
            # 计算CCI
            cci = (tp - tp_ma) / (0.015 * mean_dev)
            
            df.loc[group.index, self.name] = cci
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df
