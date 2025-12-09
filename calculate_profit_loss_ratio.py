import numpy as np

# 用户提供的分组数据
group_data = [
    {"group": 1, "avg_return": -0.005351, "win_rate": 0.4657},
    {"group": 2, "avg_return": 0.004766, "win_rate": 0.5006},
    {"group": 3, "avg_return": 0.010564, "win_rate": 0.5392},
    {"group": 4, "avg_return": 0.014811, "win_rate": 0.5651},
    {"group": 5, "avg_return": 0.018424, "win_rate": 0.5933},
    {"group": 6, "avg_return": 0.018683, "win_rate": 0.5852},
    {"group": 7, "avg_return": 0.018974, "win_rate": 0.5771},
    {"group": 8, "avg_return": 0.021771, "win_rate": 0.5874},
    {"group": 9, "avg_return": 0.024133, "win_rate": 0.6062},
    {"group": 10, "avg_return": 0.033343, "win_rate": 0.6360}
]

print("基于提供的分组收益数据计算盈亏比：")
print("=" * 65)
print(f"{'组号':<4} | {'平均收益率':<10} | {'胜率':<6} | {'盈亏比':<8} | {'备注':<15}")
print("=" * 65)

for group in group_data:
    group_num = group["group"]
    avg_return = group["avg_return"]
    win_rate = group["win_rate"]
    
    # 使用简化模型计算盈亏比
    # 假设：总交易次数为100，盈利交易的平均盈利和亏损交易的平均亏损相同
    total_trades = 100
    win_trades = win_rate * total_trades
    loss_trades = total_trades - win_trades
    
    # 计算盈亏比
    if win_rate > 0 and win_rate < 1:
        # 使用平均收益率和胜率计算盈亏比的近似值
        # 公式推导：
        # avg_return = (win_trades * P + loss_trades * L) / total_trades
        # 其中 P 是平均盈利，L 是平均亏损（负数）
        # 盈亏比 R = P / |L|
        # 代入可得：avg_return = (win_trades * R * |L| - loss_trades * |L|) / total_trades
        # 整理得：avg_return = |L| * (win_trades * R - loss_trades) / total_trades
        # 我们假设 |L| 是平均收益率的某种比例，这里使用一个合理的近似值
        
        # 对于正收益的组，使用以下方法计算盈亏比
        if avg_return > 0:
            # 计算盈利的总贡献
            total_profit_contribution = avg_return * total_trades
            
            # 假设亏损的总贡献为负的盈利总贡献的某个比例
            # 这里我们使用一个简单的模型：总亏损贡献 = -total_profit_contribution * (loss_trades / win_trades)
            # 这个假设基于盈亏平衡的概念
            total_loss_contribution = -total_profit_contribution * (loss_trades / win_trades)
            
            # 计算平均盈利和平均亏损
            avg_profit = (total_profit_contribution) / win_trades
            avg_loss = abs(total_loss_contribution / loss_trades)
            
            if avg_loss > 0:
                profit_loss_ratio = avg_profit / avg_loss
            else:
                profit_loss_ratio = float('inf')
        else:
            # 对于负收益的组，盈亏比通常没有意义
            profit_loss_ratio = -1.0
    else:
        profit_loss_ratio = -1.0
    
    # 添加备注
    if group_num == 10:
        remark = "最佳分组"
    elif group_num == 1:
        remark = "最差分组"
    elif avg_return > 0:
        remark = "正收益"
    else:
        remark = "负收益"
    
    print(f"{group_num:<4} | {avg_return:<10.6f} | {win_rate:<6.4f} | {profit_loss_ratio:<8.4f} | {remark:<15}")

print("=" * 65)
print("注：以上盈亏比是基于简化模型的近似计算结果。")
print("准确的盈亏比需要基于每个分组的详细交易数据进行计算。")