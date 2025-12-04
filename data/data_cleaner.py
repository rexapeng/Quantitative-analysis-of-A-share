import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import datetime
import sys
import multiprocessing as mp
from tqdm import tqdm
warnings.filterwarnings('ignore')

# 导入项目配置
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
try:
    from config.config import RAW_DATA_DIR, CLEANED_DATA_DIR as PROCESSED_DATA_DIR, LOG_DIR
except ImportError:
    # 如果配置文件导入失败，使用默认路径
    RAW_DATA_DIR = "./data/raw"
    PROCESSED_DATA_DIR = "./data/processed"
    LOG_DIR = "./log"

class DataCleaner:
    def __init__(self, raw_data_path=RAW_DATA_DIR, cleaned_data_path=PROCESSED_DATA_DIR):
        """
        初始化数据清洗器
        
        Parameters:
        raw_data_path: 原始数据路径
        cleaned_data_path: 清洗后数据保存路径
        """
        self.raw_data_path = Path(raw_data_path)
        self.cleaned_data_path = Path(cleaned_data_path)
        self.cleaned_data_path.mkdir(parents=True, exist_ok=True)
        
        # 创建log目录（使用项目统一的LOG_DIR）
        self.log_path = Path(LOG_DIR)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # 数据质量报告
        self.quality_report = []
    
    def clean_single_file(self, file_path):
        """
        清洗单个股票文件
        
        Parameters:
        file_path: 股票数据文件路径
        """
        try:
            # 读取数据
            df = pd.read_csv(file_path)
            
            # 记录原始数据信息
            original_rows = len(df)
            # 从文件名提取股票代码 (去掉 _history 部分)
            stock_code = file_path.stem.replace('_history', '')
            
            # 字符转数值处理
            numeric_columns = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn']
            # 注意：pctChg在原始数据中可能不存在，因为是在get_data.py中计算的
            for col in numeric_columns:
                if col in df.columns:
                    # 将字符串类型的数值转换为数字，处理特殊字符
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 如果没有pctChg列，则计算它
            if 'pctChg' not in df.columns and all(col in df.columns for col in ['close', 'preclose']):
                # 计算涨跌幅: (收盘价 - 前收盘价) / 前收盘价 * 100
                df['pctChg'] = (df['close'] - df['preclose']) / df['preclose'] * 100
                # 处理可能的无穷大或NaN值
                df['pctChg'] = df['pctChg'].replace([float('inf'), -float('inf')], 0)
                df['pctChg'] = df['pctChg'].fillna(0)
            
            # 缺失值处理
            # 价格数据使用前值填充
            price_columns = ['open', 'high', 'low', 'close', 'preclose']
            for col in price_columns:
                if col in df.columns:
                    df[col] = df[col].fillna(method='ffill')
            
            # 成交量数据缺失填0
            volume_columns = ['volume', 'amount']
            for col in volume_columns:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            # 其他字段缺失值处理
            if 'turn' in df.columns:
                df['turn'] = df['turn'].fillna(0)
            if 'pctChg' in df.columns:
                df['pctChg'] = df['pctChg'].fillna(0)
            
            # 日期格式化
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                
                # 计算十日收益率: (当前收盘价 - 10天前收盘价) / 10天前收盘价 * 100
                df['ten_day_return'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100
                df['ten_day_return'] = df['ten_day_return'].replace([float('inf'), -float('inf')], 0)
                df['ten_day_return'] = df['ten_day_return'].fillna(0)
                
                # 获取最早日期用于文件命名
                if len(df) > 0:
                    earliest_date = df['date'].min().strftime('%Y%m%d')
                else:
                    earliest_date = 'unknown'
            
            # 更严格的质控检查
            quality_deductions = 0
            
            # 检查关键价格列是否存在
            required_price_cols = ['open', 'high', 'low', 'close', 'preclose']
            missing_price_cols = [col for col in required_price_cols if col not in df.columns]
            quality_deductions += len(missing_price_cols) * 5  # 每缺少一个关键列扣5分
            
            # 检查关键价格是否有负值（不合理）
            for col in required_price_cols:
                if col in df.columns:
                    negative_count = (df[col] < 0).sum()
                    quality_deductions += negative_count * 2  # 每个负价格扣2分
                    
            # 检查成交量是否有负值
            if 'volume' in df.columns:
                negative_volume = (df['volume'] < 0).sum()
                quality_deductions += negative_volume * 2
                
            if 'amount' in df.columns:
                negative_amount = (df['amount'] < 0).sum()
                quality_deductions += negative_amount * 2
            
            # 检查数据重复情况
            duplicate_rows = df.duplicated().sum()
            quality_deductions += duplicate_rows * 3  # 每个重复行扣3分
            
            # 计算质量分数 (满分100分)
            missing_data = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            quality_score = 100.0
            if total_cells > 0:
                quality_score -= (missing_data / total_cells) * 100  # 缺失值扣分
            quality_score -= min(quality_deductions, 50)  # 其他质量问题最多扣50分
            quality_score = max(0, quality_score)  # 确保不低于0分

            # 保存清洗后的数据，使用与原始文件相同的命名规则但保存到不同目录
            cleaned_file_name = f"{stock_code}_history.csv"
            cleaned_file_path = self.cleaned_data_path / cleaned_file_name
            df.to_csv(cleaned_file_path, index=False)
            
            # 返回处理结果信息
            return {
                'stock_code': stock_code,
                'original_rows': original_rows,
                'cleaned_rows': len(df),
                'missing_values': missing_data,
                'duplicate_rows': duplicate_rows,
                'negative_prices': sum((df[col] < 0).sum() for col in required_price_cols if col in df.columns),
                'quality_score': quality_score,
                'success': True
            }
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            stock_code = file_path.stem.replace('_history', '')
            return {
                'stock_code': stock_code,
                'success': False
            }
    
    def clean_single_file_worker(self, file_path):
        """
        清洗单个股票文件的工作函数（用于多进程处理）
        
        Parameters:
        file_path: 股票数据文件路径
        """
        try:
            # 读取数据
            df = pd.read_csv(file_path)
            
            # 记录原始数据信息
            original_rows = len(df)
            # 从文件名提取股票代码 (去掉 _history 部分)
            stock_code = file_path.stem.replace('_history', '')
            
            # 字符转数值处理
            numeric_columns = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn']
            # 注意：pctChg在原始数据中可能不存在，因为是在get_data.py中计算的
            for col in numeric_columns:
                if col in df.columns:
                    # 将字符串类型的数值转换为数字，处理特殊字符
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 如果没有pctChg列，则计算它
            if 'pctChg' not in df.columns and all(col in df.columns for col in ['close', 'preclose']):
                # 计算涨跌幅: (收盘价 - 前收盘价) / 前收盘价 * 100
                df['pctChg'] = (df['close'] - df['preclose']) / df['preclose'] * 100
                # 处理可能的无穷大或NaN值
                df['pctChg'] = df['pctChg'].replace([float('inf'), -float('inf')], 0)
                df['pctChg'] = df['pctChg'].fillna(0)
            
            # 缺失值处理
            # 价格数据使用前值填充
            price_columns = ['open', 'high', 'low', 'close', 'preclose']
            for col in price_columns:
                if col in df.columns:
                    df[col] = df[col].fillna(method='ffill')
            
            # 成交量数据缺失填0
            volume_columns = ['volume', 'amount']
            for col in volume_columns:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            # 其他字段缺失值处理
            if 'turn' in df.columns:
                df['turn'] = df['turn'].fillna(0)
            if 'pctChg' in df.columns:
                df['pctChg'] = df['pctChg'].fillna(0)
            
            # 日期格式化
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                
                # 计算十日收益率: (当前收盘价 - 10天前收盘价) / 10天前收盘价 * 100
                df['ten_day_return'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100
                df['ten_day_return'] = df['ten_day_return'].replace([float('inf'), -float('inf')], 0)
                df['ten_day_return'] = df['ten_day_return'].fillna(0)
                
                # 获取最早日期用于文件命名
                if len(df) > 0:
                    earliest_date = df['date'].min().strftime('%Y%m%d')
                else:
                    earliest_date = 'unknown'
            
            # 更严格的质控检查
            quality_deductions = 0
            
            # 检查关键价格列是否存在
            required_price_cols = ['open', 'high', 'low', 'close', 'preclose']
            missing_price_cols = [col for col in required_price_cols if col not in df.columns]
            quality_deductions += len(missing_price_cols) * 5  # 每缺少一个关键列扣5分
            
            # 检查关键价格是否有负值（不合理）
            for col in required_price_cols:
                if col in df.columns:
                    negative_count = (df[col] < 0).sum()
                    quality_deductions += negative_count * 2  # 每个负价格扣2分
                    
            # 检查成交量是否有负值
            if 'volume' in df.columns:
                negative_volume = (df['volume'] < 0).sum()
                quality_deductions += negative_volume * 2
                
            if 'amount' in df.columns:
                negative_amount = (df['amount'] < 0).sum()
                quality_deductions += negative_amount * 2
            
            # 检查数据重复情况
            duplicate_rows = df.duplicated().sum()
            quality_deductions += duplicate_rows * 3  # 每个重复行扣3分
            
            # 计算质量分数 (满分100分)
            missing_data = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            quality_score = 100.0
            if total_cells > 0:
                quality_score -= (missing_data / total_cells) * 100  # 缺失值扣分
            quality_score -= min(quality_deductions, 50)  # 其他质量问题最多扣50分
            quality_score = max(0, quality_score)  # 确保不低于0分

            # 保存清洗后的数据，使用与原始文件相同的命名规则但保存到不同目录
            cleaned_file_name = f"{stock_code}_history.csv"
            cleaned_file_path = self.cleaned_data_path / cleaned_file_name
            df.to_csv(cleaned_file_path, index=False)
            
            # 返回处理结果信息
            return {
                'stock_code': stock_code,
                'original_rows': original_rows,
                'cleaned_rows': len(df),
                'missing_values': missing_data,
                'duplicate_rows': duplicate_rows,
                'negative_prices': sum((df[col] < 0).sum() for col in required_price_cols if col in df.columns),
                'quality_score': quality_score,
                'success': True
            }
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            stock_code = file_path.stem.replace('_history', '')
            return {
                'stock_code': stock_code,
                'success': False
            }

    def clean_all_files(self):
        """
        清洗所有股票数据文件（多进程版本）
        """
        print("开始清洗数据...")
        
        # 获取所有CSV文件，匹配get_data.py保存的文件命名模式
        csv_files = list(self.raw_data_path.glob("*_history.csv"))
        print(f"找到 {len(csv_files)} 个文件待处理")
        
        # 使用多进程处理文件
        num_processes = min(mp.cpu_count(), len(csv_files))
        print(f"使用 {num_processes} 个进程进行数据清洗...")
        
        # 使用tqdm显示进度条
        with mp.Pool(processes=num_processes) as pool:
            # 使用imap方法可以实时显示进度
            results = list(tqdm(
                pool.imap(self.clean_single_file_worker, csv_files),
                total=len(csv_files),
                desc="清洗进度"
            ))
        
        # 收集处理结果
        success_count = 0
        for result in results:
            if result['success']:
                success_count += 1
                # 将结果添加到质量报告中
                self.quality_report.append({
                    'stock_code': result['stock_code'],
                    'original_rows': result['original_rows'],
                    'cleaned_rows': result['cleaned_rows'],
                    'missing_values': result['missing_values'],
                    'duplicate_rows': result['duplicate_rows'],
                    'negative_prices': result['negative_prices'],
                    'quality_score': result['quality_score']
                })
        
        print(f"数据清洗完成，成功处理 {success_count}/{len(csv_files)} 个文件")
        
        # 生成并保存数据质量报告
        self.generate_quality_report()
    
    def generate_quality_report(self):
        """
        生成数据质量报告
        """
        if not self.quality_report:
            print("没有数据可生成报告")
            return
        
        # 转换为DataFrame
        report_df = pd.DataFrame(self.quality_report)
        
        # 保存完整报告到log目录，带时间戳
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.log_path / f"data_quality_report_{timestamp}.csv"
        report_df.to_csv(report_path, index=False)
        print(f"数据质量报告已保存至: {report_path}")
        
        # 显示质量最差的10个文件
        self.print_worst_quality_files()
    
    def print_worst_quality_files(self, top_n=10):
        """
        打印数据质量最差的N个文件详情
        
        Parameters:
        top_n: 显示最差的N个文件，默认10个
        """
        if not self.quality_report:
            print("没有数据质量报告可显示")
            return
        
        # 按质量分数排序，分数越低质量越差
        report_df = pd.DataFrame(self.quality_report)
        worst_files = report_df.nsmallest(top_n, 'quality_score')
        
        print(f"\n数据质量最差的{top_n}个文件:")
        print("=" * 80)
        # 使用格式化字符串确保对齐
        print("{:<15} {:<10} {:<12} {:<12} {:<10}".format('股票代码', '原始行数', '清洗后行数', '缺失值数量', '质量分数'))
        print("-" * 80)
        
        for _, row in worst_files.iterrows():
            print("{:<15} {:<10} {:<12} {:<12} {:<10.2f}".format(
                row['stock_code'], 
                row['original_rows'], 
                row['cleaned_rows'], 
                row['missing_values'], 
                row['quality_score']
            ))
        
        print("=" * 80)

def main():
    """
    主函数
    """
    # 实例化DataCleaner，使用与get_data.py一致的路径配置
    cleaner = DataCleaner(raw_data_path=RAW_DATA_DIR, cleaned_data_path='./data/processed')
    cleaner.clean_all_files()

if __name__ == "__main__":
    main()