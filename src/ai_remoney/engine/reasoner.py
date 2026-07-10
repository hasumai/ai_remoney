"""大资金行为推理引擎

核心逻辑：给定一条信息，推理大资金会如何反应。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Signal(str, Enum):
    ENTER = "enter"        # 大资金大概率进场 → 抢跑
    COUNTER = "counter"    # 大资金大概率出货 → 反制
    WATCH = "watch"        # 不确定 → 观察
    SKIP = "skip"          # 无关 → 忽略


class Certainty(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationLevel(str, Enum):
    V0 = "V0"  # 传闻/未证实
    V1 = "V1"  # 单一来源
    V2 = "V2"  # 多源交叉验证
    V3 = "V3"  # 官方/一手数据


@dataclass
class Intelligence:
    """一条情报"""
    summary: str
    source: str
    dimension: str  # 8 维之一
    verification: VerificationLevel = VerificationLevel.V0
    affected_sectors: list[str] = field(default_factory=list)
    affected_stocks: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BigMoneyRead:
    """大资金解读结果"""
    will_see: bool           # 大资金会看到吗
    interpretation: str      # 他们会怎么解读（利好/利空/中性）
    likely_action: str       # 可能的行动描述
    timing: str              # 行动时间窗口
    signal: Signal           # 信号
    certainty: Certainty     # 确定性
    reasoning_chain: str     # 推理链


def reason(intel: Intelligence, market_context: dict | None = None) -> BigMoneyRead:
    """对一条情报执行大资金行为推理。

    这是核心推理函数。根据信息维度、核验等级和市场上下文，
    推理大资金的可能反应。

    Args:
        intel: 情报对象
        market_context: 市场上下文 {volume, trend, sentiment, ...}

    Returns:
        BigMoneyRead 解读结果
    """
    # V0 信息不做进场判断
    if intel.verification in (VerificationLevel.V0, VerificationLevel.V1):
        return BigMoneyRead(
            will_see=True,
            interpretation="信息核验等级不足",
            likely_action="无法判断",
            timing="N/A",
            signal=Signal.WATCH,
            certainty=Certainty.LOW,
            reasoning_chain=f"核验等级 {intel.verification.value}，不足以支撑判断。需升至 V2+。",
        )

    # 维度路由
    dimension_reasoners = {
        "市场热度": _reason_market_heat,
        "国家政策": _reason_policy,
        "头部厂商": _reason_industry_leader,
        "消费端": _reason_consumer,
        "国际关系": _reason_international,
        "供应链": _reason_supply_chain,
        "突发灾害": _reason_disaster,
        "AI与机器人": _reason_ai_robotics,
    }

    reasoner = dimension_reasoners.get(intel.dimension, _reason_generic)
    return reasoner(intel, market_context or {})


def _reason_market_heat(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    """市场热度维度推理"""
    volume = ctx.get("volume", 0)
    if volume > 10000:
        interpretation = "万亿成交活跃，大资金有出货窗口"
        signal = Signal.WATCH  # 过热可能是顶
    elif volume < 5000:
        interpretation = "地量，大资金可能在布局"
        signal = Signal.WATCH  # 冰点可能是底
    else:
        interpretation = "正常交投"
        signal = Signal.SKIP
    return BigMoneyRead(True, interpretation, "观望", "持续", signal, Certainty.MEDIUM, f"成交量 {volume}亿")


def _reason_policy(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    """政策维度推理——政策是大资金最强的驱动信号"""
    return BigMoneyRead(
        True,
        f"政策信号：{intel.summary[:80]}",
        "政策发布后当日/次日即反应，大资金会快速入场",
        "当日-次日",
        Signal.ENTER,
        Certainty.MEDIUM,
        f"政策级别判断 + 是否超预期 + 对应板块映射 → {intel.summary[:100]}",
    )


def _reason_industry_leader(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "龙头动向→上下游联动", "1-3日", Signal.WATCH, Certainty.MEDIUM, intel.summary[:100])


def _reason_consumer(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "消费数据验证后加仓或出货", "3-7日", Signal.WATCH, Certainty.MEDIUM, intel.summary[:100])


def _reason_international(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    """国际关系维度——反应极快"""
    return BigMoneyRead(
        True,
        f"地缘事件：{intel.summary[:80]}",
        "地缘事件大资金反应极快（分钟内），映射贵金属/能源/军工",
        "即时-当日",
        Signal.ENTER,
        Certainty.MEDIUM,
        f"地缘冲突→避险资产→映射A股标的 → {intel.summary[:100]}",
    )


def _reason_supply_chain(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "运价先行→航运/石油标的", "1-3日", Signal.ENTER, Certainty.MEDIUM, intel.summary[:100])


def _reason_disaster(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "灾后重建逻辑→建材/工程", "1-3日", Signal.ENTER, Certainty.MEDIUM, intel.summary[:100])


def _reason_ai_robotics(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "概念驱动→快进快出", "当日-3日", Signal.ENTER, Certainty.LOW, f"AI/机器人概念→{intel.summary[:100]}")


def _reason_generic(intel: Intelligence, ctx: dict) -> BigMoneyRead:
    return BigMoneyRead(True, intel.summary[:80], "未知维度", "无法判断", Signal.WATCH, Certainty.LOW, intel.summary[:100])
