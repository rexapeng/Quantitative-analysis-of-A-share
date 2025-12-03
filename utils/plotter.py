import matplotlib.pyplot as plt
import os
from config import RESULT_DIR, TIMESTAMP, PLOT_SAVE_FORMAT, PLOT_WIDTH, PLOT_HEIGHT, PLOT_STYLE
from logger_config import engine_logger

plt.style.use(PLOT_STYLE)

class Plotter:
    def __init__(self, cerebro):
        self.cerebro = cerebro
        self.logger = engine_logger
        
    def save_plot(self):
        """保存图表"""
        try:
            self.logger.info("开始绘制并保存图表")
            
            # 兼容性修复：检查并添加_exactbars属性
            if not hasattr(self.cerebro, '_exactbars'):
                self.cerebro._exactbars = 0
            
            # 设置图形大小
            figs = self.cerebro.plot()
            
            # 保存图表
            for i, fig_list in enumerate(figs):
                for j, fig in enumerate(fig_list):
                    filename = os.path.join(
                        RESULT_DIR, 
                        f"backtest_plot_{TIMESTAMP}_{i}_{j}.{PLOT_SAVE_FORMAT}"
                    )
                    fig.set_size_inches(PLOT_WIDTH, PLOT_HEIGHT)
                    fig.savefig(filename, dpi=300, bbox_inches='tight')
                    self.logger.info(f"图表已保存: {filename}")
                    
            plt.close('all')  # 关闭所有图形以释放内存
            self.logger.info("图表绘制完成")
            
        except Exception as e:
            self.logger.error(f"图表绘制失败: {e}")
            raise