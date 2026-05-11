"""FinLab-based source for attention/disposal data.

FinLab tables used:
- `disposal_information`: 處置事件 with start/end/measure/auction interval (TWSE + TPEx + CB)
- `trading_attention`: 注意事件 log; we count per-stock occurrences in the last 30 weekdays

FinLab refreshes 19:00 (margin 21:30) on each trading day.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class DisposalRow:
    code: str
    name: str
    measure: str              # 第一次處置 / 第二次處置 / 收足全部款券 / ...
    auction_minutes: int | None
    period_start: date
    period_end: date
    condition: str            # 處置條件 short text
    prepay_full: bool         # parsed from 處置內容


def _is_common_stock(code: str) -> bool:
    """Keep 4-digit common stocks; drop ETFs (00xx), CBs (5 digits), warrants (6 digits)."""
    base = code.rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if not base.isdigit():
        return False
    if len(base) != 4:
        return False
    return not base.startswith("00")


def _detect_prepay_full(text: str) -> bool:
    return any(s in text for s in ("全體投資人", "所有投資人", "全面預收"))


def _to_python_date(ts) -> date:
    return ts.date() if hasattr(ts, "date") else ts


def load_active_disposals(today: date) -> list[DisposalRow]:
    """Disposal rows whose [start, end] window contains `today`.

    Common stocks only (no ETF/CB/warrant)."""
    import pandas as pd
    from finlab import data

    df = data.get("disposal_information").copy()
    df["處置開始時間"] = pd.to_datetime(df["處置開始時間"])
    df["處置結束時間"] = pd.to_datetime(df["處置結束時間"])
    today_ts = pd.Timestamp(today)
    active = df[(df["處置開始時間"] <= today_ts) & (df["處置結束時間"] >= today_ts)]

    rows: list[DisposalRow] = []
    for _, r in active.iterrows():
        code = str(r["symbol"]).strip()
        if not _is_common_stock(code):
            continue
        minutes = int(r["分時交易"]) if r["分時交易"] == r["分時交易"] else None  # NaN-safe
        rows.append(DisposalRow(
            code=code,
            name=str(r["證券名稱"]).strip(),
            measure=str(r["處置措施"]).strip(),
            auction_minutes=minutes,
            period_start=_to_python_date(r["處置開始時間"]),
            period_end=_to_python_date(r["處置結束時間"]),
            condition=str(r["處置條件"]).strip(),
            prepay_full=_detect_prepay_full(str(r["處置內容"])),
        ))
    return rows


def coalesce_per_stock(rows: list[DisposalRow]) -> list[DisposalRow]:
    """A stock can have multiple active rows (1st + 2nd + extra measures).
    Pick the most restrictive: 第二次處置 > 第一次處置 > others; tie-break by latest start."""
    rank = {"第二次處置": 3, "第一次處置": 2}
    best: dict[str, DisposalRow] = {}
    for r in rows:
        key = r.code
        if key not in best:
            best[key] = r
            continue
        cur = best[key]
        if (rank.get(r.measure, 1), r.period_start) > (rank.get(cur.measure, 1), cur.period_start):
            best[key] = r
    return list(best.values())


def count_notices_per_stock(today: date, lookback_days: int = 30) -> dict[str, int]:
    """Count attention events per stock in the past N calendar days.

    Common stocks only.
    """
    import pandas as pd
    from finlab import data

    df = data.get("trading_attention").copy()
    df["date"] = pd.to_datetime(df["date"])
    df["symbol"] = df["symbol"].astype(str)
    cutoff = pd.Timestamp(today - timedelta(days=lookback_days))
    recent = df[(df["date"] >= cutoff) & (df["date"] <= pd.Timestamp(today))]
    recent = recent[recent["symbol"].map(_is_common_stock)]
    return {k: int(v) for k, v in recent.groupby("symbol").size().to_dict().items()}
