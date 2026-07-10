"""稀土板块近一周/近一月日线数据"""
import sys
sys.path.insert(0, './src')
sys.stdout.reconfigure(encoding='utf-8')

import akshare as ak

stocks = {
    'sh600111': '北方稀土',
    'sh600392': '盛和资源',
    'sh600259': '广晟有色',
    'sz000970': '中科三环',
    'sz000831': '中国稀土',
}

for code, name in stocks.items():
    try:
        # Try Sina source first (faster)
        df = ak.stock_zh_a_hist(symbol=code.replace('sh','').replace('sz',''), period='daily', adjust='qfq')
        if len(df) == 0:
            print(f"{name}: no data")
            continue

        recent = df.tail(15)
        print(f"\n## {name} ({code}) — 近15个交易日")
        print(f"| 日期 | 开盘 | 收盘 | 最高 | 最低 | 涨跌% |")
        print(f"|------|------|------|------|------|-------|")
        for _, row in recent.iterrows():
            pct = (row['收盘'] - row['开盘']) / row['开盘'] * 100 if row['开盘'] else 0
            print(f"| {row['日期']} | {row['开盘']:.2f} | {row['收盘']:.2f} | {row['最高']:.2f} | {row['最低']:.2f} | {pct:+.2f}% |")

        # Key stats
        close5 = recent['收盘'].iloc[-6] if len(recent) > 5 else recent['收盘'].iloc[0]
        close10 = recent['收盘'].iloc[-11] if len(recent) > 10 else recent['收盘'].iloc[0]
        close20 = recent['收盘'].iloc[-21] if len(recent) > 20 else recent['收盘'].iloc[0]
        latest = recent['收盘'].iloc[-1]
        high15 = recent['最高'].max()
        low15 = recent['最低'].min()

        pct5 = (latest - close5) / close5 * 100
        pct10 = (latest - close10) / close10 * 100
        pct20 = (latest - close20) / close20 * 100
        from_high = (latest - high15) / high15 * 100

        print(f"\n**统计**: 5日{pct5:+.1f}% | 10日{pct10:+.1f}% | 20日{pct20:+.1f}% | 距15日高点{from_high:.1f}% | 15日区间 {low15:.2f}-{high15:.2f}")
    except Exception as e:
        print(f"\n{name}: FAIL - {type(e).__name__}: {e}")
