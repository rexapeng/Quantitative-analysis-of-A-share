import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_DIR, TIMESTAMP

def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器（循环日志）
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建不同的日志记录器
main_logger = setup_logger('main', f'main_{TIMESTAMP}.log')
engine_logger = setup_logger('engine', f'engine_{TIMESTAMP}.log')
strategy_logger = setup_logger('strategy', f'strategy_{TIMESTAMP}.log')
data_logger = setup_logger('data', f'data_{TIMESTAMP}.log')