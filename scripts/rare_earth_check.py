"""Check rare earth sector stocks real-time."""
import sys
sys.path.insert(0, './src')
sys.stdout.reconfigure(encoding='utf-8')
from ai_remoney.data.sina_fetcher import fetch_quote

stocks = {
    'sh600111': '北方稀土',
    'sh600392': '盛和资源',
    'sh600259': '广晟有色',
    'sz000970': '中科三环',
    'sz000831': '中国稀土',
    'sh600010': '包钢股份',
    'sz300748': '金力永磁',
}

print("# 稀土板块实时行情\n")
print("| 名称 | 代码 | 现价 | 涨跌% | 最高 | 最低 | 昨收 |")
print("|------|------|------|-------|------|------|------|")
for code, name in stocks.items():
    q = fetch_quote(code)
    if q:
        print(f"| {name} | {code} | {q.close:.2f} | {q.pct_chg:+.2f}% | {q.high:.2f} | {q.low:.2f} | {q.prev_close:.2f} |")
    else:
        print(f"| {name} | {code} | - | - | - | - | - |")
