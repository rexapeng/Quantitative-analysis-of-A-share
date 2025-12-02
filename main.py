import os

# 数据配置
DATA_PATH = "your_stock_data.csv"  # 您的A股数据文件路径
START_DATE = "2014-01-01"
END_DATE = "2024-01-01"

# 回测配置
INITIAL_CASH = 100000.0
COMMISSION = 0.001  # 0.1%手续费
STAKE = 100  # 每次交易股数

# 输出配置
RESULT_DIR = "results"