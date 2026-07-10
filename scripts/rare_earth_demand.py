"""稀土需求端板块 7/9-7/10 表现"""
import sys
sys.path.insert(0, './src')
sys.stdout.reconfigure(encoding='utf-8')
from ai_remoney.data.sina_fetcher import fetch_quote

stocks = {
    # 新能源车（稀土永磁电机最大需求）
    'sz300750': '宁德时代',
    'sz002594': '比亚迪',
    # 风电
    'sh601012': '隆基绿能',
    'sz300274': '阳光电源',
    # 机器人
    'sh688017': '绿的谐波',
    'sz300124': '汇川技术',
    # AI/服务器
    'sh603019': '中科曙光',
    'sz300308': '中际旭创',
    # 空调（季节性需求）
    'sz000651': '格力电器',
    'sz000333': '美的集团',
    # 军工（稀土另一需求端）
    'sh600760': '中航沈飞',
    'sh600150': '中国船舶',
    # 稀土（对比基准）
    'sh600111': '北方稀土',
    'sh600392': '盛和资源',
    'sz000970': '中科三环',
}

print("# 稀土需求端 vs 稀土板块 7/10 表现\n")
print("| 板块 | 标的 | 涨跌% | 对稀土的影响 |")
print("|------|------|-------|-------------|")

demand_groups = {
    '🔋 新能源车': ['宁德时代', '比亚迪'],
    '💨 风电光伏': ['隆基绿能', '阳光电源'],
    '🤖 机器人': ['绿的谐波', '汇川技术'],
    '🖥 AI/算力': ['中科曙光', '中际旭创'],
    '❄ 空调消费': ['格力电器', '美的集团'],
    '🛡 军工': ['中航沈飞', '中国船舶'],
}

稀土组 = ['北方稀土', '盛和资源', '中科三环']

for group, names in demand_groups.items():
    for name in names:
        code = [k for k, v in stocks.items() if v == name][0]
        q = fetch_quote(code)
        if q:
            impact = ""
            if q.pct_chg > 5:
                impact = "🟢 强拉动"
            elif q.pct_chg > 0:
                impact = "🟢 弱拉动"
            elif q.pct_chg > -3:
                impact = "🟡 中性"
            elif q.pct_chg > -5:
                impact = "🟠 拖累"
            else:
                impact = "🔴 严重拖累"
            print(f"| {group} | {name} | {q.pct_chg:+.2f}% | {impact} |")

print(f"| | | | |")
print(f"| **稀土矿** | **北方稀土** | — | ← 你的持仓 |")
print(f"| **稀土磁材** | **中科三环** | — | |")
