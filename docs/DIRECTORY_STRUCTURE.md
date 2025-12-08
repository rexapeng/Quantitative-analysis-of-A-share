# 项目目录结构说明

## 目录结构概述

本项目采用统一的目录结构管理所有生成的报告、日志和结果文件。所有文件根据类型分类存储，并按日期进行细分管理。

## 主要目录结构

```
项目根目录/
├── data/                  # 数据目录
│   ├── raw/               # 原始数据
│   ├── processed/         # 处理后的数据
│   └── databases/         # 数据库文件
├── reports/               # 报告目录
│   ├── factor_analysis/   # 因子分析报告
│   ├── backtest/          # 回测报告
│   ├── qlib/              # Qlib分析报告
│   └── summary/           # 汇总报告
├── logs/                  # 日志目录
│   ├── data_fetching/     # 数据获取日志
│   ├── factor_calculation/ # 因子计算日志
│   ├── factor_analysis/   # 因子分析日志
│   ├── backtest/          # 回测日志
│   └── system/            # 系统日志
├── factor_results/        # 因子结果目录
│   ├── calculated/        # 计算后的因子
│   ├── analyzed/          # 分析后的因子
│   └── machine_learning/  # 机器学习因子结果
├── backtest_results/      # 回测结果目录
│   ├── strategy/          # 策略回测结果
│   ├── portfolio/         # 投资组合结果
│   └── plots/             # 图表结果
└── temp/                  # 临时文件目录
```

## 日期细分管理

所有生成的文件都会按照日期进行细分管理，每个目录下都会自动创建以当前日期（YYYYMMDD格式）命名的子目录，用于存储当天生成的文件。

例如，2023年10月15日生成的因子分析报告将存储在：
```
reports/factor_analysis/20231015/
```

## 统一文件管理系统

### 使用FileManager保存文件

项目提供了统一的`FileManager`类，用于管理所有文件的保存操作。可以通过以下方式使用：

```python
from utils.file_manager import save_file

# 保存因子分析报告
save_file(report_content, 'factor_report', 'my_factor_analysis')

# 保存回测结果
save_file(backtest_result, 'strategy_result', 'my_backtest', with_datetime=True)
```

### 支持的文件类型

| 文件类型 | 保存目录 | 说明 |
|---------|---------|------|
| factor_report | reports/factor_analysis/YYYYMMDD/ | 因子分析报告 |
| backtest_report | reports/backtest/YYYYMMDD/ | 回测报告 |
| qlib_report | reports/qlib/YYYYMMDD/ | Qlib分析报告 |
| summary_report | reports/summary/YYYYMMDD/ | 汇总报告 |
| calculated_factor | factor_results/calculated/YYYYMMDD/ | 计算后的因子 |
| analyzed_factor | factor_results/analyzed/YYYYMMDD/ | 分析后的因子 |
| ml_factor | factor_results/machine_learning/YYYYMMDD/ | 机器学习因子结果 |
| strategy_result | backtest_results/strategy/YYYYMMDD/ | 策略回测结果 |
| portfolio_result | backtest_results/portfolio/YYYYMMDD/ | 投资组合结果 |
| backtest_plot | backtest_results/plots/YYYYMMDD/ | 回测图表 |

### 保存参数说明

- `content`: 要保存的内容，可以是字符串、DataFrame或其他可序列化对象
- `file_type`: 文件类型，决定保存的目录
- `file_name`: 文件名（不含扩展名）
- `with_datetime`: 是否在文件名中包含日期时间（格式：YYYYMMDD_HHMMSS），默认False

## 配置文件

所有目录配置都集中在`config/directory_config.py`文件中，包括：

- 基础目录定义
- 各类型文件的存储目录
- 日期子目录生成函数
- 目录创建函数

可以通过修改该文件来调整目录结构。

## 日志配置

日志系统使用`config/logger_config.py`进行配置，所有日志都会自动保存到对应的日期子目录中。

## 初始化

项目启动时会自动创建所有必要的目录。可以通过以下方式手动初始化目录结构：

```python
from config.directory_config import create_all_directories

create_all_directories()
```