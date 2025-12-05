import pandas as pd
import numpy as np
from typing import Dict, List
from scipy.stats import pearsonr, spearmanr
from tqdm import tqdm
from config.logger_config import data_logger

class FactorAnalyzer:
    """
    因子分析器，用于分析因子有效性
    """
    
    def __init__(self):
        self.logger = data_logger
        self.analysis_results = {}
        
    def analyze_factor_returns(self, df: pd.DataFrame, forward_periods: List[int] = [1, 5, 10]) -> Dict:
        """
        分析因子与未来收益的相关性
        
        Parameters:
        df: 包含因子和收益率的数据
        forward_periods: 向前预测的周期列表
        
        Returns:
        分析结果字典
        """
        if df is None or df.empty:
            self.logger.error("输入数据为空，无法进行因子分析")
            return {}
            
        # 确保日期是索引或列，避免同时存在日期列和日期索引级别
        has_date_column = 'date' in df.columns
        has_date_index = 'date' in df.index.names
        
        # 如果date同时是索引和列，移除date列以避免歧义
        if has_date_column and has_date_index:
            df = df.drop('date', axis=1)
            has_date_column = False
            self.logger.info("数据同时包含date列和date索引级别，已移除date列")
        
        # 处理日期信息
        if has_date_column:
            try:
                df['date'] = pd.to_datetime(df['date'])
            except Exception as e:
                self.logger.error(f"转换日期列失败: {e}")
        elif has_date_index:
            # 单一索引情况
            if len(df.index.names) == 1:
                df.index = pd.to_datetime(df.index)
            # 复合索引情况 - 不创建临时date列，后续操作通过索引访问
            else:
                try:
                    # 确保date索引是datetime类型
                    df = df.reorder_levels(['date', 'code']) if 'code' in df.index.names else df
                    df.index.set_levels(pd.to_datetime(df.index.get_level_values('date')), level='date', inplace=True)
                except Exception as e:
                    self.logger.error(f"转换日期索引失败: {e}")
        else:
            self.logger.error("数据中缺少日期信息")
            return {}
        
        # 确保包含收盘价列用于计算收益率
        if 'close' not in df.columns:
            self.logger.error("数据中缺少收盘价(close)列")
            return {}
        
        # 计算所需的未来收益率（如果不存在）
        for period in forward_periods:
            fwd_return_col = f'{period}_day_return'
            if fwd_return_col not in df.columns:
                # 按股票分组计算未来收益率
                self.logger.info(f"计算{period}日收益率")
                # 确保数据按股票和日期排序
                try:
                    if 'code' in df.columns:
                        if 'date' in df.columns:
                            df = df.sort_values(['code', 'date'])
                        elif 'date' in df.index.names:
                            df = df.sort_values(['code']).sort_index(level='date')
                        # 使用shift(-period)计算未来收益率
                        df[fwd_return_col] = df.groupby('code')['close'].pct_change(periods=period).shift(-period)
                    elif 'stock' in df.columns:
                        if 'date' in df.columns:
                            df = df.sort_values(['stock', 'date'])
                        elif 'date' in df.index.names:
                            df = df.sort_values(['stock']).sort_index(level='date')
                        # 使用shift(-period)计算未来收益率
                        df[fwd_return_col] = df.groupby('stock')['close'].pct_change(periods=period).shift(-period)
                    elif 'code' in df.index.names:
                        # 处理code作为索引的情况
                        df = df.sort_index()
                        df[fwd_return_col] = df.groupby(level='code')['close'].pct_change(periods=period).shift(-period)
                    elif 'stock' in df.index.names:
                        # 处理stock作为索引的情况
                        df = df.sort_index()
                        df[fwd_return_col] = df.groupby(level='stock')['close'].pct_change(periods=period).shift(-period)
                    else:
                        self.logger.error("数据中缺少股票标识列(code或stock)")
                        return {}
                except Exception as e:
                    self.logger.error(f"计算{period}日收益率时出错: {e}")
                    return {}
        
        self.logger.info(f"开始分析因子对未来收益的预测能力，当前数据包含{len(df)}行，{len(df.columns)}列")
        results = {}
        
        # 获取所有因子列（排除基本行情列和收益率列）
        basic_cols = ['open', 'high', 'low', 'close', 'volume', 'preclose', 'turn', 'pctChg', 'code', 'stock', 'adjustflag', 'tradestatus', 'isST']
        # 排除所有收益率列
        return_cols = [col for col in df.columns if '_day_return' in col]
        exclude_cols = basic_cols + return_cols + ['date']
        factor_cols = [col for col in df.columns if col not in exclude_cols]
        
        self.logger.info(f"检测到{len(factor_cols)}个因子列: {factor_cols}")
        
        # 计算每个因子与未来收益的相关性
        for factor in tqdm(factor_cols, desc="分析因子有效性"):
            if factor not in df.columns:
                continue
                
            results[factor] = {}
            
            # 遍历每个预测周期
            for period in forward_periods:
                fwd_return_col = f'{period}_day_return'  # 使用计算好的收益率
            
                # 检查因子的整体分布情况，特别是KDJ_J_LESS_THAN_0
                if factor == 'KDJ_J_LESS_THAN_0':
                    self.logger.info(f"因子{factor}的整体分布：唯一值={df[factor].nunique()}, 均值={df[factor].mean():.4f}, 标准差={df[factor].std():.4f}, NaN值占比={df[factor].isna().mean():.4f}")
                
                # 判断是单只股票还是多只股票
                is_single_stock = False
                stock_count = 0
                if 'code' in df.columns:
                    stock_count = df['code'].nunique()
                elif 'stock' in df.columns:
                    stock_count = df['stock'].nunique()
                elif 'code' in df.index.names:
                    stock_count = df.index.get_level_values('code').nunique()
                elif 'stock' in df.index.names:
                    stock_count = df.index.get_level_values('stock').nunique()
                
                if stock_count == 1:
                    self.logger.info(f"检测到单只股票，将使用时间序列相关性分析")
                    is_single_stock = True
                
                try:
                    if is_single_stock:
                        # 单只股票：使用时间序列相关性分析
                        valid_data = df[[factor, fwd_return_col]].dropna()
                        
                        if len(valid_data) < 30:  # 时间序列数据太少则跳过
                            self.logger.warning(f"因子{factor}的有效时间序列数据不足30个样本，跳过分析")
                            daily_ics = []
                            daily_spearmans = []
                        else:
                            # 检查数据是否为恒定值
                            if valid_data[factor].nunique() == 1 or valid_data[fwd_return_col].nunique() == 1:
                                self.logger.warning(f"因子{factor}或收益率数据为恒定值，无法计算相关性")
                                daily_ics = []
                                daily_spearmans = []
                            else:
                                # 计算时间序列相关性
                                pearson_ic, _ = pearsonr(valid_data[factor], valid_data[fwd_return_col])
                                spearman_corr, _ = spearmanr(valid_data[factor], valid_data[fwd_return_col])
                                
                                daily_ics = [pearson_ic] if not np.isnan(pearson_ic) else []
                                daily_spearmans = [spearman_corr] if not np.isnan(spearman_corr) else []
                    else:
                        # 多只股票：使用横截面IC值分析（原逻辑）
                        daily_ics = []
                        daily_spearmans = []
                        
                        # 确保date存在（可能是索引或列）
                        if 'date' not in df.columns and 'date' not in df.index.names:
                            self.logger.error("数据中缺少date列或date索引")
                            continue
                        
                        # 遍历每个日期，先检查date是索引还是列
                        if 'date' in df.columns:
                            for date, date_data in df.groupby('date'):
                                valid_data = date_data[[factor, fwd_return_col]].dropna()
                                
                                if len(valid_data) < 20:  # 当天股票数量太少则跳过
                                    continue
                                
                                # 检查数据是否为恒定值
                                if valid_data[factor].nunique() == 1 or valid_data[fwd_return_col].nunique() == 1:
                                    # 对于KDJ_J_LESS_THAN_0因子，记录更多详细信息
                                    if factor == 'KDJ_J_LESS_THAN_0':
                                        self.logger.info(f"日期{date}: 因子{factor}值为恒定值={valid_data[factor].nunique()}, 唯一值={valid_data[factor].unique()[0]}, 有效股票数={len(valid_data)}")
                                    continue
                                
                                # 计算当天的IC值
                                pearson_ic, _ = pearsonr(valid_data[factor], valid_data[fwd_return_col])
                                spearman_corr, _ = spearmanr(valid_data[factor], valid_data[fwd_return_col])
                                
                                if not np.isnan(pearson_ic):
                                    daily_ics.append(pearson_ic)
                                if not np.isnan(spearman_corr):
                                    daily_spearmans.append(spearman_corr)
                        elif 'date' in df.index.names:
                            for date, date_data in df.groupby(level='date'):
                                valid_data = date_data[[factor, fwd_return_col]].dropna()
                                
                                if len(valid_data) < 20:  # 当天股票数量太少则跳过
                                    continue
                                
                                # 检查数据是否为恒定值
                                if valid_data[factor].nunique() == 1 or valid_data[fwd_return_col].nunique() == 1:
                                    # 对于KDJ_J_LESS_THAN_0因子，记录更多详细信息
                                    if factor == 'KDJ_J_LESS_THAN_0':
                                        self.logger.info(f"日期{date}: 因子{factor}值为恒定值={valid_data[factor].nunique()}, 唯一值={valid_data[factor].unique()[0]}, 有效股票数={len(valid_data)}")
                                    continue
                                
                                # 计算当天的IC值
                                pearson_ic, _ = pearsonr(valid_data[factor], valid_data[fwd_return_col])
                                spearman_corr, _ = spearmanr(valid_data[factor], valid_data[fwd_return_col])
                                
                                if not np.isnan(pearson_ic):
                                    daily_ics.append(pearson_ic)
                                if not np.isnan(spearman_corr):
                                    daily_spearmans.append(spearman_corr)
                        else:
                            self.logger.error("数据中缺少date列或date索引")
                            continue
                    
                    self.logger.info(f"因子{factor}的有效IC值数量: {len(daily_ics)}, 有效Spearman值数量: {len(daily_spearmans)}")
                    
                    if daily_ics:
                        # 计算平均IC值和相关统计量
                        mean_ic = np.mean(daily_ics)
                        std_ic = np.std(daily_ics)
                        ir = mean_ic / std_ic if std_ic != 0 else 0  # 信息比率
                        
                        mean_spearman = np.mean(daily_spearmans) if daily_spearmans else np.nan
                        
                        results[factor][period] = {
                            'mean_ic': mean_ic,
                            'std_ic': std_ic,
                            'ir': ir,
                            'mean_spearman': mean_spearman,
                            'ic': mean_ic,  # 使用平均IC值作为最终IC值
                            'positive_ic_rate': (np.array(daily_ics) > 0).mean()
                        }
                    else:
                        results[factor][period] = {
                            'mean_ic': np.nan,
                            'std_ic': np.nan,
                            'ir': np.nan,
                            'mean_spearman': np.nan,
                            'ic': np.nan,
                            'positive_ic_rate': np.nan
                        }
                except Exception as e:
                    self.logger.error(f"计算因子{factor}的IC值时出错: {e}")
                    results[factor][period] = {
                        'mean_ic': np.nan,
                        'std_ic': np.nan,
                        'ir': np.nan,
                        'mean_spearman': np.nan,
                        'ic': np.nan,
                        'positive_ic_rate': np.nan
                    }
        
        self.analysis_results = results
        
        # 记录有效因子分析结果的数量
        valid_results_count = sum(1 for factor, factor_results in results.items() 
                                 for period, metrics in factor_results.items() 
                                 if not np.isnan(metrics['ic']))
        self.logger.info(f"因子收益分析完成，共产生{valid_results_count}个有效因子分析结果")
        return results
    
    def get_top_factors(self, period: int = 10, top_n: int = 10) -> pd.DataFrame:
        """
        获取表现最好的因子
        
        Parameters:
        period: 预测周期
        top_n: 返回前N个因子
        
        Returns:
        包含因子IC值的DataFrame
        """
        if not self.analysis_results:
            raise ValueError("尚未进行因子分析，请先调用analyze_factor_returns方法")
            
        factor_ic = []
        for factor, results in self.analysis_results.items():
            if period in results:
                # 无论ic值是否有效，都将因子加入列表
                factor_ic.append({
                    'factor': factor,
                    'ic': results[period].get('ic', np.nan),
                    'abs_ic': abs(results[period].get('ic', np.nan)) if 'ic' in results[period] and not np.isnan(results[period].get('ic')) else np.nan,
                        'mean_ic': results[period].get('mean_ic', np.nan),
                        'std_ic': results[period].get('std_ic', np.nan),
                        'ir': results[period].get('ir', np.nan),
                        'mean_spearman': results[period].get('mean_spearman', np.nan),
                        'positive_ic_rate': results[period].get('positive_ic_rate', np.nan)
                    })
                
        df_ic = pd.DataFrame(factor_ic)
        
        # 即使没有数据，也确保DataFrame包含必要的列
        if df_ic.empty:
            self.logger.warning("没有有效的因子分析结果")
            return pd.DataFrame(columns=['factor', 'ic', 'abs_ic', 'mean_ic', 'std_ic', 'ir', 'mean_spearman', 'positive_ic_rate'])
        
        # 确保abs_ic列存在后再排序
        if 'abs_ic' in df_ic.columns:
            # 先尝试按abs_ic排序，如果有NaN值则放在最后
            df_ic = df_ic.sort_values('abs_ic', ascending=False, na_position='last')
            # 然后返回前top_n个因子，包含NaN值
            df_ic = df_ic.head(top_n)
        else:
            self.logger.error("abs_ic列不存在，无法进行排序")
            df_ic = df_ic.head(top_n)
        
        return df_ic
    
    def analyze_factor_stability(self, df: pd.DataFrame, factor: str, window: int = 60) -> Dict:
        """
        分析因子稳定性（滚动IC）
        
        Parameters:
        df: 数据
        factor: 因子名称
        window: 滚动窗口大小
        
        Returns:
        稳定性分析结果
        """
        if factor not in df.columns:
            raise ValueError(f"因子 {factor} 不存在于数据中")
            
        # 滚动计算IC值，使用十日收益率
        rolling_ic = []
        for i in range(window, len(df)):
            window_data = df.iloc[i-window:i]
            valid_data = window_data[[factor, 'ten_day_return']].dropna()
            
            if len(valid_data) > 10:
                ic, _ = pearsonr(valid_data[factor], valid_data['ten_day_return'])
                rolling_ic.append({
                    'date': df.index[i],
                    'ic': ic
                })
                
        if rolling_ic:
            ic_series = pd.DataFrame(rolling_ic).set_index('date')['ic']
            stability_metrics = {
                'mean_ic': ic_series.mean(),
                'std_ic': ic_series.std(),
                'ir': ic_series.mean() / ic_series.std() if ic_series.std() != 0 else 0,  # 信息比率
                'positive_ic_rate': (ic_series > 0).mean(),  # 正向IC占比
                'ic_series': ic_series
            }
            return stability_metrics
        else:
            return {}