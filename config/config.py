import os
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'stock_data'
}

# 输出目录配置
OUTPUT_DIR = 'output'
LOG_DIR = os.path.join(OUTPUT_DIR, 'logs')
RESULT_DIR = os.path.join(OUTPUT_DIR, 'reports')

# 回测配置
BACKTEST_CONFIG = {
    'start_date': '2025-10-01',     # 回测开始日期
    'end_date': '2025-12-03',       # 回测结束日期
    'symbols': [],       # 交易标的列表，空列表表示所有标的
                                   # 标的格式示例: ['sh.600999', 'sz.000001', 'sh.600000']
                                   # 其中 sh 表示上海证券交易所，sz 表示深圳证券交易所
    'strategy': 'stock_selection',  # 策略名称：'sma'、'rsi_sma' 或 'stock_selection'
}

# 策略配置
# SMA策略配置
SMA_CONFIG = {
    'short_period': 10,
    'long_period': 30,
    'stake': 100,
}

# RSI-SMA策略配置
RSI_SMA_CONFIG = {
    'sma_short_period': 5,
    'sma_long_period': 15,
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 40,  # 提高超卖阈值，更容易触发买入
    'stop_loss': 0.05,
    'take_profit': 0.10,
    'risk_per_trade': 0.02,
}

# 选股策略配置
STOCK_SELECTION_CONFIG = {
    'hold_days': 10,          # 固定持仓天数
    'top_stocks_count': 5,    # 买入前N只股票
    'min_score': 50,          # 最低评分要求
}

# 经纪商配置
INITIAL_CASH = 100000              # 初始资金
COMMISSION_RATE = 0.00025            # 手续费率(0.025%)
STAMP_DUTY_RATE = 0.001             # 印花税率(0.1%)

# 添加缺失的配置项
# RESULT_DIR 已在顶部定义为 os.path.join(OUTPUT_DIR, 'reports')
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')  # 时间戳
REPORT_FORMAT = 'pdf'         # 报告格式

# 调试配置
DEBUG_MODE = True             # 调试模式开关
DEBUG_LEVEL = 'DEBUG'         # 调试日志级别: DEBUG, INFO, WARNING, ERROR

# 图表配置
PLOT_SAVE_FORMAT = 'png'      # 图表保存格式
PLOT_WIDTH = 12               # 图表宽度(inches)
PLOT_HEIGHT = 8               # 图表高度(inches)
# 修改图表样式为有效的matplotlib样式名称
PLOT_STYLE = 'seaborn-v0_8'   # 图表样式(seaborn更新后的正确样式名称)
PLOT_ENABLE = True            # 是否启用图表绘制功能


# 确保必要的目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# 数据目录配置
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
CLEANED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

# 数据文件路径配置
STOCK_DATA_FILE = os.path.join(CLEANED_DATA_DIR, 'stock_data.csv')
INDEX_DATA_FILE = os.path.join(CLEANED_DATA_DIR, 'index_data.csv')
FINANCIAL_DATA_FILE = os.path.join(CLEANED_DATA_DIR, 'financial_data.csv')

# 数据库配置（如果使用数据库存储清洗后的数据）
DATABASE_PATH = os.path.join(DATA_DIR, 'stock_data_cleaned.db')

# 清洗后数据的相关配置参数
DATA_CONFIG = {
    'date_format': '%Y-%m-%d',
    'encoding': 'utf-8',
    'fillna_method': 'ffill',  # 缺失值填充方法
    'columns_mapping': {       # 清洗后标准列名映射
        'trade_date': 'date',
        'stock_code': 'code',
        'open_price': 'open',
        'high_price': 'high',
        'low_price': 'low',
        'close_price': 'close',
        'volume': 'volume',
        'amount': 'amount'
    }
}

# 因子计算相关配置
FACTOR_CONFIG = {
    'lookback_periods': [5, 10, 20, 60],  # 回看周期
    'moving_average_windows': [5, 10, 20, 30, 60],  # 均线窗口
    'forward_periods': [1, 5, 10],  # 因子预测周期（默认值，会被user_selected_period覆盖）
    'analysis_window': 60,  # 滚动分析窗口
    'n_quantiles': 5,  # 分组数量
    'preprocessing_method': 'standard',  # 预处理方法
    'user_selected_period': 5  # 用户选择的收益率周期（1-60日，None表示使用默认forward_periods）
}

# 单只股票分析配置
SINGLE_STOCK = "sh.600036"  # 默认分析的股票代码

# 因子数据保存目录
FACTOR_DATA_DIR = "/factory/data/"

# 指数成分股配置
INDEX_COMPONENTS = {
    'hs300': '沪深300',      # 沪深300成分股
    'zz500': '中证500',      # 中证500成分股
    'zz1000': '中证1000',    # 中证1000成分股
    'zz2000': '中证2000'     # 中证2000成分股
}

# 因子分析范围配置
FACTOR_ANALYSIS_SCOPE = {
    'scope_type': 'index_components',  # 分析范围类型: 'single_stock' 或 'index_components'
    'single_stock': 'sh.600036',   # 单只股票代码
    'index_code': 'hs300',         # 指数代码，当scope_type为'index_components'时有效
    'use_qlib': False              # 是否使用Qlib进行端到端因子分析
}

if __name__ == "__main__":
    print(f"项目根目录: {os.path.dirname(__file__)}")
    print(f"数据目录: {DATA_DIR}")
    print(f"原始数据目录: {RAW_DATA_DIR}")
    print(f"清洗后数据目录: {CLEANED_DATA_DIR}")