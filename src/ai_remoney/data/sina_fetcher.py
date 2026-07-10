"""Sina Finance 直接 API — 绕过 Eastmoney 代理限制

实时行情: https://hq.sinajs.cn/list={code}
历史日线: https://money.finance.sina.com.cn/quotes_service/api/...
"""

import urllib.request
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StockQuote:
    code: str
    name: str
    close: float
    open: float
    high: float
    low: float
    prev_close: float
    pct_chg: float
    volume: int

    @property
    def is_limit_up(self) -> bool:
        return abs(self.pct_chg - 10.0) < 0.5

    @property
    def is_limit_down(self) -> bool:
        return abs(self.pct_chg + 10.0) < 0.5


STOCK_MAP = {
    # 券商
    "东方财富": "sz300059",
    "中信证券": "sh600030",
    "华泰证券": "sh601688",
    # 保险
    "中国平安": "sh601318",
    "中国人寿": "sh601628",
    # 黄金
    "山东黄金": "sh600547",
    "中金黄金": "sh600489",
    # 军工
    "中航沈飞": "sh600760",
    "中国船舶": "sh600150",
    # 航天
    "航天电子": "sh600879",
    # 石油石化
    "中石油": "sh601857",
    "中石化": "sh600028",
    "恒力石化": "sh600346",
    "荣盛石化": "sz002493",
    # 油运
    "中远海能": "sh600026",
    "招商轮船": "sh601872",
    # 新能源
    "阳光电源": "sz300274",
    "隆基绿能": "sh601012",
    "宁德时代": "sz300750",
    # AI/半导体
    "中科曙光": "sh603019",
    "中际旭创": "sz300308",
    # 旅游
    "张家界": "sz000430",
    "桂林旅游": "sz000978",
    # 水利/建材
    "中国电建": "sh601669",
    "海螺水泥": "sh600585",
}


def fetch_quote(code: str) -> StockQuote | None:
    """获取单只股票实时行情

    Args:
        code: 新浪格式代码 (sh600547, sz300059)

    Returns:
        StockQuote or None if failed
    """
    try:
        url = f'https://hq.sinajs.cn/list={code}'
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('gbk')
        parts = data.split('"')[1].split(',')
        return StockQuote(
            code=code,
            name=parts[0],
            open=float(parts[1]),
            prev_close=float(parts[2]),
            close=float(parts[3]),
            high=float(parts[4]),
            low=float(parts[5]),
            volume=int(parts[8]) if parts[8] else 0,
            pct_chg=(float(parts[3]) - float(parts[2])) / float(parts[2]) * 100,
        )
    except Exception as e:
        return None


def fetch_batch_quotes(names: list[str]) -> dict[str, StockQuote | None]:
    """批量获取多只股票行情

    Args:
        names: ["东方财富", "山东黄金", ...]

    Returns:
        {name: StockQuote or None, ...}
    """
    results = {}
    for name in names:
        code = STOCK_MAP.get(name)
        if code:
            results[name] = fetch_quote(code)
        else:
            results[name] = None
    return results


def fetch_all_signal_stocks() -> dict[str, StockQuote | None]:
    """获取所有信号相关股票行情"""
    return fetch_batch_quotes(list(STOCK_MAP.keys()))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    quotes = fetch_all_signal_stocks()
    print(f"# 个股行情快照 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n")
    print("| 名称 | 代码 | 收盘 | 涨跌 | 最高 | 最低 | 成交量 | 状态 |")
    print("|------|------|------|------|------|------|--------|------|")
    for name, q in sorted(quotes.items()):
        if q:
            status = ""
            if q.is_limit_up:
                status = "🔥 涨停"
            elif q.is_limit_down:
                status = "❄ 跌停"
            elif q.pct_chg > 5:
                status = "📈 大涨"
            elif q.pct_chg < -5:
                status = "📉 大跌"
            vol_str = f"{q.volume/10000:.0f}万" if q.volume else "-"
            print(f"| {name} | {q.code} | {q.close:.2f} | {q.pct_chg:+.2f}% | {q.high:.2f} | {q.low:.2f} | {vol_str} | {status} |")
        else:
            print(f"| {name} | - | - | - | - | - | - | 获取失败 |")
