import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import glob
import multiprocessing as mp
from functools import partial
import sys
import random
import threading
from multiprocessing import Manager
import io
import contextlib

# ==================== 配置项 ====================
# 数据存储目录
DATA_DIR = "./data/raw"

# 可选的数据范围: "all"(全部A股), "hs300"(沪深300成分股), "sz50"(上证50成分股)
STOCK_SCOPE = "all"#可选值: "all", "hs300", "sz50"

# 是否在保存阶段显示无有效数据的股票信息
SHOW_NO_DATA_STOCKS = True

# 时间范围设置（修改为合理的历史日期范围）
START_DATE = "2023-01-01"  # 开始日期
END_DATE = datetime.now().strftime('%Y-%m-%d')    # 结束日期设为昨天

# 请求间隔（秒）
REQUEST_DELAY = 0.1

# 获取字段
FIELDS = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"

# 重试轮数
MAX_RETRIES = 100

# 并发进程数
NUM_PROCESSES = 20

# 重试时的并发进程数
RETRY_NUM_PROCESSES = 20

# 登录重试延迟（秒）
LOGIN_RETRY_DELAY = 0.1

# 进度锁
progress_lock = threading.Lock()

# 控制是否显示登录/登出信息
SHOW_LOGIN_LOGOUT = False

# 进度更新间隔（秒）
PROGRESS_UPDATE_INTERVAL = 0.1

# 日志配置
ENABLE_BAOSTOCK_LOG_REDIRECT = True
LOG_DIR = "./log"

# ===============================================

# 日志缓冲区
baostock_log_buffer = io.StringIO()

def setup_baostock_logging():
    """
    设置baostock日志重定向到文件
    """
    if ENABLE_BAOSTOCK_LOG_REDIRECT:
        # 创建日志目录
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        # 创建日志文件名
        log_filename = f"{LOG_DIR}/baostock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        return log_filename
    return None

def flush_baostock_logs(log_filename):
    """
    将缓存中的baostock日志写入文件
    """
    if ENABLE_BAOSTOCK_LOG_REDIRECT and log_filename:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(baostock_log_buffer.getvalue())
        baostock_log_buffer.seek(0)
        baostock_log_buffer.truncate()

def get_all_stocks(log_file=None):
    """
    获取股票列表（根据 STOCK_SCOPE 配置获取不同范围的股票）
    """
    # 保存原始stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    if ENABLE_BAOSTOCK_LOG_REDIRECT:
        sys.stdout = baostock_log_buffer
        sys.stderr = baostock_log_buffer
    
    try:
        if SHOW_LOGIN_LOGOUT:
            print("正在登录baostock...")
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            if SHOW_LOGIN_LOGOUT:
                print(f"登录失败: {lg.error_msg}")
            return None
        if SHOW_LOGIN_LOGOUT:
            print("登录成功")
        
        # 使用当前日期获取股票列表可能会导致问题，改用历史日期
        reference_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 根据 STOCK_SCOPE 获取不同的股票列表
        if STOCK_SCOPE == "hs300":
            # 获取沪深300成分股
            if SHOW_LOGIN_LOGOUT:
                print("正在获取沪深300成分股列表...")
            rs = bs.query_hs300_stocks(reference_date)
        elif STOCK_SCOPE == "sz50":
            # 获取上证50成分股
            if SHOW_LOGIN_LOGOUT:
                print("正在获取上证50成分股列表...")
            rs = bs.query_sz50_stocks(reference_date)
        else:
            # 获取全A股股票列表
            if SHOW_LOGIN_LOGOUT:
                print("正在获取全A股股票列表...")
            rs = bs.query_all_stock(day=reference_date)
            
        if rs.error_code != '0':
            if SHOW_LOGIN_LOGOUT:
                print(f"获取股票列表失败: {rs.error_msg}")
            try:
                bs.logout()
            except:
                pass
            return None
        
        # 保存股票数据
        all_stocks = []
        count = 0
        while (rs.error_code == '0') & rs.next():
            all_stocks.append(rs.get_row_data())
            count += 1
            # 每1000条显示一次进度
            if count % 1000 == 0 and SHOW_LOGIN_LOGOUT:
                print(f"已读取 {count} 条记录...")
        
        if SHOW_LOGIN_LOGOUT:
            print(f"总共读取到 {len(all_stocks)} 条股票数据")
        
        # 转换为DataFrame
        if STOCK_SCOPE in ["hs300", "sz50"]:
            result = pd.DataFrame(all_stocks, columns=rs.fields)
            # 重命名列以匹配全A股格式
            result.rename(columns={'stock_code': 'code', 'stock_name': 'code_name'}, inplace=True)
        else:
            result = pd.DataFrame(all_stocks, columns=rs.fields)
        
        # 过滤掉指数和非股票代码（保留A股股票代码）
        if STOCK_SCOPE == "all":
            result = result[
                (result['code'].str.startswith('sh.6')) | 
                (result['code'].str.startswith('sz.0')) | 
                (result['code'].str.startswith('sz.3'))
            ]
        
        try:
            bs.logout()
            if SHOW_LOGIN_LOGOUT:
                print("baostock已登出")
        except:
            pass
        
        return result
    finally:
        # 恢复原始stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        # 刷新日志
        if ENABLE_BAOSTOCK_LOG_REDIRECT and log_file:
            flush_baostock_logs(log_file)

def load_existing_data(stock_code):
    """
    加载已存在的个股历史数据
    """
    filename = f"{DATA_DIR}/{stock_code}_history.csv"
    if os.path.exists(filename):
        try:
            existing_data = pd.read_csv(filename)
            return existing_data
        except Exception as e:
            print(f"读取 {stock_code} 历史数据失败: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_stock_data(stock_code, stock_data):
    """
    保存个股历史数据到独立文件
    """
    if stock_data is None or stock_data.empty:
        return False
        
    filename = f"{DATA_DIR}/{stock_code}_history.csv"
    
    # 如果文件存在，加载现有数据并合并
    if os.path.exists(filename):
        try:
            existing_data = pd.read_csv(filename)
            # 合并数据并去重
            combined_data = pd.concat([existing_data, stock_data], ignore_index=True)
            # 按日期排序并去重
            combined_data = combined_data.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        except Exception as e:
            print(f"合并 {stock_code} 数据时出错: {e}")
            combined_data = stock_data
    else:
        combined_data = stock_data
    
    # 保存数据
    try:
        combined_data.to_csv(filename, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"保存 {stock_code} 数据失败: {e}")
        return False

def format_time(seconds):
    """
    将秒数格式化为易读的时间格式
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:.0f}h {minutes:.0f}m {secs:.0f}s"

def update_progress_bar(current, total, start_time, prefix='', suffix='', length=50):
    """
    更新进度条显示（线程安全），包含预计剩余时间
    """
    with progress_lock:
        elapsed_time = time.time() - start_time
        if current > 0 and elapsed_time > 0:
            # 计算预计总时间和剩余时间
            estimated_total_time = elapsed_time * total / current
            remaining_time = estimated_total_time - elapsed_time
            eta_str = f" ETA: {format_time(remaining_time)}"
        else:
            eta_str = " ETA: --"
        
        if total == 0:
            percent = "100.0"
            filled_length = length
        else:
            percent = f"{100 * (current / float(total)):.1f}"
            filled_length = int(length * current // total)
        
        bar = '█' * filled_length + '-' * (length - filled_length)
        
        # 使用 \r 回到行首，并用 ljust 填充保证覆盖之前的字符
        output = f'{prefix} |{bar}| {percent}% {suffix}{eta_str}'
        print(f'\r{output}'.ljust(100), end='', flush=True)
        
        # 如果完成，输出换行
        if current == total:
            total_time = time.time() - start_time
            print(f"\n总耗时: {format_time(total_time)}")

def login_with_retry(max_retries=3):  # 登录重试次数固定为3次
    """
    带重试机制的登录函数
    """
    for attempt in range(max_retries):
        lg = bs.login()
        if lg.error_code == '0':
            return lg
        else:
            # 只在最后一次尝试失败时才打印错误信息
            if attempt == max_retries - 1:
                print(f"登录失败 (尝试 {attempt + 1}/{max_retries}): {lg.error_msg}", file=sys.stderr)
            if attempt < max_retries - 1:
                # 随机延迟后重试
                delay = LOGIN_RETRY_DELAY + random.uniform(0, 1)
                time.sleep(delay)
    
    return None

def get_stock_history_once(stock_code, stock_name, start_date, end_date, log_file=None):
    """
    获取单只股票的历史行情数据（单次尝试，不重试）
    """
    # 保存原始stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    if ENABLE_BAOSTOCK_LOG_REDIRECT:
        sys.stdout = baostock_log_buffer
        sys.stderr = baostock_log_buffer
    
    try:
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            return None
        
        try:
            # 获取历史行情数据（指定后复权）
            rs = bs.query_history_k_data_plus(
                stock_code,
                FIELDS,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="1"# 后复权
            )
            
            # 记录详细的查询状态
            query_info = f"查询 {stock_code}({stock_name}) | 时间范围: {start_date} 到 {end_date} | 错误代码: {rs.error_code}"
            if rs.error_code != '0':
                query_info += f" | 错误信息: {rs.error_msg}"
            print(query_info)  # 打印查询信息用于调试
            
            if rs.error_code == '0':
                # 成功获取数据
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    try:
                        bs.logout()
                    except:
                        pass
                    return result
                else:
                    # 数据为空
                    try:
                        bs.logout()
                    except:
                        pass
                    return pd.DataFrame()
            else:
                try:
                    bs.logout()
                except:
                    pass
                return None
                    
        except Exception as e:
            try:
                bs.logout()
            except:
                pass
            return None
    finally:
        # 恢复原始stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        # 刷新日志
        if ENABLE_BAOSTOCK_LOG_REDIRECT and log_file:
            flush_baostock_logs(log_file)

def get_stock_history_mp(args):
    """
    多进程版本：获取单只股票的历史行情数据（单次尝试）
    args: ((stock_code, stock_name, start_date, end_date), index, total, log_file)
    """
    stock_info, index, total, log_file = args
    stock_code, stock_name, start_date, end_date = stock_info
    
    # 检查是否已有数据，确定实际开始日期
    existing_data = load_existing_data(stock_code)
    if not existing_data.empty:
        # 获取最新日期并加一天作为新的开始日期
        latest_date = existing_data['date'].max()
        actual_start_date = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        # 如果最新数据已经是今天，则跳过
        if latest_date >= end_date:
            # 不再在此处更新进度条
            return stock_code, existing_data, True, True  # True表示成功或已存在, 第二个True表示已保存
        else:
            start_date = actual_start_date
    
    # 单次尝试获取历史行情数据
    result = get_stock_history_once(stock_code, stock_name, start_date, end_date, log_file)
    
    # 如果获取成功，尝试保存
    if result is not None and not result.empty:
        # 合并已有数据
        if not existing_data.empty:
            result = pd.concat([existing_data, result], ignore_index=True)
            # 去重并按日期排序
            result = result.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        
        # 立即保存本轮获取的数据
        save_success = save_stock_data(stock_code, result)
        return stock_code, result, True, save_success  # True表示获取成功, save_success表示保存是否成功
    else:
        # 返回空数据和False表示失败
        combined_data = existing_data if not existing_data.empty else pd.DataFrame()
        return stock_code, combined_data, False, False  # False表示获取失败

def get_stock_history_mp_for_retry(args):
    """
    专门为重试设计的多进程函数
    args: (stock_code, stock_name, start_date, end_date, existing_data, log_file)
    """
    stock_code, stock_name, start_date, end_date, existing_data, log_file = args
    
    # 检查是否已有数据，确定实际开始日期
    if not existing_data.empty:
        # 获取最新日期并加一天作为新的开始日期
        latest_date = existing_data['date'].max()
        actual_start_date = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        # 如果最新数据已经是今天，则跳过
        if latest_date >= end_date:
            return stock_code, existing_data, True, True  # True表示成功或已存在, 第二个True表示已保存
        else:
            start_date = actual_start_date
    
    # 单次尝试获取历史行情数据
    result = get_stock_history_once(stock_code, stock_name, start_date, end_date, log_file)
    
    # 如果获取成功，尝试保存
    if result is not None and not result.empty:
        # 合并已有数据
        if not existing_data.empty:
            result = pd.concat([existing_data, result], ignore_index=True)
            # 去重并按日期排序
            result = result.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        
        # 立即保存本轮获取的数据
        save_success = save_stock_data(stock_code, result)
        return stock_code, result, True, save_success  # True表示获取成功, save_success表示保存是否成功
    else:
        # 返回空数据和False表示失败
        combined_data = existing_data if not existing_data.empty else pd.DataFrame()
        return stock_code, combined_data, False, False  # False表示获取失败

def retry_failed_stocks_in_round(failed_stocks, round_num, start_time, log_file):
    """
    在指定轮次中重试失败的股票数据获取
    """
    if not failed_stocks:
        return [], []
    
    print(f"\n第 {round_num} 轮重试 {len(failed_stocks)} 只失败的股票...")
    
    # 初始化重试进度条
    update_progress_bar(0, len(failed_stocks), start_time, prefix=f'第{round_num}轮重试:', suffix=f'已完成 0/{len(failed_stocks)}')
    
    retry_results = []
    still_failed_stocks = []
    last_update_time = time.time()
    
    # 使用多进程并发重试
    with mp.Pool(processes=RETRY_NUM_PROCESSES, maxtasksperchild=20) as pool:
        # 使用 imap_unordered 并发执行
        results_iter = pool.imap_unordered(get_stock_history_mp_for_retry, failed_stocks)
        
        for i, (stock_code, stock_data, fetch_success, save_success) in enumerate(results_iter):
            # 无论保存是否成功，只要获取成功就记录结果
            retry_results.append((stock_code, stock_data, fetch_success, save_success))
            
            # 如果获取失败或者保存失败，加入下一轮重试列表
            if not fetch_success or not save_success:
                still_failed_stocks.append((stock_code, "", "", "", stock_data, log_file))
            
            # 更新重试进度条（基于时间间隔而非固定次数）
            current_time = time.time()
            if current_time - last_update_time >= PROGRESS_UPDATE_INTERVAL:
                update_progress_bar(i + 1, len(failed_stocks), start_time, prefix=f'第{round_num}轮重试:', suffix=f'已完成 {i + 1}/{len(failed_stocks)}')
                last_update_time = current_time
    
    # 最后一次更新确保显示100%
    update_progress_bar(len(failed_stocks), len(failed_stocks), start_time, prefix=f'第{round_num}轮重试:', suffix=f'已完成 {len(failed_stocks)}/{len(failed_stocks)}')
    
    # 统计本轮重试的成功和失败数量
    fetch_success_count = sum(1 for _, _, fetch_success, _ in retry_results if fetch_success)
    save_fail_count = sum(1 for _, _, fetch_success, save_success in retry_results if fetch_success and not save_success)
    fail_count = len(retry_results) - fetch_success_count
    
    print(f"第 {round_num} 轮重试结果: 获取成功 {fetch_success_count} 只，获取失败 {fail_count} 只，保存失败 {save_fail_count} 只")
    
    return retry_results, still_failed_stocks

def main():
    """
    主函数：获取全A股股票指定日期范围的日线行情并保存到独立CSV文件（多进程版本）
    """
    # 设置baostock日志重定向
    log_file = setup_baostock_logging()
    if log_file and ENABLE_BAOSTOCK_LOG_REDIRECT:
        print(f"baostock日志将保存到: {log_file}")
    
    # 创建数据存储目录
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 使用配置的日期范围
    start_date = START_DATE
    end_date = END_DATE
    
    print(f"获取时间范围: {start_date} 到 {end_date}")
    
    # 获取全A股股票列表
    print("正在获取全A股股票列表...")
    all_stocks_df = get_all_stocks(log_file)
    
    if all_stocks_df is None or all_stocks_df.empty:
        print("未能获取到全A股股票列表")
        return
    
    print(f"共获取到 {len(all_stocks_df)} 只A股股票")
    
    # 剔除指数类型的股票
    # 指数通常以 sh.000 或 sz.399 开头
    original_count = len(all_stocks_df)
    all_stocks_df = all_stocks_df[
        ~((all_stocks_df['code'].str.startswith('sh.000')) | 
          (all_stocks_df['code'].str.startswith('sz.399')))
    ]
    print(f"剔除指数后剩余 {len(all_stocks_df)} 只股票 (原 {original_count} 只)")
    
    # 准备股票信息列表，包含索引信息
    stock_info_list = []
    total_count = len(all_stocks_df)
    for index, (_, row) in enumerate(all_stocks_df.iterrows()):
        stock_info = (row['code'], row['code_name'], start_date, end_date)
        stock_info_list.append((stock_info, index, total_count, log_file))
    
    # 使用多进程并发下载
    print(f"使用 {NUM_PROCESSES} 个进程并发下载数据...")
    print("开始下载...")
    
    # 记录开始时间
    start_time = time.time()
    
    # 初始化进度条
    update_progress_bar(0, total_count, start_time, prefix='下载进度:', suffix='已完成 0/{}'.format(total_count))
    
    success_count = 0
    failed_stocks = []  # 存储失败的股票信息用于重试
    results = {}  # 使用字典存储结果，便于快速查找和更新
    
    # 创建进程池
    with mp.Pool(processes=NUM_PROCESSES, maxtasksperchild=20) as pool:
        # 使用 imap_unordered 方法逐个获取结果并更新进度
        results_iter = pool.imap_unordered(get_stock_history_mp, stock_info_list)
        
        last_update_time = time.time()
        last_log_flush_time = time.time()
        
        for i, result in enumerate(results_iter):
            stock_code, stock_data, fetch_success, save_success = result
            
            # 存储结果到字典中
            results[stock_code] = stock_data
            
            # 如果获取失败或者保存失败，记录失败的股票信息，用于后续重试
            if not fetch_success or not save_success:
                stock_info = stock_info_list[i][0]  # (stock_code, stock_name, start_date, end_date)
                failed_stocks.append((*stock_info, stock_data, log_file))  # 添加existing_data和log_file
                # 移除了失败提示的打印语句
            
            # 控制进度条更新频率，基于时间间隔而不是固定次数
            current_time = time.time()
            if current_time - last_update_time >= PROGRESS_UPDATE_INTERVAL:
                # 在主进程中更新进度条
                update_progress_bar(i + 1, total_count, start_time, prefix='下载进度:', suffix=f'已完成 {i + 1}/{total_count}')
                last_update_time = current_time
            
            # 定期刷新baostock日志到文件
            if ENABLE_BAOSTOCK_LOG_REDIRECT and log_file and time.time() - last_log_flush_time > 5:
                flush_baostock_logs(log_file)
                last_log_flush_time = time.time()
    
    # 最后一次更新确保显示100%
    update_progress_bar(total_count, total_count, start_time, prefix='下载进度:', suffix=f'已完成 {total_count}/{total_count}')
    
    # 刷新剩余的日志
    if ENABLE_BAOSTOCK_LOG_REDIRECT and log_file:
        flush_baostock_logs(log_file)
    
    # 分轮次重试失败的股票
    retry_round = 0
    while failed_stocks and retry_round < MAX_RETRIES:
        retry_round += 1
        retry_start_time = time.time()
        
        # 准备重试参数（补充完整信息）
        complete_failed_stocks = []
        for stock_code, stock_name, start_date, end_date, existing_data, log_file in failed_stocks:
            if not stock_name:  # 如果是之前重试轮次的数据，需要补充信息
                # 从all_stocks_df中查找股票名称
                stock_row = all_stocks_df[all_stocks_df['code'] == stock_code]
                if not stock_row.empty:
                    stock_name = stock_row.iloc[0]['code_name']
            complete_failed_stocks.append((stock_code, stock_name, start_date, end_date, existing_data, log_file))
        
        # 执行重试
        retry_results, still_failed_stocks = retry_failed_stocks_in_round(complete_failed_stocks, retry_round, retry_start_time, log_file)
        
        # 更新结果和失败列表
        failed_stocks = []
        for stock_code, stock_data, fetch_success, save_success in retry_results:
            results[stock_code] = stock_data
            # 如果获取失败或者保存失败，加入下一轮重试
            if not fetch_success or not save_success:
                # 从all_stocks_df中查找股票信息
                stock_row = all_stocks_df[all_stocks_df['code'] == stock_code]
                if not stock_row.empty:
                    stock_name = stock_row.iloc[0]['code_name']
                    failed_stocks.append((stock_code, stock_name, start_date, end_date, stock_data, log_file))
                else:
                    failed_stocks.append((stock_code, "", start_date, end_date, stock_data, log_file))
    
    # 对无有效数据的股票进行额外重试
    no_data_stocks = []
    for stock_code, stock_data in results.items():
        if stock_data is None or stock_data.empty:
            no_data_stocks.append(stock_code)
    
    # 对无数据股票进行重试
    if no_data_stocks and retry_round < MAX_RETRIES:
        print(f"\n对 {len(no_data_stocks)} 只无数据股票进行额外重试...")
        no_data_failed_stocks = []
        
        # 构建无数据股票的重试列表
        for stock_code in no_data_stocks:
            stock_row = all_stocks_df[all_stocks_df['code'] == stock_code]
            if not stock_row.empty:
                stock_name = stock_row.iloc[0]['code_name']
                stock_info = (stock_code, stock_name, start_date, end_date)
                no_data_failed_stocks.append((*stock_info, pd.DataFrame(), log_file))
        
        # 进行额外重试
        extra_retry_round = 0
        while no_data_failed_stocks and retry_round + extra_retry_round < MAX_RETRIES:
            extra_retry_round += 1
            retry_start_time = time.time()
            
            print(f"\n第 {retry_round + extra_retry_round} 轮重试 {len(no_data_failed_stocks)} 只无数据股票...")
            
            # 初始化重试进度条
            update_progress_bar(0, len(no_data_failed_stocks), retry_start_time, 
                              prefix=f'第{retry_round + extra_retry_round}轮重试:', 
                              suffix=f'已完成 0/{len(no_data_failed_stocks)}')
            
            still_failed_stocks = []
            last_update_time = time.time()
            
            # 使用多进程并发重试
            with mp.Pool(processes=RETRY_NUM_PROCESSES, maxtasksperchild=20) as pool:
                # 使用 imap_unordered 并发执行
                results_iter = pool.imap_unordered(get_stock_history_mp_for_retry, no_data_failed_stocks)
                
                for i, (stock_code, stock_data, fetch_success, save_success) in enumerate(results_iter):
                    # 更新结果
                    results[stock_code] = stock_data
                    
                    # 如果仍然失败，加入下一轮重试列表
                    if not fetch_success or not save_success or stock_data.empty:
                        still_failed_stocks.append((stock_code, "", "", "", stock_data, log_file))
                    
                    # 更新重试进度条
                    current_time = time.time()
                    if current_time - last_update_time >= PROGRESS_UPDATE_INTERVAL:
                        update_progress_bar(i + 1, len(no_data_failed_stocks), retry_start_time, 
                                          prefix=f'第{retry_round + extra_retry_round}轮重试:', 
                                          suffix=f'已完成 {i + 1}/{len(no_data_failed_stocks)}')
                        last_update_time = current_time
            
            # 最后一次更新确保显示100%
            update_progress_bar(len(no_data_failed_stocks), len(no_data_failed_stocks), retry_start_time, 
                              prefix=f'第{retry_round + extra_retry_round}轮重试:', 
                              suffix=f'已完成 {len(no_data_failed_stocks)}/{len(no_data_failed_stocks)}')
            
            print(f"第 {retry_round + extra_retry_round} 轮重试结果: "
                  f"获取成功 {len(no_data_failed_stocks) - len(still_failed_stocks)} 只，"
                  f"仍失败 {len(still_failed_stocks)} 只")
            
            no_data_failed_stocks = []
            for stock_code, _, _, _, stock_data, _ in still_failed_stocks:
                # 从all_stocks_df中查找股票信息
                stock_row = all_stocks_df[all_stocks_df['code'] == stock_code]
                if not stock_row.empty:
                    stock_name = stock_row.iloc[0]['code_name']
                    no_data_failed_stocks.append((stock_code, stock_name, start_date, end_date, stock_data, log_file))
                else:
                    no_data_failed_stocks.append((stock_code, "", start_date, end_date, stock_data, log_file))
    
    # 转换结果为列表格式
    results_list = list(results.items())
    
    # 保存最终结果统计
    fetch_success_count = sum(1 for stock_code, stock_data in results_list 
                             if stock_data is not None and not stock_data.empty)
    
    print("\n正在统计保存结果...")
    save_progress = 0
    last_update_time = time.time()
    
    # 记录保存开始时间
    save_start_time = time.time()
    
    # 收集无有效数据的股票信息
    no_data_stocks = []
    
    for stock_code, stock_data in results_list:
        if stock_data is not None and not stock_data.empty:
            if save_stock_data(stock_code, stock_data):
                success_count += 1
            else:
                print(f"{stock_code} 最终保存失败")
        else:
            no_data_stocks.append(stock_code)
        
        save_progress += 1
        # 控制保存进度条更新频率
        current_time = time.time()
        if current_time - last_update_time >= PROGRESS_UPDATE_INTERVAL:
            update_progress_bar(save_progress, len(results_list), save_start_time, prefix='保存进度:', suffix=f'已完成 {save_progress}/{len(results_list)}')
            last_update_time = current_time
    
    # 最后一次更新确保显示100%
    update_progress_bar(len(results_list), len(results_list), save_start_time, prefix='保存进度:', suffix=f'已完成 {len(results_list)}/{len(results_list)}')
    
    # 在进度条结束后显示无有效数据的股票信息
    if SHOW_NO_DATA_STOCKS and no_data_stocks:
        print(f"\n以下 {len(no_data_stocks)} 只股票无有效数据:")
        for i, stock_code in enumerate(no_data_stocks, 1):
        # 查找股票名称
            stock_row = all_stocks_df[all_stocks_df['code'] == stock_code]
            stock_name = stock_row.iloc[0]['code_name'] if not stock_row.empty else "未知"
        
            # 检查是否有本地历史数据
            existing_file = f"{DATA_DIR}/{stock_code}_history.csv"
            if os.path.exists(existing_file):
                try:
                    existing_data = pd.read_csv(existing_file)
                    if not existing_data.empty:
                        date_range = f"{existing_data['date'].min()} 至 {existing_data['date'].max()}"
                        record_count = len(existing_data)
                        print(f"{i}. {stock_code} ({stock_name}) - 本地数据: {record_count}条 ({date_range})")
                    else:
                        print(f"{i}. {stock_code} ({stock_name}) - 本地数据文件为空")
                except Exception as e:
                    print(f"{i}. {stock_code} ({stock_name}) - 读取本地数据失败: {str(e)}")
            else:
                # 提供更多关于为什么没有数据的信息
                print(f"{i}. {stock_code} ({stock_name}) - 无本地数据")
                # 可以考虑在这里添加对该股票的单独查询，检查是否真的没有数据
    
    # 保存股票列表
    component_filename = f"{DATA_DIR}/all_stocks_{datetime.now().strftime('%Y%m%d')}.csv"
    all_stocks_df.to_csv(component_filename, index=False, encoding='utf-8-sig')
    print(f"\n股票列表已保存至: {component_filename}")
    
    print(f"\n下载完成: {success_count}/{fetch_success_count} 只股票数据保存成功")
    if retry_round > 0 or 'extra_retry_round' in locals():
        total_rounds = retry_round + (extra_retry_round if 'extra_retry_round' in locals() else 0)
        print(f"经过 {total_rounds} 轮重试")
    
    # 显示部分文件示例
    csv_files = glob.glob(f"{DATA_DIR}/*_history.csv")
    if csv_files:
        print(f"\n示例文件:")
        for i, file in enumerate(csv_files[:3]):
            df = pd.read_csv(file)
            stock_code = os.path.basename(file).replace('_history.csv', '')
            print(f"{i+1}. {stock_code}: {len(df)} 条记录")
    
if __name__ == '__main__':
    main()