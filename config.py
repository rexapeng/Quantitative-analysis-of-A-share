import os
from datetime import datetime

# 数据配置
# 修改：将DATA_DIR指向清洗后的数据目录
DATA_DIR = "data/processed"  # 存放股票CSV文件的目录
STOCK_LIST = None  # 股票列表，如 ['sh.600999', 'sz.000001']，None表示所有股票
# 修改：更新单个股票的文件名格式
SINGLE_STOCK = "sh.600999_(20140101)"  # 单个股票回测时使用的股票代码（示例）

# 回测配置
START_DATE = "2014-01-01"
END_DATE = "2024-01-01"
INITIAL_CASH = 100000.0
COMMISSION = 0.001  # 0.1%手续费
STAKE = 100  # 每次交易股数
SLIPPAGE = 0.0  # 滑点

# 回测模式
BACKTEST_MODE = "single"  # single 或 multi

# 策略配置
STRATEGY_NAME = "SMAStrategy"
STRATEGY_PARAMS = {
    'short_period': 10,
    'long_period': 30,
    'stake': 100
}

# 输出配置
RESULT_DIR = "results"
LOG_DIR = "logs"
REPORT_FORMAT = "html"  # html, pdf, json

# 图表配置
PLOT_ENABLE = True
PLOT_STYLE = "classic"  # classic, seaborn
PLOT_SAVE_FORMAT = "png"  # png, svg, pdf
PLOT_WIDTH = 12
PLOT_HEIGHT = 8

# 时间戳用于唯一标识本次回测
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# 创建输出目录
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
# 修改：不再自动创建DATA_DIR，因为数据现在存储在data/processed目录下
os.makedirs("data/processed", exist_ok=True)