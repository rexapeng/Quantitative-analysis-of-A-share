# 基础类
from .base import Factor, FactorManager


# 成交量类因子
from .volume_factors import (
    VolumeFactor, AmountFactor, VolumeChangeRateFactor, AmountChangeRateFactor,
    VolumeRankFactor, VolumeMeanFactor, VolumeStdFactor, VolumeToMeanFactor,
    VolumeAmplitudeFactor, VolumeAccumulationFactor
)

# 趋势类因子
from .trend_factors import (
    MA5Factor, MA10Factor, MA20Factor, MA50Factor, MA100Factor,
    EMA5Factor, EMA12Factor, EMA20Factor, EMA26Factor, EMA50Factor, EMA100Factor, EMA200Factor,
    SMA60Factor, SMA120Factor, SMA240Factor,
    MACDFactor, MACD_SignalFactor, MACD_HistogramFactor, MACD_CrossoverFactor,
    RSI3Factor, RSI7Factor, RSI14Factor, RSI21Factor, RSI28Factor,
    ADXFactor, ADX20Factor, ADX28Factor,
    ATRFactor, ATR7Factor, ATR20Factor,
    BollingerBandFactor, ParabolicSARFactor,
    CCI7Factor, CCI14Factor, CCI21Factor,
    DMAFactor
)

# 波动性类因子
from .volatility_factors import (
    BollingerBandsFactor, TrueRangeFactor, AverageTrueRangeFactor, 
    VolatilityFactor, DownsideDeviationFactor, UlcerIndexFactor, 
    HistoricalVolatilityFactor, ParkinsonVolatilityFactor
)

# 动量类因子
from .momentum_factors import (
    MomentumFactor, RSIFactor, MACDFactor, WilliamsRFactor, StochasticFactor,
    RateOfChangeFactor
)

# 形态类因子
from .pattern_factors import (
    DoubleBottomFactor, DoubleTopFactor,
    HeadShoulderBottomFactor, HeadShoulderTopFactor,
    TripleBottomFactor, TripleTopFactor,
    RoundBottomFactor, RoundTopFactor,
    VBottomFactor, VTopFactor,
    AscendingTriangleFactor, DescendingTriangleFactor,
    SymmetricalTriangleFactor, AscendingWedgeFactor,
    DescendingWedgeFactor, RectanglePatternFactor,
    GapPatternFactor, DojiPatternFactor,
    HammerPatternFactor
)

# 自定义因子
from .custom_factor_template import (
    CustomFactorTemplate, CustomMomentumFactor, CustomVolatilityFactor, CustomVolumeFactor,
    KDJ_J_Factor, MACD_DIFF_Factor
)

# 工具函数
from .utils import (
    get_database_connection, load_stock_data, load_stock_list, batch_process,
    calculate_execution_time, validate_factor_data, clean_factor_data,
    get_factor_table_name, create_factor_table, update_factor_table, get_all_factor_tables
)

__all__ = [
    # 基础类
    'Factor', 'FactorManager',
    
    
    # 成交量类因子
    'VolumeFactor', 'AmountFactor', 'VolumeChangeRateFactor', 'AmountChangeRateFactor',
    'VolumeRankFactor', 'VolumeMeanFactor', 'VolumeStdFactor', 'VolumeToMeanFactor',
    'VolumeAmplitudeFactor', 'VolumeAccumulationFactor',
    
    # 趋势类因子
    'MA5Factor', 'MA10Factor', 'MA20Factor', 'MA50Factor', 'MA100Factor',
    'EMA5Factor', 'EMA12Factor', 'EMA20Factor', 'EMA26Factor', 'EMA50Factor', 'EMA100Factor', 'EMA200Factor',
    'SMA60Factor', 'SMA120Factor', 'SMA240Factor',
    'MACDFactor', 'MACD_SignalFactor', 'MACD_HistogramFactor', 'MACD_CrossoverFactor',
    'RSI3Factor', 'RSI7Factor', 'RSI14Factor', 'RSI21Factor', 'RSI28Factor',
    'ADXFactor', 'ADX20Factor', 'ADX28Factor',
    'ATRFactor', 'ATR7Factor', 'ATR20Factor',
    'BollingerBandFactor', 'ParabolicSARFactor',
    'CCI7Factor', 'CCI14Factor', 'CCI21Factor',
    'DMAFactor',
    
    # 波动性类因子
    'BollingerBandsFactor', 'TrueRangeFactor', 'AverageTrueRangeFactor', 
    'VolatilityFactor', 'DownsideDeviationFactor', 'UlcerIndexFactor', 
    'HistoricalVolatilityFactor', 'ParkinsonVolatilityFactor',
    
    # 动量类因子
    'MomentumFactor', 'RSIFactor', 'MACDFactor', 'WilliamsRFactor', 'StochasticFactor',
    'RateOfChangeFactor',
    
    # 形态类因子
    'DoubleBottomPatternFactor', 'DoubleTopPatternFactor',
    'HeadAndShouldersBottomPatternFactor', 'HeadAndShouldersTopPatternFactor',
    'TripleBottomPatternFactor', 'TripleTopPatternFactor',
    'CupAndHandlePatternFactor', 'InverseCupAndHandlePatternFactor',
    'VBottomPatternFactor', 'VTopPatternFactor',
    'AscendingTrianglePatternFactor', 'DescendingTrianglePatternFactor',
    'SymmetricalTrianglePatternFactor', 'AscendingWedgePatternFactor',
    'DescendingWedgePatternFactor', 'RectanglePatternFactor',
    'GapPatternFactor', 'DojiPatternFactor',
    'HammerPatternFactor', 'ShootingStarPatternFactor',
    'MorningStarPatternFactor', 'EveningStarPatternFactor',
    
    # 自定义因子
    'CustomFactorTemplate', 'CustomMomentumFactor', 'CustomVolatilityFactor', 'CustomVolumeFactor', 'KDJ_J_Factor', 'MACD_DIFF_Factor',
    
    # 工具函数
    'get_database_connection', 'load_stock_data', 'load_stock_list', 'batch_process',
    'calculate_execution_time', 'validate_factor_data', 'clean_factor_data',
    'get_factor_table_name', 'create_factor_table', 'update_factor_table', 'get_all_factor_tables',
    
    # 动态加载函数
    'get_all_factor_classes', 'get_factor_classes_by_category'
]

def get_all_factor_classes():
    """
    获取所有因子类的列表，用于动态加载因子
    
    Returns:
        list: 所有Factor的子类
    """
    import inspect
    
    # 获取当前模块
    current_module = __import__(__name__)
    
    # 收集所有Factor的子类
    factor_classes = []
    for name in __all__:
        obj = getattr(current_module, name, None)
        if inspect.isclass(obj) and issubclass(obj, Factor) and obj is not Factor:
            factor_classes.append(obj)
    
    return factor_classes

def get_factor_classes_by_category():
    """
    按类别获取因子类
    
    Returns:
        dict: 按类别分类的因子类字典
    """
    # 定义因子类别和对应的类名
    categories = {
        'volume': [
            'VolumeFactor', 'AmountFactor', 'VolumeChangeRateFactor', 'AmountChangeRateFactor',
            'VolumeRankFactor', 'VolumeMeanFactor', 'VolumeStdFactor', 'VolumeToMeanFactor',
            'VolumeAmplitudeFactor', 'VolumeAccumulationFactor'
        ],
        'volatility': [
            'BollingerBandsFactor', 'TrueRangeFactor', 'AverageTrueRangeFactor', 
            'VolatilityFactor', 'DownsideDeviationFactor', 'UlcerIndexFactor', 
            'HistoricalVolatilityFactor', 'ParkinsonVolatilityFactor'
        ],
        'momentum': [
            'MomentumFactor', 'RSIFactor', 'MACDFactor', 'WilliamsRFactor', 'StochasticFactor',
            'RateOfChangeFactor'
        ],
        'trend': [
            'MA5Factor', 'MA10Factor', 'MA20Factor', 'MA50Factor', 'MA100Factor',
            'EMA5Factor', 'EMA12Factor', 'EMA20Factor', 'EMA26Factor', 'EMA50Factor', 'EMA100Factor', 'EMA200Factor',
            'SMA60Factor', 'SMA120Factor', 'SMA240Factor',
            'MACD_SignalFactor', 'MACD_HistogramFactor', 'MACD_CrossoverFactor',
            'RSI3Factor', 'RSI7Factor', 'RSI14Factor', 'RSI21Factor', 'RSI28Factor',
            'ADXFactor', 'ADX20Factor', 'ADX28Factor',
            'ATRFactor', 'ATR7Factor', 'ATR20Factor',
            'BollingerBandFactor', 'ParabolicSARFactor',
            'CCI7Factor', 'CCI14Factor', 'CCI21Factor',
            'DMAFactor'
        ],
        'pattern': [
            'DoubleBottomPatternFactor', 'DoubleTopPatternFactor',
            'HeadAndShouldersBottomPatternFactor', 'HeadAndShouldersTopPatternFactor',
            'TripleBottomPatternFactor', 'TripleTopPatternFactor',
            'CupAndHandlePatternFactor', 'InverseCupAndHandlePatternFactor',
            'VBottomPatternFactor', 'VTopPatternFactor',
            'AscendingTrianglePatternFactor', 'DescendingTrianglePatternFactor',
            'SymmetricalTrianglePatternFactor', 'AscendingWedgePatternFactor',
            'DescendingWedgePatternFactor', 'RectanglePatternFactor',
            'GapPatternFactor', 'DojiPatternFactor',
            'HammerPatternFactor', 'ShootingStarPatternFactor',
            'MorningStarPatternFactor', 'EveningStarPatternFactor'
        ],
        'custom': [
            'CustomFactorTemplate', 'CustomMomentumFactor', 'CustomVolatilityFactor', 'CustomVolumeFactor',
            'KDJ_J_Factor', 'MACD_DIFF_Factor'
        ]
    }
    
    # 获取当前模块
    current_module = __import__(__name__)
    
    # 按类别收集因子类
    result = {}
    for category, class_names in categories.items():
        result[category] = []
        for class_name in class_names:
            obj = getattr(current_module, class_name, None)
            if obj:
                result[category].append(obj)
    
    return result