import os
import sys
import pandas as pd
import numpy as np
import qlib
from qlib.constant import REG_US
from qlib.data import D
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.evaluate import (backtest, risk_analysis)
from qlib.contrib.report import analysis_model, analysis_position
from qlib.contrib.model.gbdt import LGBModel
from qlib.utils import exists_qlib_data, init_instance_by_config
from config.logger_config import data_logger

class QlibFactorAnalyzer:
    """
    使用Qlib库的端到端因子分析器
    """
    
    def __init__(self, provider_uri=None, region=REG_US):
        self.logger = data_logger
        self.provider_uri = provider_uri or "~/.qlib/qlib_data/us_data"
        self.region = region
        self.init_qlib()
        
    def init_qlib(self):
        """
        初始化Qlib环境
        """
        try:
            if not exists_qlib_data(self.provider_uri):
                self.logger.info(f"Qlib数据不存在，正在准备数据: {self.provider_uri}")
                # 下载数据
                from qlib.data import get_data
                get_data(self.provider_uri, region=self.region)
            
            # 初始化qlib
            qlib.init(provider_uri=self.provider_uri, region=self.region)
            self.logger.info("Qlib环境初始化成功")
        except Exception as e:
            self.logger.error(f"初始化Qlib环境失败: {e}")
            raise
    
    def load_data(self, instruments=None, start_time="2010-01-01", end_time="2020-12-31", freq="day"):
        """
        加载数据
        """
        try:
            # 如果没有指定标的，使用默认的沪深300成分股
            if instruments is None:
                instruments = "csi300"
                self.logger.info("未指定标的，使用沪深300成分股")
            
            # 获取标的列表
            if isinstance(instruments, str):
                instruments = D.instruments(instruments)
            
            self.logger.info(f"加载{len(instruments)}个标的的数据，时间范围: {start_time} - {end_time}")
            
            # 构建数据处理器
            data_handler_config = {
                "start_time": start_time,
                "end_time": end_time,
                "fit_start_time": start_time,
                "fit_end_time": end_time.replace("-12-31", "-06-30"),  # 训练集截止到年中
                "instruments": instruments,
                "handler": Alpha158,  # 使用内置的Alpha158因子集
            }
            
            handler = init_instance_by_config(data_handler_config)
            self.logger.info("数据加载完成")
            return handler
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            raise
    
    def calculate_factors(self, handler):
        """
        使用Qlib计算因子
        """
        try:
            self.logger.info("开始计算因子")
            # 获取因子数据
            factors = handler.get_feature()
            labels = handler.get_label()
            self.logger.info(f"因子计算完成，共{len(factors.columns)}个因子")
            return factors, labels
        except Exception as e:
            self.logger.error(f"计算因子失败: {e}")
            raise
    
    def analyze_factors(self, factors, labels):
        """
        因子分析
        """
        try:
            self.logger.info("开始因子分析")
            
            # 计算IC值
            from qlib.utils import flist
            from qlib.contrib.evaluate import calc_ic
            
            ic = calc_ic(factors, labels, ic_method="rank")
            ic_mean = ic.mean()
            ic_std = ic.std()
            ic_ir = ic_mean / ic_std
            
            self.logger.info(f"因子IC分析完成")
            self.logger.info(f"平均IC: {ic_mean.mean():.4f}")
            self.logger.info(f"IC标准差: {ic_std.mean():.4f}")
            self.logger.info(f"平均IR: {ic_ir.mean():.4f}")
            
            # 计算各因子的IC/IR
            factor_analysis_result = {
                "ic": ic,
                "ic_mean": ic_mean,
                "ic_std": ic_std,
                "ic_ir": ic_ir
            }
            
            return factor_analysis_result
        except Exception as e:
            self.logger.error(f"因子分析失败: {e}")
            raise
    
    def train_model(self, handler, model_config=None):
        """
        训练因子模型
        """
        try:
            self.logger.info("开始训练因子模型")
            
            # 默认使用LGBModel
            if model_config is None:
                model_config = {
                    "class": "LGBModel",
                    "module_path": "qlib.contrib.model.gbdt",
                    "kwargs": {
                        "loss": "mse",
                        "colsample_bytree": 0.8879,
                        "learning_rate": 0.0421,
                        "subsample": 0.8789,
                        "lambda_l1": 205.6999,
                        "lambda_l2": 580.9768,
                        "max_depth": 8,
                        "num_leaves": 210,
                        "num_threads": 20,
                    },
                }
            
            # 初始化模型
            model = init_instance_by_config(model_config)
            
            # 获取训练和测试数据
            train_data, test_data = handler.prepare(
                [handler.get_cols(feature_group="feature"), handler.get_cols(feature_group="label")],
                mix=False
            )
            
            # 训练模型
            model.fit(train_data)
            
            self.logger.info("模型训练完成")
            return model
        except Exception as e:
            self.logger.error(f"训练模型失败: {e}")
            raise
    
    def backtest_strategy(self, model, handler, start_time="2020-01-01", end_time="2020-12-31"):
        """
        使用训练好的因子进行回测
        """
        try:
            self.logger.info(f"开始回测，时间范围: {start_time} - {end_time}")
            
            # 定义策略配置
            strategy_config = {
                "class": "TopkDropoutStrategy",
                "module_path": "qlib.contrib.strategy",
                "kwargs": {
                    "topk": 50,
                    "n_drop": 5,
                },
            }
            
            # 定义回测配置
            backtest_config = {
                "start_time": start_time,
                "end_time": end_time,
                "account": 1000000,
                "benchmark": "SH000300",
                "exchange_kwargs": {
                    "freq": "day",
                    "limit_threshold": 0.095,
                    "deal_price": "close",
                    "open_cost": 0.0005,
                    "close_cost": 0.0015,
                    "min_cost": 5,
                },
            }
            
            # 获取回测数据
            _, port_gen = backtest(
                model=model,
                strategy=strategy_config,
                handler=handler,
                backtest_config=backtest_config,
                verbose=True
            )
            
            # 计算回测指标
            report_normal, positions = analysis_position.report_graph(port_gen)
            analysis_result = dict(**report_normal, **positions)
            
            # 风险分析
            risk_analysis_result = risk_analysis(analysis_result, mode="simple")
            
            self.logger.info("回测完成")
            return risk_analysis_result
        except Exception as e:
            self.logger.error(f"回测失败: {e}")
            raise
    
    def run_end_to_end_analysis(self, instruments=None, start_time="2010-01-01", end_time="2020-12-31"):
        """
        运行端到端因子分析
        """
        try:
            self.logger.info("开始端到端因子分析")
            
            # 1. 加载数据
            handler = self.load_data(instruments=instruments, start_time=start_time, end_time=end_time)
            
            # 2. 计算因子
            factors, labels = self.calculate_factors(handler)
            
            # 3. 因子分析
            factor_analysis_result = self.analyze_factors(factors, labels)
            
            # 4. 训练模型
            model = self.train_model(handler)
            
            # 5. 回测策略
            # 使用后一半时间作为回测期
            mid_time = f"{int((int(start_time[:4]) + int(end_time[:4])) / 2)}-01-01"
            backtest_result = self.backtest_strategy(model, handler, start_time=mid_time, end_time=end_time)
            
            self.logger.info("端到端因子分析完成")
            
            return {
                "factor_analysis": factor_analysis_result,
                "backtest_result": backtest_result
            }
        except Exception as e:
            self.logger.error(f"端到端因子分析失败: {e}")
            raise
    
    def close(self):
        """
        关闭Qlib环境
        """
        try:
            qlib.exit()
            self.logger.info("Qlib环境已关闭")
        except Exception as e:
            self.logger.error(f"关闭Qlib环境失败: {e}")
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()