import pandas as pd
import numpy as np
import os
import sys
import datetime
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# 添加项目根目录到sys.path以简化导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入配置
from config.config import CLEANED_DATA_DIR, SINGLE_STOCK, FACTOR_CONFIG, FACTOR_DATA_DIR, FACTOR_ANALYSIS_SCOPE

# 导入数据加载器
from data.data_feed import AStockDataLoader

# 导入因子相关模块
from factor.factor_calculator import FactorCalculator
from factor.factor_preprocessor import FactorPreprocessor
from factor.factor_analyzer import FactorAnalyzer
from factor.factor_combiner import FactorCombiner
from factor.portfolio_analyzer import PortfolioAnalyzer
# 导入Qlib因子分析器
from factor.qlib_factor_analyzer import QlibFactorAnalyzer

# 导入日志
from config.logger_config import data_logger

print("所有模块导入完成！")

def run_factor_analysis():
    """
    运行完整的因子分析流程
    """
    data_logger.info("开始因子分析流程")
    
    # 检查用户是否在配置中选择了特定的收益率周期
    user_selected_period = FACTOR_CONFIG.get('user_selected_period')
    if user_selected_period is not None:
        if 1 <= user_selected_period <= 60:
            data_logger.info(f"使用用户选择的收益率周期: {user_selected_period}日")
            # 更新forward_periods为用户选择的周期
            FACTOR_CONFIG['forward_periods'] = [user_selected_period]
        else:
            data_logger.warning(f"用户选择的收益率周期 {user_selected_period} 无效（应为1-60日），将使用默认周期")
    else:
        data_logger.info(f"使用默认的收益率周期: {FACTOR_CONFIG['forward_periods']}")
    
    # 获取分析范围配置
    scope_type = FACTOR_ANALYSIS_SCOPE['scope_type']
    
    # 确保因子数据保存目录存在
    if not os.path.exists(FACTOR_DATA_DIR):
        os.makedirs(FACTOR_DATA_DIR)
        data_logger.info(f"创建目录: {FACTOR_DATA_DIR}")
    
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    
    # 检查是否使用Qlib进行因子分析
    use_qlib = FACTOR_ANALYSIS_SCOPE.get('use_qlib', False)
    
    if use_qlib:
        # 使用Qlib进行端到端因子分析
        run_qlib_factor_analysis(current_date)
    elif scope_type == 'single_stock':
        # 单只股票分析模式
        stock_code = FACTOR_ANALYSIS_SCOPE.get('single_stock', SINGLE_STOCK)
        run_single_stock_analysis(stock_code, current_date)
    elif scope_type == 'index_components':
        # 指数成分股分析模式
        index_code = FACTOR_ANALYSIS_SCOPE.get('index_code', 'hs300')
        run_index_components_analysis(index_code, current_date)
    else:
        data_logger.error(f"无效的分析范围类型: {scope_type}")
    
    data_logger.info("因子分析流程完成")

def run_qlib_factor_analysis(current_date):
    """
    使用Qlib库进行端到端因子分析
    """
    data_logger.info("开始使用Qlib进行端到端因子分析")
    
    try:
        # 创建Qlib因子分析器实例
        analyzer = QlibFactorAnalyzer()
        
        # 运行端到端分析
        results = analyzer.run_end_to_end_analysis(
            instruments="csi300",  # 使用沪深300成分股
            start_time="2015-01-01",
            end_time="2020-12-31"
        )
        
        # 保存分析结果
        output_dir = os.path.join(os.path.dirname(__file__), 'output', 'qlib_reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存因子分析结果
        factor_analysis_file = os.path.join(output_dir, f"qlib_factor_analysis_{current_date}.json")
        import json
        with open(factor_analysis_file, 'w', encoding='utf-8') as f:
            # 转换numpy类型为Python原生类型
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, (np.float64, np.float32)):
                    return float(obj)
                elif isinstance(obj, (np.int64, np.int32)):
                    return int(obj)
                elif isinstance(obj, dict):
                    return {k: convert_numpy(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                return obj
            
            json.dump(convert_numpy(results), f, indent=2, ensure_ascii=False)
        
        data_logger.info(f"Qlib因子分析结果保存到: {factor_analysis_file}")
        
        # 保存回测结果到CSV
        backtest_file = os.path.join(output_dir, f"qlib_backtest_results_{current_date}.csv")
        if 'backtest_result' in results:
            backtest_df = pd.DataFrame(results['backtest_result'], index=[0])
            backtest_df.to_csv(backtest_file, index=False)
            data_logger.info(f"Qlib回测结果保存到: {backtest_file}")
        
        print("\n=== Qlib因子分析完成 ===")
        print("回测结果:")
        if 'backtest_result' in results:
            for key, value in results['backtest_result'].items():
                print(f"{key}: {value}")
        
    except Exception as e:
        data_logger.error(f"Qlib因子分析失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()
    
    data_logger.info("Qlib因子分析流程完成")

def run_single_stock_analysis(stock_code, current_date):
    """
    对单只股票进行因子分析
    """
    data_logger.info(f"开始单只股票分析: {stock_code}")
    
    # 1. 加载数据
    file_path = os.path.join(CLEANED_DATA_DIR, f"{stock_code}_history.csv")
    if not os.path.exists(file_path):
        data_logger.error(f"数据文件不存在: {file_path}")
        return
    
    data_logger.info(f"加载数据: {file_path}")
    df = AStockDataLoader.load_single_csv(file_path)
    
    # 2. 计算因子
    calculator = FactorCalculator()
    factor_df = calculator.calculate_all_factors(df)
    data_logger.info(f"因子计算完成，共{len(factor_df.columns)}列")
    
    # 保存原始因子数据
    raw_factor_file = os.path.join(FACTOR_DATA_DIR, f"{stock_code}_raw_factors_{current_date}.csv")
    factor_df.to_csv(raw_factor_file, index=True)
    data_logger.info(f"原始因子数据保存到: {raw_factor_file}")
    
    # 暂时不进行预处理，等合并所有股票数据后进行横截面标准化
    processed_df = factor_df
    
    # 保存预处理后的因子数据
    processed_factor_file = os.path.join(FACTOR_DATA_DIR, f"{stock_code}_processed_factors_{current_date}.csv")
    processed_df.to_csv(processed_factor_file, index=True)
    data_logger.info(f"预处理后的因子数据保存到: {processed_factor_file}")
    
    # 4. 因子分析
    analyzer = FactorAnalyzer()
    analysis_results = analyzer.analyze_factor_returns(
        processed_df, 
        forward_periods=FACTOR_CONFIG['forward_periods']
    )
    
    # 5. 获取表现最好的因子
    # 遍历所有预测周期，分别打印IC值
    for period in FACTOR_CONFIG['forward_periods']:
        print(f"\n\n=== {period}日收益率对应的因子IC值 ===")
        
        # 打印Top 10因子
        top_factors = analyzer.get_top_factors(period=period, top_n=10)
        print(f"Top 10 Factors by IC ({period}日周期):")
        print(top_factors.to_string())
        
        # 打印所有因子的IC值
        print(f"\nAll Factors IC Values ({period}日周期):")
        all_factors = analyzer.get_top_factors(period=period, top_n=100)
        print(all_factors.to_string())
    
    # 保存因子分析结果
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存因子分析结果到CSV文件
    ic_results_file = os.path.join(output_dir, f"{stock_code}_ic_results_{current_date}.csv")
    all_factors.to_csv(ic_results_file, index=False)
    data_logger.info(f"因子IC分析结果保存到: {ic_results_file}")
    
    # 保存详细的因子分析结果到JSON文件
    import json
    import datetime
    import numpy as np
    
    # 构造详细的IC结果（包含所有周期）
    detailed_ic_results = []
    for factor, results in analyzer.analysis_results.items():
        for period in FACTOR_CONFIG['forward_periods']:
            if period in results:
                result = results[period]
                detailed_ic_results.append({
                    'factor': factor,
                    'period': period,
                    'ic': result.get('ic', np.nan),
                    'mean_ic': result.get('mean_ic', np.nan),
                    'std_ic': result.get('std_ic', np.nan),
                    'ir': result.get('ir', np.nan),
                    'mean_spearman': result.get('mean_spearman', np.nan),
                    'positive_ic_rate': result.get('positive_ic_rate', np.nan)
                })
    
    # 保存到JSON文件
    json_results_file = os.path.join(output_dir, f"{stock_code}_detailed_ic_results_{current_date}.json")
    with open(json_results_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_ic_results, f, ensure_ascii=False, indent=2, default=str)
    data_logger.info(f"详细因子IC分析结果保存到: {json_results_file}")
    
    # 保存分析结果到Excel文件，方便查看
    try:
        import pandas as pd
        detailed_df = pd.DataFrame(detailed_ic_results)
        excel_results_file = os.path.join(output_dir, f"{stock_code}_ic_results_{current_date}.xlsx")
        detailed_df.to_excel(excel_results_file, index=False)
        data_logger.info(f"因子IC分析结果保存到Excel文件: {excel_results_file}")
    except ImportError:
        data_logger.warning("无法保存到Excel文件，需要安装openpyxl或xlrd库")
    
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

def process_single_stock(stock_code, cleaned_data_dir, preprocessing_method):
    """
    处理单只股票的因子计算和预处理
    这个函数将被多进程调用
    """
    file_path = os.path.join(cleaned_data_dir, f"{stock_code}_history.csv")
    
    if not os.path.exists(file_path):
        data_logger.warning(f"数据文件不存在: {file_path}")
        return None
    
    try:
        # 1. 加载数据
        df = AStockDataLoader.load_single_csv(file_path)
        
        # 2. 计算因子
        calculator = FactorCalculator()
        factor_df = calculator.calculate_all_factors(df)
        factor_df['code'] = stock_code  # 添加股票代码列
        
        # 3. 因子预处理
        preprocessor = FactorPreprocessor()
        processed_df = preprocessor.preprocess_factors(
            factor_df, 
            method=preprocessing_method
        )
        
        # 重置索引，避免合并时索引重复
        processed_df = processed_df.reset_index()
        return processed_df
        
    except Exception as e:
        data_logger.error(f"处理股票{stock_code}失败: {e}")
        return None

def run_index_components_analysis(index_code, current_date):
    """
    对指数成分股进行因子分析
    """
    data_logger.info(f"开始指数成分股分析: {index_code}")
    
    # 获取指数成分股列表
    # 这里需要根据实际情况从数据文件或数据库中获取成分股列表
    # 暂时使用示例代码，实际应用中需要替换为真实的成分股获取逻辑
    components = get_index_components(index_code)
    
    if not components:
        data_logger.error(f"未获取到{index_code}的成分股列表")
        return
    
    data_logger.info(f"共获取到{len(components)}只成分股")
    
    # 批量处理成分股 - 使用多进程
    all_processed_dfs = []
    
    # 设置进程池大小，使用50个进程
    num_processes = 50
    data_logger.info(f"使用{num_processes}个进程进行并行处理")
    
    # 准备参数列表
    params = [(stock_code, CLEANED_DATA_DIR, FACTOR_CONFIG['preprocessing_method']) for stock_code in components]
    
    # 使用进程池并行处理
    with Pool(processes=num_processes) as pool:
        # 使用tqdm显示进度
        results = list(tqdm(pool.starmap(process_single_stock, params, chunksize=10), 
                           desc="处理成分股", total=len(components)))
    
    # 收集结果，过滤掉None值
    for result in results:
        if result is not None:
            all_processed_dfs.append(result)
    
    if not all_processed_dfs:
        data_logger.error("没有成功处理任何成分股")
        return
    
    # 合并所有股票的处理后数据
    combined_df = pd.concat(all_processed_dfs, axis=0)
    
    # 获取因子数量信息
    basic_cols = ['open', 'high', 'low', 'close', 'volume', 'preclose', 'turn', 'pctChg', 'code', 'stock', 'date', 'adjustflag', 'tradestatus', 'isST', 'ten_day_return']
    factor_cols = [col for col in combined_df.columns if col not in basic_cols]
    data_logger.info(f"共计算得到{len(factor_cols)}个因子")
    data_logger.info(f"因子列列表: {factor_cols}")
    
    # 对合并后的数据进行横截面标准化（按日期分组）
    data_logger.info(f"开始对{len(factor_cols)}个因子进行横截面标准化")
    preprocessor = FactorPreprocessor()
    
    # 复制一份数据用于标准化
    standardized_df = combined_df.copy()
    
    # 检查并移除重复的(date, code)对
    data_logger.info(f"标准化前数据行数: {len(standardized_df)}")
    standardized_df = standardized_df.drop_duplicates(subset=['date', 'code'])
    data_logger.info(f"移除重复项后数据行数: {len(standardized_df)}")
    
    # 按日期分组，对每个日期的所有股票进行标准化
    for factor in tqdm(factor_cols, desc="进行横截面标准化"):
        # 检查是否为二值因子（只有0和1两个值）
        unique_values = standardized_df[factor].unique()
        is_binary_factor = len(unique_values) == 2 and set(unique_values).issubset({0, 1})
        
        if is_binary_factor:
            # 二值因子跳过标准化，保持原始值
            data_logger.info(f"因子{factor}是二值因子，跳过横截面标准化")
            continue
        else:
            # 使用rank转换代替standardize，因为rank转换更适合横截面比较
            standardized_df[factor] = standardized_df.groupby('date')[factor].rank(pct=True)
    
    data_logger.info(f"横截面标准化完成")
    
    # 使用股票代码和日期作为复合索引
    standardized_df.set_index(['date', 'code'], inplace=True)
    
    # 保存合并后的因子数据
    raw_factor_file = os.path.join(FACTOR_DATA_DIR, f"{index_code}_raw_factors_{current_date}.csv")
    combined_df.to_csv(raw_factor_file, index=True)
    data_logger.info(f"原始因子数据保存到: {raw_factor_file}")
    
    # 4. 因子分析
    analyzer = FactorAnalyzer()
    analysis_results = analyzer.analyze_factor_returns(
        standardized_df, 
        forward_periods=FACTOR_CONFIG['forward_periods']
    )
    
    # 5. 获取表现最好的因子
    # 遍历所有预测周期，分别打印和保存IC值
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    for period in FACTOR_CONFIG['forward_periods']:
        print(f"\n=== {period}日收益率对应的因子IC值 ({index_code}) ===")
        
        # 打印Top 10因子
        top_factors = analyzer.get_top_factors(period=period, top_n=10)
        print(f"\nTop 10 Factors by IC ({period}日周期):")
        print(top_factors)
        
        # 打印所有因子的IC值
        all_factors = analyzer.get_top_factors(period=period, top_n=100)
        print(f"\nAll Factors IC Values ({period}日周期):")
        print(all_factors.to_string())
        
        # 保存到CSV
        ic_file = os.path.join(output_dir, f"{index_code}_factor_ic_values_{period}day_{current_date}.csv")
        all_factors.to_csv(ic_file, index=True)
        data_logger.info(f"因子IC值 ({period}日周期) 保存到: {ic_file}")
    
    # 保存到JSON
    import json
    json_file = os.path.join(output_dir, f"{index_code}_factor_analysis_results_{current_date}.json")
    
    # 添加日志来检查analyzer.analysis_results的结构
    data_logger.info(f"分析结果包含的因子数: {len(analyzer.analysis_results)}")
    if analyzer.analysis_results:
        first_factor = next(iter(analyzer.analysis_results))
        data_logger.info(f"第一个因子 '{first_factor}' 包含的周期数: {len(analyzer.analysis_results[first_factor])}")
        data_logger.info(f"第一个因子包含的周期: {list(analyzer.analysis_results[first_factor].keys())}")
    
    # 构造详细的因子分析结果
    detailed_results = {}
    for factor, results in analyzer.analysis_results.items():
        detailed_results[factor] = {}
        for period, metrics in results.items():
            detailed_results[factor][f'period_{period}'] = {
                'ic': float(metrics['ic']) if not np.isnan(metrics['ic']) else None,
                'mean_ic': float(metrics['mean_ic']) if not np.isnan(metrics['mean_ic']) else None,
                'std_ic': float(metrics['std_ic']) if not np.isnan(metrics['std_ic']) else None,
                'ir': float(metrics['ir']) if not np.isnan(metrics['ir']) else None,
                'mean_spearman': float(metrics['mean_spearman']) if not np.isnan(metrics['mean_spearman']) else None,
                'positive_ic_rate': float(metrics['positive_ic_rate']) if not np.isnan(metrics['positive_ic_rate']) else None
            }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    data_logger.info(f"详细因子分析结果保存到: {json_file}")
    
    # 保存到Excel（如果可用）
    try:
        excel_file = os.path.join(output_dir, f"{index_code}_factor_analysis_results_{current_date}.xlsx")
        with pd.ExcelWriter(excel_file) as writer:
            all_factors.to_excel(writer, sheet_name='Top_Factors')
            
            # 保存每个周期的因子结果
            for period in FACTOR_CONFIG['forward_periods']:
                period_factors = []
                for factor, results in analyzer.analysis_results.items():
                    if period in results:
                        metrics = results[period]
                        period_factors.append({
                            'factor': factor,
                            'ic': metrics['ic'],
                            'mean_ic': metrics['mean_ic'],
                            'std_ic': metrics['std_ic'],
                            'ir': metrics['ir'],
                            'mean_spearman': metrics['mean_spearman'],
                            'positive_ic_rate': metrics['positive_ic_rate']
                        })
                
                period_df = pd.DataFrame(period_factors)
                period_df = period_df.sort_values('abs_ic', ascending=False) if 'abs_ic' in period_df.columns else period_df
                period_df.to_excel(writer, sheet_name=f'Period_{period}')
        
        data_logger.info(f"因子分析结果保存到Excel: {excel_file}")
    except ImportError:
        data_logger.warning("无法保存到Excel，需要安装openpyxl")
    
    # 6. 因子组合
    combiner = FactorCombiner()
    
    # 确保top_factors不为空且包含factor列
    if not top_factors.empty and 'factor' in top_factors.columns:
        top_factor_names = top_factors.head(5)['factor'].tolist()
        
        # IC加权合成
        ic_combined = combiner.combine_factors_ic_weighted(
            standardized_df, 
            top_factor_names
        )
        
        # 回归合成
        regression_combined = combiner.combine_factors_regression(
            standardized_df, 
            top_factor_names
        )
        
        # 排序和合成
        rank_combined = combiner.combine_factors_rank_sum(
            standardized_df, 
            top_factor_names
        )
        
        # 7. 组合分析
        portfolio_analyzer = PortfolioAnalyzer()
        
        # 使用合成因子构建组合
        # 确保ic_combined是Series类型
        if not isinstance(ic_combined, pd.Series):
            ic_combined = pd.Series(ic_combined)
        
        # 直接赋值，因为现在索引应该完全匹配
        standardized_df['combined_factor'] = ic_combined
        portfolio_df = portfolio_analyzer.construct_factor_portfolio(
            standardized_df, 
            'combined_factor', 
            n_quantiles=FACTOR_CONFIG['n_quantiles']
        )
        
        # 保存Q1-Q5组合的具体信息（包含股票代码、日期、因子值和组合标签）
        portfolio_details_file = os.path.join(output_dir, f"{index_code}_q1_q5_portfolios_{current_date}.csv")
        
        # 处理索引和列名冲突问题
        export_df = portfolio_df.copy()
        # 如果'date'列已经存在但索引中也有'date'级别，先删除列
        if 'date' in export_df.columns and 'date' in export_df.index.names:
            export_df = export_df.drop('date', axis=1)
        # 重置索引以包含日期和代码信息
        export_df.reset_index(inplace=True)
        # 保存到CSV文件
        export_df.to_csv(portfolio_details_file, index=True)
        data_logger.info(f"Q1-Q5组合详情保存到: {portfolio_details_file}")
        # 保持原始portfolio_df的索引不变，无需重新设置
        
        # 计算组合收益
        portfolio_returns = portfolio_analyzer.calculate_portfolio_returns(portfolio_df)
        print("\nPortfolio Returns:")
        print(portfolio_returns)
        
        # 显示Q1-Q5组合的部分详细信息
        print("\nQ1-Q5组合示例数据（前10条）:")
        print(portfolio_df[['combined_factor', 'portfolio']].head(10))
        
        # 保存Q1-Q5组合的详细信息到CSV文件
        output_dir = os.path.join(os.path.dirname(__file__), 'output', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        portfolio_details_file = os.path.join(output_dir, f"{index_code}_q1_q5_portfolios_{current_date}.csv")
        
        # 重置索引以包含日期和代码信息
        export_df = portfolio_df.copy()
        # 如果'date'列已经存在但索引中也有'date'级别，先删除列
        if 'date' in export_df.columns and 'date' in export_df.index.names:
            export_df = export_df.drop('date', axis=1)
        export_df = export_df.reset_index()
        
        # 只保存必要的列以减少文件大小
        columns_to_save = ['date', 'code', 'combined_factor', 'portfolio', 'pctChg']
        export_df = export_df[columns_to_save]
        
        # 保存到CSV文件
        export_df.to_csv(portfolio_details_file, index=False)
        print(f"\nQ1-Q5组合详细信息已保存到: {portfolio_details_file}")
        
        # 计算IC指标
        ic_metrics = portfolio_analyzer.calculate_ic_metrics(
            standardized_df, 
            'combined_factor'
        )
        print("\nIC Metrics:")
        for key, value in ic_metrics.items():
            print(f"{key}: {value}")
    else:
        data_logger.warning("没有足够的因子进行组合")
        return

def get_index_components(index_code):
    """
    获取指数成分股列表
    
    Args:
        index_code (str): 指数代码，如'hs300', 'zz500'等
        
    Returns:
        list: 成分股代码列表
    """
    # 获取实际存在的数据文件中的所有股票代码
    processed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    csv_files = [f for f in os.listdir(processed_dir) if f.endswith('_history.csv')]
    existing_stocks = [f.replace('_history.csv', '') for f in csv_files]
    
    data_logger.info(f"共获取到{len(existing_stocks)}只股票作为{index_code}成分股")
    
    return existing_stocks

if __name__ == "__main__":
    run_factor_analysis()