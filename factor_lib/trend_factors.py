import pandas as pd
import numpy as np
from .base import Factor

class MA5Factor(Factor):
    """
    5日简单移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ma5')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算5日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=5).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MA10Factor(Factor):
    """
    10日简单移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ma10')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算10日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=10).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MA20Factor(Factor):
    """
    20日简单移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ma20')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算20日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=20).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MA50Factor(Factor):
    """
    50日简单移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ma50')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算50日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=50).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MA100Factor(Factor):
    """
    100日简单移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ma100')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算100日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=100).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA12Factor(Factor):
    """
    12日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema12')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算12日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=12, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA26Factor(Factor):
    """
    26日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema26')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算26日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=26, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

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

class MACD_HistogramFactor(Factor):
    """
    MACD柱状图因子
    """
    def __init__(self):
        super().__init__(name='macd_histogram')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算MACD柱状图
        for ts_code, group in df.groupby('ts_code'):
            # 计算12日EMA
            ema12 = group['close'].ewm(span=12, adjust=False).mean()
            # 计算26日EMA
            ema26 = group['close'].ewm(span=26, adjust=False).mean()
            # 计算MACD线
            macd_line = ema12 - ema26
            # 计算信号线（9日EMA）
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            # 计算柱状图
            histogram = macd_line - signal_line
            df.loc[group.index, self.name] = histogram
        
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

class RSI7Factor(Factor):
    """
    7日相对强弱指标因子
    """
    def __init__(self):
        super().__init__(name='rsi7')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI
        def rsi(series, window=7):
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # 逐组计算并使用loc赋值，避免索引不匹配问题
        for ts_code, group in df.groupby('ts_code'):
            rsi_values = rsi(group['close'], window=7)
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

class BollingerBandFactor(Factor):
    """
    布林带因子（价格与中轨的距离）
    """
    def __init__(self, window=20, std_dev=2):
        super().__init__(name=f'bollinger_band_{window}')
        self.window = window
        self.std_dev = std_dev
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算布林带因子
        for ts_code, group in df.groupby('ts_code'):
            ma = group['close'].rolling(window=self.window).mean()
            std = group['close'].rolling(window=self.window).std()
            # 计算价格与中轨的距离（标准化）
            factor_value = (group['close'] - ma) / std
            df.loc[group.index, self.name] = factor_value
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class ParabolicSARFactor(Factor):
    """
    抛物线转向因子
    """
    def __init__(self):
        super().__init__(name='parabolic_sar')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算抛物线转向指标
        for ts_code, group in df.groupby('ts_code'):
            high = group['high'].values
            low = group['low'].values
            close = group['close'].values
            
            sar = np.zeros_like(close)
            sar[0] = low[0]
            
            # 初始参数
            af = 0.02  # 加速因子初始值
            af_step = 0.02  # 加速因子步长
            af_max = 0.2  # 加速因子最大值
            trend = 1  # 趋势方向：1为上升，-1为下降
            ep = high[0]  # 极值点
            
            for i in range(1, len(close)):
                if trend == 1:
                    # 上升趋势
                    sar[i] = sar[i-1] + af * (ep - sar[i-1])
                    # 调整SAR不超过前一天的最低价
                    sar[i] = min(sar[i], low[i-1])
                    
                    # 检查是否翻转
                    if close[i] < sar[i]:
                        trend = -1
                        sar[i] = ep
                        af = 0.02
                        ep = low[i]
                    else:
                        if high[i] > ep:
                            ep = high[i]
                            af = min(af + af_step, af_max)
                else:
                    # 下降趋势
                    sar[i] = sar[i-1] + af * (ep - sar[i-1])
                    # 调整SAR不低于前一天的最高价
                    sar[i] = max(sar[i], high[i-1])
                    
                    # 检查是否翻转
                    if close[i] > sar[i]:
                        trend = 1
                        sar[i] = ep
                        af = 0.02
                        ep = high[i]
                    else:
                        if low[i] < ep:
                            ep = low[i]
                            af = min(af + af_step, af_max)
            
            # 计算因子值：价格与SAR的比值
            factor_value = close / sar
            df.loc[group.index, self.name] = factor_value
        
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

class EMA5Factor(Factor):
    """
    5日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema5')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算5日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=5, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA20Factor(Factor):
    """
    20日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema20')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算20日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=20, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA50Factor(Factor):
    """
    50日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema50')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算50日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=50, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA100Factor(Factor):
    """
    100日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema100')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算100日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=100, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class EMA200Factor(Factor):
    """
    200日指数移动平均线因子
    """
    def __init__(self):
        super().__init__(name='ema200')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算200日指数移动平均线
        df[self.name] = df.groupby('ts_code')['close'].ewm(span=200, adjust=False).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class SMA60Factor(Factor):
    """
    60日简单移动平均线因子（季线）
    """
    def __init__(self):
        super().__init__(name='sma60')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算60日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=60).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class SMA120Factor(Factor):
    """
    120日简单移动平均线因子（半年线）
    """
    def __init__(self):
        super().__init__(name='sma120')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算120日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=120).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class SMA240Factor(Factor):
    """
    240日简单移动平均线因子（年线）
    """
    def __init__(self):
        super().__init__(name='sma240')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算240日简单移动平均线
        df[self.name] = df.groupby('ts_code')['close'].rolling(window=240).mean().reset_index(level=0, drop=True)
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class MACD_CrossoverFactor(Factor):
    """
    MACD金叉死叉信号因子
    """
    def __init__(self):
        super().__init__(name='macd_crossover')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算MACD金叉死叉信号
        for ts_code, group in df.groupby('ts_code'):
            # 计算12日EMA
            ema12 = group['close'].ewm(span=12, adjust=False).mean()
            # 计算26日EMA
            ema26 = group['close'].ewm(span=26, adjust=False).mean()
            # 计算MACD线
            macd_line = ema12 - ema26
            # 计算信号线（9日EMA）
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            # 生成金叉死叉信号：金叉=1，死叉=-1，否则=0
            crossover = pd.Series(0, index=group.index)
            crossover[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1  # 金叉
            crossover[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1  # 死叉
            
            df.loc[group.index, self.name] = crossover
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df

class RSI3Factor(Factor):
    """
    3日相对强弱指标因子（超短期）
    """
    def __init__(self):
        super().__init__(name='rsi3')
    
    def calculate(self, data):
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算RSI
        def rsi(series, window=3):
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # 逐组计算并使用loc赋值，避免索引不匹配问题
        for ts_code, group in df.groupby('ts_code'):
            rsi_values = rsi(group['close'], window=3)
            df.loc[group.index, self.name] = rsi_values
        
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
