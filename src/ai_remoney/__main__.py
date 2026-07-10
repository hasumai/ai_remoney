"""CLI 入口 — 分析用户输入的新闻/信息"""

import sys
from ai_remoney.dimensions.classifier import classify
from ai_remoney.engine.reasoner import reason, Intelligence, VerificationLevel
from ai_remoney.signals.reporter import DailyReport


def analyze_news(text: str, source: str = "用户输入", verification: str = "V1") -> str:
    """分析一条新闻并返回信号"""
    # 1. 维度分类
    dims = classify(text)
    top_dim = dims[0][0] if dims else "未分类"
    confidence = dims[0][1] if dims else 0.0

    # 2. 构建情报对象
    intel = Intelligence(
        summary=text[:200],
        source=source,
        dimension=top_dim,
        verification=VerificationLevel(verification),
    )

    # 3. 推理
    read = reason(intel)

    # 4. 生成报告
    report = DailyReport()
    report.add_signal(intel, read)

    # 5. 输出
    output = []
    output.append(f"📌 维度：{top_dim}（置信度 {confidence:.0%}）")
    output.append(f"🔍 大资金会看到吗：{'会' if read.will_see else '不会'}")
    output.append(f"📖 解读：{read.interpretation}")
    output.append(f"⏱ 时间窗口：{read.timing}")
    output.append(f"🎯 信号：{read.signal.value.upper()}")
    output.append(f"📊 确定性：{read.certainty.value}")
    output.append(f"💭 推理链：{read.reasoning_chain}")

    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(analyze_news(text))
    else:
        print("用法：python -m ai_remoney <新闻文本>")
