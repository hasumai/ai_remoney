"""Check today's index data."""
import sys
sys.path.insert(0, './src')
sys.stdout.reconfigure(encoding='utf-8')
import akshare as ak

indices = {
    'sh000001': '上证指数',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sh000688': '科创50',
}

for code, name in indices.items():
    try:
        df = ak.stock_zh_index_daily(symbol=code)
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        pct = (latest['close'] - prev['close']) / prev['close'] * 100
        print(f"{name}: {latest['close']:.2f} ({pct:+.2f}%) date={latest['date']}")
    except Exception as e:
        print(f"{name}: {e}")
