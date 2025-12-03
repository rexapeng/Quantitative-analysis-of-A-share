import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataCleaner:
    def __init__(self, raw_data_path='./data/raw', cleaned_data_path='./data/cleaned'):
        """
        初始化数据清洗器
        
        Parameters:
        raw_data_path: 原始数据路径
        cleaned_data_path: 清洗后数据保存路径
        """
        self.raw_data_path = Path(raw_data_path)
        self.cleaned_data_path = Path(cleaned_data_path)
        self.cleaned_data_path.mkdir(parents=True, exist_ok=True)
        
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
            stock_code = file_path.stem
            
            # 字符转数值处理
            numeric_columns = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn', 'pctChg']
            for col in numeric_columns:
                if col in df.columns:
                    # 将字符串类型的数值转换为数字，处理特殊字符
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
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
            df['turn'] = df['turn'].fillna(0)
            df['pctChg'] = df['pctChg'].fillna(0)
            
            # 日期格式化
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
            # 生成数据质量报告
            missing_data = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            quality_score = (1 - missing_data / total_cells) * 100 if total_cells > 0 else 100
            
            self.quality_report.append({
                'stock_code': stock_code,
                'original_rows': original_rows,
                'cleaned_rows': len(df),
                'missing_values': missing_data,
                'quality_score': quality_score
            })
            
            # 保存清洗后的数据
            cleaned_file_path = self.cleaned_data_path / f"{stock_code}.csv"
            df.to_csv(cleaned_file_path, index=False)
            
            return True
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return False
    
    def clean_all_files(self):
        """
        清洗所有股票数据文件
        """
        print("开始清洗数据...")
        
        # 获取所有CSV文件
        csv_files = list(self.raw_data_path.glob("*.csv"))
        print(f"找到 {len(csv_files)} 个文件待处理")
        
        # 逐个处理文件
        success_count = 0
        for i, file_path in enumerate(csv_files):
            if self.clean_single_file(file_path):
                success_count += 1
            
            # 显示进度
            if (i + 1) % 100 == 0:
                print(f"已处理 {i + 1}/{len(csv_files)} 个文件")
        
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
        
        # 保存完整报告
        report_path = self.cleaned_data_path / "data_quality_report.csv"
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
        print(f"{'股票代码':<10} {'原始行数':<10} {'清洗后行数':<12} {'缺失值数量':<12} {'质量分数':<10}")
        print("-" * 80)
        
        for _, row in worst_files.iterrows():
            print(f"{row['stock_code']:<10} {row['original_rows']:<10} {row['cleaned_rows']:<12} "
                  f"{row['missing_values']:<12} {row['quality_score']:<10.2f}")
        
        print("=" * 80)

def main():
    """
    主函数
    """
    cleaner = DataCleaner()
    cleaner.clean_all_files()

if __name__ == "__main__":
    main()