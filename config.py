import os
from datetime import datetime

# 数据配置
DATA_PATH = "your_stock_data.csv"  # 您的A股数据文件路径
START_DATE = "2014-01-01"
END_DATE = "2024-01-01"

# 回测配置
INITIAL_CASH = 100000.0
COMMISSION = 0.001  # 0.1%手续费
STAKE = 100  # 每次交易股数
SLIPPAGE = 0.0  # 滑点

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