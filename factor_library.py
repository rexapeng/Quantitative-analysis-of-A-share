import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class Factor(ABC):
    """因子基类"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    def calculate(self, data):
        pass

class FactorLibrary:
    """因子库类"""
    
    def __init__(self):
        self.factors = {}
        self._initialize_proven_factors()
    
    def _initialize_proven_factors(self):
        """初始化已被证明有效的因子"""
        # 1. 市值因子 (Size)
        self.add_factor(MarketCapFactor())
        
        # 2. 账面市值比因子 (Book-to-Market)
        self.add_factor(BookToMarketFactor())
        
        # 3. 动量因子 (Momentum)
        self.add_factor(MomentumFactor())
        
        # 4. 波动率因子 (Volatility)
        self.add_factor(VolatilityFactor())
        
        # 5. 盈利因子 (Profitability)
        self.add_factor(ProfitabilityFactor())
        
        # 6. 估值因子 (Value)
        self.add_factor(ValueFactor())
        
        # 7. 成长因子 (Growth)
        self.add_factor(GrowthFactor())
        
        # 8. 质量因子 (Quality)
        self.add_factor(QualityFactor())
        
        # 9. 流动性因子 (Liquidity)
        self.add_factor(LiquidityFactor())
        
        # 10. 情绪因子 (Sentiment)
        self.add_factor(SentimentFactor())
    
    def add_factor(self, factor):
        """添加因子到因子库"""
        self.factors[factor.name] = factor
    
    def get_factor(self, name):
        """获取指定因子"""
        return self.factors.get(name)
    
    def list_factors(self):
        """列出所有因子"""
        return {name: factor.description for name, factor in self.factors.items()}
    
    def calculate_all_factors(self, data):
        """计算所有因子"""
        results = {}
        for name, factor in self.factors.items():
            try:
                results[name] = factor.calculate(data)
            except Exception as e:
                results[name] = f"Error calculating {name}: {str(e)}"
        return results

# 1. 市值因子 (Market Cap Factor)
class MarketCapFactor(Factor):
    def __init__(self):
        super().__init__("market_cap", "市值因子：公司总市值的对数\n数据来源：股票价格 × 流通股本\n数据获取方式：\n- 股票价格：各大行情软件、交易所官网、Tushare、Yahoo Finance等\n- 流通股本：上市公司定期报告、交易所披露信息")
    
    def calculate(self, data):
        """
        计算市值因子
        data应包含'market_cap'列
        """
        if 'market_cap' not in data.columns:
            raise ValueError("数据中缺少 market_cap 列")
        return np.log(data['market_cap'])

# 2. 账面市值比因子 (Book-to-Market Factor)
class BookToMarketFactor(Factor):
    def __init__(self):
        super().__init__("book_to_market", "账面市值比因子：账面价值与市场价值的比率\n数据来源：财务报表中的股东权益/总市值\n数据获取方式：\n- 财务报表：上市公司公告、巨潮资讯网、Wind、Tushare等\n- 总市值：同市值因子")
    
    def calculate(self, data):
        """
        计算账面市值比因子
        data应包含'book_value'和'market_value'列
        """
        if 'book_value' not in data.columns or 'market_value' not in data.columns:
            raise ValueError("数据中缺少 book_value 或 market_value 列")
        return data['book_value'] / data['market_value']

# 3. 动量因子 (Momentum Factor)
class MomentumFactor(Factor):
    def __init__(self):
        super().__init__("momentum", "动量因子：过去一段时间的价格变化率\n数据来源：股票历史价格数据\n数据获取方式：\n- 历史价格数据：Yahoo Finance、Tushare、各大券商接口等")
    
    def calculate(self, data):
        """
        计算动量因子
        data应包含'price'列，且为时间序列数据
        """
        if 'price' not in data.columns:
            raise ValueError("数据中缺少 price 列")
        # 计算过去12个月相对于过去1个月的收益率
        if len(data) < 252:  # 假设一年约252个交易日
            raise ValueError("数据长度不足")
        return data['price'].pct_change(252 - 21)  # 12个月减去1个月

# 4. 波动率因子 (Volatility Factor)
class VolatilityFactor(Factor):
    def __init__(self):
        super().__init__("volatility", "波动率因子：价格的标准差\n数据来源：股票历史收益率数据\n数据获取方式：\n- 基于历史价格计算得出，数据源同动量因子")
    
    def calculate(self, data):
        """
        计算波动率因子
        data应包含'returns'列
        """
        if 'returns' not in data.columns:
            raise ValueError("数据中缺少 returns 列")
        return data['returns'].rolling(window=252).std() * np.sqrt(252)  # 年化波动率

# 5. 盈利因子 (Profitability Factor)
class ProfitabilityFactor(Factor):
    def __init__(self):
        super().__init__("profitability", "盈利因子：ROE (净资产收益率)\n数据来源：利润表中的净利润/资产负债表中的股东权益\n数据获取方式：\n- 财务报表数据：Wind、Tushare、国泰安CSMAR、巨潮资讯网等")
    
    def calculate(self, data):
        """
        计算盈利因子
        data应包含'net_income'和'equity'列
        """
        if 'net_income' not in data.columns or 'equity' not in data.columns:
            raise ValueError("数据中缺少 net_income 或 equity 列")
        return data['net_income'] / data['equity']

# 6. 估值因子 (Value Factor)
class ValueFactor(Factor):
    def __init__(self):
        super().__init__("value", "估值因子：市盈率的倒数\n数据来源：股票价格/每股收益(EPS)\n数据获取方式：\n- 股价数据：同市值因子\n- EPS数据：上市公司财报、专业数据库如Wind、Tushare等")
    
    def calculate(self, data):
        """
        计算估值因子
        data应包含'pe_ratio'列
        """
        if 'pe_ratio' not in data.columns:
            raise ValueError("数据中缺少 pe_ratio 列")
        return 1 / data['pe_ratio']

# 7. 成长因子 (Growth Factor)
class GrowthFactor(Factor):
    def __init__(self):
        super().__init__("growth", "成长因子：收入增长率\n数据来源：利润表中的营业收入\n数据获取方式：\n- 营业收入数据：上市公司定期报告、Wind、Tushare等专业数据库")
    
    def calculate(self, data):
        """
        计算成长因子
        data应包含'revenue'列
        """
        if 'revenue' not in data.columns:
            raise ValueError("数据中缺少 revenue 列")
        return data['revenue'].pct_change(periods=4)  # 假设季度数据，计算同比增速

# 8. 质量因子 (Quality Factor)
class QualityFactor(Factor):
    def __init__(self):
        super().__init__("quality", "质量因子：资产回报率\n数据来源：利润表中的净利润/资产负债表中的总资产\n数据获取方式：\n- 净利润和总资产数据：上市公司财务报告、Wind、Tushare等")
    
    def calculate(self, data):
        """
        计算质量因子
        data应包含'net_income'和'total_assets'列
        """
        if 'net_income' not in data.columns or 'total_assets' not in data.columns:
            raise ValueError("数据中缺少 net_income 或 total_assets 列")
        return data['net_income'] / data['total_assets']

# 9. 流动性因子 (Liquidity Factor)
class LiquidityFactor(Factor):
    def __init__(self):
        super().__init__("liquidity", "流动性因子：换手率\n数据来源：成交量/流通股本\n数据获取方式：\n- 成交量：各大交易系统、行情接口\n- 流通股本：上市公司公告、专业数据库")
    
    def calculate(self, data):
        """
        计算流动性因子
        data应包含'volume'和'shares_outstanding'列
        """
        if 'volume' not in data.columns or 'shares_outstanding' not in data.columns:
            raise ValueError("数据中缺少 volume 或 shares_outstanding 列")
        return data['volume'] / data['shares_outstanding']

# 10. 情绪因子 (Sentiment Factor)
class SentimentFactor(Factor):
    def __init__(self):
        super().__init__("sentiment", "情绪因子：基于新闻情感分析的因子\n数据来源：财经新闻、社交媒体、研报等文本数据的情感分析得分\n数据获取方式：\n- 新闻数据：各大财经媒体API、爬虫获取\n- 社交媒体：微博、股吧等平台API\n- 研报数据：卖方研究平台\n- 情感分析：自然语言处理工具如SnowNLP、jieba等")
    
    def calculate(self, data):
        """
        计算情绪因子
        data应包含'sentiment_score'列
        """
        if 'sentiment_score' not in data.columns:
            raise ValueError("数据中缺少 sentiment_score 列")
        return data['sentiment_score']