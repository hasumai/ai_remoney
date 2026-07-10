"""稀土近两周日线 — 直接走 Sina 历史 API（不走 Eastmoney）"""
import urllib.request, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

stocks = [
    ('sh600111', '北方稀土'),
    ('sh600392', '盛和资源'),
    ('sh600259', '广晟有色'),
    ('sz000970', '中科三环'),
    ('sz000831', '中国稀土'),
]

for code, name in stocks:
    try:
        # Sina daily kline API
        url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen=20'
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))

        print(f"\n## {name} ({code})")
        print(f"| 日期 | 开盘 | 收盘 | 最高 | 最低 | 成交量 |")
        print(f"|------|------|------|------|------|--------|")
        closes = []
        highs = []
        lows = []
        for d in data[-15:]:
            o = float(d['open'])
            c = float(d['close'])
            h = float(d['high'])
            l = float(d['low'])
            closes.append(c)
            highs.append(h)
            lows.append(l)
            vol = d['volume']
            pct = (c - o) / o * 100
            print(f"| {d['day']} | {o:.2f} | {c:.2f} | {h:.2f} | {l:.2f} | {vol} |")

        if len(closes) >= 6:
            latest = closes[-1]
            pct5 = (latest - closes[-6]) / closes[-6] * 100
            pct10 = (latest - closes[-11]) / closes[-11] * 100 if len(closes) >= 11 else 0
            pct20 = (latest - closes[0]) / closes[0] * 100
            from_high = (latest - max(highs)) / max(highs) * 100
            print(f"\n**统计**: 5日{pct5:+.1f}% | 10日{pct10:+.1f}% | 20日{pct20:+.1f}% | 距高点{from_high:.1f}% | 区间 {min(lows):.2f}-{max(highs):.2f}")
    except Exception as e:
        print(f"\n{name}: FAIL - {e}")
