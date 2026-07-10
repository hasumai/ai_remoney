"""Test individual stock data availability."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.stdout.reconfigure(encoding='utf-8')

import akshare as ak

stocks = {
    '东方财富': '300059',
    '山东黄金': '600547',
    '中航沈飞': '600760',
    '航天电子': '600879',
    '中信证券': '600030',
    '中国船舶': '600150',
    '恒力石化': '600346',
    '中远海能': '600026',
    '阳光电源': '300274',
    '张家界': '000430',
}

for name, code in stocks.items():
    try:
        df = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
        if len(df) == 0:
            print(f'{name}({code}): no data')
            continue
        latest = df.iloc[-1]
        prev5 = df.iloc[-6] if len(df) > 5 else df.iloc[0]
        prev20 = df.iloc[-21] if len(df) > 20 else df.iloc[0]
        pct5 = (latest['收盘'] - prev5['收盘']) / prev5['收盘'] * 100
        pct20 = (latest['收盘'] - prev20['收盘']) / prev20['收盘'] * 100
        print(f"{name}({code}): close={latest['收盘']:.2f} | 5d={pct5:+.1f}% | 20d={pct20:+.1f}% | date={latest['日期']}")
    except Exception as e:
        print(f'{name}({code}): FAIL - {type(e).__name__}: {e}')
