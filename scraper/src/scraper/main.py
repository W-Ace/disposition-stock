"""Entry point: produce snapshot.json for the frontend."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from .classify import classify, ClassifiedStock
from .dates import TAIPEI, today_taipei
from .enrich import enrich
from .source import coalesce_per_stock, count_notices_per_stock, load_active_disposals


def _serialize(s: ClassifiedStock, e) -> dict:
    return {
        "code": s.code,
        "name": (e.name if e and e.name else s.name),
        "market": e.market if e else None,
        "bucket": s.bucket,
        "industry": e.industry if e else None,
        "close": e.close if e else None,
        "change": e.change if e else None,
        "change_pct": e.change_pct if e else None,
        "value_100m": e.value_100m if e else None,
        "can_intraday": e.can_intraday if e else False,
        "notice_count_30d": s.notice_count_30d,
        "measure": s.measure,
        "auction_minutes": s.auction_minutes,
        "prepay_full": s.prepay_full,
        "period_start": s.period_start.isoformat() if s.period_start else None,
        "period_end": s.period_end.isoformat() if s.period_end else None,
        "condition": s.condition,
    }


def build_snapshot(today: date | None = None) -> dict:
    today = today or today_taipei()
    print(f"[main] trading day: {today}")

    import finlab
    finlab.login()

    disposals = coalesce_per_stock(load_active_disposals(today))
    print(f"[main] active disposals (after coalesce): {len(disposals)}")

    notice_counts = count_notices_per_stock(today, lookback_days=30)
    print(f"[main] 30-day attention: {len(notice_counts)} stocks with ≥1 notice")

    classified = classify(today, disposals, notice_counts)
    print(f"[main] classified: {len(classified)} stocks")

    enrich_map = enrich([s.code for s in classified])
    print(f"[main] enriched: {sum(1 for v in enrich_map.values() if v.close is not None)} with price")

    buckets: dict[str, list[dict]] = {"risk": [], "disposal": [], "exiting": []}
    for s in classified:
        buckets[s.bucket].append(_serialize(s, enrich_map.get(s.code)))

    buckets["risk"].sort(key=lambda x: -x["notice_count_30d"])
    buckets["disposal"].sort(key=lambda x: x["period_end"] or "")
    buckets["exiting"].sort(key=lambda x: x["period_end"] or "")

    return {
        "updated_at": datetime.now(TAIPEI).isoformat(timespec="seconds"),
        "trading_day": today.isoformat(),
        **buckets,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="../web/public/data/snapshot.json", type=Path)
    ap.add_argument("--date", help="Override trading day (YYYY-MM-DD)")
    args = ap.parse_args()

    today = date.fromisoformat(args.date) if args.date else None
    snap = build_snapshot(today=today)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snap, ensure_ascii=False, indent=2))
    print(f"[main] wrote {args.output}: risk={len(snap['risk'])} disposal={len(snap['disposal'])} exiting={len(snap['exiting'])}")


if __name__ == "__main__":
    main()
