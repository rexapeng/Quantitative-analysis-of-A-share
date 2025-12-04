import pandas as pd
import numpy as np
import time
import os
import baostock as bs
from datetime import datetime

class AShareDataCollector:
    """
    A股数据收集器
    负责收集基本面和消息面数据并保存到/raw目录
    """
    
    def __init__(self):
        """
        初始化数据收集器
        """
        self.raw_dir = './raw'
        
        # 创建raw目录如果不存在
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
    
    def collect_basic_data(self):
        """
        收集基础数据（股票列表、基本信息等）
        """
        print("正在收集股票基础数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        
        try:
            # 获取股票列表
            rs = bs.query_all_stock(day=datetime.now().strftime('%Y-%m-%d'))
            stock_list = []
            while (rs.error_code == '0') & rs.next():
                stock_list.append(rs.get_row_data())
            
            if stock_list:
                stock_df = pd.DataFrame(stock_list, columns=rs.fields)
                # 过滤出A股股票（沪深两市）
                stock_df = stock_df[stock_df['code'].str.startswith(('sh.6', 'sz.0', 'sz.3'))]
                # 转换代码格式为ts格式以便后续使用
                stock_df['ts_code'] = stock_df['code'].apply(
                    lambda x: x.split('.')[1] + '.SH' if x.startswith('sh') else x.split('.')[1] + '.SZ'
                )
                stock_df.to_csv(f'{self.raw_dir}/stock_basic.csv', index=False)
            
            print(f"基础数据已保存至 {self.raw_dir}")
            
        finally:
            # 登出baostock
            bs.logout()
    
    def collect_financial_data_baostock(self, start_date='20200101'):
        """
        使用baostock收集财务数据（资产负债表、利润表、现金流量表等）
        :param start_date: 开始日期
        """
        print("正在使用baostock收集财务数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        
        try:
            # 获取股票列表
            stock_list = pd.read_csv(f'{self.raw_dir}/stock_basic.csv')
            ts_codes = stock_list['ts_code'].tolist()
            
            # 转换TS代码为baostock格式 (sh.600000, sz.000001)
            bs_codes = []
            for code in ts_codes:
                if code.endswith('.SH'):
                    bs_codes.append(f"sh.{code.split('.')[0]}")
                elif code.endswith('.SZ'):
                    bs_codes.append(f"sz.{code.split('.')[0]}")
            
            # 收集资产负债表
            balance_sheets = []
            for i, code in enumerate(bs_codes):  # 处理所有股票
                try:
                    rs = bs.query_balance_data(code=code, start_year=start_date[:4])
                    while (rs.error_code == '0') & rs.next():
                        balance_sheets.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}资产负债表")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}资产负债表失败: {e}")
            
            if balance_sheets:
                # 将数据转换为DataFrame
                balance_columns = rs.fields if rs else []
                balance_df = pd.DataFrame(balance_sheets, columns=balance_columns)
                balance_df.to_csv(f'{self.raw_dir}/balancesheet_baostock.csv', index=False)
            
            # 收集利润表
            income_statements = []
            for i, code in enumerate(bs_codes):
                try:
                    rs = bs.query_profit_data(code=code, start_year=start_date[:4])
                    while (rs.error_code == '0') & rs.next():
                        income_statements.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}利润表")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}利润表失败: {e}")
            
            if income_statements:
                # 将数据转换为DataFrame
                income_columns = rs.fields if rs else []
                income_df = pd.DataFrame(income_statements, columns=income_columns)
                income_df.to_csv(f'{self.raw_dir}/income_baostock.csv', index=False)
            
            # 收集现金流量表
            cashflow_statements = []
            for i, code in enumerate(bs_codes):
                try:
                    rs = bs.query_cash_flow_data(code=code, start_year=start_date[:4])
                    while (rs.error_code == '0') & rs.next():
                        cashflow_statements.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}现金流量表")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}现金流量表失败: {e}")
            
            if cashflow_statements:
                # 将数据转换为DataFrame
                cashflow_columns = rs.fields if rs else []
                cashflow_df = pd.DataFrame(cashflow_statements, columns=cashflow_columns)
                cashflow_df.to_csv(f'{self.raw_dir}/cashflow_baostock.csv', index=False)
                
        finally:
            # 登出baostock
            bs.logout()
        
        print(f"baostock财务数据已保存至 {self.raw_dir}")
    
    def collect_performance_data_baostock(self, start_date='20200101'):
        """
        使用baostock收集业绩预告数据
        :param start_date: 开始日期
        """
        print("正在使用baostock收集业绩预告数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        
        try:
            # 获取股票列表
            stock_list = pd.read_csv(f'{self.raw_dir}/stock_basic.csv')
            bs_codes = stock_list['code'].tolist()
            
            # 收集业绩预告数据
            performance_forecast = []
            current_year = datetime.now().year
            
            for i, code in enumerate(bs_codes):
                try:
                    # 查询最近几年的业绩预告
                    for year in range(int(start_date[:4]), current_year + 1):
                        rs = bs.query_forecast_report(code=code, year=year)
                        while (rs.error_code == '0') & rs.next():
                            performance_forecast.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}业绩预告")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}业绩预告失败: {e}")
            
            if performance_forecast:
                # 将数据转换为DataFrame
                forecast_columns = rs.fields if rs else []
                forecast_df = pd.DataFrame(performance_forecast, columns=forecast_columns)
                forecast_df.to_csv(f'{self.raw_dir}/performance_forecast_baostock.csv', index=False)
                
        finally:
            # 登出baostock
            bs.logout()
        
        print(f"baostock业绩预告数据已保存至 {self.raw_dir}")
    
    def collect_dividend_data_baostock(self):
        """
        使用baostock收集分红送股数据
        """
        print("正在使用baostock收集分红送股数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        
        try:
            # 获取股票列表
            stock_list = pd.read_csv(f'{self.raw_dir}/stock_basic.csv')
            bs_codes = stock_list['code'].tolist()
            
            # 收集分红送股数据
            dividend_data = []
            for i, code in enumerate(bs_codes):
                try:
                    rs = bs.query_dividend_data(code=code)
                    while (rs.error_code == '0') & rs.next():
                        dividend_data.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}分红送股数据")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}分红送股数据失败: {e}")
            
            if dividend_data:
                # 将数据转换为DataFrame
                dividend_columns = rs.fields if rs else []
                dividend_df = pd.DataFrame(dividend_data, columns=dividend_columns)
                dividend_df.to_csv(f'{self.raw_dir}/dividend_baostock.csv', index=False)
                
        finally:
            # 登出baostock
            bs.logout()
        
        print(f"baostock分红送股数据已保存至 {self.raw_dir}")
    
    def collect_indicator_data_baostock(self, start_date='20200101'):
        """
        使用baostock收集股票估值指标等衍生指标数据
        :param start_date: 开始日期
        """
        print("正在使用baostock收集估值指标数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock登录失败: {lg.error_msg}")
            return
        
        try:
            # 获取股票列表
            stock_list = pd.read_csv(f'{self.raw_dir}/stock_basic.csv')
            bs_codes = stock_list['code'].tolist()
            
            # 收集估值指标数据
            indicator_data = []
            for i, code in enumerate(bs_codes):
                try:
                    rs = bs.query_stock_basic(code=code)
                    while (rs.error_code == '0') & rs.next():
                        indicator_data.append(rs.get_row_data())
                    print(f"进度: {i+1}/{len(bs_codes)} - 已获取{code}基本指标")
                    time.sleep(0.1)  # 控制访问频率
                except Exception as e:
                    print(f"获取{code}基本指标失败: {e}")
            
            if indicator_data:
                # 将数据转换为DataFrame
                indicator_columns = rs.fields if rs else []
                indicator_df = pd.DataFrame(indicator_data, columns=indicator_columns)
                indicator_df.to_csv(f'{self.raw_dir}/indicator_baostock.csv', index=False)
                
        finally:
            # 登出baostock
            bs.logout()
        
        print(f"baostock基本指标数据已保存至 {self.raw_dir}")
    
    def collect_fundamental_data_only(self):
        """
        只收集基本面数据（基础数据+财务数据）
        """
        print("开始收集A股基本面数据...")
        
        # 收集基础数据
        self.collect_basic_data()
        
        # 收集财务数据(使用baostock)
        self.collect_financial_data_baostock()
        
        # 收集业绩预告数据
        self.collect_performance_data_baostock()
        
        # 收集分红送股数据
        self.collect_dividend_data_baostock()
        
        # 收集估值指标数据
        self.collect_indicator_data_baostock()
        
        print("A股基本面数据收集完成!")
    
    def collect_all_data(self):
        """
        收集所有数据（仅基本面数据）
        """
        print("开始收集A股全量数据...")
        
        # 收集基础数据
        self.collect_basic_data()
        
        # 收集财务数据(使用baostock)
        self.collect_financial_data_baostock()
        
        # 收集业绩预告数据
        self.collect_performance_data_baostock()
        
        # 收集分红送股数据
        self.collect_dividend_data_baostock()
        
        # 收集估值指标数据
        self.collect_indicator_data_baostock()
        
        print("所有数据收集完成!")

def main():
    """
    主函数：执行数据收集任务
    """
    # 注意：需要在环境变量中设置TUSHARE_TOKEN或者直接传入token
    collector = AShareDataCollector()
    
    # 执行基本面数据收集
    collector.collect_fundamental_data_only()

if __name__ == "__main__":
    main()