#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多因子选股脚本

功能：
1. 手动配置日期、选股范围、多因子及因子权重
2. 从数据库加载因子数据
3. 计算多因子值（与多因子分析文件方法一致）
4. 按多因子值从高到低选择前50只股票
5. 生成包含股票代码、名称、行业、多因子值等信息的TXT报告
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置和工具函数
from config.config import get_full_path
from factor_lib.utils import get_database_connection, load_stock_data
from utils.file_manager import save_file

# 手动配置参数
# =============================================================================
# 请在以下配置中设置选股参数
# =============================================================================
SELECTION_CONFIG = {
    "SELECTION_DATE": "2025-12-05",  # 选股日期
    "SELECTION_SCOPE": "SZ50",  # 选股范围：SZ50/HS300/ALL_A
    "FACTORS": {
        # 因子名称: 权重值，权重总和必须为1
        "momentum_20": 0.2,
        "rsi_24": 0.15,
        "volatility_20": 0.15,
        "macd": 0.2,
        "volume": 0.1,
        "kdj_j": 0.2
    },
    "TOP_N": 50,  # 选择前N只股票
    "REPORT_PATH": "factor_results/analyzed"  # 报告保存路径
}

# 验证权重总和是否为1
weights_sum = sum(SELECTION_CONFIG["FACTORS"].values())
if abs(weights_sum - 1.0) > 0.001:
    raise ValueError(f"因子权重总和必须为1，当前总和为{weights_sum}")

class MultiFactorStockSelector:
    def __init__(self, config):
        self.config = config
        self.date = config["SELECTION_DATE"]
        self.scope = config["SELECTION_SCOPE"]
        self.factors = config["FACTORS"]
        self.top_n = config["TOP_N"]
        
        self.stock_data = None
        self.selected_stocks = None

    def load_data_from_database(self):
        """
        从数据库加载选股所需的因子数据和股票基本信息
        """
        print(f"从数据库加载{self.date}的因子数据...")
        
        # 连接数据库
        conn = get_database_connection()
        if conn is None:
            print("无法连接到数据库")
            return False
        
        try:
            # 加载股票数据
            # 注意：这里需要根据实际数据库表结构调整查询
            self.stock_data = load_stock_data(conn, start_date=self.date, end_date=self.date)
            
            if self.stock_data is None or self.stock_data.empty:
                print("没有找到指定日期的股票数据")
                return False
            
            # 根据选股范围筛选
            if self.scope == "SZ50":
                # 这里需要根据实际情况实现SZ50的筛选逻辑
                pass  # 示例：self.stock_data = self.stock_data[self.stock_data['is_sz50'] == 1]
            elif self.scope == "HS300":
                # 这里需要根据实际情况实现HS300的筛选逻辑
                pass  # 示例：self.stock_data = self.stock_data[self.stock_data['is_hs300'] == 1]
            
            print(f"成功加载{len(self.stock_data)}只股票的因子数据")
            
        except Exception as e:
            print(f"从数据库加载数据失败: {str(e)}")
            return False
        finally:
            conn.close()
        
        return True

    def calculate_multi_factor_value(self):
        """
        计算多因子值，方法与多因子分析文件一致
        """
        print("计算多因子值...")
        
        if self.stock_data is None:
            print("请先加载数据")
            return False
        
        # 计算加权因子和（与multi_factor_combination.py中的方法一致）
        combined = 0
        for factor_name, weight in self.factors.items():
            combined += self.stock_data[factor_name] * weight
        
        self.stock_data['multi_factor_value'] = combined
        print("多因子值计算完成")
        
        return True

    def select_stocks(self):
        """
        按多因子值从高到低选择前N只股票
        """
        print(f"选择多因子值前{self.top_n}的股票...")
        
        if 'multi_factor_value' not in self.stock_data.columns:
            print("请先计算多因子值")
            return False
        
        # 按多因子值降序排序
        self.stock_data = self.stock_data.sort_values(by='multi_factor_value', ascending=False)
        
        # 选择前N只股票
        self.selected_stocks = self.stock_data.head(self.top_n)
        
        print(f"成功选择{len(self.selected_stocks)}只股票")
        
        return True

    def generate_txt_report(self):
        """
        生成TXT格式的选股报告
        """
        print("生成选股报告...")
        
        if self.selected_stocks is None:
            print("请先完成选股")
            return False
        
        # 构建报告内容
        report_content = []
        report_content.append("=" * 80)
        report_content.append("多因子选股报告")
        report_content.append("=" * 80)
        report_content.append(f"选股日期: {self.date}")
        report_content.append(f"选股范围: {self.scope}")
        report_content.append(f"选择股票数量: {self.top_n}")
        report_content.append("因子及权重:")
        for factor, weight in self.factors.items():
            report_content.append(f"  - {factor}: {weight:.2f}")
        report_content.append("=" * 80)
        
        # 表头
        report_content.append("排名 | 股票代码 | 股票名称 | 行业 | 多因子值")
        report_content.append("-" * 80)
        
        # 股票列表
        for i, (_, stock) in enumerate(self.selected_stocks.iterrows(), 1):
            report_content.append(f"{i:4d} | {stock['code']:6s} | {stock['name']:10s} | {stock['industry']:8s} | {stock['multi_factor_value']:10.6f}")
        
        report_content.append("=" * 80)
        report_content.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("=" * 80)
        
        # 保存报告
        report_text = "\n".join(report_content)
        report_path = save_file(
            report_text, 
            'factor_report', 
            'multi_factor_stock_selection', 
            with_datetime=True, 
            format='txt'
        )
        
        print(f"选股报告已保存至: {report_path}")
        return True

    def run_selection(self):
        """
        执行完整的选股流程
        """
        print("开始多因子选股流程...")
        
        # 1. 加载数据
        if not self.load_data_from_database():
            return False
        
        # 2. 计算多因子值
        if not self.calculate_multi_factor_value():
            return False
        
        # 3. 选择股票
        if not self.select_stocks():
            return False
        
        # 4. 生成报告
        if not self.generate_txt_report():
            return False
        
        print("多因子选股流程完成！")
        return True

if __name__ == "__main__":
    try:
        # 创建选股器实例
        selector = MultiFactorStockSelector(SELECTION_CONFIG)
        
        # 执行选股流程
        selector.run_selection()
        
    except Exception as e:
        print(f"选股过程中发生错误: {str(e)}")
        sys.exit(1)