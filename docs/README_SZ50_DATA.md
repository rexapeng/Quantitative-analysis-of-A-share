# 上证50成分股行情数据获取工具

该工具用于获取上证50成分股过去十年的日线行情数据，并将数据存储到SQLite数据库中。

## 功能特性

- 自动获取当前上证50成分股列表
- 获取每只股票过去十年的日线行情数据
- 将数据存储到SQLite数据库中，方便后续分析
- 支持自动安装必要的Python库
- 提供详细的错误处理和进度显示

## 前置条件

1. Python 3.6+ 环境
2. tushare pro账号（用于获取数据）

## 安装和使用步骤

### 1. 获取tushare token

- 访问 [tushare.pro](https://tushare.pro/register?reg=466207) 注册账号
- 登录后，在个人主页获取您的接口TOKEN

### 2. 配置脚本

打开 `data/get_sz50_data.py` 文件，找到以下行并替换为您的tushare token：

```python
TS_TOKEN = 'your_token_here'  # 请替换为您自己的tushare token
```

### 3. 运行脚本

在命令行中执行以下命令：

```bash
cd c:\Users\Administrator\Desktop\Quantitative-analysis-of-A-share
python data/get_sz50_data.py
```

## 数据说明

### 数据来源

使用 [tushare pro](https://tushare.pro/) API 获取数据，需要有效的token。

### 数据内容

- **股票代码**：ts_code
- **交易日期**：trade_date
- **开盘价**：open
- **最高价**：high
- **最低价**：low
- **收盘价**：close
- **前收盘价**：pre_close
- **涨跌额**：change
- **涨跌幅(%)**：pct_chg
- **成交量(手)**：vol
- **成交额(千元)**：amount

### 数据存储

数据将存储在项目根目录下的 `sz50_stock_data.db` SQLite数据库中，表名为 `daily_quotes`。

## 注意事项

1. tushare pro有访问频率限制，免费用户建议不要频繁运行脚本
2. 首次运行可能需要较长时间，因为要获取大量数据
3. 如果网络中断或遇到错误，脚本会显示错误信息，但已获取的数据不会丢失
4. 可以根据需要修改脚本中的日期范围和其他参数

## 数据查询示例

可以使用SQLite客户端或Python查询数据库中的数据：

```python
import sqlite3
import pandas as pd

# 连接数据库
conn = sqlite3.connect('sz50_stock_data.db')

# 查询所有数据
df = pd.read_sql_query("SELECT * FROM daily_quotes", conn)

# 查询特定股票的数据
df = pd.read_sql_query("SELECT * FROM daily_quotes WHERE ts_code='600000.SH'", conn)

# 查询特定日期范围的数据
df = pd.read_sql_query("SELECT * FROM daily_quotes WHERE trade_date BETWEEN '20200101' AND '20201231'", conn)

# 关闭连接
conn.close()
```

## 更新日志

- v1.0: 初始版本，支持获取上证50成分股过去十年日线数据并存储到SQLite数据库