"""信号日报生成器

汇总多维度推理结果，输出结构化信号日报。
"""

from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

from ai_remoney.engine.reasoner import BigMoneyRead, Signal, Intelligence


@dataclass
class DailyReport:
    """信号日报"""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    market_heat: dict = field(default_factory=dict)
    signals: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add_signal(self, intel: Intelligence, read: BigMoneyRead):
        self.signals.append({
            "summary": intel.summary,
            "source": intel.source,
            "dimension": intel.dimension,
            "verification": intel.verification.value,
            "affected_sectors": intel.affected_sectors,
            "affected_stocks": intel.affected_stocks,
            "interpretation": read.interpretation,
            "likely_action": read.likely_action,
            "timing": read.timing,
            "signal": read.signal.value,
            "certainty": read.certainty.value,
            "reasoning": read.reasoning_chain,
        })

    def summarize(self) -> dict:
        counts = Counter(s["signal"] for s in self.signals)
        return {
            "enter": counts.get("enter", 0),
            "counter": counts.get("counter", 0),
            "watch": counts.get("watch", 0),
            "skip": counts.get("skip", 0),
            "total": len(self.signals),
            "actionable": counts.get("enter", 0) + counts.get("counter", 0),
        }

    def to_markdown(self) -> str:
        """输出 Markdown 格式日报"""
        lines = [
            f"## 📡 信号日报 {self.date}",
            "",
            "### 🌡 市场热度",
            f"- 前日成交量：{self.market_heat.get('prev_day', 'N/A')}",
            f"- 7日均量：{self.market_heat.get('avg_7d', 'N/A')}",
            f"- 本月累计：{self.market_heat.get('monthly', 'N/A')}",
            f"- 水温：{self.market_heat.get('temperature', 'N/A')}",
            "",
            "### 📋 新增信号",
            "",
            "| # | 信息 | 维度 | 核验 | 标的 | 信号 | 确定性 | 时间窗口 |",
            "|---|------|------|------|------|------|--------|----------|",
        ]
        for i, s in enumerate(self.signals, 1):
            signal_emoji = {"enter": "🟢", "counter": "🔴", "watch": "🟡", "skip": "⚪"}.get(s["signal"], "❓")
            lines.append(
                f"| {i} | {s['summary'][:60]} | {s['dimension']} | {s['verification']} "
                f"| {', '.join(s['affected_sectors'][:2]) or '待定'} "
                f"| {signal_emoji} {s['signal']} | {s['certainty']} | {s['timing']} |"
            )

        s = self.summarize()
        lines.extend([
            "",
            "### 📊 信号汇总",
            f"- 🟢 ENTER: {s['enter']}",
            f"- 🔴 COUNTER: {s['counter']}",
            f"- 🟡 WATCH: {s['watch']}",
            f"- ⚪ SKIP: {s['skip']}",
            f"- **可操作信号：{s['actionable']} / {s['total']}**",
        ])

        # V0/V1 警告
        low_v = [sig for sig in self.signals if sig["verification"] in ("V0", "V1")]
        if low_v:
            lines.extend([
                "",
                "### ⚠️ 核验不足",
                f"以下 {len(low_v)} 条信息核验等级不足（V0-V1），**不作进场依据**：",
            ])
            for sig in low_v:
                lines.append(f"- [{sig['verification']}] {sig['summary'][:80]}")

        return "\n".join(lines)
