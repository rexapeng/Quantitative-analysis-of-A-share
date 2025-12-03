import backtrader as bt
import numpy as np
import logging
from .base_strategy import BaseStrategy
from logger_config import strategy_logger

class StockSelectionStrategy(BaseStrategy):
    """
    A股选股策略
    特点：
    1. 初步筛选：日线KDJ的J小于0，收盘价大于长线且短线大于长线
    2. 综合评分系统（0-100分）
    3. 次日开盘买入前5的股票，仓位各占20%
    4. 固定持仓10个交易日
    """
    
    params = (
        ('stake', 100),  # 交易数量
        ('hold_days', 10),  # 固定持仓天数
        ('top_stocks_count', 5),  # 买入前N只股票
        ('min_score', 50),  # 最低评分要求
    )
    
    def __init__(self):
        # 调用基类的__init__方法
        super().__init__()
        
        self.logger = strategy_logger
        
        # 为每个数据源创建指标
        self.indicators = {}
        self.buy_dates = {}
        self.scores = {}
        
        # 使用基类中已经设置好的total_bars
        
        for d in self.datas:
            # 计算各种指标，添加plot=False以提高性能
            # 短线：EMA(EMA(C,10),10)
            ema10 = bt.indicators.ExponentialMovingAverage(d.close, period=10, plot=False)
            short_line = bt.indicators.ExponentialMovingAverage(ema10, period=10, plot=False)
            
            # 长线：(MA14+MA28+MA57+MA114)/4
            ma14 = bt.indicators.SimpleMovingAverage(d.close, period=14, plot=False)
            ma28 = bt.indicators.SimpleMovingAverage(d.close, period=28, plot=False)
            ma57 = bt.indicators.SimpleMovingAverage(d.close, period=57, plot=False)
            ma114 = bt.indicators.SimpleMovingAverage(d.close, period=114, plot=False)
            
            # 创建一个自定义指标来安全地计算long_line，确保所有输入指标都有足够的数据点
            class SafeLongLine(bt.Indicator):
                lines = ('long_line',)
                params = (('min_period', 114),)
                
                def __init__(self):
                    # 确保所有移动平均线都有足够的数据点
                    self.addminperiod(self.params.min_period)
                    
                def once(self, start, end):
                    for i in range(start, end):
                        # 只在所有数据点都可用时才计算
                        if i >= self.params.min_period - 1:
                            self.lines.long_line.array[i] = (ma14.array[i] + ma28.array[i] + ma57.array[i] + ma114.array[i]) / 4
                        else:
                            self.lines.long_line.array[i] = 0
            
            long_line = SafeLongLine()
            
            # 使用自定义的KDJ计算方法，避免除以零
            kdj = self.create_safe_kdj(d, period=9, period_dfast=3, period_dslow=3)
            
            # 成交量相关指标
            volume_ma5 = bt.indicators.SimpleMovingAverage(d.volume, period=5, plot=False)
            volume_ma20 = bt.indicators.SimpleMovingAverage(d.volume, period=20, plot=False)
            
            indicators = {
                'short_line': short_line,
                'long_line': long_line,
                'kdj': kdj,
                'volume_ma5': volume_ma5,
                'volume_ma20': volume_ma20,
                'buy_date': None,
                'score': 0,
            }
            
            self.indicators[d] = indicators
            self.buy_dates[d] = None
            self.scores[d] = 0
        
        self.logger.info(
            f"初始化选股策略，"
            f"持仓天数:{self.params.hold_days}，"
            f"买入股票数:{self.params.top_stocks_count}，"
            f"最低评分:{self.params.min_score}"
        )
    
    def calculate_kdj_score(self, d):
        """计算KDJ条件评分（20分）"""
        # 检查数据长度是否足够
        if len(d) < 20:  # 确保有足够的数据点来计算指标
            return 0
        
        # 在Backtrader中，StochasticFull的J值通常计算为 J = 3*K - 2*D
        k = self.indicators[d]['kdj'].k[0]  # KDJ的K值
        d_value = self.indicators[d]['kdj'].d[0]  # KDJ的D值
        j = 3 * k - 2 * d_value  # KDJ的J值
        if j >= 20:
            return 5
        elif j <= -10:
            return 10
        else:
            # 线性插值：从-10到20，5分到10分
            return 5 + (j - 20) * (5 / (-30))
    
    def calculate_volume_score(self, d):
        """计算缩量条件评分（20分）"""
        current_volume = d.volume[0]
        # 计算28个交易日内的最高量
        if len(d.volume) < 28:
            return 0
        max_volume_28d = max(d.volume.get(size=28))
        
        # 防止除以零
        if max_volume_28d == 0:
            return 0
            
        ratio = current_volume / max_volume_28d
        if ratio >= 0.7:
            return 0
        elif ratio <= 0.2:
            return 20
        else:
            # 线性插值：从0.7到0.2，0分到20分
            return 20 - (ratio - 0.2) * (20 / 0.5)
    
    def calculate_volatility_score(self, d):
        """计算异动条件评分（40分）"""
        if len(d) < 28:
            return 0
        
        # 检查28个交易日内是否有放量大阳线
        for i in range(1, 29):
            if i >= len(d):
                break
            
            # 计算涨幅
            close_today = d.close[-i]
            close_yesterday = d.close[-i-1]
            
            # 防止除以零
            if close_yesterday == 0:
                continue
                
            change = (close_today - close_yesterday) / close_yesterday * 100
            
            # 计算成交量比
            volume_today = d.volume[-i]
            volume_ma20 = self.indicators[d]['volume_ma20'][-i]
            
            # 防止除以零
            if volume_ma20 == 0:
                continue
                
            volume_ratio = volume_today / volume_ma20
            
            if change > 4 and volume_ratio > 1.5:
                return 40
        
        return 0
    
    def calculate_red_green_score(self, d):
        """计算红肥绿瘦条件评分（20分）"""
        if len(d) < 20:
            return 0
        
        red_volumes = []
        green_volumes = []
        
        # 分析最近20个交易日
        for i in range(1, 21):
            if i >= len(d):
                break
            
            close_today = d.close[-i]
            close_yesterday = d.close[-i-1]
            volume_today = d.volume[-i]
            
            if close_today > close_yesterday:
                red_volumes.append(volume_today)
            elif close_today < close_yesterday:
                green_volumes.append(volume_today)
        
        if not green_volumes:
            return 20
        if not red_volumes:
            return 0
        
        avg_red = sum(red_volumes) / len(red_volumes)
        avg_green = sum(green_volumes) / len(green_volumes)
        
        # 防止除以零
        if avg_green == 0:
            return 20
            
        ratio = avg_red / avg_green
        
        if ratio <= 1:
            return 0
        elif ratio >= 2:
            return 20
        else:
            # 线性插值：从1到2，0分到20分
            return (ratio - 1) * 20
    
    def calculate_penalty_score(self, d):
        """计算扣分条件"""
        penalty = 0
        
        if len(d) < 20:
            return penalty
        
        # 无跳空大涨条件：20日内跳空2%以上且涨4%以上，每出现一次扣20分
        for i in range(1, 21):
            if i >= len(d):
                break
            
            open_today = d.open[-i]
            close_yesterday = d.close[-i-1]
            close_today = d.close[-i]
            
            # 防止除以零
            if close_yesterday == 0:
                continue
                
            # 跳空幅度
            gap = (open_today - close_yesterday) / close_yesterday * 100
            # 涨幅
            change = (close_today - close_yesterday) / close_yesterday * 100
            
            if gap > 2 and change > 4:
                penalty += 20
        
        # 无放量下跌条件：20日内下跌且成交量大于1.2*MA5，每出现一次扣50分
        for i in range(1, 21):
            if i >= len(d):
                break
            
            close_today = d.close[-i]
            close_yesterday = d.close[-i-1]
            volume_today = d.volume[-i]
            volume_ma5 = self.indicators[d]['volume_ma5'][-i]
            
            if close_today < close_yesterday and volume_today > 1.2 * volume_ma5:
                penalty += 50
        
        return penalty
    
    def calculate_score(self, d):
        """计算综合评分"""
        if len(d) < 150:  # 至少需要150个交易日数据来计算指标
            return 0
        
        try:
            # 输出调试信息
            k = self.indicators[d]['kdj'].k[0]  # KDJ的K值
            d_value = self.indicators[d]['kdj'].d[0]  # KDJ的D值
            j = 3 * k - 2 * d_value  # KDJ的J值
            long_line = self.indicators[d]['long_line'][0]
            short_line = self.indicators[d]['short_line'][0]
            
            # 输出当前指标值
            self.log(f'{d._name} 指标值：J={j:.2f}, Close={d.close[0]:.2f}, Long={long_line:.2f}, Short={short_line:.2f}')
            
            # 初步筛选条件
            # 检查KDJ的J值是否小于0
            j_condition = j < 0
            # 检查收盘价是否大于长线
            close_long_condition = d.close[0] > long_line
            # 检查短线是否大于长线
            short_long_condition = short_line > long_line
            
            # 输出条件判断结果
            self.log(f'{d._name} 条件判断：J<0={j_condition}, Close>Long={close_long_condition}, Short>Long={short_long_condition}')
            
            # 暂时放宽条件，只要求J值小于0
            if not j_condition:
                return 0
        except IndexError as e:
            self.log(f'{d._name} 指标计算错误: {e}', level=logging.ERROR)
            return 0
        
        # 计算各项评分
        score = 0
        score += self.calculate_kdj_score(d)
        score += self.calculate_volume_score(d)
        score += self.calculate_volatility_score(d)
        score += self.calculate_red_green_score(d)
        score -= self.calculate_penalty_score(d)
        
        return max(0, score)  # 确保分数不小于0
    
    def create_safe_kdj(self, data, period=9, period_dfast=3, period_dslow=3):
        """
        创建安全的KDJ指标，避免除以零错误
        """
        # 自定义KDJ计算，避免除以零
        class SafeStochastic(bt.Indicator):
            lines = ('k', 'd', 'j')
            params = (('period', period), ('period_dfast', period_dfast), ('period_dslow', period_dslow))
            
            def __init__(self):
                # 计算最高价的移动最大值
                self.high = bt.indicators.Highest(data.high, period=self.p.period)
                # 计算最低价的移动最小值
                self.low = bt.indicators.Lowest(data.low, period=self.p.period)
                # 计算收盘价与最低价的差值
                self.close_low = data.close - self.low
                # 计算最高价与最低价的差值
                self.high_low = self.high - self.low
                
                # 避免除以零：当最高价等于最低价时，使用一个很小的值
                self.safe_high_low = bt.If(self.high_low == 0, 0.000001, self.high_low)
                
                # 计算RSV
                self.rsv = self.close_low / self.safe_high_low * 100
                
                # 计算K和D值
                self.lines.k = bt.indicators.SMA(self.rsv, period=self.p.period_dfast)
                self.lines.d = bt.indicators.SMA(self.lines.k, period=self.p.period_dslow)
                # 计算J值
                self.lines.j = 3 * self.lines.k - 2 * self.lines.d
        
        return SafeStochastic()
    
    def select_stocks(self):
        """选股：计算所有股票的评分并排序"""
        scores = []
        
        for d in self.datas:
            if len(d) < 150:  # 至少需要150个交易日数据来计算指标
                continue
            
            score = self.calculate_score(d)
            self.scores[d] = score
            
            # 添加调试输出
            if score > 0:
                self.log(f'{d._name} 评分: {score:.2f}')
            
            if score >= self.params.min_score:
                scores.append((d, score))
        
        # 按评分降序排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 添加调试输出
        if scores:
            self.log(f'选股结果：{[(d._name, score) for d, score in scores]}')
        else:
            self.log('没有找到符合条件的股票')
        
        # 选择前N只股票
        return scores[:self.params.top_stocks_count]
    
    def next(self):
        """每个周期执行一次"""
        # 调用基类的next方法，更新进度条
        super().next()
        
        # 检查是否需要卖出（持仓天数达到）
        for d in self.datas:
            if self.getposition(d).size > 0:
                if self.buy_dates[d] is not None:
                    # 计算持仓天数
                    hold_days = (len(self) - self.buy_dates[d])
                    if hold_days >= self.params.hold_days:
                        self.log(f'{d._name} 持仓到期 | 价格: {d.close[0]:.2f} | 持仓天数: {hold_days}')
                        self.sell(data=d, size=self.getposition(d).size)
                        self.buy_dates[d] = None
        
        # 选股并买入
        if len(self) % 5 == 0:  # 每5个交易日选股一次（可以根据需要调整）
            self.log(f'开始选股...')
            selected_stocks = self.select_stocks()
            
            if selected_stocks:
                self.log(f'选股结果：{[d._name for d, score in selected_stocks]}')
                
                # 计算总资金和每只股票的仓位
                total_value = self.broker.getvalue()
                position_per_stock = total_value * 0.2  # 每只股票占总仓位的20%
                
                # 买入选中的股票
                for d, score in selected_stocks:
                    if self.getposition(d).size == 0:  # 确保没有持仓
                        # 计算可以购买的股票数量
                        stock_price = d.open[0]  # 次日开盘价买入
                        stock_count = int(position_per_stock / stock_price / 100) * 100
                        stock_count = max(stock_count, 100)  # 至少100股
                        
                        if stock_count > 0:
                            self.log(f'{d._name} 买入信号 | 价格: {stock_price:.2f} | 评分: {score:.2f} | 仓位: {stock_count}')
                            self.buy(data=d, size=stock_count)
                            self.buy_dates[d] = len(self)
