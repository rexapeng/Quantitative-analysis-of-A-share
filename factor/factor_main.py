import pandas as pd
import os
from data.data_feed import AStockDataLoader
from factor.factor_calculator import FactorCalculator
from factor.factor_preprocessor import FactorPreprocessor
from factor.factor_analyzer import FactorAnalyzer
from factor.factor_combiner import FactorCombiner
from factor.portfolio_analyzer import PortfolioAnalyzer
from config import DATA_DIR, SINGLE_STOCK, FACTOR_CONFIG
from logger_config import data_logger

def run_factor_analysis():
    """
    运行完整的因子分析流程
    """
    data_logger.info("开始因子分析流程")
    
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
        method=FACTOR_CONFIG['preprocessing_method']
    )
    
    # 4. 因子分析
    analyzer = FactorAnalyzer()
    analysis_results = analyzer.analyze_factor_returns(
        processed_df, 
        forward_periods=FACTOR_CONFIG['forward_periods']
    )
    
    # 5. 获取表现最好的因子
    top_factors = analyzer.get_top_factors(period=1, top_n=10)
    print("Top 10 Factors by IC:")
    print(top_factors)
    
    # 6. 因子组合
    combiner = FactorCombiner()
    top_factor_names = top_factors.head(5)['factor'].tolist()
    
    # IC加权合成
    ic_combined = combiner.combine_factors_ic_weighted(
        processed_df, 
        top_factor_names
    )
    
    # 回归合成
    regression_combined = combiner.combine_factors_regression(
        processed_df, 
        top_factor_names
    )
    
    # 排序和合成
    rank_combined = combiner.combine_factors_rank_sum(
        processed_df, 
        top_factor_names
    )
    
    # 7. 组合分析
    portfolio_analyzer = PortfolioAnalyzer()
    
    # 使用合成因子构建组合
    processed_df['combined_factor'] = ic_combined
    portfolio_df = portfolio_analyzer.construct_factor_portfolio(
        processed_df, 
        'combined_factor', 
        n_quantiles=FACTOR_CONFIG['n_quantiles']
    )
    
    # 计算组合收益
    portfolio_returns = portfolio_analyzer.calculate_portfolio_returns(portfolio_df)
    print("\nPortfolio Returns:")
    print(portfolio_returns)
    
    # 计算IC指标
    ic_metrics = portfolio_analyzer.calculate_ic_metrics(
        processed_df, 
        'combined_factor'
    )
    print("\nIC Metrics:")
    for key, value in ic_metrics.items():
        print(f"{key}: {value}")
    
    data_logger.info("因子分析流程完成")

if __name__ == "__main__":
    run_factor_analysis()