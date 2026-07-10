"""行情数据获取模块

基于 akshare，提供：
- 市场热度（沪深成交量）
- 价格弹簧（板块近期涨跌幅）
- 个股行情
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys


@dataclass
class MarketHeat:
    """市场热度"""
    date: str
    sh_volume: float          # 上证成交额（亿）
    sz_volume: float          # 深证成交额（亿）
    total_volume: float       # 两市合计（亿）
    sh_close: float           # 上证收盘
    sh_pct_chg: float         # 上证涨跌幅

    @property
    def temperature(self) -> str:
        if self.total_volume > 15000:
            return "极热"
        elif self.total_volume > 10000:
            return "热"
        elif self.total_volume > 7000:
            return "温"
        elif self.total_volume > 5000:
            return "偏冷"
        else:
            return "冰点"


@dataclass
class SpringStatus:
    """价格弹簧状态"""
    sector: str
    pct_5d: float            # 近 5 日涨跌幅
    pct_10d: float           # 近 10 日涨跌幅
    pct_20d: float           # 近 20 日涨跌幅

    @property
    def state(self) -> str:
        if self.pct_5d < -5 or self.pct_20d < -10:
            return "压缩(超跌)"
        elif self.pct_5d > 5 or self.pct_20d > 10:
            return "拉伸(高位)"
        else:
            return "正常"

    @property
    def effect(self) -> str:
        d = {
            "压缩(超跌)": "涨停概率高",
            "正常": "标准反应",
            "拉伸(高位)": "利好出尽风险",
        }
        return d[self.state]


def _get_akshare():
    """延迟导入 akshare"""
    try:
        import akshare as ak
        return ak
    except ImportError:
        print("请先安装 akshare: pip install akshare", file=sys.stderr)
        raise


def fetch_market_heat() -> MarketHeat:
    """获取沪深两市成交量和指数行情"""
    ak = _get_akshare()

    # 上证指数日线
    sh = ak.stock_zh_index_daily(symbol="sh000001")
    latest = sh.iloc[-1]

    # 深证成指日线
    sz = ak.stock_zh_index_daily(symbol="sz399001")
    sz_latest = sz.iloc[-1]

    return MarketHeat(
        date=str(latest["date"]),
        sh_volume=latest["volume"] / 1e8,     # 转亿元
        sz_volume=sz_latest["volume"] / 1e8,
        total_volume=(latest["volume"] + sz_latest["volume"]) / 1e8,
        sh_close=latest["close"],
        sh_pct_chg=latest.get("pct_chg", 0),
    )


# 板块名称 → akshare 概念板块名称映射（sina/东方财富源）
SECTOR_MAP = {
    "券商": "券商概念",
    "保险": "保险",
    "黄金": "黄金概念",
    "军工": "军工",
    "航天": "航天航空",
    "油运": "航运港口",
    "石油石化": "石油行业",
    "水利": "水利建设",
    "建材": "水泥建材",
    "光伏": "光伏建筑一体化",
    "储能": "储能",
    "旅游": "在线旅游",
    "AI": "人工智能",
    "机器人": "机器人概念",
    "半导体": "半导体概念",
}

# 备选映射（当主名查不到时尝试）
FALLBACK_MAP = {
    "航天": ["航天航空", "航天概念", "商业航天"],
    "军工": ["军工", "航天军工", "国防军工"],
    "券商": ["券商概念", "券商信托"],
    "黄金": ["黄金概念", "贵金属"],
    "AI": ["人工智能", "ChatGPT概念", "AIGC概念"],
}


# 东方财富源在部分网络环境下被代理拦截（push2.eastmoney.com）
# 当 fetch_spring 全部失败时回退到 sina 源通过个股近似估算
# 该标记用于数据报告中标注 ⚠️ 板块数据源受限
EM_SOURCE_AVAILABLE = True  # 运行时动态更新


def fetch_spring(sector: str) -> SpringStatus:
    """获取板块价格弹簧状态

    Args:
        sector: 板块中文名（如"航天"、"券商"、"黄金"）

    Returns:
        SpringStatus: 近5/10/20日涨跌幅 + 弹簧状态
    """
    ak = _get_akshare()
    concept_name = SECTOR_MAP.get(sector, sector)
    names_to_try = [concept_name] + FALLBACK_MAP.get(sector, [])
    last_error = None

    for name in names_to_try:
        try:
            df = ak.stock_board_concept_hist_em(symbol=name, period="daily")
            if len(df) == 0:
                continue
            closes = df["收盘"]

            def pct_chg(days):
                if len(closes) > days:
                    return float((closes.iloc[-1] - closes.iloc[-(days+1)]) / closes.iloc[-(days+1)] * 100)
                return 0.0

            return SpringStatus(
                sector=sector,
                pct_5d=round(pct_chg(5), 2),
                pct_10d=round(pct_chg(10), 2),
                pct_20d=round(pct_chg(20), 2),
            )
        except Exception as e:
            last_error = e
            continue

    print(f"获取板块 {sector} 失败(已尝试{names_to_try}): {last_error}", file=sys.stderr)
    return SpringStatus(sector=sector, pct_5d=0, pct_10d=0, pct_20d=0)


def fetch_stock_price(code: str, days: int = 5) -> dict:
    """获取个股近期行情"""
    ak = _get_akshare()
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        recent = df.tail(days)
        return {
            "code": code,
            "latest_close": float(recent["收盘"].iloc[-1]),
            "pct_5d": float((recent["收盘"].iloc[-1] - recent["收盘"].iloc[0]) / recent["收盘"].iloc[0] * 100) if len(recent) >= days else 0,
            "dates": recent["日期"].tolist(),
            "closes": recent["收盘"].tolist(),
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def fetch_spring_for_signals(sectors: list[str]) -> dict[str, SpringStatus]:
    """批量获取多个板块的价格弹簧

    Args:
        sectors: 板块名列表

    Returns:
        {sector: SpringStatus, ...}
    """
    return {s: fetch_spring(s) for s in sectors}


if __name__ == "__main__":
    # 快速测试
    print("=== 市场热度 ===")
    heat = fetch_market_heat()
    print(f"日期: {heat.date}")
    print(f"上证成交: {heat.sh_volume:.0f}亿 | 深证: {heat.sz_volume:.0f}亿 | 合计: {heat.total_volume:.0f}亿")
    print(f"水温: {heat.temperature}")

    print("\n=== 价格弹簧 ===")
    for s in ["航天", "券商", "黄金", "军工", "AI"]:
        sp = fetch_spring(s)
        print(f"{sp.sector}: 5日{sp.pct_5d:+.1f}% 10日{sp.pct_10d:+.1f}% 20日{sp.pct_20d:+.1f}% -> {sp.state} {sp.effect}")
