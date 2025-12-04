import pandas as pd
import os
import alphalens as al
import matplotlib.pyplot as plt
from data.data_feed import AStockDataLoader
from factor.factor_calculator import FactorCalculator
from factor.factor_preprocessor import FactorPreprocessor
from config import DATA_DIR, SINGLE_STOCK, ALPHALENS_SETTINGS
from logger_config import data_logger

def run_factor_analysis():
    """
    运行完整的因子分析流程，使用Alphalens库简化分析过程
    """
    data_logger.info("开始因子分析流程（使用Alphalens）")
    
    # 1. 加载数据
    file_path = os.path.join(DATA_DIR, f"{SINGLE_STOCK}.csv")
    data_logger.info(f"加载数据: {file_path}")
    df = AStockDataLoader.load_single_csv(file_path)
    
    # 2. 计算因子
    calculator = FactorCalculator()
    factor_df = calculator.calculate_all_factors(df)
    data_logger.info(f"因子计算完成，共{len(factor_df.columns)}列")
    
    # 3. 因子预处理
    preprocessor = FactorPreprocessor()
    processed_df = preprocessor.preprocess_factors(
        factor_df, 
        method='standard'
    )
    
    # 4. 准备Alphalens所需的数据格式
    # 获取因子列（排除基本的价格和成交量列）
    basic_cols = ['open', 'high', 'low', 'close', 'volume', 'preclose', 'turn', 'pctChg', 'date']
    factor_cols = [col for col in processed_df.columns if col not in basic_cols]
    
    # 创建价格数据（用于计算收益）
    prices = processed_df[['close']].copy()
    prices.index = processed_df.index
    
    # 选取几个代表性的因子进行分析
    selected_factors = ['RSI', 'MACD_HIST', 'BB_POSITION', 'VOLUME_RATIO'][:2]  # 限制为2个因子避免过多输出
    
    for factor_name in selected_factors:
        if factor_name not in processed_df.columns:
            continue
            
        # 构建因子数据
        factor_series = processed_df[factor_name].dropna()
        
        # 构建价格数据
        price_data = processed_df.loc[factor_series.index, 'close']
        # 重新构建索引以确保对应关系正确
        factor_data = pd.Series(factor_series.values, 
                               index=pd.MultiIndex.from_arrays([
                                   factor_series.index, 
                                   [SINGLE_STOCK] * len(factor_series)
                               ], names=['date', 'asset']))
        
        prices_data = pd.DataFrame({
            SINGLE_STOCK: price_data
        }).loc[price_data.index]
        
        try:
            # 使用Alphalens进行因子分析
            factor_data = factor_data.dropna()
            factor_clean = al.utils.get_clean_factor_and_forward_returns(
                factor=factor_data,
                prices=prices_data,
                periods=ALPHALENS_SETTINGS['periods'],
                max_loss=ALPHALENS_SETTINGS['max_loss'],
                quantiles=ALPHALENS_SETTINGS['quantiles']
            )
            
            # 创建分析结果目录
            results_dir = "factor_results"
            os.makedirs(results_dir, exist_ok=True)
            
            # 生成报告
            print(f"\n=== {factor_name} 因子分析报告 ===")
            
            # 1. 因子收益率分析
            mean_ret_by_q = al.performance.mean_return_by_quantile(factor_clean)
            print("各分位数组平均收益:")
            print(mean_ret_by_q[0].tail())
            
            # 2. 信息系数(IC)
            ic = al.performance.factor_information_coefficient(factor_clean)
            print(f"\n信息系数(IC)统计:")
            print(ic.describe())
            
            # 3. 因子换手率
            turnover = al.performance.factor_rank_autocorrelation(factor_clean)
            print(f"\n因子自相关性(换手率):")
            print(turnover.tail())
            
            # 4. 生成图表
            # 因子分位数组收益图
            al.plotting.plot_quantile_returns_bar(mean_ret_by_q, 
                                                 title=f"{factor_name}因子各分位数组平均收益")
            plt.savefig(os.path.join(results_dir, f"{factor_name}_quantile_returns.png"), 
                       bbox_inches='tight', dpi=300)
            
            # 因子收益率随时间变化
            al.plotting.plot_quantile_returns_violin(mean_ret_by_q, 
                                                    title=f"{factor_name}因子各分位数组收益分布")
            plt.savefig(os.path.join(results_dir, f"{factor_name}_returns_violin.png"), 
                       bbox_inches='tight', dpi=300)
            
            # IC值时间序列图
            al.plotting.plot_ic_ts(ic, title=f"{factor_name}因子信息系数(IC)时间序列")
            plt.savefig(os.path.join(results_dir, f"{factor_name}_ic_ts.png"), 
                       bbox_inches='tight', dpi=300)
            
            # IC值分布直方图
            al.plotting.plot_ic_hist(ic, title=f"{factor_name}因子信息系数(IC)分布")
            plt.savefig(os.path.join(results_dir, f"{factor_name}_ic_hist.png"), 
                       bbox_inches='tight', dpi=300)
            
            plt.close('all')
            
            data_logger.info(f"{factor_name}因子分析完成，结果已保存到{results_dir}目录")
            
        except Exception as e:
            data_logger.error(f"{factor_name}因子分析失败: {e}")
            continue
    
    data_logger.info("因子分析流程完成（使用Alphalens）")

if __name__ == "__main__":
    run_factor_analysis()