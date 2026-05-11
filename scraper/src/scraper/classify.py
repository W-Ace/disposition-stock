"""Classify into risk / disposal / exiting buckets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Sequence

from .source import DisposalRow

RISK_THRESHOLD = 8          # 風險股：30 日累計注意 ≥ N 次。
                            # 處置觸發是 30 日內 12 次，所以 8+ 代表已逼近門檻；
                            # 數字調小會大幅增加候選名單。
EXITING_DAYS_LEFT = 1       # 即將出關：處置迄日 - 今日 ≤ 1 個營業日


@dataclass
class ClassifiedStock:
    code: str
    name: str
    bucket: str               # 'risk' / 'disposal' / 'exiting'
    notice_count_30d: int
    measure: str | None
    auction_minutes: int | None
    prepay_full: bool
    period_start: date | None
    period_end: date | None
    condition: str | None


def _weekdays_between(a: date, b: date) -> int:
    if b < a:
        return 0
    n = 0
    cur = a
    while cur <= b:
        if cur.weekday() < 5:
            n += 1
        cur += timedelta(days=1)
    return n


def classify(
    today: date,
    disposals: Sequence[DisposalRow],
    notice_counts: dict[str, int],
) -> list[ClassifiedStock]:
    out: list[ClassifiedStock] = []
    in_disposal: set[str] = set()

    for d in disposals:
        in_disposal.add(d.code)
        days_left = _weekdays_between(today, d.period_end) - 1
        bucket = "exiting" if days_left <= EXITING_DAYS_LEFT else "disposal"
        out.append(ClassifiedStock(
            code=d.code, name=d.name, bucket=bucket,
            notice_count_30d=notice_counts.get(d.code, 0),
            measure=d.measure, auction_minutes=d.auction_minutes,
            prepay_full=d.prepay_full,
            period_start=d.period_start, period_end=d.period_end,
            condition=d.condition,
        ))

    for code, count in notice_counts.items():
        if code in in_disposal or count < RISK_THRESHOLD:
            continue
        out.append(ClassifiedStock(
            code=code, name=code, bucket="risk",
            notice_count_30d=count,
            measure=None, auction_minutes=None, prepay_full=False,
            period_start=None, period_end=None, condition=None,
        ))

    return out
