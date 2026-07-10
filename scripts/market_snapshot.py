"""生成市场快照（行情+板块弹簧），输出 UTF-8 Markdown。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.stdout.reconfigure(encoding='utf-8')

from ai_remoney.data.fetcher import fetch_market_heat, fetch_spring_for_signals

SECTORS = ["航天", "券商", "保险", "黄金", "军工", "石油石化", "油运", "水利", "建材", "光伏", "储能", "旅游", "AI", "机器人", "半导体"]

print("# 市场快照")

heat = fetch_market_heat()
print(f"\n## 市场热度")
print(f"- 日期: {heat.date}")
print(f"- 上证: {heat.sh_volume:.0f}亿 | 深证: {heat.sz_volume:.0f}亿 | 合计: {heat.total_volume:.0f}亿")
print(f"- 水温: {heat.temperature}")
print(f"- 上证收盘: {heat.sh_close:.1f}")

print(f"\n## 板块价格弹簧")
print(f"| 板块 | 5日涨跌 | 10日涨跌 | 20日涨跌 | 弹簧状态 | 催化剂效果 |")
print(f"|------|---------|---------|---------|---------|-----------|")

springs = fetch_spring_for_signals(SECTORS)
for s in SECTORS:
    sp = springs[s]
    flag = "⚠️" if sp.pct_5d == 0 and sp.pct_10d == 0 else ""
    print(f"| {sp.sector}{flag} | {sp.pct_5d:+.1f}% | {sp.pct_10d:+.1f}% | {sp.pct_20d:+.1f}% | {sp.state} | {sp.effect} |")
