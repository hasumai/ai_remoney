"""Sina Finance direct API — bypasses akshare + Eastmoney proxy."""
import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

codes = {
    'sh600547': '山东黄金',
    'sh600760': '中航沈飞',
    'sh600879': '航天电子',
    'sh600030': '中信证券',
    'sh600150': '中国船舶',
    'sh600346': '恒力石化',
    'sh600026': '中远海能',
    'sz300059': '东方财富',
    'sz300274': '阳光电源',
    'sz000430': '张家界',
    'sh601318': '中国平安',
}

for code, name in codes.items():
    try:
        url = f'https://hq.sinajs.cn/list={code}'
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('gbk')
        parts = data.split('"')[1].split(',')
        s_name = parts[0]
        open_p = float(parts[1])
        close_y = float(parts[2])
        close = float(parts[3])
        high = float(parts[4])
        low = float(parts[5])
        volume = parts[8] if parts[8] else '0'
        pct = (close - close_y) / close_y * 100 if close_y else 0
        print(f"{name}({code}): close={close:.2f} open={open_p:.2f} high={high:.2f} low={low:.2f} pct={pct:+.2f}% volume={volume}")
    except Exception as e:
        print(f"{name}({code}): FAIL - {e}")
