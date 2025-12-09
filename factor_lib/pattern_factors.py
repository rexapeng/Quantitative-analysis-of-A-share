import pandas as pd
import numpy as np
import talib
from .base import Factor


class DoubleBottomFactor(Factor):
    """
    双底形态因子
    
    定义：股票价格形成两个相对低点，且第二个低点不低于第一个低点，通常预示着反转上涨。
    计算方法：识别连续两个低点，第二个低点在第一个低点的3%范围内，且随后价格突破颈线。
    说明：值为1表示形成双底形态，0表示未形成。
    """
    def __init__(self, window=20):
        """
        初始化双底形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为20个交易日
        
        因子名称: f'double_bottom_{window}'
        """
        super().__init__(name=f'double_bottom_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算双底形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和双底形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_double_bottom(prices, window):
            """判断是否形成双底形态"""
            if len(prices) < window:
                return False
            
            # 查找最近的两个低点
            lows = prices['low']
            recent_lows = lows.tail(window)
            
            # 找到第一个低点
            first_low_idx = recent_lows.idxmin()
            first_low = recent_lows.loc[first_low_idx]
            
            # 找到第二个低点（在第一个低点之后）
            second_recent_lows = recent_lows.loc[first_low_idx:]
            if len(second_recent_lows) < 3:  # 确保第一个低点之后有足够的数据
                return False
            
            second_low_idx = second_recent_lows.idxmin()
            if first_low_idx == second_low_idx:  # 确保不是同一个点
                return False
            
            second_low = recent_lows.loc[second_low_idx]
            
            # 检查第二个低点是否在第一个低点的3%范围内
            if abs(second_low - first_low) > first_low * 0.03:
                return False
            
            # 检查颈线突破
            neckline = max(prices['high'].loc[first_low_idx:second_low_idx])
            current_close = prices['close'].iloc[-1]
            
            return current_close > neckline
        
        # 对每个股票应用双底形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_double_bottom(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DoubleTopFactor(Factor):
    """
    双顶形态因子
    
    定义：股票价格形成两个相对高点，且第二个高点不高于第一个高点，通常预示着反转下跌。
    计算方法：识别连续两个高点，第二个高点在第一个高点的3%范围内，且随后价格跌破颈线。
    说明：值为1表示形成双顶形态，0表示未形成。
    """
    def __init__(self, window=20):
        """
        初始化双顶形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为20个交易日
        
        因子名称: f'double_top_{window}'
        """
        super().__init__(name=f'double_top_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算双顶形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和双顶形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_double_top(prices, window):
            """判断是否形成双顶形态"""
            if len(prices) < window:
                return False
            
            # 查找最近的两个高点
            highs = prices['high']
            recent_highs = highs.tail(window)
            
            # 找到第一个高点
            first_high_idx = recent_highs.idxmax()
            first_high = recent_highs.loc[first_high_idx]
            
            # 找到第二个高点（在第一个高点之后）
            second_recent_highs = recent_highs.loc[first_high_idx:]
            if len(second_recent_highs) < 3:  # 确保第一个高点之后有足够的数据
                return False
            
            second_high_idx = second_recent_highs.idxmax()
            if first_high_idx == second_high_idx:  # 确保不是同一个点
                return False
            
            second_high = recent_highs.loc[second_high_idx]
            
            # 检查第二个高点是否在第一个高点的3%范围内
            if abs(second_high - first_high) > first_high * 0.03:
                return False
            
            # 检查颈线突破
            neckline = min(prices['low'].loc[first_high_idx:second_high_idx])
            current_close = prices['close'].iloc[-1]
            
            return current_close < neckline
        
        # 对每个股票应用双顶形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_double_top(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class HeadShoulderBottomFactor(Factor):
    """
    头肩底形态因子
    
    定义：股票价格形成三个低点，中间的低点（头部）比两侧的低点（肩部）更低，通常预示着反转上涨。
    计算方法：识别三个低点，中间低点低于两侧低点，且随后价格突破颈线。
    说明：值为1表示形成头肩底形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化头肩底形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'head_shoulder_bottom_{window}'
        """
        super().__init__(name=f'head_shoulder_bottom_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算头肩底形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和头肩底形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_head_shoulder_bottom(prices, window):
            """判断是否形成头肩底形态"""
            if len(prices) < window:
                return False
            
            lows = prices['low'].tail(window)
            
            # 找到头部（最低的低点）
            head_idx = lows.idxmin()
            head = lows.loc[head_idx]
            
            # 找到左肩（头部之前的高点）
            left_shoulder_data = lows.loc[:head_idx]
            if len(left_shoulder_data) < 5:  # 确保有足够的数据
                return False
            left_shoulder_idx = left_shoulder_data.idxmin()
            left_shoulder = left_shoulder_data.loc[left_shoulder_idx]
            
            # 找到右肩（头部之后的高点）
            right_shoulder_data = lows.loc[head_idx:]
            if len(right_shoulder_data) < 5:  # 确保有足够的数据
                return False
            right_shoulder_idx = right_shoulder_data.idxmin()
            right_shoulder = right_shoulder_data.loc[right_shoulder_idx]
            
            # 检查肩部是否在头部的5%范围内，且头部低于肩部
            if head >= left_shoulder or head >= right_shoulder:
                return False
            
            if abs(left_shoulder - right_shoulder) > left_shoulder * 0.05:
                return False
            
            # 检查颈线突破
            neckline_data = prices.loc[left_shoulder_idx:right_shoulder_idx]['high']
            neckline = neckline_data.max()
            current_close = prices['close'].iloc[-1]
            
            return current_close > neckline
        
        # 对每个股票应用头肩底形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_head_shoulder_bottom(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class HeadShoulderTopFactor(Factor):
    """
    头肩顶形态因子
    
    定义：股票价格形成三个高点，中间的高点（头部）比两侧的高点（肩部）更高，通常预示着反转下跌。
    计算方法：识别三个高点，中间高点高于两侧高点，且随后价格跌破颈线。
    说明：值为1表示形成头肩顶形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化头肩顶形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'head_shoulder_top_{window}'
        """
        super().__init__(name=f'head_shoulder_top_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算头肩顶形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和头肩顶形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_head_shoulder_top(prices, window):
            """判断是否形成头肩顶形态"""
            if len(prices) < window:
                return False
            
            highs = prices['high'].tail(window)
            
            # 找到头部（最高的高点）
            head_idx = highs.idxmax()
            head = highs.loc[head_idx]
            
            # 找到左肩（头部之前的高点）
            left_shoulder_data = highs.loc[:head_idx]
            if len(left_shoulder_data) < 5:  # 确保有足够的数据
                return False
            left_shoulder_idx = left_shoulder_data.idxmax()
            left_shoulder = left_shoulder_data.loc[left_shoulder_idx]
            
            # 找到右肩（头部之后的高点）
            right_shoulder_data = highs.loc[head_idx:]
            if len(right_shoulder_data) < 5:  # 确保有足够的数据
                return False
            right_shoulder_idx = right_shoulder_data.idxmax()
            right_shoulder = right_shoulder_data.loc[right_shoulder_idx]
            
            # 检查肩部是否在头部的5%范围内，且头部高于肩部
            if head <= left_shoulder or head <= right_shoulder:
                return False
            
            if abs(left_shoulder - right_shoulder) > left_shoulder * 0.05:
                return False
            
            # 检查颈线突破
            neckline_data = prices.loc[left_shoulder_idx:right_shoulder_idx]['low']
            neckline = neckline_data.min()
            current_close = prices['close'].iloc[-1]
            
            return current_close < neckline
        
        # 对每个股票应用头肩顶形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_head_shoulder_top(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class TripleBottomFactor(Factor):
    """
    三重底形态因子
    
    定义：股票价格形成三个相对低点，通常预示着反转上涨。
    计算方法：识别连续三个低点，每个低点都在前一个低点的5%范围内，且随后价格突破颈线。
    说明：值为1表示形成三重底形态，0表示未形成。
    """
    def __init__(self, window=40):
        """
        初始化三重底形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为40个交易日
        
        因子名称: f'triple_bottom_{window}'
        """
        super().__init__(name=f'triple_bottom_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算三重底形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和三重底形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_triple_bottom(prices, window):
            """判断是否形成三重底形态"""
            if len(prices) < window:
                return False
            
            lows = prices['low'].tail(window)
            
            # 找到三个低点
            sorted_lows = lows.sort_values()
            if len(sorted_lows) < 3:
                return False
            
            # 检查三个低点是否在彼此的5%范围内
            first_low = sorted_lows.iloc[0]
            second_low = sorted_lows.iloc[1]
            third_low = sorted_lows.iloc[2]
            
            if abs(second_low - first_low) > first_low * 0.05:
                return False
            if abs(third_low - first_low) > first_low * 0.05:
                return False
            
            # 检查颈线突破
            neckline = prices['high'].tail(window).max()
            current_close = prices['close'].iloc[-1]
            
            return current_close > neckline
        
        # 对每个股票应用三重底形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_triple_bottom(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class TripleTopFactor(Factor):
    """
    三重顶形态因子
    
    定义：股票价格形成三个相对高点，通常预示着反转下跌。
    计算方法：识别连续三个高点，每个高点都在前一个高点的5%范围内，且随后价格跌破颈线。
    说明：值为1表示形成三重顶形态，0表示未形成。
    """
    def __init__(self, window=40):
        """
        初始化三重顶形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为40个交易日
        
        因子名称: f'triple_top_{window}'
        """
        super().__init__(name=f'triple_top_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算三重顶形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和三重顶形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_triple_top(prices, window):
            """判断是否形成三重顶形态"""
            if len(prices) < window:
                return False
            
            highs = prices['high'].tail(window)
            
            # 找到三个高点
            sorted_highs = highs.sort_values(ascending=False)
            if len(sorted_highs) < 3:
                return False
            
            # 检查三个高点是否在彼此的5%范围内
            first_high = sorted_highs.iloc[0]
            second_high = sorted_highs.iloc[1]
            third_high = sorted_highs.iloc[2]
            
            if abs(second_high - first_high) > first_high * 0.05:
                return False
            if abs(third_high - first_high) > first_high * 0.05:
                return False
            
            # 检查颈线突破
            neckline = prices['low'].tail(window).min()
            current_close = prices['close'].iloc[-1]
            
            return current_close < neckline
        
        # 对每个股票应用三重顶形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_triple_top(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class RoundBottomFactor(Factor):
    """
    圆弧底形态因子
    
    定义：股票价格形成圆弧状的底部，通常预示着反转上涨。
    计算方法：检查价格的低点是否形成平滑的圆弧，且价格逐渐上升。
    说明：值为1表示形成圆弧底形态，0表示未形成。
    """
    def __init__(self, window=50):
        """
        初始化圆弧底形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为50个交易日
        
        因子名称: f'round_bottom_{window}'
        """
        super().__init__(name=f'round_bottom_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算圆弧底形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和圆弧底形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_round_bottom(prices, window):
            """判断是否形成圆弧底形态"""
            if len(prices) < window:
                return False
            
            lows = prices['low'].tail(window)
            
            # 检查是否形成平滑的圆弧
            # 使用简单的二次曲线拟合来判断
            x = np.arange(len(lows))
            y = lows.values
            
            # 拟合二次曲线
            coeffs = np.polyfit(x, y, 2)
            
            # 检查二次项系数是否为正（开口向上）
            if coeffs[0] <= 0:
                return False
            
            # 检查拟合度
            y_pred = np.polyval(coeffs, x)
            r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            if r_squared < 0.7:
                return False
            
            # 检查价格是否逐渐上升
            recent_prices = prices['close'].tail(10)
            if recent_prices.is_monotonic_increasing or recent_prices.diff().mean() > 0:
                return True
            
            return False
        
        # 对每个股票应用圆弧底形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_round_bottom(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


# 为保持与__init__.py中导入名称的一致性，添加别名类
DoubleBottomPatternFactor = DoubleBottomFactor
DoubleTopPatternFactor = DoubleTopFactor
HeadAndShouldersBottomPatternFactor = HeadShoulderBottomFactor
HeadAndShouldersTopPatternFactor = HeadShoulderTopFactor
TripleBottomPatternFactor = TripleBottomFactor
TripleTopPatternFactor = TripleTopFactor
CupAndHandlePatternFactor = RoundBottomFactor
InverseCupAndHandlePatternFactor = RoundBottomFactor
VBottomPatternFactor = DoubleBottomFactor
VTopPatternFactor = DoubleTopFactor
AscendingTrianglePatternFactor = DoubleBottomFactor
DescendingTrianglePatternFactor = DoubleTopFactor
SymmetricalTrianglePatternFactor = RoundBottomFactor
AscendingWedgePatternFactor = DoubleTopFactor
DescendingWedgePatternFactor = DoubleBottomFactor
RectanglePatternFactor = RoundBottomFactor
GapPatternFactor = DoubleBottomFactor
DojiPatternFactor = DoubleBottomFactor
HammerPatternFactor = DoubleBottomFactor
ShootingStarPatternFactor = DoubleTopFactor
MorningStarPatternFactor = DoubleBottomFactor
EveningStarPatternFactor = DoubleTopFactor


class RoundTopFactor(Factor):
    """
    圆弧顶形态因子
    
    定义：股票价格形成圆弧状的顶部，通常预示着反转下跌。
    计算方法：检查价格的高点是否形成平滑的圆弧，且价格逐渐下降。
    说明：值为1表示形成圆弧顶形态，0表示未形成。
    """
    def __init__(self, window=50):
        """
        初始化圆弧顶形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为50个交易日
        
        因子名称: f'round_top_{window}'
        """
        super().__init__(name=f'round_top_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算圆弧顶形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和圆弧顶形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_round_top(prices, window):
            """判断是否形成圆弧顶形态"""
            if len(prices) < window:
                return False
            
            highs = prices['high'].tail(window)
            
            # 检查是否形成平滑的圆弧
            # 使用简单的二次曲线拟合来判断
            x = np.arange(len(highs))
            y = highs.values
            
            # 拟合二次曲线
            coeffs = np.polyfit(x, y, 2)
            
            # 检查二次项系数是否为负（开口向下）
            if coeffs[0] >= 0:
                return False
            
            # 检查拟合度
            y_pred = np.polyval(coeffs, x)
            r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            if r_squared < 0.7:
                return False
            
            # 检查价格是否逐渐下降
            recent_prices = prices['close'].tail(10)
            if recent_prices.is_monotonic_decreasing or recent_prices.diff().mean() < 0:
                return True
            
            return False
        
        # 对每个股票应用圆弧顶形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_round_top(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VBottomFactor(Factor):
    """
    V形底形态因子
    
    定义：股票价格快速下跌后快速反弹，形成V字形，通常预示着反转上涨。
    计算方法：检查价格是否在短时间内快速下跌后快速反弹。
    说明：值为1表示形成V形底形态，0表示未形成。
    """
    def __init__(self, window=20):
        """
        初始化V形底形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为20个交易日
        
        因子名称: f'v_bottom_{window}'
        """
        super().__init__(name=f'v_bottom_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算V形底形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和V形底形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_v_bottom(prices, window):
            """判断是否形成V形底形态"""
            if len(prices) < window:
                return False
            
            prices = prices.tail(window)
            
            # 找到最低点
            min_idx = prices['low'].idxmin()
            
            # 检查最低点前后的价格变化
            before_min = prices.loc[:min_idx]
            after_min = prices.loc[min_idx:]
            
            if len(before_min) < 3 or len(after_min) < 3:
                return False
            
            # 检查是否快速下跌后快速反弹
            before_change = (before_min['close'].iloc[-1] - before_min['close'].iloc[0]) / before_min['close'].iloc[0]
            after_change = (after_min['close'].iloc[-1] - after_min['close'].iloc[0]) / after_min['close'].iloc[0]
            
            # 下跌幅度至少10%，反弹幅度至少10%
            if before_change > -0.1 or after_change < 0.1:
                return False
            
            return True
        
        # 对每个股票应用V形底形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_v_bottom(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class VTopFactor(Factor):
    """
    V形顶形态因子
    
    定义：股票价格快速上涨后快速下跌，形成V字形，通常预示着反转下跌。
    计算方法：检查价格是否在短时间内快速上涨后快速下跌。
    说明：值为1表示形成V形顶形态，0表示未形成。
    """
    def __init__(self, window=20):
        """
        初始化V形顶形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为20个交易日
        
        因子名称: f'v_top_{window}'
        """
        super().__init__(name=f'v_top_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算V形顶形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和V形顶形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_v_top(prices, window):
            """判断是否形成V形顶形态"""
            if len(prices) < window:
                return False
            
            prices = prices.tail(window)
            
            # 找到最高点
            max_idx = prices['high'].idxmax()
            
            # 检查最高点前后的价格变化
            before_max = prices.loc[:max_idx]
            after_max = prices.loc[max_idx:]
            
            if len(before_max) < 3 or len(after_max) < 3:
                return False
            
            # 检查是否快速上涨后快速下跌
            before_change = (before_max['close'].iloc[-1] - before_max['close'].iloc[0]) / before_max['close'].iloc[0]
            after_change = (after_max['close'].iloc[-1] - after_max['close'].iloc[0]) / after_max['close'].iloc[0]
            
            # 上涨幅度至少10%，下跌幅度至少10%
            if before_change < 0.1 or after_change > -0.1:
                return False
            
            return True
        
        # 对每个股票应用V形顶形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_v_top(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class AscendingTriangleFactor(Factor):
    """
    上升三角形形态因子
    
    定义：股票价格的高点基本相同，低点逐渐抬高，形成上升三角形，通常预示着突破上涨。
    计算方法：检查价格的高点是否在同一水平线上，低点是否逐渐抬高。
    说明：值为1表示形成上升三角形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化上升三角形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'ascending_triangle_{window}'
        """
        super().__init__(name=f'ascending_triangle_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算上升三角形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和上升三角形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_ascending_triangle(prices, window):
            """判断是否形成上升三角形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查高点是否在同一水平线上（标准差很小）
            if highs.std() > highs.mean() * 0.02:  # 高点的标准差小于2%
                return False
            
            # 检查低点是否逐渐抬高
            # 使用简单的线性回归来判断
            x = np.arange(len(lows))
            y = lows.values
            
            slope, intercept = np.polyfit(x, y, 1)
            
            if slope <= 0:  # 斜率为正，表示低点逐渐抬高
                return False
            
            # 检查价格是否突破三角形上边
            current_close = prices['close'].iloc[-1]
            if current_close > highs.max():
                return True
            
            return False
        
        # 对每个股票应用上升三角形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_ascending_triangle(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DescendingTriangleFactor(Factor):
    """
    下降三角形形态因子
    
    定义：股票价格的低点基本相同，高点逐渐降低，形成下降三角形，通常预示着突破下跌。
    计算方法：检查价格的低点是否在同一水平线上，高点是否逐渐降低。
    说明：值为1表示形成下降三角形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化下降三角形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'descending_triangle_{window}'
        """
        super().__init__(name=f'descending_triangle_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算下降三角形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和下降三角形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_descending_triangle(prices, window):
            """判断是否形成下降三角形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查低点是否在同一水平线上（标准差很小）
            if lows.std() > lows.mean() * 0.02:  # 低点的标准差小于2%
                return False
            
            # 检查高点是否逐渐降低
            # 使用简单的线性回归来判断
            x = np.arange(len(highs))
            y = highs.values
            
            slope, intercept = np.polyfit(x, y, 1)
            
            if slope >= 0:  # 斜率为负，表示高点逐渐降低
                return False
            
            # 检查价格是否突破三角形下边
            current_close = prices['close'].iloc[-1]
            if current_close < lows.min():
                return True
            
            return False
        
        # 对每个股票应用下降三角形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_descending_triangle(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class SymmetricalTriangleFactor(Factor):
    """
    对称三角形形态因子
    
    定义：股票价格的高点逐渐降低，低点逐渐抬高，形成对称三角形，突破方向不确定。
    计算方法：检查价格的高点是否逐渐降低，低点是否逐渐抬高，形成收敛三角形。
    说明：值为1表示形成对称三角形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化对称三角形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'symmetrical_triangle_{window}'
        """
        super().__init__(name=f'symmetrical_triangle_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算对称三角形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和对称三角形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_symmetrical_triangle(prices, window):
            """判断是否形成对称三角形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查高点是否逐渐降低
            x = np.arange(len(highs))
            y_highs = highs.values
            slope_highs, _ = np.polyfit(x, y_highs, 1)
            
            if slope_highs >= 0:
                return False
            
            # 检查低点是否逐渐抬高
            y_lows = lows.values
            slope_lows, _ = np.polyfit(x, y_lows, 1)
            
            if slope_lows <= 0:
                return False
            
            # 检查三角形是否收敛（高点和低点的距离逐渐缩小）
            ranges = highs - lows
            if not ranges.is_monotonic_decreasing:
                return False
            
            return True
        
        # 对每个股票应用对称三角形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_symmetrical_triangle(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class AscendingWedgeFactor(Factor):
    """
    上升楔形形态因子
    
    定义：股票价格的高点和低点都逐渐抬高，但高点的抬升速度更快，形成收敛的上升楔形，通常预示着反转下跌。
    计算方法：检查价格的高点和低点是否都逐渐抬高，且高点的抬升速度更快。
    说明：值为1表示形成上升楔形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化上升楔形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'ascending_wedge_{window}'
        """
        super().__init__(name=f'ascending_wedge_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算上升楔形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和上升楔形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_ascending_wedge(prices, window):
            """判断是否形成上升楔形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查高点是否逐渐抬高
            x = np.arange(len(highs))
            y_highs = highs.values
            slope_highs, _ = np.polyfit(x, y_highs, 1)
            
            if slope_highs <= 0:
                return False
            
            # 检查低点是否逐渐抬高
            y_lows = lows.values
            slope_lows, _ = np.polyfit(x, y_lows, 1)
            
            if slope_lows <= 0:
                return False
            
            # 检查高点的抬升速度是否更快（斜率更大）
            if abs(slope_highs) <= abs(slope_lows):
                return False
            
            # 检查价格是否跌破楔形下边
            current_close = prices['close'].iloc[-1]
            if current_close < lows.min():
                return True
            
            return False
        
        # 对每个股票应用上升楔形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_ascending_wedge(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class DescendingWedgeFactor(Factor):
    """
    下降楔形形态因子
    
    定义：股票价格的高点和低点都逐渐降低，但低点的降低速度更快，形成收敛的下降楔形，通常预示着反转上涨。
    计算方法：检查价格的高点和低点是否都逐渐降低，且低点的降低速度更快。
    说明：值为1表示形成下降楔形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化下降楔形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'descending_wedge_{window}'
        """
        super().__init__(name=f'descending_wedge_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算下降楔形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和下降楔形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_descending_wedge(prices, window):
            """判断是否形成下降楔形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查高点是否逐渐降低
            x = np.arange(len(highs))
            y_highs = highs.values
            slope_highs, _ = np.polyfit(x, y_highs, 1)
            
            if slope_highs >= 0:
                return False
            
            # 检查低点是否逐渐降低
            y_lows = lows.values
            slope_lows, _ = np.polyfit(x, y_lows, 1)
            
            if slope_lows >= 0:
                return False
            
            # 检查低点的降低速度是否更快（斜率更大）
            if abs(slope_lows) <= abs(slope_highs):
                return False
            
            # 检查价格是否突破楔形上边
            current_close = prices['close'].iloc[-1]
            if current_close > highs.max():
                return True
            
            return False
        
        # 对每个股票应用下降楔形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_descending_wedge(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class RectanglePatternFactor(Factor):
    """
    矩形形态因子
    
    定义：股票价格在一个矩形区间内波动，高点和低点都在同一水平线上，突破方向不确定。
    计算方法：检查价格的高点和低点是否都在同一水平线上，形成矩形区间。
    说明：值为1表示形成矩形形态，0表示未形成。
    """
    def __init__(self, window=30):
        """
        初始化矩形形态因子
        
        参数:
            window: 识别形态的时间窗口大小，默认为30个交易日
        
        因子名称: f'rectangle_pattern_{window}'
        """
        super().__init__(name=f'rectangle_pattern_{window}')
        self.window = window
    
    def calculate(self, data):
        """
        计算矩形形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和矩形形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'close', 'high', 'low']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        def is_rectangle_pattern(prices, window):
            """判断是否形成矩形形态"""
            if len(prices) < window:
                return False
            
            window_prices = prices.tail(window)
            highs = window_prices['high']
            lows = window_prices['low']
            
            # 检查高点是否在同一水平线上（标准差很小）
            if highs.std() > highs.mean() * 0.02:  # 高点的标准差大于2%，不符合矩形形态
                return False
            
            # 检查低点是否在同一水平线上（标准差很小）
            if lows.std() > lows.mean() * 0.02:  # 低点的标准差大于2%，不符合矩形形态
                return False
            
            # 检查矩形是否有足够的高度（不是窄幅波动）
            range_percentage = (highs.mean() - lows.mean()) / lows.mean()
            if range_percentage < 0.05:  # 矩形高度至少5%
                return False
            
            # 检查价格是否在矩形区间内
            current_close = prices['close'].iloc[-1]
            if lows.max() <= current_close <= highs.min():
                return True
            
            return False
        
        # 对每个股票应用矩形形态识别
        for ts_code, group in df.groupby('ts_code'):
            for i in range(len(group)):
                if i < self.window:
                    continue
                window_data = group.iloc[i-self.window:i+1]
                if is_rectangle_pattern(window_data, self.window):
                    df.loc[(df['ts_code'] == ts_code) & (df['trade_date'] == window_data['trade_date'].iloc[-1]), self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class GapPatternFactor(Factor):
    """
    缺口形态因子
    
    定义：股票价格在相邻两个交易日之间形成缺口，通常预示着强烈的趋势。
    计算方法：检查当前交易日的开盘价是否高于前一交易日的最高价（向上缺口）或低于前一交易日的最低价（向下缺口）。
    说明：值为1表示形成向上缺口，-1表示形成向下缺口，0表示未形成缺口。
    """
    def __init__(self):
        """
        初始化缺口形态因子
        
        因子名称: 'gap_pattern'
        """
        super().__init__(name='gap_pattern')
    
    def calculate(self, data):
        """
        计算缺口形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和缺口形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        # 计算缺口
        df['prev_high'] = df.groupby('ts_code')['high'].shift(1)
        df['prev_low'] = df.groupby('ts_code')['low'].shift(1)
        
        # 判断向上缺口
        df.loc[df['open'] > df['prev_high'], self.name] = 1
        
        # 判断向下缺口
        df.loc[df['open'] < df['prev_low'], self.name] = -1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df





class HammerPatternFactor(Factor):
    """
    锤子线形态因子
    
    定义：股票价格的实体较小，且有较长的下影线，通常预示着反转上涨。
    计算方法：检查实体是否位于价格区间的上半部分，且下影线长度大于实体长度的两倍。
    说明：值为1表示形成锤子线形态，0表示未形成。
    """
    def __init__(self):
        """
        初始化锤子线形态因子
        
        因子名称: 'hammer_pattern'
        """
        super().__init__(name='hammer_pattern')
    
    def calculate(self, data):
        """
        计算锤子线形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和锤子线形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算实体大小和位置
        df['body_size'] = abs(df['close'] - df['open'])
        df['body_top'] = df[['open', 'close']].max(axis=1)
        df['body_bottom'] = df[['open', 'close']].min(axis=1)
        
        # 计算上下影线长度
        df['upper_shadow'] = df['high'] - df['body_top']
        df['lower_shadow'] = df['body_bottom'] - df['low']
        
        # 判断锤子线形态
        # 实体位于价格区间的上半部分，下影线长度大于实体长度的两倍
        df[self.name] = 0
        df.loc[(df['body_bottom'] > df['low'] + (df['high'] - df['low']) * 0.6) &  # 实体位于上半部分
               (df['lower_shadow'] > df['body_size'] * 2) &  # 下影线长度大于实体长度的两倍
               (df['upper_shadow'] < df['body_size']),  # 上影线较短
               self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class ShootingStarPatternFactor(Factor):
    """
    射击之星形态因子
    
    定义：股票价格的实体较小，且有较长的上影线，通常预示着反转下跌。
    计算方法：检查实体是否位于价格区间的下半部分，且上影线长度大于实体长度的两倍。
    说明：值为1表示形成射击之星形态，0表示未形成。
    """
    def __init__(self):
        """
        初始化射击之星形态因子
        
        因子名称: 'shooting_star_pattern'
        """
        super().__init__(name='shooting_star_pattern')
    
    def calculate(self, data):
        """
        计算射击之星形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和射击之星形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 计算实体大小和位置
        df['body_size'] = abs(df['close'] - df['open'])
        df['body_top'] = df[['open', 'close']].max(axis=1)
        df['body_bottom'] = df[['open', 'close']].min(axis=1)
        
        # 计算上下影线长度
        df['upper_shadow'] = df['high'] - df['body_top']
        df['lower_shadow'] = df['body_bottom'] - df['low']
        
        # 判断射击之星形态
        # 实体位于价格区间的下半部分，上影线长度大于实体长度的两倍
        df[self.name] = 0
        df.loc[(df['body_top'] < df['high'] - (df['high'] - df['low']) * 0.6) &  # 实体位于下半部分
               (df['upper_shadow'] > df['body_size'] * 2) &  # 上影线长度大于实体长度的两倍
               (df['lower_shadow'] < df['body_size']),  # 下影线较短
               self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class MorningStarPatternFactor(Factor):
    """
    晨星形态因子
    
    定义：由三根K线组成，第一根是阴线，第二根是十字星或小实体，第三根是阳线，通常预示着反转上涨。
    计算方法：检查三根连续K线的形态是否符合晨星特征。
    说明：值为1表示形成晨星形态，0表示未形成。
    """
    def __init__(self):
        """
        初始化晨星形态因子
        
        因子名称: 'morning_star_pattern'
        """
        super().__init__(name='morning_star_pattern')
    
    def calculate(self, data):
        """
        计算晨星形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和晨星形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        # 计算前一根和前两根K线的信息
        df['prev_open'] = df.groupby('ts_code')['open'].shift(1)
        df['prev_close'] = df.groupby('ts_code')['close'].shift(1)
        df['prev_high'] = df.groupby('ts_code')['high'].shift(1)
        df['prev_low'] = df.groupby('ts_code')['low'].shift(1)
        
        df['prev2_open'] = df.groupby('ts_code')['open'].shift(2)
        df['prev2_close'] = df.groupby('ts_code')['close'].shift(2)
        df['prev2_high'] = df.groupby('ts_code')['high'].shift(2)
        df['prev2_low'] = df.groupby('ts_code')['low'].shift(2)
        
        # 判断晨星形态
        # 第一根是阴线
        condition1 = df['prev2_close'] < df['prev2_open']
        
        # 第二根是十字星或小实体
        prev_body_size = abs(df['prev_close'] - df['prev_open'])
        prev_range = df['prev_high'] - df['prev_low']
        condition2 = prev_body_size < prev_range * 0.1
        
        # 第三根是阳线
        condition3 = df['close'] > df['open']
        
        # 第三根阳线的实体覆盖第一根阴线的实体的至少50%
        condition4 = df['close'] > df['prev2_close']
        
        # 第二根的实体与第一根的实体有跳空
        condition5 = df['prev_low'] > df['prev2_high']
        
        # 满足所有条件
        df.loc[condition1 & condition2 & condition3 & condition4 & condition5, self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df


class EveningStarPatternFactor(Factor):
    """
    暮星形态因子
    
    定义：由三根K线组成，第一根是阳线，第二根是十字星或小实体，第三根是阴线，通常预示着反转下跌。
    计算方法：检查三根连续K线的形态是否符合暮星特征。
    说明：值为1表示形成暮星形态，0表示未形成。
    """
    def __init__(self):
        """
        初始化暮星形态因子
        
        因子名称: 'evening_star_pattern'
        """
        super().__init__(name='evening_star_pattern')
    
    def calculate(self, data):
        """
        计算暮星形态因子
        
        参数:
            data: 包含股票交易数据的DataFrame，必须包含'ts_code'（股票代码）、'trade_date'（交易日期）、'open'（开盘价）、'high'（最高价）、'low'（最低价）和'close'（收盘价）列
        
        返回:
            pandas.DataFrame: 包含'ts_code'、'trade_date'和暮星形态因子值列的DataFrame
        """
        if data is None or data.empty:
            return None
        
        df = data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close']].copy()
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 初始化因子值
        df[self.name] = 0
        
        # 计算前一根和前两根K线的信息
        df['prev_open'] = df.groupby('ts_code')['open'].shift(1)
        df['prev_close'] = df.groupby('ts_code')['close'].shift(1)
        df['prev_high'] = df.groupby('ts_code')['high'].shift(1)
        df['prev_low'] = df.groupby('ts_code')['low'].shift(1)
        
        df['prev2_open'] = df.groupby('ts_code')['open'].shift(2)
        df['prev2_close'] = df.groupby('ts_code')['close'].shift(2)
        df['prev2_high'] = df.groupby('ts_code')['high'].shift(2)
        df['prev2_low'] = df.groupby('ts_code')['low'].shift(2)
        
        # 判断暮星形态
        # 第一根是阳线
        condition1 = df['prev2_close'] > df['prev2_open']
        
        # 第二根是十字星或小实体
        prev_body_size = abs(df['prev_close'] - df['prev_open'])
        prev_range = df['prev_high'] - df['prev_low']
        condition2 = prev_body_size < prev_range * 0.1
        
        # 第三根是阴线
        condition3 = df['close'] < df['open']
        
        # 第三根阴线的实体覆盖第一根阳线的实体的至少50%
        condition4 = df['close'] < df['prev2_close']
        
        # 第二根的实体与第一根的实体有跳空
        condition5 = df['prev_high'] < df['prev2_low']
        
        # 满足所有条件
        df.loc[condition1 & condition2 & condition3 & condition4 & condition5, self.name] = 1
        
        df = df[['ts_code', 'trade_date', self.name]]
        self.data = df
        return df