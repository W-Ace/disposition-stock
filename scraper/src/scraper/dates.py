"""Date utilities for Taiwan stock trading calendar."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

TAIPEI = ZoneInfo("Asia/Taipei")


def today_taipei() -> date:
    return datetime.now(TAIPEI).date()


def to_roc(d: date) -> str:
    """2026-05-11 -> '115/05/11'."""
    return f"{d.year - 1911:03d}/{d.month:02d}/{d.day:02d}"


def from_roc(s: str) -> date:
    """'115/05/11' or '1150511' -> date."""
    s = s.strip()
    if "/" in s:
        y, m, d = s.split("/")
    else:
        y, m, d = s[:-4], s[-4:-2], s[-2:]
    return date(int(y) + 1911, int(m), int(d))


def to_compact_ad(d: date) -> str:
    """2026-05-11 -> '20260511' (for TWSE query strings)."""
    return d.strftime("%Y%m%d")


def recent_weekdays(end: date, n: int) -> list[date]:
    """Return the last `n` weekdays (Mon-Fri) ending on or before `end`.

    Does not account for TW market holidays — those days yield empty data
    which we tolerate downstream.
    """
    out: list[date] = []
    cur = end
    while len(out) < n:
        if cur.weekday() < 5:
            out.append(cur)
        cur -= timedelta(days=1)
    return out
